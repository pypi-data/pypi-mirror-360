#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr  8 11:44:42 2022

@author: benjamin
"""

import h5py
import numpy as np
import os

def export_data(file_name, names, keys, values):    
    """ Stores data in HDF5 """
    with h5py.File(file_name, 'w') as hf:
        for key, value in zip(keys, values):            
            hf.create_dataset(key, data=value)        
        string2h5(hf, names, "names")

def string2h5(hf, x, key):
    """ Stores a list of strings in HDF5 """
    asciiList = [n.encode("ascii", "ignore") for n in x]
    hf.create_dataset(key, data=asciiList)
    
def read_section(hdf5_file):
    """ Extracts data from HDF5 file for Tau analysis """
    
    with h5py.File(hdf5_file, "r") as hf:
        chunk = hf["signal"][()]
        sr = hf["sampling_frequency"][()]        
        
    return chunk, sr

def read_solution(hdf5_file):
    """ Import solution stored in hdf5_file """    
    
    if not os.path.isfile(hdf5_file):
        raise ValueError(hdf5_file, " does not exist")
        
    keys = ["observed_position", "filtered_position", "modeled_position", 
                   "unit_boundaries", "global_error", "local_error", "shape", 
                   "first_activation_step", "second_activation_step", "onset", 
                   "slope", "target", "sampling_frequency"]    
    with h5py.File(hdf5_file, "r") as hf:
        datas = [hf[key][()] for key in keys]
        
    return datas, keys

def write_solution(Trajectory, hdf5_file):
    """ Export fitting solutions into hdf5 file """

    indices = [m.indices[0] for m in Trajectory.movement_units]
    indices.append(len(Trajectory.signal))
    modeled_signal = Trajectory.sibling.signal
    keys = ["global_error", "local_error", "shape", "first_activation_step",
            "second_activation_step", "onset", "slope", "target"]

    datas = [np.array(getattr(Trajectory.parameters, key), dtype=float) for key in keys]

    with h5py.File(hdf5_file, "w") as hf:
        [hf.create_dataset(key, data=value) for key, value in zip(keys, datas)]
        hf.create_dataset("observed_position", data=Trajectory.signal)
        hf.create_dataset("filtered_position", data=Trajectory.filtered_signal)
        hf.create_dataset("modeled_position", data=modeled_signal)
        hf.create_dataset("unit_boundaries", data=indices)
        hf.create_dataset("sampling_frequency", data=Trajectory.sampling_frequency)
