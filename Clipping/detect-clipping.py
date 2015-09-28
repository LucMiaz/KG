import matplotlib.pyplot as plt
from scipy.io import wavfile # get the api
from scipy.fftpack import fft

def histogram(xn, K):
    """returns the histogram of discrete time signal xn with K bins in histogram"""
    N=len(xn)
    xmin=xn[0]
    xmax=xn[0]
    #find min and max values of signal xn
    for n in range(0,N):
        if xn[n]<xmin:
            xmin=xn[n]
        if xn[n]>xmax:
            xmax=xn[n]
    #setting histogram to 0
    H=[0 for i in range(0,K)]
    for n in range(0,N):
        #calculate y(n)=(x(n)-x_min)/(x_max-x_min)
        yn=((xn[n]-xmin)/(xmax-xmin))#normalize
        #calculate bin index
        k=int(K*yn)
        #add one to the right bin index
        if k<K:
            H[k]+=1
        else:
            H[k-1]+=1
    return H




fs, data = wavfile.read('C:/lucmiaz/KG_dev_branch/KG/Clipping/n-05-15-src2.wav') # load the data
a = data.T[0] # this is a two channel soundtrack, I get the first track 
#remove [0] if mono file

b=[(ele/2**8.)*2-1 for ele in a] # this is 8-bit track, b is now normalized on [-1,1)
c = fft(b) # create a list of complex number
d = len(c)/2  # you only need half of the fft list
#plt.plot(abs(c[:(d-1)]), color='#5ab4ac') 
#plt.plot(b, color='#d8b365')
#plt.show()
#h=histogram(b,16000)
#plt.plot(h,color='#5ab4ac')
#plt.show()
#def isclipped(
e=a.clip(0,6000)
f=[(ele/2**8.)*2-1 for ele in e]
g=histogram(f,100)
plt.bar(range(0,100),g,color='#d8b365')

plt.show()