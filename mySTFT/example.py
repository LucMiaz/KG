"""
Example using myStft
- stft
- Visualizer
"""

if __name__ == "__main__":
    
    import sys
    sys.path.append('D:\GitHub\myKG\kg')
    sys.path.append('D:\GitHub\myKG\Measurements_example\various_passby')
    import acoustics
    from time_signal import timeSignal
## crete signal
    sR = 1024
    NF = sR*20
    t = np.arange(0,NF)/sR
    f = 200/20
    omega = 2*np.pi*f
    #noise = acoustics.generator.white(NF)
    A = np.sqrt(2)*(2e-5)* 10 **(5/20)
    y =np.cos(omega*t**2) #+ 10 **(-30/20)*noise)
    sn = {'y':y,'t':t,'sR':sR}
    ## Read signal from zug
    timeSignal._setup('D:\GitHub\myKG\Measurements_example\MBBMZugExample\Messdaten_Matlab')
    signal = timeSignal('m_0100')
    mic=1
    signal.read_signal(mic)
    sn = signal.get_signal(mic)
    
    ##Read signal from wav
    
    # s = acoustics.Signal.from_wav('kreischen.wav')
    # sn = {'y':s.pick(),'t':s.times(),'sR':s.fs}
    ##Run App
    
    STFT( sn=sn['y'], M = sR-1, N = sR, R=(sR-1),sR = sR)
    app = QApplication(sys.argv)
    form = stftWidget(sn)
    form.show()#showFullScreen() 
    app.exec_()