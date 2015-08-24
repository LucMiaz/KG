import numpy as np
from scipy.fftpack import fft, ifft
# Caso continuo e infinito
# una funzione f é simmetrica (even) se f(t)=f(-t), analogamente si definisce 
# antisimmetria
# Proprietàa della FT:
# se la funzione f(t) é simmetrca  allora F[f(t)](omega) é simmetrica
#
# Caso discreto e finito
# Analogamente si pù definire una serie x(n) simmetrica se x(-n)= x(n)
# Nel caso in cui finito bisogna osservare la sua continuazione periodica 
# (attenzione a N se pari o dispari)
# le proprietàa sono analoge al caso continuo
#
# Se la sequenza/funzione é reale e simmetrica, allora la trasformata sarà 
# reale e simmetrica 

## Esempi
N = 14
x = np.random.randint(0,2,N)
xs = x
xs[1:] = xs[1:]+(x[1:])[::-1]
Xs = fft(xs,N)

f, ax = plt.subplots(3,sharex=True)
for axes in ax :
    axes.grid()
    for spine in ['left', 'bottom']:
        axes.spines[spine].set_position('zero')
ax[0].plot(xs,'or')
ax[0].vlines(np.arange(0,len(xs)),[0],xs,'r')

ax[1].plot(np.abs(Xs),'ob')
ax[1].vlines(np.arange(0,len(np.abs(Xs))),[0],np.abs(Xs),'b')

ax[2].plot(np.imag(Xs),'ob')
ax[2].vlines(np.arange(0,len(np.imag(Xs))),[0],np.imag(Xs),'b')