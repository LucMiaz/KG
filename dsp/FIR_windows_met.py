import numpy as np
from scipy.fftpack import fft, ifft



## tentativo window methods

N = 501# odd
fcut= 0.8
k = np.round(fcut*(N-1)/2)
lowpass = np.zeros((N-1)/2)
lowpass[:k] = 1/N 
H = np.hstack([1/N,lowpass,lowpass[::-1]])
shift = np.exp(1j*2*np.pi/N*(N-1)/2*np.arange(0,N-1))
h = ifft(H *shift )

#-----------
f, ax = plt.subplots(2,sharex=True)
for axes in ax :
    axes.grid()
    for spine in ['left', 'bottom']:
        axes.spines[spine].set_position('zero')
ax[0].plot(H,'or')
ax[0].vlines(np.arange(0,len(H)),[0],H,'r')
ax[1].plot(h,'ob')
ax[1].vlines(np.arange(0,len(h)),[0],h,'b')


##FIR

## h triangolo shifted

N = 11# odd
#
s= 0
shift = np.exp(1j*2*np.pi/N*s*np.arange(0,N))

h1=np.arange(0,(N-1)/2)
h = np.hstack([h1,(N-1)/2,h1[::-1]])*shift
H = fft(h,100)

f, ax = plt.subplots(3,sharex=True)
for axes in ax :
    axes.grid()
    for spine in ['left', 'bottom']:
        axes.spines[spine].set_position('zero')
ax[0].plot(h,'or')
ax[0].vlines(np.arange(0,len(h)),[0],h,'r')
ax[1].plot(np.abs(H),'ob')
ax[1].vlines(np.arange(0,len(np.abs(H))),[0],np.abs(H),'b')
ax[2].plot(np.angle(H),'ob')
ax[2].vlines(np.arange(0,len(np.angle(H))),[0],np.angle(H),'b')

##allpass non shift

#shift
N = 11# odd
#
s= 0
shift = np.exp(1j*2*np.pi/N*s*np.arange(0,N))

h = np.zeros(N)
h[N-1]=1
h*=shift
H = fft(h,10)

f, ax = plt.subplots(3,sharex=True)
for axes in ax :
    axes.grid()
    for spine in ['left', 'bottom']:
        axes.spines[spine].set_position('zero')
ax[0].plot(h,'or')
ax[0].vlines(np.arange(0,len(h)),[0],h,'r')
ax[1].plot(np.abs(H),'ob')
ax[1].vlines(np.arange(0,len(np.abs(H))),[0],np.abs(H),'b')
ax[2].plot(np.angle(H),'ob')
ax[2].vlines(np.arange(0,len(np.angle(H))),[0],np.angle(H),'b')

##non shift
N = 40# odd
#
omega0 = 1.5
r = 0.7
alpha = r*np.exp(1j*omega0)
g = np.hstack([0,[alpha**n for n in range(0,N)]])

h = - np.conjugate(alpha)*g[1:]+g[:-1]
H = fft(h,233)

f, ax = plt.subplots(3,sharex=True)
for axes in ax :
    axes.grid()
    for spine in ['left', 'bottom']:
        axes.spines[spine].set_position('zero')
ax[0].plot(h,'or')
ax[0].vlines(np.arange(0,len(h)),[0],h,'r')
ax[1].plot(np.abs(H),'ob')
ax[1].vlines(np.arange(0,len(np.abs(H))),[0],np.abs(H),'b')
ax[2].plot(np.angle(H),'ob')
ax[2].vlines(np.arange(0,len(np.angle(H))),[0],np.angle(H),'b')