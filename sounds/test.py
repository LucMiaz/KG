import matplotlib.pyplot as plt
from scipy.io import wavfile # get the api
fs, data = wavfile.read('test.wav') # load the data
a = data.T[0] # this is a two channel soundtrack, I get the first track
b=[(ele/2**8.)*2-1 for ele in a] # this is 8-bit track, b is now normalized on [-1,1)
c = sfft.fft(b) # create a list of complex number
d = len(c)/2  # you only need half of the fft list
plt.plot(abs(c[:(d-1)]),'r') 
plt.show()