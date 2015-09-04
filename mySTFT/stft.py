'''
short Time Fourier Transform tools
calculations:
- stft
- PSD
plots:
- plot PSD
- stft Widget
'''

import numpy as np
import scipy 
from scipy.fftpack import fft,fftfreq, ifft, fftshift
from scipy.signal import  hann,lfilter, filtfilt, decimate

OLA_WINDOWS = ['hann', 'hamming', 'triang','blackman']


def cola_test_window(window, R):
    #todo: control test
    ''' COLA for given hop and its normalization factor
    param:
    - window 
    - R : hop size
    return:
    - bool: True if Cola
    - np.array: normalization if cola else ola array
    - before: 0 pad at begin such that signal is invertible
    - after: 0 pad at end such that signal is invertible
    remarks:
    - before and after works if len(x)-1 is multiple of R
    '''
    M = len(window)
    #first window(first frame) with complete ola 
    R0 = M - M%R
    ola = np.zeros(3*M)
    for shift in np.arange(0,2*M,R):
        win = np.zeros(3*M)
        win[shift:shift+M] += window
        ola += win
    ola = ola[R0:R0+M]
    normCola = np.unique(np.round(ola,10))
    #calculate 0-padding before and after such that ola dont0affect
    before = int(np.arange(0,(M-1)//2+1, R).max())
    after = int(np.arange(0, M//2+1 , R).max())
    if len(normCola)==1:
        return(True, normCola, before, after)
    else:
        return(False, ola, None, None)

def pad_to_multiple_of_hoop(x,R):
    ''' 0-pad signal such that len(xnew)-1 is multiple of R (hoop)
        with this padding in STFT first element and last element have a centered 
        windows on it
    '''
    lenxnew = np.ceil((len(x)-1)/R)*R + 1
    padN = int(lenxnew - len(x))
    return(np.pad(x, (0,padN), 'constant', constant_values = 0), padN)
    
def pad_for_invertible(x,M,R):
    ''' 0-pad signal such that xnew has inverse stft when computed with COLA window
        x[0]lies at xnew[l*R] for l int
        remarks:
        - len(x)-1 has to be multiple of R
    '''
    before = int(np.arange(0,(M-1)//2+1, R).max())
    after = int(np.arange(0, M//2+1 , R).max())
    x = np.pad(x, (before,after), 'constant', constant_values = 0)
    return(x, before, after)
    
def stft(x, M, N = None , R = None, overlap = 2, sR=1, window = 'hann', invertible = True):
    """Calculate short time fourier transform of x
    param:
    - M: window length
    - N: FFT length
    - R:  hopsize
    - sR: sampling Rate
    - ola: overlapping
    - window: window type
    - invertible: test if window and hoop is COLA. 
      If True than window is normalized
    return:
    - X: np.array of stft of x
    - freq: np.array frequency vector of stft
    - f_i: np.array with center frame of stft
    - param: parameter decribing stft
    
    Info in:
    - http://www.dsprelated.com/freebooks/sasp/Overlap_Add_OLA_STFT_Processing.html
    - x is 0-padded such that last element of 0-padded x has a centered window 
    see pad_n
    
    """
    #hoop 
    if R == None:
        R = M//overlap
    else:
       overlap = np.floor(M/R)
       
    if R <= 0 or R > M:
        raise(ValueError('R should be between 1 and M')) 
        
    # 0-pad signal such that len(xnew)-1 is multiple of R
    # first element and last element have a centered windows on it
    x, padN = pad_to_multiple_of_hoop(x,R)
        
    #window    
    w =  scipy.signal.get_window(window, M, fftbins = True)
    # the window has to be symmetric(% M) around the center frame
    # for a symmetric odd length (M) window centering is obvious
    # for a length (M) window we set fftbins = True
    
    if invertible:
        # test if window and R fulfill Cola requirement 
        invertible, normCOLA, before, after = cola_test_window(w, R)
        
    #if test passed x padding and window normalization    
    if invertible:
        x = np.pad(x, (before,after), 'constant', constant_values = 0)
        w /= normCOLA
        padN = (padN,before,after)
        frames_added=(before/R, after/R)

    # f_i frame vector, window centered at time m*R
    frame_i = np.arange(0 , len(x) , R , dtype=int)
    
    #0-pad begin/end of signal such thath window at f_i[0] = 0 and f_i.max exist
    x = np.pad(x, (M//2,(M-1)//2), 'constant', constant_values = 0)
    
    #FFT length
    if N == None:
        N=M
    if N < M:
        raise(ValueError('N should be >= M '))
        
    #freqency vector
    freq = fftfreq(N, 1/sR)
    
    #prepare STFT array
    X = np.zeros(N*len(frame_i), dtype=np.complex128).reshape(len(frame_i),N)
    
    #calculate FFT of shifted windows
    for i , frame in enumerate(frame_i):
        X[i,:] = fft(x[frame:frame+M] * w,n = N)
    #correct phase of stft
    shift =  np.exp(-1j*2*np.pi/sR*np.outer(frame_i - M//2  ,freq))
    X = X * shift
    return(X, freq, frame_i, \
            {'M':M, 'N':N, 'overlap':np.round(overlap,2),'sR':sR, \
             'R':R, 'window':window, '0-pad': padN, 'invertible': invertible,\
             'normCOLA':normCOLA,'frames_added':frames_added }
            )
    
def istft(X, param):
        """
        parameter: 
        - X: STFT np.array
        - param: parametr of the given STFT
        
        return:
        - reconstructed time signal
        Remarks:
        - if window,R COLA and x is 0-padded (x->x') then ISTFT(STFT(x')) = x'
        """
        M = param['M']
        R = param['R']
        N = param['N']
        sR = param['sR']
        #calculate ferquency vetor
        freq = fftfreq(N, 1/sR)
        #test if param and X are compatible in dimension
        lenf_i, n = X.shape
        # np.array with center frame of stft
        f_i = np.arange(0,lenf_i*R , R)
        # time vector padded front and back
        x = np.zeros(f_i.max() + 1 + 2*(M//2))
        shift =  np.exp(1j*2*np.pi/sR*np.outer(f_i- M//2 ,freq))
        X = X * shift
        for i, frame in enumerate(f_i):
            x[frame : frame + M] += np.real(ifft(X[i,:]))[0:M]
        return(x[M//2:-(M-1)//2 ])

def stft_spectrum(X, param):
    '''return spectrum N points,
       if N > len x sameresult
    '''
    freq = fftfreq(param['N'],1/param['sR'])
    return(X.sum(axis=0), freq)
    
def adjust_PSD_time_freq(PS_i, freq, t_i, t0, tmax, tmin, fmax, fmin):
    #todo: implement
    '''
    return a 
    '''
    return(X, freq, t)
    
def stft_PSD(X, param):
    #Magnitude singlesided
    R = param['R']
    N = param['N']
    sR = param['sR']
    lenf_i,n= X.shape
    #calculate frquency vetor
    freq = fftfreq(N, 1/param['sR'])
    f_i = np.arange(0,lenf_i*R , R)
    df = sR / N
    w =  scipy.signal.get_window(param['window'], param['M'], fftbins = True)
    # TODO: CONTROL NORMALIZATION
    norm = np.sqrt((w**2).mean())
    if  param['invertible']:
        X *= (param['normCOLA']/norm)
    else:
        X /= norm
    #onesided
    PS_i = (2*abs(X)**2)[:,1:(N+1)//2]/df
    # normalizzazione x spettro vale prms^2= sum PS
    #A =  1 / (np.sum(window)**2) * (2/3)  
    #print((np.sum(window)**2)/(np.sum(window**2))
    return(PS_i, freq[1:(N+1)//2], f_i/sR)
    
def stft_prms(X, param):
    '''prms value from stft
    '''
    #todo: compare with MBBM fast(MAGNITUDE)
    PSD, freq, t_i = stft_PSD(X,param)
    return(PSD.mean(1), t_i )
    
def frequency_resolution(N,sR):
    '''
    return df,dt
    '''
    return(sR/N,N/sR)

def time_resolution(df,sR):
    '''
    return N dt
    '''
    return(sR /(df),1/(df))
    

    
    