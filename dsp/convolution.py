"""
Comparison of circular convolution with linear convolution in time and FFT domain
"""
import numpy as np
import scipy
from scipy.fftpack import fft, ifft



#ciclic convolution 1
def circonvolve(h,x):
    N = len(h)
    if not len(x) == N :
        raise(ValueError)
    y = []
    for n in range(0,N):
        y.append(np.sum([h[i]*x[(n-i)%N] for i in range(0,N)]))
        
    return(np.array(y))
    
def circonvolvefft(h,x):
    N = len(h)
    if not len(x) == N :
        raise(ValueError)
    return(ifft(fft(h)*fft(x)))

##example
    
#signals to convolve
x1 = np.array([-1,2,3,-2,-1,-4,6,7,1,-3,-5,-2,-1,1])
h1 = np.array([1,0,-1,0,2,0,-2,0,3,0,-3])

f1, ax = plt.subplots(4,sharex=True,sharey=True)
for axes in ax :
    axes.grid()
    for spine in ['left', 'bottom']:
        axes.spines[spine].set_position('zero')
ax[0].plot(h1,'or')
ax[0].vlines(np.arange(0,len(h1)),[0],h1,'r')
ax[0].plot(x1,'ob')
ax[0].vlines(np.arange(0,len(x1)),[0],x1,'b')
#reversed x1
#ax[0].plot(x1[::-1],'og')

#linear convolve
y1 = np.convolve(h1,x1)
ax[1].plot(y1,'oc')
ax[1].vlines(np.arange(0,len(x1)+len(h1)-1),[0],y1,'c')

#ciclic convolution with 0-padded signals
N= len(x1)
for Nz in [N,N+5,2*N-1]:
    h = np.lib.pad(h1, (0,Nz-len(h1)), 'constant', constant_values=0)
    x = np.lib.pad(x1, (0,Nz-len(x1)), 'constant', constant_values=0)
    y= circonvolve(h,x)
    ax[2].plot(y,'o')
    ax[2].vlines(np.arange(0,len(y)),[0],y)

#ciclic fft convolution with 0-padded signals

N= len(x1)
for Nz in [N,N+5,2*N-1]:
    h = np.lib.pad(h1, (0,Nz-len(h1)), 'constant', constant_values=0)
    x = np.lib.pad(x1, (0,Nz-len(x1)), 'constant', constant_values=0)
    yfft = circonvolvefft(h,x)
    ax[3].plot(yfft,'o')
    ax[3].vlines(np.arange(0,len(yfft)),[0],yfft)

ylim = np.ceil(np.abs(y1).max())+1
ax[0].set_ylim(-ylim,ylim)
#ax[0].set_xlim(-1,len(x1)+len(h1))


##ciclic convolution 2 




