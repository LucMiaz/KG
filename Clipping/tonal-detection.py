import scipy, pylab
def stft(x, fs, framesz, hop):
    framesamp = int(framesz*fs)
    hopsamp = int(hop*fs)
    w = scipy.hanning(framesamp)
    X = scipy.array([scipy.fft(w*x[i:i+framesamp]) 
                     for i in range(0, len(x)-framesamp, hopsamp)])
    return X,w
    
def sinedistance(X,w,M=3):
    """computes the sine distance.
    S is the signal spectrum
    nmS will be the normalized magnitude spectrum of the signal
    w is the frame window
    nw will be the normalized frame window
    (normalized on S(0)=1, w(0)=1)
    M is "the number of points of the spectrum at each side around the point k to be compared"
    """
    S=abs(X.T)
    sd=[]
    for k in range(min(S),max(S)):
        sdk=0
        for m in range(-M,M):
            sdk+=(abs(nmS[k+m]/nmS[k])-abs(nw[m]/nw[0]))**2
        sdk=(sdk/(2*M+1))**0.5
    return sd
    
def tonaldetection(x,fs,framesz=0.05, hopsz=0.025,threshold=0.25, M=3):
    """
    x                    #signal
    fs                   # sampling rate at 8 kHz
    Timlength=len(x)/fs  # time length
    framesz = 0.050      # frame size of 50 milliseconds
    hopsz = 0.025        # hop size of 25 milliseconds
    threshold =0.25      # sensibility of detection
    M=3                  # span of evaluated neighborhood in sine-distance
    """
    Timelength=len(x)/fs
    X,w = stft(x, fs, framesz, hopsz)
    sd=sinedistance(X,w)
    sdTF=[(sd[k]>threshold) for k in range(0,len(sd))]
    return sdTF

if __name__ == '__main__':
    from scipy.io import wavfile # get the api
    fs, data = wavfile.read('C:/lucmiaz/KG_dev_branch/KG/Clipping/n-05-15-src2.wav') # load the data
    a = data.T[0] # this is a two channel soundtrack, I get the first track 
#remove [0] if mono file
    b=[(ele/2**8.)*2-1 for ele in a]
    TF=stft(b,fs,0.05,0.025)
    #TF=tonaldetection(b,fs)
    print(TF)