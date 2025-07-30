#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 14 18:31:54 2022

@author: benjamin
"""

import numpy as np
import math

def compute_coeffs(a, dydt, targets):

    N, L = (len(dydt), len(targets))
    c = np.zeros((N, L))
    c[0, :] = dydt[0] - targets
    for n in range(1, N):
        cn = 0
        for i in range(n):
            cn += c[i,:]*a**(n-i) * math.comb(n, i)*math.factorial(i)
        c[n, :] = (dydt[n] - cn)/math.factorial(n)

    return c

def stam_sequence(y, target, tspan, tau, tvec, sr, slope=0, N=10):
    """ Computes a trajectory for a given articulatory command """

    dydt = np.zeros(N)
    dydt[0] = y[-1]
    dy = y * 1
    onset, offset = tspan
    for n in range(1, N):
        if len(dy) >= 2:
            dy = np.diff(dy)
            dydt[n] = dy[-1] * sr

    a = -1/tau
    tvec_tmp = np.linspace(onset, offset, int((offset-onset)*sr + 1)) - onset
    V = np.vander(tvec_tmp[1:], N, True)

    if slope == 0:
        c = np.array(compute_coeffs(a, dydt, [target]))
        y1 = (V @ c).squeeze() * np.exp(a*tvec_tmp[1:]) + target
    else:
        moving_target = target + slope * tvec_tmp
        c = np.array(compute_coeffs(a, dydt, moving_target[1:]))
        y1 = np.diag((V @ c).squeeze() * np.exp(a*tvec_tmp[1:])) + moving_target[1:]

    [y.append(x) for x in y1]
    [tvec.append(t + onset) for t in tvec_tmp[1:]]
    return y, tvec
