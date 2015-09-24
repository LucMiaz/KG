"""
Tests for :func:`acoustics.signal`
"""
from mySTFT.stft import *
import numpy as np
from numpy.testing import assert_almost_equal, assert_array_almost_equal, assert_array_equal, assert_approx_equal

import pytest

@pytest.fixture(params = OLA_WINDOWS)
def window(request):
    return request.param

def test_window_0(window):
    """Test window normalization.
    """
    M = np.random.randint(1,1024)
    w = scipy.signal.get_window(window, M,fftbins = True)
    assert_array_almost_equal(w.max(),1.0 )
    
#todo  : test for window COLA
      
@pytest.mark.parametrize(
    "x,R,xPadded,padN", [
    ( np.array([0,1,2,3,4,5,6]), 7, np.array([0,1,2,3,4,5,6,0]), 1 ),
    ( np.array([0,1,2,3,4,5,6,7]), 7, np.array([0,1,2,3,4,5,6,7]), 0 ),
    ( np.array([0,1,2,3,4,5,6,7,8]), 7, np.array([0,1,2,3,4,5,6,7,8,0,0,0,0,0,0]), 6 ),
    ( np.array([0,1,2,3,4,5,6,7,8,9,10,11,12]), 4, np.array([0,1,2,3,4,5,6,7,8,9,10,11,12]), 0 ),
    ( np.array([0,1,2,3,4,5,6,7,8,9,10,11]), 4, np.array([0,1,2,3,4,5,6,7,8,9,10,11,0]), 1 )
    ])
def test_pad_to_multiple_of_hoop(x,R,xPadded,padN):
    y, padN1 = pad_to_multiple_of_hoop(x,R)
    np.testing.assert_array_equal(y,xPadded)
    np.testing.assert_array_equal(pad_to_multiple_of_hoop(y,R)[0],xPadded)
    assert(padN==padN1)
    
@pytest.mark.parametrize(
    "x,M,R,before,after", [
    ( np.array([0,1,2,3,4,5,6,7]), 7,1,3,3),
    ( np.array([0,1,2,3,4,5,6,7]), 7,3,3,3),
    ( np.array([0,1,2,3,4,5,6,7]), 6,1,2,3),
    ( np.array([0,1,2,3,4,5,6,7]), 6,2,2,2),
    ( np.array([0,1,2,3,4,5,6,7]), 6,3,0,3),
    ( np.array([0,1,2,3,4,5,6,7]), 7,2,2,2),
    ( np.array([0,1,2,3,4,5,6,7,8,9,10]), 10,5,0,5),
    ( np.array([0,1,2,3,4,5,6,7,8,9,10]), 11,5,5,5),
    ( np.array([0,1,2,3,4,5,6]), 13,3,6,6)
    ])
def test_pad_for_invertible(x,M,R,before , after):
    _, before1, after1 = pad_for_invertible(x,M,R)
    assert(before == before1)
    assert(after == after1)

#pytest.mark.xfail(("6*9", 42))

#todo  : PARAMETRIZE test

# def test_stft_istft():
#     M = 111
#     R = M//2
#     window = 'hann'
#     N = 1024
#     sR = 1
#     #prepare signal
#     x = np.sin(np.arange(0,2*np.pi,0.01)*3)
#     xPadded , padN = pad_for_given_hoop(x,R)
#     w =  scipy.signal.get_window(window, M, fftbins = True)
#     assert(len(xPadded) % R == 1)
#     invertible, normCola, before, after = cola_test_window(w,R)
#     
#     if invertible:
#     #calc STFT
#     X, freq, f_i, param = stft(x, M=M, R=R, N=N, sR=sR, window = window )
#     padN, before , after = param['0-pad']
#     xPadded2 = np.pad(xPadded,(before,after), 'constant', constant_values = 0)
#     y = istft(X,param)
#     assert(len(y) == len(xPadded2))
#     np.testing.assert_array_almost_equal(xPadded2,y)

#todo: test spectrum fft <-> stft