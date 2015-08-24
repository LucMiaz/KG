# Squared signals 
#
#
import scipy.signal
import numpy as np
import matplotlib.pyplot as plt
from scipy.fftpack import fft, fftshift, fftfreq

##COLA
M = 7
ola = 1
R = (M-1)//ola
w = scipy.signal.get_window('hann',M)
ww = scipy.signal.hann(M,sym = True)
norm = [np.sum([ w[i] for i in range(s,M,R)]) for s in range(0,R)]

l = 10
f_i= np.arange((M-1)/2,l*M-(M-1)/2,R)

w_i =[]
for nl,nu in zip(f_i-(M-1)/2, -f_i-(M-1)/2+l*M-1):
    window = np.lib.pad(w, (int(nl),int(nu)), 'constant', constant_values=0)
    w_i.append(window)

f1, ax = plt.subplots(2)
ax[0].plot(ww,color = 'red')
ax[0].plot(w)

sum = np.zeros(l*M)
for win in w_i:
    ax[1].plot(win)
    sum+=win
ax[1].plot(sum)
ax[0].grid()
print(norm)
print(np.sum(w))

