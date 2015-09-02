"""
Tests for :func:`acoustics.signal`
"""
from mySTFT.stft import *
import numpy as np
from numpy.testing import assert_almost_equal, assert_array_almost_equal, assert_array_equal, assert_approx_equal

import pytest


# @pytest.mark.parametrize(
#     "u,h", [
#     ( np.array([1,2,3,4,3,2,1], dtype='float'), np.array([1,2,3,4], dtype='float') ),
#     ( np.array([1,2,3,4,3,2,1,1], dtype='float'), np.array([1,2,3,4,5], dtype='float') ),
#     ])
# def test_convolve_lti(u, h):
#     """Test whether :func:`acoustics.signal.convolve` behaves properly when 
#     performing a convolution with a time-invariant system.
#     """
#     H = np.tile(h, (len(u), 1)).T
# 
#     np.testing.assert_array_almost_equal(convolveLTV(u,H), convolveLTI(u,h))
#     np.testing.assert_array_almost_equal(convolveLTV(u,H,mode='full'), convolveLTI(u,h,mode='full'))
#     np.testing.assert_array_almost_equal(convolveLTV(u,H,mode='valid'), convolveLTI(u,h,mode='valid'))
#     np.testing.assert_array_almost_equal(convolveLTV(u,H,mode='same'), convolveLTI(u,h,mode='same'))
#     

@pytest.fixture(params = OLA_WINDOWS)
def window(request):
    return request.param

def test_window_0(window):
    """Test window normalization.
    """
    M = np.random.randint(1,1024)
    w = scipy.signal.get_window(window, M,fftbins = True)
    assert_array_equal(w.max(),1.0 )
      
@pytest.mark.parametrize(
    "x,R,xnew,padN", [
    ( np.array([0,1,2,3,4,5,6]), 7, np.array([0,1,2,3,4,5,6,0]), 1 ),
    ( np.array([0,1,2,3,4,5,6,7]), 7, np.array([0,1,2,3,4,5,6,7]), 0 ),
    ( np.array([0,1,2,3,4,5,6,7,8]), 7, np.array([0,1,2,3,4,5,6,7,8,0,0,0,0,0,0]), 6 ),
    ( np.array([0,1,2,3,4,5,6,7,8,9,10,11,12]), 4, np.array([0,1,2,3,4,5,6,7,8,9,10,11,12]), 0 ),
    ( np.array([0,1,2,3,4,5,6,7,8,9,10,11]), 4, np.array([0,1,2,3,4,5,6,7,8,9,10,11,0]), 1 )
    ])
def test_pad_for_given_hoop(x,R,xnew,padN):
    xnew1, padN1 = pad_for_given_hoop(x,R)
    np.testing.assert_array_equal(xnew1,xnew)
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

#todo ISTFT test
