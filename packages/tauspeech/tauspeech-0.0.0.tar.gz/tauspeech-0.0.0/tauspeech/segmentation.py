#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul  4 16:19:27 2022

@author: benjamin
"""

from ._trajectory import Trajectory

def create_trajectory(y, sr):
    return Trajectory("signal", y,
                      "sampling_frequency", sr, 
                      "nature", "observation")