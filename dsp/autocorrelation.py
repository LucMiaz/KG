# calculation of power spectrum(autocorrelation) 
# of infinite sequence(with finite non-0 elements) with 
# FFT and circonvolution
# 
#
import scipy.signal
import numpy as np
import matplotlib.pyplot as plt
from scipy.fftpack import fft, fftshift, fftfreq

def circonvolve(h,x):
    N = len(h)
    if not len(x) == N :
        raise(ValueError('h and x should have same len'))
    y = []
    for n in range(0,N):
        y.append(np.sum([h[i]*x[(n-i)%N] for i in range(0,N)]))
        
    return(np.array(y))
    
def circonvolvefft(h,x):
    if not len(x) == len(h) :
        raise(ValueError)
    return(ifft(fft(h)*fft(x)))
    
def circcorrelate(x,y):
    y = np.conjugate(y)
    y = np.pad(y[::-1],(0,len(x)-len(y)),mode='constant',constant_values=0)
    return(circonvolve(x,y))
    
def circcorrelatefft(x,y):
    y = np.conjugate(y)
    y = np.pad(y[::-1],(0,len(x)-len(y)),mode='constant',constant_values=0)
    return(circonvolvefft(x,y))

##Segnali
N=100
t = np.arange(0,N)
x = 2*np.sin(2*np.pi/N*5*t+np.pi)+ np.random.normal(0,2,N)
xz = np.pad(x,(0,N-1),mode='constant',constant_values=0)
E = np.sum(x**2)


f1, ax = plt.subplots(4,sharex=True)
#
ax[0].plot(xz)
ax[1].plot(scipy.signal.correlate(x,x),label= 'linear')
ax[1].plot(scipy.signal.convolve(x,np.conjugate(x)[::-1]),label= 'linear')
ax[1].plot(np.tile(E,len(x)),label= 'Energy')
#
ax[2].plot(circcorrelate(x,x),label= 'circ')
ax[2].plot(circcorrelate(xz,x),label= 'circ-0-padded')
ax[2].plot(fftshift(circcorrelate(xz,x)),label= 'shift circ-0-padded')


ax[3].plot(circcorrelatefft(x,x),label= 'circ FFT')
ax[3].plot(circcorrelatefft(xz,x),label= 'circ-0-padded FFT')


for axes in ax :
    axes.grid()
    