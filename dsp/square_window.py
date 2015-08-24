# Squared signals 
#
#
import scipy.signal
import numpy as np
import matplotlib.pyplot as plt
from scipy.fftpack import fft, fftshift, fftfreq

N = 20 #1024, provare con numero diverso da 2^l



##Segnali
#segnale1: impulso di lunghezza N
x1 = np.ones(N)
#fft
X1 = fftshift(fft(x1,N)) 
freq = fftshift(fftfreq(N, 1/(2*np.pi)))
#DTFT
freqw = np.linspace(-np.pi, np.pi, 800);
X_dtft = (np.sin(freqw*N/2)/ np.sin(freqw/2))* np.exp(-1j * freqw * (N-1) / 2);
#
f1, ax = plt.subplots(2,sharex=True)
ax[0].plot(freqw,np.abs(X_dtft))
ax[1].plot(freqw,np.angle(X_dtft))
ax[0].plot(freq,np.abs(X1),'o',label= 'fft')
ax[1].plot(freq,np.angle(X1),'o',label= 'fft')

#add zero padding

for Nz in [21,22,23,2*N]:
    Xz = fftshift(fft(x1,Nz)) 
    freqz = fftshift(fftfreq(Nz, 1/(2*np.pi)))
    ax[0].plot(freqz,np.abs(Xz),'.')
    ax[1].plot(freqz,np.angle(Xz),'.' )
for a in ax :
    a.legend()
    a.grid()
f1.show()
