#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul  4 10:15:36 2022

@author: benjamin
"""

import numpy as np
import warnings
from scipy import integrate

def activation_window(t, time_points):
    """ returns the gradual activation function at point t """
    ta, tb, tc, td = time_points
    if t < ta:
        return 0
    if t >= ta and t < tb:
        return np.sin(2*np.pi*(t-ta)/(4*(tb-ta)))
    if t >= tb and t < tc:
        return 1
    if t >= tc and t < td:
        return np.sin(2*np.pi*(t-td)/(4*(tc-td)))
    if t >= td:
        return 0
    
def compute_mass_coeff(y0, dy0, target, k, a=1):
    """ Returns the coefficients for critically damped displacement """
    return y0 - target, dy0 + np.sqrt(k)*(y0 - target)

def critically_damped_oscillator(k, M, init_pos, target_pos, t0, t1, dy0=0,
                      sr=1, activation="rect", time_points=None):

        t = np.linspace(t0, t1, int(np.round((t1-t0)*sr))+1)

        if activation == "gradual":
            a = np.array([activation_window(tp, time_points) for tp in t])
        else:
            a = 1
        k *= a
        A, B = compute_mass_coeff(init_pos, dy0, target_pos, k, a)
        y = ((A + B*(t-t0)) * np.exp(-np.sqrt(k)*(t-t0))) + target_pos
        return y, t

def limits_activation_points(time_points):
    """ Redefine time points so that they are positive, less than 1 and
    in increasing order """
    time_points[time_points < 0] = 0
    time_points[time_points > 1] = 1
    return np.sort(time_points)

def mass_spring_model(k, M, init_pos, target_pos, t0, t1, dy0=0,
                      sr=1, d=0, b=None, activation="rect", time_points=None):
    """ Computes the displacement of a damped mass-spring system """

    t = np.linspace(t0, t1, int((t1-t0)*sr)+1)
    y0 = [init_pos, dy0]
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore")
        y = integrate.odeint(nlmss, y0, t, args=(target_pos, k, M,
                                                  time_points,
                                                  activation, d, b))[:, 0]
    return y, t

def mass_spring_sequence(y, target, tspan, tau, tvec, sr, d=0,
                         activation="rect", time_points=None):
    """ Computes a trajectory for a given articulatory command """

    onset, offset = tspan
    if len(y) < 2:
        dy0 = 0
    else:
        dy0 = np.diff(y)[-1] * sr
    if activation == "rect":
        y_tmp, tvec_tmp = critically_damped_oscillator(tau, 1, y[-1], target,
                                                       onset, offset, dy0,
                                                       sr=sr)
    else:
        y_tmp, tvec_tmp = mass_spring_model(tau, 1, y[-1], target, onset, offset,
                                            dy0, sr=sr, d=d, b=None,
                                            activation=activation,
                                            time_points=time_points)

    for y1, t1 in zip(y_tmp[1:], tvec_tmp[1:]):
        y.append(y1)
        tvec.append(t1)
    return y, tvec

def nlmss(y, t, yt, k, M, time_points=None, activation="rect", d=0, b=None):
    if activation == "gradual":
        a = activation_window(t, time_points)
    else:
        a = 1
    if b is None:
        b = 2*np.sqrt(k*M)
    return np.array([y[1], -a/M*(b*y[1]+k*(y[0]-yt)-(d*k)*(y[0]-yt)**3)])