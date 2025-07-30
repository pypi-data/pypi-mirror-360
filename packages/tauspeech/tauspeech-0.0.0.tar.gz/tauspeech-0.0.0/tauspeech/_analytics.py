# -*- coding: utf-8 -*-
"""
Created on Thu Apr 25 10:44:44 2024

@author: belie
"""

import numpy as np


def get_amplitude(X_0, X_T):
    return X_0 - X_T

def get_duration(t_0, t_T):
    return t_T - t_0

def get_peak_velocity(X_0, X_T, t_0, t_T, k):
    return np.abs((2*np.abs(get_amplitude(X_0, X_T))/(get_duration(t_0, t_T)*np.sqrt(k*(2-k)))) * (1 - k / (2-k))**(1/k - 1))

def get_peak_velocity_loc(k):
    return np.sqrt(k/(2-k))

def get_peak_deceleration(X_0, X_T, t_0, t_T, k):
    A = get_amplitude(X_0, X_T)
    T = get_duration(t_0, t_T)
    return np.real(2*A/(k*T**2)*(6/(2-k)*(1-k)*((1-3*k/(2-k))**(1/k-2)) - 
                          (1-3*k/(2-k))**(1/k-1)))

def get_peak_deceleration_loc(k):
    return np.sqrt(3*k/(2-k))

