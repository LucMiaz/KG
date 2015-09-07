"""
Example using myStft
- stft
- Visualizer
"""
#todo convert in notebook
#todo use stft
if __name__ == "__main__":
    
    import sys
    sys.path.append('D:\GitHub\myKG')
    import mySTFT
    from mySTFT.stft import *
    # import mySTFT.Visualizer as Visualizer
    import acoustics
    from kg.time_signal import timeSignal
    from mySTFT.stftWidget import *
    import numpy as np
    from PySide import QtGui, QtCore
    import matplotlib.pyplot as plt
    ##signal1
    # create signal
    sR = 1024
    NF = sR*20
    t = np.arange(0,NF)/sR
    f = 200/20
    omega = 2*np.pi*f
    noise = acoustics.generator.white(NF)
    A = np.sqrt(2)*(2e-5)* 10 **(5/20)
    y =np.cos(omega*t*(t+5)) + 10 **(-30/20)*noise
    sn = {'y':y,'t':t,'sR':sR}
    ##signal2 
    #Read signal from wav
    path = 'D:\GitHub\myKG\Measurements_example\\various_passby'
    s = acoustics.Signal.from_wav(path+'/kreischen.wav')
    sn = {'y':s.pick(),'t':s.times(),'sR':s.fs}
    sn['y'] = sn['y'][7*s.fs:9*s.fs]

    #set stft parameters
    sR = sn['sR']
    M = 8916 #1021
    R = M//6
    window = 'hann'
    #prepare signal such tha invertible
    x , _= pad_to_multiple_of_hoop(sn['y'], R)
    xPadded, before,__=  pad_for_invertible(x,M,R)
    tPadded = (np.arange(0,len(xPadded))- before)/ sR
    N = M #len(xPadded)
    
    #calc STFT
    X, freq, f_i, param = stft(x, M=M, R=R, N=N, sR=sR, window = window, invertible = True )
    padN, before , after = param['0-pad']
    print(param['0-pad'])
    print(param['hoop_added'])
    #istft
    yPadded = istft(X,param)
    y = yPadded[before : - after]
    np.testing.assert_array_almost_equal(x,y)

    #plots
    #x STFT and inverse
    f,ax = plt.subplots(2,sharex = True)
    ax[0].plot(tPadded, xPadded, '-', label='original')
    ax[0].plot(tPadded, yPadded, '-', label = 'istft(stft(x))',alpha = 0.5)
    ax[0].legend()
    plot_spectrogram(X, param, ax[1], freqscale = 'lin', t0 = 0, tmin = 0, tmax=0.8,fmin=1500,fmax=15000)
    #np.testing.assert_array_equal(SS,X)

    #spectrum
    #fft
    N2 = len(xPadded)
    Xs2 = fft(xPadded,n=N2)
    freq2 = fftfreq(N2,1/sR)
    #plot
    
    PSD, freq, t_i =  stft_PSD(X, param)
    Xs, freq = stft_spectrum(X, param)
    
    f, ax = plt.subplots(2,sharex = True)
    ax[0].plot(freq2[1:N2//2],np.log10(abs(Xs2)**2)[1:N2//2],'-r',label = 'fft spectrum')
    ax[0].plot(freq[1:N//2],np.log10(abs(Xs)**2)[1:N//2],'-', label = 'stft spectrum', alpha = 0.5)
    #angle
    ax[1].plot(freq2[1:N2//2], np.unwrap(np.angle(Xs2))[1:N2//2],'or',label = 'fft angle ')
    ax[1].plot(freq[1:N//2], np.unwrap(np.angle(Xs))[1:N//2],'.',label = 'stft angle ')
    for a in ax:
        a.grid(True)
        a.legend()