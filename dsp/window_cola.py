# Test a nd plot Overlap Add of windows
#
#
import scipy.signal
import numpy as np
import matplotlib.pyplot as plt
from scipy.fftpack import fft, fftshift, fftfreq

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
    ola = ola[R0:R0+M]
    normCola = np.unique(np.round(ola,10))
    print(normCola)
    if len(normCola)==1:
        return(True, normCola)
    else:
        return(False, ola)

##COLA
M = 23
ola = 3.2
R = 1
win='hann'

print(calc_ola('hann',M,R))


