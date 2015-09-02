
import numpy as np
import scipy 
from scipy.fftpack import fft,fftfreq, ifft
from scipy.signal import  hann,lfilter, filtfilt, decimate
import matplotlib.pyplot as plt

OLA_WINDOWS = ['hann', 'hamming', 'triang']

def calc_ola(window, M, R):
    window = scipy.signal.get_window(window, M, fftbins = True)
    
    f1, ax = plt.subplots(1)
    R0 = M - M%R
    #ax.axvline(R0,linewidth=3.0,color='black')
    plt.axvspan(R0, R0+M-1, facecolor='grey', alpha=0.5)
    #ax.axvline(R0+M-1,linewidth=3.0,color='black')
    
    ola = np.zeros(3*M)
    w_i = []
    for shift in np.arange(0,2*M,R):
        win = np.zeros(3*M)
        win[shift:shift+M] += window
        w_i.append(win)
        if shift == R0:
            ax.plot(win, '-o', linewidth=2.5)
        else:
            ax.plot(win)
        ola += win
    ax.plot(ola, '-or')    

    return(ola[R0:R0+M])

calc_ola('hann',13,8)