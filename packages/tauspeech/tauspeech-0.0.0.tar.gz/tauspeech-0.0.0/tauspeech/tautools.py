#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 18 14:14:10 2022

@author: benjamin
"""

import numpy as np


def generate_tau(k, initial_position, final_position, N, sr=1, oversampling=1):
    """ Returns the position velocity and acceleration of a Tau-guided movement """

    T = (N-1)/sr
    t = np.linspace(0, T, N)        
    t_ratio = (1-(np.square(t).astype('f')/np.square(T).astype('f')))
    X0 = (initial_position - final_position)
    x = X0*(t_ratio)**(1/k) + final_position   
    v = abs(2*X0*t/(k*T**2)*(1-t**2/T**2)**(1/k-1))
    if oversampling > 1:  
        N = int(T*sr*oversampling) + 1
        t = np.linspace(0, T, N)
    t_ratio = -t**2/T**2 + 1
    t_ratio[t_ratio <= np.finfo(float).eps] = np.finfo(float).eps

    a = -np.sign(X0)*(4*(X0)*t**2*(t_ratio)**(1/k - 2)*(1/k - 1)/(k*T**4) -
         2*(X0)*(t_ratio)**(1/k - 1)/(k*T**2))

    return x, v, a