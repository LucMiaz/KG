import matplotlib.pyplot as plt
from scipy.io import wavfile # get the api
from scipy.fftpack import fft

def isclipped(xn, K=301, threshold=0.55, displayhist=False, normalizehist=False):
    """
    Tells if the signal xn is clipped or not based on the test by Sergei Aleinik, Yuri Matveev.
    Returns a boolean. 
    Reference: Aleinik S. and Matveev Y. 2014 : Detection of Clipped Fragments in Speech Signals, in International Journal of Electrical, Computer, Energetic, Electronic and Communication Engineering. World Academy of Science, Engineering and Technology, 8, 2, 286--292.
"""
    N=len(xn)
    H=histogram(xn,K,display=displayhist, normalize=normalizehist)
    #Find the very left non-zero k_l histogram bin index
    kl=0
    while H[kl]==0 and kl<=K/2:
        k+=1
    #Find the very right non-zero k_r histogram bin index
    kr=K-1
    while H[kr]==0 and kr>=K/2:
        kr-=1
    #Calculate Denom=k_r-k_l
    Denom=kr-kl
    #sets parameters
    yl0=H[kl]
    yr0=H[kr]
    dl=0
    dr=0
    Dmax=0
    #iteration
    while kr>kl :
        kl+=1
        kr-=1
        if H[kl]<=yl0:
            dl+=1
        else:
            yl0=H[kl]
            dl=0
        if H[kr]<=yr0:
            dr+=1
        else:
            yr0=H[kr]
            dr=0
        Dmax=max(Dmax,dl,dr)
    Rcl=2*Dmax/Denom
    return Rcl>threshold
    
def histogram(xn, K, display=False, normalize=False):
    """returns the function histogram of discrete time signal xn with K bins in histogram"""
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
    if normalize:
        maximum=max(H)
        H=[i/maximum for i in H]
    if display:
        plt.bar(range(0,K),H,color='#d8b365')
    return H

fs, data = wavfile.read('C:/lucmiaz/KG_dev_branch/KG/Measurements_example/various_passby/kreischen.wav') # load the data
a = data.T # this is a two channel soundtrack, I get the first track 
#remove [0] if mono file

b=[(ele/2**8.)*2-1 for ele in a] # this is 8-bit track, b is now normalized on [-1,1)
#c = fft(b) # create a list of complex number
#d = len(c)/2  # you only need half of the fft list
#plt.plot(abs(c[:(d-1)]), color='#5ab4ac') 
#plt.plot(b, color='#d8b365')
#plt.show()
ret=isclipped(b,displayhist=True, normalizehist=True)
print(ret)
#plt.plot(h,color='#5ab4ac')
#plt.show()

#e=a.clip(-6000,6000)
#f=[(ele/2**8.)*2-1 for ele in e]
#g=histogram(f,100, True, True)
#ret=isclipped(f,displayhist=True, normalizehist=True)
#print(ret)
plt.show()
