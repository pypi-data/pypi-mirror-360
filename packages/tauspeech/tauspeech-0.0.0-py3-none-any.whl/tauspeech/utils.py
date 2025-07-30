#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat May 25 15:48:04 2019

@author: benjamin
"""

import numpy as np
import scipy.io
import scipy.interpolate
import scipy.signal
import scipy.stats


def find_indices(pks, tvec):
    """ Find the indices used for comparison """
    t_pks = tvec[pks]
    t_min, t_max = (t_pks[1], t_pks[-1])
    return [x for x in range(len(tvec)) if tvec[x] <= t_max and tvec[x]>= t_min]

def find_nan(sensor_obj):
    """ Find if NaN samples and where they are """

    signal = sensor_obj.signal
    sr = sensor_obj.sampling_frequency
    idx = np.isnan(signal)
    idx_nan = [x for x in range(len(signal)) if idx[x]]

    return idx_nan, len(idx_nan) / sr

def find_peaks(sequence, peak_type='all'):
    """ Find the peaks of sequence """
    assert peak_type in ['all', 'min', 'max']
    if peak_type in ["all", 'min']:          
        pm = scipy.signal.argrelmin(np.array(sequence))[0]
        pks = [p for p in pm]
    else:
        pks = []
    if peak_type in ['all', 'max']:
        pp = scipy.signal.argrelmax(np.array(sequence))[0]    
        [pks.append(p) for p in pp]    
    return np.sort(np.insert(pks, 0, 0))

def get_constants(y_obs, pks, tvec):
    """ Returns the constants used for optimization """
    idx = find_indices(pks, tvec)
    t_end = tvec[-1]
    y0 = y_obs[0]

    return y0, t_end, idx

def getdirection(x):
    return x.split("_")[-1]

def interp1(x_i, y_i, x_o, kind="linear", fill_value="extrapolate"):
    """ 1D Interpolation """
    f = scipy.interpolate.interp1d(x_i, y_i, kind=kind, fill_value=fill_value)
    return f(x_o)

def sectioning(x, sr, peak_type='all'):

    tvec = np.arange(len(x)) / sr    
    pks = find_peaks(x, peak_type=peak_type)
    
    if len(pks) > 2:
        idx_comp = find_indices(pks, tvec)        
    else:
        idx_comp = [i for i in range(len(x))]        
    pks = np.append(pks, len(x)-1).astype(int)
    return pks, idx_comp

def sort_onsets(onsets, tmax=None):
    onsets = np.sort(onsets)
    onsets[0] = np.max((0, onsets[0]))
    if tmax is not None:
        onsets = np.append(onsets, tmax)
    return onsets

def unirandom(a=0, b=1, n=1):
    """ Generate n random numbers unifromly distributed between a and b """
    return abs(a-b) * np.random.rand(n) + min(a, b)

def tangential_distance(x, axis=0):
    """ Computes the tangential distance from x """
    if len(x.shape) > 2:
        raise ValueError("x should be a 2D matrix")
    if len(x.shape) == 1:
        return np.insert(np.cumsum(np.diff(abs(x))), 0, 0)
    if axis == 1:
        x = x.T
    return np.insert(np.cumsum(np.sqrt(np.sum(np.diff(x, axis=0)**2, 
                                              axis=1))),
                     0, 0)
    