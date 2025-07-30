#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul  4 10:18:19 2022

@author: benjamin
"""

import numpy as np
import warnings
from ._cdo import mass_spring_sequence, limits_activation_points
from ._stam import stam_sequence
from .utils import (interp1, sort_onsets)

def multisequence(y0, targets, onsets, taus, sr, N=10, model="stam", slopes=None,
                  activation="rect", time_points=None, ds=None):
    """ Computes trajectories for a whole sequence of articulatory commands """
    if onsets[0] > 0:
        tvec = list(np.linspace(0, onsets[0], int(onsets[0]*sr)+1))
        y = list(y0 * np.ones_like(tvec))
    else:
        y = [y0]
        tvec = [0]

    nb_seg = len(np.unique(onsets)) - 1
    onsets = np.unique(onsets).tolist()

    for n in range(nb_seg):
        curr_time_points = None
        target = targets[n]
        onset = onsets[n]
        offset = onsets[n+1]
        if slopes is not None:
            slope = slopes[n]
        else:
            slope = 0
        if ds is not None:
            d = ds[n]
        else:
            d = 0

        if time_points is not None:
            tp_pts = limits_activation_points(time_points[n,:]) * (offset - onset)
            curr_time_points = (onset, onset + tp_pts[0],
                                onset + tp_pts[1], offset)
        if offset > onset:
            tau = taus[n]
            if model == "stam":
                y, tvec = stam_sequence(y, target, [onset, offset], tau,
                                   tvec, sr, slope=slope, N=N)
            elif "cdo" in model:
                y, tvec = mass_spring_sequence(y, target, [onset, offset], tau,
                                            tvec, sr, d=d,
                                            activation=activation,
                                            time_points=curr_time_points)

    t_o = np.linspace(0, tvec[-1] , int(tvec[-1]*sr + 1))
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore")
        y_out = interp1(tvec, y, t_o)
    return y_out, t_o

def trajectory_model(x, y0, sr, N, tmax, initial_onsets=None,
                     model="stam", activation="rect", nonlinear=False):
    """ Computes trajectories from temporary solution """
    if model == "stam":
        nb_seg = int(len(x)/4)
        targets = x[:nb_seg]
        onsets = sort_onsets(x[nb_seg:2*nb_seg], tmax)
        taus = x[2*nb_seg:3*nb_seg]
        slopes = x[3*nb_seg:]
        time_points = None
        ds = None
    else:
        slopes = None
        if activation == "rect" and not nonlinear:
            nb_seg = int(len(x)/2)
            targets = x[:nb_seg]
            taus = x[nb_seg:2*nb_seg]
            time_points = None
            ds = None
        if activation == "gradual" and not nonlinear:
            nb_seg = int(len(x)/4)
            targets = x[:nb_seg]
            taus = x[nb_seg:2*nb_seg]
            first_time_point = x[2*nb_seg:3*nb_seg]
            second_time_point = x[3*nb_seg:]
            time_points = np.hstack((np.array(first_time_point).reshape(-1,1),
                                     np.array(second_time_point).reshape(-1,1)))
            ds = None
        if activation == "rect" and nonlinear:
            nb_seg = int(len(x)/3)
            targets = x[:nb_seg]
            taus = x[nb_seg:2*nb_seg]
            ds = x[2*nb_seg:]
            time_points = None
        if activation == "gradual" and nonlinear:
            nb_seg = int(len(x)/5)
            targets = x[:nb_seg]
            taus = x[nb_seg:2*nb_seg]
            first_time_point = x[2*nb_seg:3*nb_seg]
            second_time_point = x[3*nb_seg:4*nb_seg]
            ds = x[4*nb_seg:]
            time_points = np.hstack((np.array(first_time_point).reshape(-1,1),
                                     np.array(second_time_point).reshape(-1,1)))
    if "cdo" in model and initial_onsets is not None:
        onsets = sort_onsets(initial_onsets, tmax)
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore")
        return multisequence(y0, targets, onsets, taus, sr, slopes=slopes,
                             N=N, model=model, activation=activation,
                             time_points=time_points, ds=ds)