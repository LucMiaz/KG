# Squared signals 
#
#
import scipy.signal
import numpy as np
import matplotlib.pyplot as plt
from scipy.fftpack import fft, fftshift, fftfreq

N = 1000#1024, provare con numero diverso da 2^l



##Segnali
#segnale1: impulso di lunghezza N
w1 = np.ones(N)
w2 = scipy.signal.flattop(N)
w3 = scipy.signal.hamming(N)
#fft
Nz = N*10
W1 = fftshift(fft(w1,Nz)) 
freq = fftshift(fftfreq(Nz, 1/(2*np.pi)))
W2 = fftshift(fft(w2,Nz)) 
#
f1, ax = plt.subplots(3)
#
ax[0].plot(w1)
ax[0].plot(w2)
ax[0].set_ylim(-1,2)
ax[1].plot(freq,np.abs(W1))
ax[2].plot(freq,np.unwrap(np.angle(W1)))
ax[1].plot(freq,np.abs(W2),label= 'fft')
ax[2].plot(freq,np.unwrap(np.angle(W2)),label= 'fft')
for axes in ax :
    axes.grid()
##
t = np.arange(0,N)
x = 2*np.sin(2*np.pi/N*5*t+np.pi)+ np.random.normal(0,2,N)

Xw1= fftshift(fft(x*w1,Nz))
Xw2= fftshift(fft(x*w2,Nz))
Xw3= fftshift(fft(x*w3,Nz))

f1, ax = plt.subplots(3)
#
ax[0].plot(x)
ax[0].plot(x*w2)
ax[1].plot(freq,np.abs(Xw1))
ax[2].plot(freq,np.unwrap(np.angle(Xw1)))
ax[1].plot(freq,np.abs(Xw2),label= 'fft')
ax[2].plot(freq,np.unwrap(np.angle(Xw2)),label= 'fft')
for axes in ax :
    axes.grid()
    
##COLA
M = 51
l = 5

ola = 2
R = (M-1)/ola
wFlat = scipy.signal.get_window('hann', M)
f_i= np.arange((M-1)/2,l*M-(M-1)/2,R)

w_i =[]
for nl,nu in zip(f_i-(M-1)/2, -f_i-(M-1)/2+l*M-1):
    window = np.lib.pad(wFlat, (int(nl),int(nu)), 'constant', constant_values=0)
    w_i.append(window)

f1, ax = plt.subplots(1)
sum = np.zeros(l*M)
for w in w_i:
    ax.plot(w)
    sum+=w
ax.plot(sum)
ax.grid()
