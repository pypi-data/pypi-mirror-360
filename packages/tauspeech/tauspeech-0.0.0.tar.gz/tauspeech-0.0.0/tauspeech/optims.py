#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 22 10:03:02 2022

@author: benjamin
"""

import numpy as np
from scipy.optimize import minimize, minimize_scalar
from ._cdo import (critically_damped_oscillator, limits_activation_points)
from ._trajectories import (trajectory_model)
from .utils import (sort_onsets, unirandom)
from .tautools import generate_tau
from joblib import Parallel, delayed
import warnings
import copy
from tqdm import tqdm
from ._parameters import solution_to_parameters


class Solution:
    # pylint: disable=too-many-instance-attributes
    # pylint: disable=pointless-string-statement

    target = None
    onset = None
    shape = None
    observed_sequence = None
    generated_sequence = None
    time_vector = None
    error = None
    first_activation_step = None
    second_activation_step = None
    slope = None

    # Constructor method
    def __init__(self, *args):
        nargin = len(args)
        for k in range(0, nargin, 2):
            key, value = args[k:k+2]
            setattr(self, key, value)
            
    def copy(self):
        """ Returns a copy of the Solution instance """
        return copy.deepcopy(self)    

def cost_function_velocity(y_obs, y_model, idx_comp=None, sr=1, a=0):
    """ Compute the error function between the observed and the modeled trajectories """

    vi = np.gradient(y_obs, 1/sr, edge_order=2)
    if idx_comp is not None:
        y_obs = np.array([y_obs[i] for i in idx_comp if i < len(y_obs)])
        y_model = np.array([y_model[i] for i in idx_comp if i < len(y_model)])
        vi = np.array([vi[i] for i in idx_comp if i < len(vi)])
        
    if a != 0:
        vmax = np.max(vi)
        wi = 1 + a * vi**2/vmax**2
    else:
        wi = np.ones(vi.shape)
    range_y = max(y_obs) - min(y_obs)
    return np.sqrt(np.sum(wi*(y_obs - y_model)**2) / np.sum(wi)) / range_y

def get_initial_solution_from_traj(trajectory, init_range=(0.01, 0.02),
                         activation="rect", model="stam"):
    """ Compute the initial solution for the optimization """
    
    nb_seg = len(trajectory.movement_units) + 1
    onsets = np.zeros(nb_seg)
    onsets[0] = 0
    taus = unirandom(init_range[0], init_range[1], nb_seg)
    targets = np.zeros_like(onsets)
    slopes = unirandom(0, 2, nb_seg)
    for n in range(nb_seg-1):
        y_tmp = trajectory.movement_units[n].signal
        t_tmp = trajectory.movement_units[n].time_vector
        onset_tmp = np.mean(t_tmp) - unirandom(0.05, 0.1)
        if model == "stam":
            onsets[n+1] = onset_tmp
            targets[n] = y_tmp[-1] + np.sign(y_tmp[-1] - y_tmp[0]) * unirandom(b=0.01)
        else:
            onsets[n+1] = t_tmp[0]
            idx = trajectory.movement_units[n].indices
            taus[n], targets[n] = initial_targets(trajectory, idx)

        slopes[n] *= np.sign(y_tmp[-1] - y_tmp[0])

    targets[-1] = trajectory.filtered_signal[-1]
    onsets = sort_onsets(onsets, None)
    x0 = []
    for target in targets:
        x0.append(target)
    if model == "stam":
        for onset in onsets:
            x0.append(onset)
    for tau in taus:
        x0.append(tau)
    if model == "stam":
        for slope in slopes:
            x0.append(slope)
    if activation == "gradual":
        for n in range(len(onsets)):
            x0.append(unirandom(0,0.5)[0])
        for n in range(len(onsets)):
            x0.append(unirandom(0.5,1)[0])
    if "nl" in model:
        for n in range(len(onsets)):
            x0.append(unirandom(0,0.99)[0])
    return x0, onsets

def initial_targets(trajectory, idx):
    """ Finds initial targets for CDO-based methods """
    start, end = idx
    y_tmp = trajectory.filtered_signal[start:end+1]
    t_tmp = trajectory.time_vector[start:end+1]
    y0 = y_tmp[0]

    if start > 0:
        dy0 = np.diff(trajectory.filtered_signal[start-1:start+1])[-1]*trajectory.sampling_frequency
    else:
        dy0 = 0
    args = (y_tmp, y0, dy0, trajectory.sampling_frequency, t_tmp[0], t_tmp[-1])
    target = y_tmp[-1] + np.sign(y_tmp[-1] - y_tmp[0]) * unirandom(b=10)
    x0 = [unirandom(100, 1000, 1)[0], target[0]]
    solution = target_optimization(x0, args, maxiter=200)
    return solution["x"]

def make_bounds(model, nb_params):
    """ Generates bounds for solutions """

    if model == "stam":
        nb_seg = int(nb_params/4)
        return (((None, None), )*nb_seg + ((None, None), )*nb_seg +
                ((0, None), )*nb_seg + ((None, None), )*nb_seg)
    if model == "scdo":
        nb_seg = int(nb_params/2)
        return (((None, None), )*nb_seg + ((1e-3, None), )*nb_seg)
    if model == "gcdo":
        nb_seg = int(nb_params/4)
        return (((None, None), )*nb_seg + ((1e-3, None), )*nb_seg +
                 ((0, 1), )*nb_seg + ((0, 1), )*nb_seg)
    if model == "nl-scdo":
        nb_seg = int(nb_params/3)
        return (((None, None), )*nb_seg + ((1e-3, None), )*nb_seg +
                 ((0, 0.99), )*nb_seg)
    if model == "nl-gcdo":
        nb_seg = int(nb_params/5)
        return (((None, None), )*nb_seg + ((1e-3, None), )*nb_seg + 
                 ((0, 1), )*nb_seg + ((0, 1), )*nb_seg +
                ((0, 0.99), )*nb_seg)

def objective(x, *args):
    """ Objective function """

    model = args[0]
    if model != "tau":
        (y_obs, y0, sr, N, idx, tmax, a, activation, initial_onsets) = args[1:]
        y_model = trajectory_model(x, y0, sr, N, tmax,
                                   initial_onsets=initial_onsets,
                                   model=model,
                                   activation=activation,
                                   nonlinear="nl" in model)[0]
    else:
        (y_obs, idx, x0, xf, sr, a, idx_comp) = args[1:]
        N = len(y_obs)
        if idx_comp is not None:
            y0 = y_obs[idx_comp[0]]
            t0 = idx_comp[0]
            T = (N-1)/sr    
            t = np.linspace(0, T, N)        
            t_ratio = (1-(np.square(t[t0]).astype('f')/np.square(T).astype('f')))
            X0 = (y0 -  xf)/(t_ratio**(1/x))
            x0 = X0 + xf
        y_model = generate_tau(x, x0, xf, N, sr)[idx]
            
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore")
        return cost_function_velocity(y_obs, y_model, idx_comp, sr, a)

def optimization(x0, args, maxiter=200, method='nelder-mead'):
    """ Launches optimization for STAM, and CDO """
    options = {'maxiter': maxiter * len(x0)}
    bounds = make_bounds(args[0], len(x0))
    result = minimize(objective, x0, args=args, method=method,
                          options=options, bounds=bounds)
    return write_solution(result["x"], args)
 

def optimization_tau(y_obs, sr=1, a=5, idx=0, idx_comp=None):
    """ Launches optimization for Tau """
    x0, xf, N = (y_obs[0], y_obs[-1], len(y_obs))
    for n in range(idx):
        y_obs = np.gradient(y_obs, 1/N)
    
    args = ("tau", y_obs, idx, x0, xf, sr, a, idx_comp)
    return minimize_scalar(objective, method="bounded",
                              bounds=(0, 1), args=args)

def parallel_optimization(trajectory, N, a, model, activation, maxiter):
    """ Runs parallel optimization processes for STAM and CDO """
    if model == "stam":
        init_range = (0.01, 0.02)
    else:
        init_range = (100, 1000)
    x0, onsets = get_initial_solution_from_traj(trajectory,                                                 
                                                   activation=activation,
                                                   init_range=init_range,
                                                   model=model)
    
    args = (model, trajectory.filtered_signal, trajectory.filtered_signal[0],
            trajectory.sampling_frequency, N, 
            trajectory.comparison_indices, trajectory.time_vector[-1],
            a, activation, onsets)
    return optimization(x0, args, method="nelder-mead", maxiter=maxiter)

def select_best_solution(solutions):
    errors = [s["fun"] for s in solutions]
    start = np.argmin(errors)
    return start, solutions[start]["x"], solutions[start]["fun"]

def target_objective(x, *args):
    """ Objective function for finding inital targets in CDO-based methods """
    (y_obs, y0, dy0, sr, onset, offset) = args
    y_model, tvec = critically_damped_oscillator(x[0], 1, y0, x[1], onset,
                                                 offset, dy0=dy0, sr=sr,
                                                 activation="step", 
                                                 time_points=None)

    return cost_function_velocity(y_obs, y_model, idx_comp=None, sr=sr, a=5)

def target_optimization(x0, args, maxiter=50, method='nelder-mead'):
    """ Launches optimization for finding inital targets in CDO-based methods """
    options={'maxiter': maxiter * len(x0)}
    bounds = ((1e-3, None), (None, None))
    return minimize(target_objective, x0, args=args, method=method,
                          options=options, bounds=bounds)

def trajectory_fitting(trajectory, N=10, sigma=4, method='nelder-mead', a=5,
                 nb_simul=1, nb_threads=1, model="tau",
                 fit="position", activation="rect", disable=True,
                 parall="processes", maxiter=200, end=1, cut_end=True,
                 change_duration=False, discard_points=False,
                 dimension=1, filt_method="gaussian"):
    """ Fits the trajectory using the specified model """
    
    trajectory.segmentation(sigma, end, dimension, filt_method)    
    if model == "tau":
        [movement.tau_fitting(a=a, method=method, 
                              change_duration=change_duration,
                              discard_points=discard_points)
         for movement in tqdm(trajectory.movement_units, disable=disable)]
        trajectory.get_movement_parameters(a=a, end=end, cut_end=cut_end)
    else:
        solutions = Parallel(n_jobs=nb_threads, prefer=parall)(delayed(parallel_optimization)(trajectory,
             N, a, model, activation, maxiter) 
                               for n in tqdm(range(nb_simul), disable=disable))
        solution = solutions[np.argmin([s.error for s in solutions])]
        
        solution_to_parameters(trajectory, solution)
        for movement, model in zip(trajectory.movement_units, 
                                   trajectory.sibling.movement_units):
            if len(movement.signal) >= 10:
                try:
                    local_error = cost_function_velocity(movement.signal, 
                                                         model.signal, a=a)
                except:
                    local_error = None
            else:
                local_error = 0
            movement.parameters.local_error = local_error
            model.parameters.local_error = local_error

def write_solution(x, args):
    """ Export solutions """
    solution = Solution()
    (model, y_obs, y0, sr, N, idx, tmax, a, activation, initial_onsets) = args
    if model == "stam":
        nb_seg = int(len(x)/4)
        keys = ["target", "onset", "shape", "slope"]
        activation = "rect"
    elif model == "scdo":# and activation == "rect":
        nb_seg = int(len(x)/2)
        keys = ["target", "shape"]
    elif model == "nl-scdo":# and activation == "rect":
        nb_seg = int(len(x)/3)
        keys = ["target", "shape", "nonlinearity"]    
    elif model == "gcdo":# and activation == "gradual":
        nb_seg = int(len(x)/4)        
        keys = ["target", "shape", "first_activation_step", 
                "second_activation_step"]
    elif model == "nl-gcdo":# and activation == "gradual":
        nb_seg = int(len(x)/5)
        keys = ["target", "shape", "first_activation_step",
                "second_activation_step", "nonlinearity"]
    for i, key in enumerate(keys):
        setattr(solution, key, x[i*nb_seg:(i+1)*nb_seg])
    if activation == "gradual":
        for n in range(nb_seg):
            tp = limits_activation_points(np.array([solution.first_activation_step[n],
                                          solution.second_activation_step[n]]))
            solution.first_activation_step[n] = tp[0]
            solution.second_activation_step[n] = tp[1]

    solution.generated_sequence, solution.time_vector = trajectory_model(x, 
                                                             y0, sr, N, tmax,
                                                             initial_onsets=initial_onsets,
                                                             model=model,
                                                             activation=activation,
                                                             nonlinear="nl" in model)
    solution.observed_sequence = y_obs
    solution.error = cost_function_velocity(y_obs, solution.generated_sequence,
                                           idx, sr, a)
    if model == "stam":
        solution.onset = sort_onsets(solution.onset)

    return solution

def ksearch(signal, prec=1e-4, fit='position', a=0):
    """ Does a search for k-value that minimizes the NRMSE
    between the fit and the observation """

    is_found = False
    limits = (0.05, 0.95)
    dk = 1e-1

    pos_obs = signal
    signal_to_fit, idx_fit = choose_fit(pos_obs, fit)
    x_0, x_t, N = (pos_obs[0], pos_obs[-1], len(pos_obs))

    while not is_found:
        k_min, err_min = ksearch_one(signal_to_fit, x_0, x_t, N,
                                     limits, dk, fit=idx_fit, a=a)
        if dk < prec:
            is_found = True
            return k_min, err_min
        else:
            limits = (max(k_min - dk, 0), min(k_min + dk, 1))
            dk = dk / 10

def ksearch_one(signal_to_fit, x_0, x_t, N, limits, dk, fit=0, a=0):
    """ Does a search for k-value for specific bounds and increment step """

    kvec = np.arange(limits[0], limits[-1]+dk, dk)
    score = []
    for k in kvec:
        if k == 0:
            k = 1e-2        
        observation = generate_tau(k, x_0, x_t, N, sr=200)[fit]
        guide = signal_to_fit[fit]
        if fit == 2:
            observation = observation[1:]
            guide = guide[1:]        
        
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore")
            R = cost_function_velocity(guide, observation, a=a)
        score.append(R)
    return kvec[np.argmin(score)], np.min(score)

def choose_fit(x, fit):
    if fit.lower() == 'position':
        idx = 0
    elif fit.lower() == 'vel':
        idx = 1
    elif fit.lower() == 'tau':
        idx = 2
    else:
        raise ValueError("Fit signal not recognized")

    v = np.gradient(x, edge_order=1)
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore",category=RuntimeWarning)
        t = (x - x[-1]) / v
    return [x, v, t], idx

