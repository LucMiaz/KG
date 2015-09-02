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
from scipy.fftpack import fft,fftfreq, ifft
from scipy.signal import  hann,lfilter, filtfilt, decimate

OLA_WINDOWS = ['hann', 'hamming', 'triang']


def cola_test_window(window, R):
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
    before = int(np.arange(0,(M+1)//2,R).max())
    after = int(np.arange(0,M//2+1,R).max())
    if len(normCola)==1:
        return(True, normCola, before, after)
    else:
        return(False, ola, None, None)

def pad_for_given_hoop(x,R):
    ''' 0-pad signal such that len(xnew)-1 is multiple of R (hoop)
        with this padding in STFT first element and last element have a centered 
        windows on it
    '''
    lenxnew = np.ceil((len(x)-1)/R)*R + 1
    padN = lenxnew - len(x)
    return( np.pad(x, (0,padN), 'constant', constant_values = 0), padN)
    
def pad_for_invertible(x,M,R):
    ''' 0-pad signal such that xnew has inverse stft when computed with COLA window
        x[0]lies at xnew[l*R] for l int
        remarks:
        - len(x)-1 has to be multiple of R
    '''
    before = int(np.arange(0,(M+1)//2,R).max())
    after = int(np.arange(0,M//2+1,R).max())
    x = np.pad(x, (before,after), 'constant', constant_values = 0)
    return(x, before, after)
    
def STFT(x, M, N = None , R = None, overlap = 2, sR=1, window = 'hann', invertible = True):
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
        
    #FFT length
    if N == None:
        N=M
    if N < M:
        raise(ValueError('N should be >= M '))
        
    # 0-pad signal such that len(xnew)-1 is multiple of R
    # first element and last element have a centered windows on it
    x, padN = pad_n(x,R)
        
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
    else:
        # normalize window 
        w /= np.sqrt((w**2).mean())
    
    # f_i frame vector, window centered at time m*R
    frame_i = np.arange(0 , len(x) , R , dtype=int)
    
    #freqency vector
    freq = fftfreq(N, 1/sR)
    
    #prepare STFT array
    X = np.zeros(N*len(frame_i), dtype=np.complex128).reshape(len(frame_i),N)
    
    #0-pad begin/end of signal such thath window at f_i[0] = 0 and f_i.max exist
    x = np.pad(x, (M//2,(M-1)//2), 'constant', constant_values = 0)
    
    #calculate FFT of shifted windows
    for i , frame in enumerate(frame_i):
        X[i,:] = fft(x[frame: frame+M] * w, n = N)* np.exp(-1j * freq * frame)
 
    return(X, freq, frame_i, \
            {'M':M, 'N':N, 'overlap':np.round(overlap,2), \
             'R':R, 'window':window, '0-pad': padN, 'inverible': invertible }
            )
    
def ISTFT(X, param):
        """
        parameter: 
        - X: STFT np.array
        - param: parametr of the given STFT
        
        return:
        - reconstructed time signal
        Remarks:
        - if window,R COLA and x is 0-padded (x->x') then ISTFT(STFT(x')) = x'
        """
        M = param['M']# Window length
        R = param['R']
        fi = STFT['f_i'] # fenster centered at time mR.
        n,lenf_i= X.shape
        if not n == param['N']:
            raise(ValueError())

        # np.array with center frame of stft
        f_i = np.arange(0,lenf_i*R + 1, R)
        # time vector padded front and back
        x = np.zeros(lenf_i*R + 1 + (M - 1))
        back = (M-1) // 2 + 1 
        
        for i, frame in enumerate( f_i - M//2):
            x[frame : frame + M] += np.real(ifft(X[i,:]))[0:M]
            
        return(x[M//2:-(M-1)//2 ])

def stft_PSD(X, freq, f_i, sR):
    #Magnitude singlesided
    N = len(freq)
    if not N%2 == 0:
        raise(ValueError('N should be even'))
    df = sR / N
    PS_i = abs(X)**2
    # normalizzazione x spettro vale prms^2= sum PS
    #A =  1 / (np.sum(window)**2) * (2/3)  
    #print((np.sum(window)**2)/(np.sum(window**2))
    # escludere le frequenze fk con k =0, k=N/2+1 
    return(2*PS_i[:,1:N/2]/df, freq[1:N/2], f_i/sR)

def stft_spectrum(X, freq, f_i, sR):
    #todo: 
    PSD, freq, t_i = stft_PSD(X,freq,f_i,sR)
    return(PSD.mean(0),freq )
    
def stft_prms(X, freq, f_i, sR):
    #todo:
    PSD, freq, t_i = stft_PSD(X,freq,f_i,sR)
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
    