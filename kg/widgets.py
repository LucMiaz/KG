import sys
import os
import numpy as np
from PySide import QtGui, QtCore
from PySide.phonon import Phonon
from PySide.QtGui import (QApplication, QMainWindow, QAction, QStyle,
                          QFileDialog)
                          
sys.path.append('D:\GitHub\myKG')
from kg.detect import *
from kg.mpl_moving_bar import Bar
from pandas.sandbox.qtpandas import DataFrameModel, DataFrameWidget
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.widgets import SpanSelector
import matplotlib.pyplot as plt
                          
class DetectControlWidget(QMainWindow):

    def __init__(self,  wavPath, canvas ,t0 = 0, bar = [], parent = None):
        QMainWindow.__init__(self, parent)
        self.setWindowTitle('listen and detect ;-)')
        #phonon 
        self._init_phonon(wavPath)
        #Attributes
        self.canvas = canvas
        self.bar = bar
        self.tShift = t0
       
        #layout
        self.vBox = QtGui.QVBoxLayout()
        self.vBox.addWidget(self.seeker)
        for k, ca in self.canvas.items():
            self.vBox.addWidget(ca)
        
        #centralwidget
        centralWidget = QtGui.QWidget()
        centralWidget.setLayout(self.vBox)
        self.setCentralWidget(centralWidget)

        # connections
        self.media.tick.connect(self._update)
    
    def _init_phonon(self, wavPath):
        # the media object controls the playback
        self.media = Phonon.MediaObject(self)
        self.audio_output = Phonon.AudioOutput(Phonon.MusicCategory, self)
        self.seeker = Phonon.SeekSlider(self)
        self.seeker.setFixedHeight(20)
        self.seeker.setMediaObject(self.media)
        self.media.setTickInterval(20)
        self.media.setCurrentSource(Phonon.MediaSource(wavPath))
        # audio data from the media object goes to the audio output object
        Phonon.createPath(self.media, self.audio_output)
        # set up actions to control the playback
        ACTIONS = [
            ('play', 'Play', QStyle.SP_MediaPlay),
            ('pause', 'Pause', QStyle.SP_MediaPause),
            ('stop', 'Stop', QStyle.SP_MediaStop)]
        self.actions = self.addToolBar('Actions')
        for name, label, icon_name in ACTIONS:
            icon = self.style().standardIcon(icon_name)
            action = QtGui.QAction(icon, label, self)
            action.setObjectName(name)
            self.actions.addAction(action)
            action.triggered.connect(getattr(self.media, name))
        
    def _update(self,t):
        for bar in self.bar:
            bar.set_x_position(t/1000 + self.tShift )
            
    @classmethod
    def from_micSignal(cls, micSn, mesPath):
        wavPath = micSn.export_to_Wav(mesPath)
        #Canvas
        plt.ioff()
        stftName = micSn.calc_stft(M=1024*4)
        fig, ax = plt.subplots(1,sharex=True)
        micSn.plot_spectrogram(stftName,ax) 
        micSn.plot_triggers(ax)
        micSn.plot_KG(ax)
        ca = FigureCanvas(fig)
        #Bar
        bar1= Bar(ax)
        return(cls(wavPath.as_posix(), {1:ca} , micSn.t.min(), [bar1]))
        
    @classmethod
    def alg_results(cls, micSn, mesPath,algorithm):
        wavPath = micSn.export_to_Wav(mesPath)
        #Canvas
        plt.ioff()
        stftName = micSn.calc_stft(M=1024*4)
        fig, axes = plt.subplots(2,sharex=True)
        ax = axes[0]
        micSn.plot_spectrogram(stftName,ax) 
        micSn.plot_triggers(ax)
        micSn.plot_KG(algorithm,ax)
        bar1= Bar(ax)
        ax = axes[1]
        micSn.plot_BPR(algorithm,ax)
        ca = FigureCanvas(fig)
        bar2= Bar(ax)
        
        return(cls(wavPath.as_posix(), {1:ca} , micSn.t.min(), [bar1,bar2]))
##
if __name__ == "__main__":
    import pathlib
    sys.path.append('D:\GitHub\myKG')
    from kg.measurement_values import measuredValues
    from kg.measurement_signal import measuredSignal
    #setup measurement
    mesPath = pathlib.Path('D:\GitHub\myKG\Measurements_example\MBBMZugExample')
    mesVal = measuredValues(mesPath.as_posix())
    mesVal.read_variables_values()
    measuredSignal.setup(mesPath.as_posix())
    
    mID = 'm_0100'
    mic = 1
    mesSn = measuredSignal(mID,mic)
    y, t, sR = mesSn.get_signal(mic)
    values = mesVal.get_variables_values(mID, mic, [ 'Tb','Te','Tp_b','Tp_e','LAEQ', 'besch'])
    micSn = MicSignal(mID, mic,y, t, sR, values)
    ## Run
    W = DetectControlWidget.from_micSignal(micSn)
    W.show()