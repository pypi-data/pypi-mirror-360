from tauspeech import (_trajectory, utils)

def test_segmentation(datachunk):
    
    sequence, sr = datachunk
    sequence_filtered = utils.gaussian_filtering(sequence, sigma=5.75)
    pks, idx = utils.sectioning(sequence_filtered, sr)
    Traj = _trajectory.Trajectory("signal", sequence, 
                                  "sampling_frequency", sr)
    Traj.segmentation(sigma=5.75)
    assert len(Traj.movement_units) == len(pks) - 1