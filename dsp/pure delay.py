import numpy as np
from scipy.fftpack import fft, ifft



##

N = 32# odd
shift=3
Hshift = np.exp(1j*2*np.pi/N*shift*np.arange(0,N))
h = ifft(Hshift )

#-----------
f, ax = plt.subplots(3,sharex=True)
for axes in ax :
    axes.grid()
    for spine in ['left', 'bottom']:
        axes.spines[spine].set_position('zero')
ax[0].plot(np.abs(Hshift),'or')
ax[0].vlines(np.arange(0,len(Hshift)),[0],np.abs(Hshift),'r')
ax[1].plot(np.angle(Hshift),'ob')
ax[2].plot(h,'ob')
ax[2].vlines(np.arange(0,len(h)),[0],h,'b')
#reversed x1
#ax[0].plot(x1[::-1],'og')
##