import scipy
import scipy.signal
import numpy as np
import matplotlib.pyplot as plt
from scipy.fftpack import fft, fftshift, fftfreq

N = 2**8 #1024, provare con numero diverso da 2^l
Nz = 2**13 # 1024, provare con numero diverso da 2^l
# sample, spacing, framerate
fs = N
dt = 1.0 / fs
#lunghezza segnale
T = dt * N
t = np.linspace(0.0, T, N)
#lunghezza segnale Zero padded
Tz = dt * Nz
tz = np.linspace(0.0, Tz, Nz)

##Segnali
#segnale1: seno con frequenza omega
omega = 21.7 * 2 * np.pi
phase = 2*np.pi*10
x1 = np.sin(omega * t - phase)


#segnale2: finestra hamming
x2 = scipy.signal.hamming(N)

#segnale3: finestra quadraze
x3 = np.ones(N)

## fft DTFT
#normale
X1,X2,X3 = [fftshift(fft(x,N)) for x in [x1,x2,x3]]

freq = fftshift(fftfreq(N,dt))
#zero padded
X1z,X2z,X3z = [fftshift(fft(x,Nz)) for x in [x1,x2,x3]]

freqz = fftshift(fftfreq(Nz,dt))

##plots
#time domain
f, ax = plt.subplots(1,sharex=True)
ax.plot(t,x1)
ax.plot(t,x2)
ax.plot(t,x3)
ax.set_ylim(-2,2)
f.show()
##
#fft
def plot1(freq,X,freqz,Xz):
    f, ax = plt.subplots(2,sharex=True)
    ax[0].plot(freqz,np.log10(np.abs(Xz)), label= 'zero,padded')
    ax[1].plot(freqz,np.angle(Xz), label= 'zero,padded')
    ax[0].plot(freq,np.log10(np.abs(X)))
    ax[1].plot(freq,np.angle(X))
    for a in ax :
        a.legend()
        a.grid()
    f.show()
plot1(freq,X1,freqz,X1z)
plot1(freq,X2,freqz,X2z)
plot1(freq,X3,freqz,X3z)