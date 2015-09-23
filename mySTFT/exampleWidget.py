"""
Example using myStft
- stft
- Visualizer
"""
#todo convert in notebook
if __name__ == "__main__":
    
    import sys
    import acoustics
    sys.path.append('D:\GitHub\myKG')
    import mySTFT
    from mySTFT.stft import *
    from mySTFT.stft_plot import *
    from mySTFT.stft_plot import stftWidget as stftWidget
    import numpy as np
    from PySide import QtGui, QtCore
    import matplotlib.pyplot as plt
    
    ##signal
    sR = 1024
    NF = sR*20
    t = np.arange(0,NF)/sR
    f = 200/20
    omega = 2*np.pi*f
    noise = acoustics.generator.white(NF)
    A = np.sqrt(2)*(2e-5)* 10 **(5/20)
    y =np.cos(omega*t*(t+5)) + 10 **(-30/20)*noise
    sn = {'y':y,'t':t,'sR':sR}

    path = 'C:\lucmiaz\KG_dev_branch\KG\Measurements_example\various_passby'
    s = acoustics.Signal.from_wav(path+'/kreischen.wav')
    sn = {'y':s.pick(),'t':s.times(),'sR':s.fs}
    sn['y'] = sn['y'][5*s.fs:8*s.fs]

    M = 1024
    app = QtGui.QApplication(sys.argv)
    form = stftWidget(sn,M=M)
    form.show()#showFullScreen() 
    app.exec_()