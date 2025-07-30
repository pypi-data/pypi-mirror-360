def test_tau_optimization(data_trajectory):
    data_trajectory.fit_trajectory(sigma=4, model="tau")
    assert data_trajectory.parameters.global_error > 0
    assert len(data_trajectory.sibling.signal) == len(data_trajectory.signal)
    assert len(data_trajectory.parameters.shape) == len(data_trajectory.movement_units)
    
def test_stam_optimization(data_trajectory):
    data_trajectory.fit_trajectory(sigma=4, model="stam", 
                                   nb_simul=1, maxiter=1)
    assert data_trajectory.parameters.global_error > 0
    assert len(data_trajectory.sibling.signal) == len(data_trajectory.signal)
    assert len(data_trajectory.parameters.shape) == len(data_trajectory.movement_units) + 1
    
def test_scdo_optimization(data_trajectory):
    data_trajectory.fit_trajectory(sigma=4, model="cdo", activation="rect", 
                                   nb_simul=1, maxiter=1)
    assert data_trajectory.parameters.global_error > 0
    assert len(data_trajectory.sibling.signal) == len(data_trajectory.signal)
    assert len(data_trajectory.parameters.shape) == len(data_trajectory.movement_units) + 1

def test_gcdo_optimization(data_trajectory):
    data_trajectory.fit_trajectory(sigma=4, model="cdo", activation="gradual", 
                                   nb_simul=1, maxiter=1)
    assert data_trajectory.parameters.global_error > 0
    assert len(data_trajectory.sibling.signal) == len(data_trajectory.signal)
    assert len(data_trajectory.parameters.shape) == len(data_trajectory.movement_units) + 1