# -*- coding: utf-8 -*-
"""
Created on Thu Apr 18 11:45:38 2024

@author: belie
"""

import numpy as np
import scipy
import statsmodels.api as sm
from scipy.interpolate import make_smoothing_spline


def gaussian_filtering(x, sigma=5.75):
    """ Apply gaussian filtering """
    return scipy.ndimage.gaussian_filter(x, sigma=sigma)

def lowess_filtering(x, order=11):
    lowess = sm.nonparametric.lowess    
    return lowess(x, np.arange(len(x)), order/len(x))[:, 1]

def savgo_smoothing(X, order):
    return scipy.signal.savgol_filter(X.T, order, 1).T

def smooth_traj(x, order, filt_method):
    if filt_method == "gaussian":
        return gaussian_filtering(x, order)
    elif filt_method == "lowess":
        return lowess_filtering(x, order)
    elif filt_method == "sav-go":
        return savgo_smoothing(x, order)
    elif filt_method == "spline":
        return spline_smoothing(x, order)

def spline_smoothing(x, time_vector):
    if not hasattr(time_vector, '__len__'):
        time_vector = np.arange(len(x)) / time_vector
    return make_smoothing_spline(time_vector, x)(time_vector)
    # spl = scipy.interpolate.splrep(range(len(x)), x, s=order)
    # return scipy.interpolate.splev(range(len(x)), spl)
    