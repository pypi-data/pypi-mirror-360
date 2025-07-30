#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul  4 15:23:30 2022

@author: benjamin
"""

import copy
from .optims import ( 
                    cost_function_velocity,
                    optimization_tau,
                    trajectory_fitting,
                    select_best_solution
                     )
from .utils import (     
    sectioning,
    tangential_distance
    )

from .smoothing import smooth_traj
from .tautools import (generate_tau)
from ._parameters import Parameters
from .hdf5tools import read_solution, write_solution
import numpy as np
import itertools

class Trajectory:
    # pylint: disable=too-many-instance-attributes
    # pylint: disable=pointless-string-statement

    signal = None
    sampling_frequency = None
    nature = None
    time_vector = None
    sibling = None
    parameters = None
    movement_units = []
    comparison_indices = None
    filtered_signal = None
        
    # Constructor method
    def __init__(self, *args):
        nargin = len(args)
        for k in range(0, nargin, 2):
            key, value = args[k:k+2]
            setattr(self, key, value)
            
    def copy(self):
        """ Returns a copy of the Trajectory instance """
        return copy.deepcopy(self)  
    
    def create_movement_unit(self, y, idx):
        """ Returns a movement object """
        if len(y[idx[0]:idx[1]]) < 10:
            for i in range(idx[0], idx[1]):
                if i in self.comparison_indices:
                    self.comparison_indices.remove(i)
        return Movement("signal", y[idx[0]:idx[1]], 
                        "sampling_frequency", self.sampling_frequency,
                        "parent", self, 
                        "time_vector", self.time_vector[idx[0]:idx[1]],
                        "indices", (idx[0], idx[1]))
    
    def create_time_vector(self):
        """ Creates the time vector """
        if self.time_vector is None:
            self.time_vector = np.arange(0, len(self.signal))/self.sampling_frequency
            
    def export_solution(self, hdf5_file):
        """ Export fitting solutions into hdf5 file """
        write_solution(self, hdf5_file)           
    
    def fit_trajectory(self, N=6, sigma=4, method='nelder-mead', a=5,
                      nb_simul=1, nb_threads=1, model="tau",
                      fit="position", activation="rect", disable=True,
                      parall="processes", maxiter=200, end=1, cut_end=True,
                      change_duration=False, discard_points=False,
                      dimension=1, filt_method="gaussian"):        
        """ Fits the trajectory using the specified model """
        if model in ["nl-scdo", "scdo", "stam", "tau"]:
            activation = "rect"
        if model in ["nl-gcdo", "gcdo"]:
            activation = "gradual"
            
        if model == "tau" and change_duration and discard_points:
            print(""""WARNING: change_duration and discard_points are
                  both enabled. Will run change_duration and 
                  ignore discard_points""")

        trajectory_fitting(self, N=N, sigma=sigma, method=method, a=a, 
                           nb_simul=nb_simul, nb_threads=nb_threads,
                           model=model, fit=fit, activation=activation, 
                           disable=disable, parall=parall, maxiter=maxiter, 
                           end=end, cut_end=cut_end, 
                           change_duration=change_duration, 
                           discard_points=discard_points,
                           dimension=dimension, filt_method=filt_method)
        
        model_trajectory = self.copy()
        model_trajectory.nature = "model"
        model_trajectory.sibling = self

    def generate_trajectory_from_parameters(self):
        x0 = self.signal[0]
        for n in range(len(self.movement_units)):
            s, o, t = [getattr(self.parameters, name)[n] for name in ["shape", 
                                                                      "onset", 
                                                                    "target"]] 
            m = self.movement_units[n]
            [setattr(m.parameters, name, x) for name, x in zip(["shape", 
                                                                "onset", 
                                                                "target"], 
                                                               [s, o, t])]
            if s is None:
                s = 0.4
                
            m.sibling.signal = generate_tau(s, x0, t,
                                 len(m.signal),
                                 sr=self.sampling_frequency)[0]
            x0 = t
        self.sibling.signal = self.trajectory_sequence()      
        
    def get_movement_parameters(self, a=5, end=1, cut_end=True):        
        """ Creates the model object from the modeled movement units 
        and assigns it to the Trajectory instance """
        if end == 1:
            # y_model = self.trajectory_sequence()
            y_model = list(itertools.chain.from_iterable([movement.sibling.signal[1:] for movement in self.movement_units]))
            y_model.insert(0, self.movement_units[0].signal[0])
        else:
            y_model = list(itertools.chain.from_iterable([movement.sibling.signal for movement in self.movement_units]))
        Model = Trajectory("sibling", self, "signal", np.array(y_model),
                           "nature", "model", 
                           "sampling_frequency", self.sampling_frequency,
                           "movement_units", 
                           [movement.sibling for movement in self.movement_units])
        self.sibling = Model
        
        self.parameters = Parameters()
        keys = ["shape", "onset", "target", "first_activation_step", 
                "second_activation_step", "slope", "local_error", "amplitude",
                "duration", "optimal_start"]
        for key in keys:
            setattr(self.parameters, 
                    key, 
                    [getattr(movement.parameters, key) 
                     for movement in self.movement_units])
        if not cut_end:
            self.comparison_indices = None
       
        try:
            self.parameters.global_error = cost_function_velocity(self.filtered_signal, 
                                                                  Model.signal, 
                                                                  idx_comp=self.comparison_indices,
                                                                  a=a)
        except:
            pass
       
    def segmentation(self, sigma=4, end=1, 
                     dimension=1, filt_method="gaussian"):
        """ Segments the signal into movement units """
        
        if dimension == 2:
            self.signal = tangential_distance(self.signal)
            peak_type = 'min'
        else:
            peak_type = 'all'
        if sigma is not None or sigma > 0:
            y_obs = smooth_traj(self.signal, sigma, filt_method)            
        else:
            y_obs = self.signal

        self.filtered_signal = y_obs        
        self.create_time_vector()
        if dimension == 2:
            y_obs = np.gradient(y_obs, 1/self.sampling_frequency)
        pks, self.comparison_indices = sectioning(y_obs, 
                                                  self.sampling_frequency,
                                                  peak_type=peak_type)
        
        nb_seg = len(pks)
        self.movement_units = [self.create_movement_unit(self.filtered_signal, 
                                                         (pks[n], pks[n+1]+end)) 
                               for n in range(nb_seg-1)]
        
    def trajectory_sequence(self):
        self.sibling.signal = list(itertools.chain.from_iterable([movement.sibling.signal[1:] for movement in self.movement_units]))
        self.sibling.signal.insert(0, self.movement_units[0].signal[0])
        
        return self.sibling.signal

        
class Movement(Trajectory):
    # pylint: disable=too-many-instance-attributes
    # pylint: disable=pointless-string-statement

    parent = None
    indices = None
    
    # Constructor method
    def __init__(self, *args):
        nargin = len(args)
        for k in range(0, nargin, 2):
            key, value = args[k:k+2]
            setattr(self, key, value)
            
    def copy(self):
        """ Returns a copy of the Trajectory instance """
        return copy.deepcopy(self)
    
    def tau_fitting(self, a=5, method="nelder-mead", change_duration=False, 
                    min_duration=0.045, discard_points=False):
        
        start = 0
        if (len(self.signal)-1)/self.parent.sampling_frequency >= min_duration:            
            n_max = int(min_duration*self.parent.sampling_frequency + 1)
            if change_duration:
                solutions = [optimization_tau(self.signal[n:], 
                                         sr=self.sampling_frequency, 
                                         a=a) for n in range(len(self.signal) - n_max)]
                start, k_fit, local_error = select_best_solution(solutions)
            if discard_points and not change_duration:
                solutions = [optimization_tau(self.signal, 
                                         sr=self.sampling_frequency, 
                                         a=a, 
                                         idx_comp=[i for i in range(n, len(self.signal))]) for
                             n in range(len(self.signal) - n_max)]
                start, k_fit, local_error = select_best_solution(solutions)               
            else:
                solution = optimization_tau(self.signal, 
                                         sr=self.sampling_frequency, 
                                         a=a)
                k_fit = solution["x"]
                local_error = solution["fun"]
            
            if not discard_points or change_duration:
                y_model = generate_tau(k_fit, 
                                     self.signal[start], self.signal[-1],
                                     len(self.signal[start:]))[0]
            else:
                T = (len(self.signal)-1)/self.sampling_frequency
                t = np.linspace(0, T, len(self.signal))        
                t_ratio = (1-(np.square(t[start]).astype('f')/np.square(T).astype('f')))
                x0 = -(self.signal[-1] -  self.signal[start])/(t_ratio**(1/k_fit)) + self.signal[-1]
                y_model = generate_tau(k_fit, 
                                     x0, self.signal[-1],
                                     len(self.signal))[0]
                
        else:
            k_fit = None
            y_model = self.signal
            local_error = None
        
        if change_duration:
            effective_start = start
        else:
            effective_start = 0

        self.parameters = Parameters("shape", k_fit, 
                                     "target", self.signal[-1],
                                     "onset", self.time_vector[start], 
                                     "amplitude", self.signal[-1] - self.signal[start],
                                     "duration", self.time_vector[-1] - self.time_vector[start],
                                     "local_error", local_error,
                                     "optimal_start", start)
        
        TauMovement = Movement("signal", y_model, "sibling", self,
                               "parameters", self.parameters, 
                               "indices", self.indices,
                               "time_vector", self.time_vector[effective_start:],
                               "sampling_frequency", self.sampling_frequency)
        self.sibling = TauMovement   
        
def import_solution(hdf5_file):
    """ Import solution stored in hdf5_file """
    datas, keys = read_solution(hdf5_file)

    new_trajectory = Trajectory("signal", datas[0],
                                    "sampling_frequency", datas[-1],
                                    "filtered_signal", datas[1],
                                    "movement_units", [])

    new_sibling = Trajectory("signal", datas[2],
                                       "sampling_frequency", datas[-1], 
                                       "parent", new_trajectory,
                                       "movement_units", [])
    new_parameters = Parameters("parent", new_trajectory)
    for key, value in zip(keys[4:12], datas[4:12]):
        setattr(new_parameters, key, value)
    new_trajectory.parameters = new_parameters
    new_trajectory.sibling = new_sibling

    nb_seg = len(datas[3]) - 1
    for n in range(nb_seg):
        local_indices = [datas[3][n], datas[3][n+1]+1]    
        if n == nb_seg - 1:
            local_indices = [datas[3][n], datas[3][n+1]]   
        new_mu = Movement("signal", 
                          new_trajectory.filtered_signal[local_indices[0]:local_indices[1]],
                          "sampling_frequency", datas[-1],
                          "indices", local_indices)
        new_local_param = Parameters("parent", new_mu)
        for key, value in zip(keys[5:12], datas[5:12]):
            setattr(new_local_param, key, value[n])
        new_mu.parameters = new_local_param
        
        new_model_mu = Movement("signal",
                        new_sibling.signal[local_indices[0]:local_indices[1]],
                        "sampling_frequency", datas[-1],
                        "indices", local_indices,
                        "sibling", new_mu, 
                        "parameters", new_local_param)
        new_mu.sibling = new_model_mu
        new_trajectory.movement_units.append(new_mu)
        new_sibling.movement_units.append(new_model_mu)
    
    return new_trajectory