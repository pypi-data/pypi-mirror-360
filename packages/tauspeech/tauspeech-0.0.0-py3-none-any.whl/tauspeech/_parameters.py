#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul  4 15:23:30 2022

@author: benjamin
"""

import copy

class Parameters:
    # pylint: disable=too-many-instance-attributes
    # pylint: disable=pointless-string-statement

    parent = None
    shape = None
    onset = None
    target = None
    first_activation_step = None
    second_activation_step = None
    slope = None
    local_error = None
    global_error = None
    amplitude = None
    duration = None
    
    # Constructor method
    def __init__(self, *args):
        nargin = len(args)
        for k in range(0, nargin, 2):
            key, value = args[k:k+2]
            setattr(self, key, value)
            
    def copy(self):
        """ Returns a copy of the Parameters instance """
        return copy.deepcopy(self)    

def solution_to_parameters(trajectory, solution):
    """ assigns solution parameters to trajectory """
    global_solution = Parameters("parent", trajectory)
    for key in ["shape", "onset", "target", "first_activation_step", 
                 "second_activation_step", "slope"]:
        setattr(global_solution, key, getattr(solution, key))
    global_solution.global_error = solution.error
    trajectory.parameters = global_solution
    Model = trajectory.copy()
    Model.nature = "model"
    Model.sibling = trajectory
    trajectory.sibling = Model
    Model.signal = solution.generated_sequence
    
    i = 0
    for movement, model in zip(trajectory.movement_units, Model.movement_units):
        model.nature = "model"
        model.sibling = movement
        movement.sibling = model
        model.signal = solution.generated_sequence[movement.indices[0]:movement.indices[1]]
        local_parameters = Parameters("parent", movement)
        if len(movement.signal) >= 10:
            for key in ["shape", "onset", "target", "first_activation_step", 
                         "second_activation_step", "slope"]:
                if getattr(solution, key) is not None:
                    try:
                        setattr(local_parameters, key, getattr(solution, key)[i])
                    except:
                        pass
            i += 1            
        else:
            local_parameters.local_error = 0
        movement.parameters = local_parameters
        model.parameters = local_parameters

