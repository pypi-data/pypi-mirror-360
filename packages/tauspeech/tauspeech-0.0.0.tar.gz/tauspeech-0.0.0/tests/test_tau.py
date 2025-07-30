from tauspeech import tautools

def test_generate_tau():
    nb_pts = 1000
    initial_gap = 10
    initial_position = 1
    final_position = initial_position - initial_gap
    k = 0.45
    position, velocity, acceleration = tautools.generate_tau(k,
                                                             initial_position,
                                                             final_position, 
                                                             nb_pts)
    
    assert len(position) == nb_pts
    assert position[0] == initial_position
    assert position[-1] == final_position
    assert position[0] - position[-1] == initial_gap