# Squared signals 
#
#
import scipy.signal
import numpy as np
import matplotlib.pyplot as plt
from scipy.fftpack import fft, fftshift, fftfreq

N = 700 #1024, provare con numero diverso da 2^l

##Segnali
omega = (3.3)*2*np.pi/N
# variare le frequenze in modo che.
# la frequenza è o non é un multiplo del periodo 
x1 = np.sin(omega*np.arange(0,N))
#fft
X1 = fftshift(fft(x1,N)) 
freq = fftshift(fftfreq(N, 1/(2*np.pi)))
#
f1, ax = plt.subplots(3)
ax[0].plot(x1)
#
ax[1].plot(freq,np.abs(X1),'o',label= 'fft')
ax[2].plot(freq,np.unwrap(np.angle(X1)),'o',label= 'fft')

# add zero padding

for Nz in [100,25000]:
    Xz = fftshift(fft(x1,Nz)) 
    freqz = fftshift(fftfreq(Nz, 1/(2*np.pi)))
    ax[1].plot(freqz,np.abs(Xz),'.')
    ax[2].plot(freqz,np.unwrap(np.angle(Xz)),'.' )
for a in ax :
    a.legend()
    a.grid()
f1.show()
