from tauspeech import (hdf5tools, utils)
import numpy as np

def test_generate_tau(datafile):
    
    sequence, sr = hdf5tools.read_section(datafile)[:2]    
    assert sr == 200
    
def test_filtering(datachunk):

    sequence_filtered = utils.gaussian_filtering(datachunk[0], sigma=5.75)
    assert len(sequence_filtered) == len(datachunk[0])
    assert np.sum(abs(sequence_filtered - datachunk[0])) > 0 

def test_segmentation(datachunk):
    
    sequence, sr = datachunk
    sequence_filtered = utils.gaussian_filtering(sequence, sigma=5.75)
    pks, idx = utils.sectioning(sequence_filtered, sr)
    assert len(pks) > 0
