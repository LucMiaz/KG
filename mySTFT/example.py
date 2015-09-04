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
#     # Read signal from zug
#     timeSignal._setup('D:\GitHub\myKG\Measurements_example\MBBMZugExample\Messdaten_Matlab')
#     signal = timeSignal('m_0100')
#     mic=1
#     signal.read_signal(mic)
#     sn = signal.get_signal(mic)
#    
    ##signal2 
    #Read signal from wav
    path = 'D:\GitHub\myKG\Measurements_example\\various_passby'
    s = acoustics.Signal.from_wav(path+'/kreischen.wav')
    sn = {'y':s.pick(),'t':s.times(),'sR':s.fs}
    sn['y'] = sn['y'][7*s.fs:9*s.fs]
#     #Run App
#     
#     STFT( sn=sn['y'], M = sR-1, N = sR, R=(sR-1),sR = sR)
#     app = QtGui.QApplication(sys.argv)
#     form = mySTFT.Visualizer(sn)
#     form.show()#showFullScreen() 
#     app.exec_()

#set parameters
    sR = sn['sR']
    M = 8916 #1021
    R = M//6
    window = 'hann'
    #prepare signal such tha invertible
    x , _= pad_to_multiple_of_hoop(sn['y'], R)
    xPadded,__,__=  pad_for_invertible(x,M,R)
    tPadded = np.arange(0,len(xPadded))/ sR
    N = M #len(xPadded)
    
    #calc STFT
    X, freq, f_i, param = stft(x, M=M, R=R, N=N, sR=sR, window = window, invertible = True )
    padN, before , after = param['0-pad']
    print(param['0-pad'])
    print(param['frames_added'])
    #istft
    yPadded = istft(X,param)
    y = yPadded[before : - after]
    np.testing.assert_array_almost_equal(x,y)
    #spectrum
    Xs,_ = stft_spectrum(X,param)
    #fft
    N2 = len(xPadded)
    Xs2 = fft(xPadded,n=N2)
    freq2 = fftfreq(N2,1/sR)
    
    #plots
    #x STFT and inverse
    f,ax = plt.subplots(2,sharex = True)
    ax[0].plot(tPadded,xPadded,'-',label='original')
    ax[0].plot(tPadded,yPadded,'-', label = 'istft(stft(x))')
    ax[0].legend()
    plot_spectrogram(X,param, ax[1],freqscale = 'lin')
    #spectrum
    f, ax = plt.subplots(2,sharex = True)
    ax[0].plot(freq2[1:N2//2],np.log10(abs(Xs2)**2)[1:N2//2],'-r',label = 'fft spectrum')
    ax[0].plot(freq[1:N//2],np.log10(abs(Xs)**2)[1:N//2],'-', label = 'stft spectrum')
    #angle
    ax[1].plot(freq2[1:N2//2],np.unwrap(np.angle(Xs2))[1:N2//2],'or',label = 'fft angle ')
    ax[1].plot(freq[1:N//2],np.unwrap(np.angle(Xs))[1:N//2],'.',label = 'stft angle ')
    for a in ax:
        a.grid(True)
        a.legend()