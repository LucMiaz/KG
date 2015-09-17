import sys
import os
import numpy as np
from PySide import QtGui, QtCore
from PySide.phonon import Phonon
from PySide.QtGui import (QApplication, QMainWindow, QAction, QStyle,
                          QFileDialog)
                          
sys.path.append('D:\GitHub\myKG')
sys.path.append('C:\LucMiaz\KG')
from kg.detect import *
from kg.mpl_moving_bar import Bar
from pandas.sandbox.qtpandas import DataFrameModel, DataFrameWidget
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.widgets import SpanSelector
import matplotlib.pyplot as plt
                          
class DetectControlWidget(QMainWindow):
    """General window creator. 
        -Audio file
        -Canvas
        -Optional moving bar. 
        """
    def __init__(self,  wavPath, canvas ,t0 = 0, bar = [], parent = None):
        QMainWindow.__init__(self, parent)
        self.setWindowTitle('listen and detect ;-)')
        #phonon 
        self._init_phonon(wavPath)#Path to the audio file
        #Attributes
        self.canvas = canvas #graphic
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
    def from_micSignal(cls, micSn):
        wavPath = micSn.export_to_Wav(mesPath)
        #Canvas
        plt.ioff()
        stftName = micSn.calc_stft(M=1024*4)
        ca = FigureCanvas(plt.subplots(1,sharex=True)[0])
        ax = ca.figure.get_axes()
        micSn.plot_spectrogram(stftName,ax[0])
        #Bar
        bar1= Bar(ax[0])
        return(cls(wavPath.as_posix(), {1:ca} , micSn.tmin, [bar1]))
        
##
class CaseCreatorWidget(DetectControlWidget):
    '''
    this is a subclass of DetectControlWidget
    this widget should allow to create cases in GUI style
    kg_ event duration is selected with mouse cursor
    case is saved using a button
    '''
<<<<<<< HEAD
    def __init__(self, micSn, wavPath, canvas ,t0 = 0, bar = [], parent = None):
=======
    def __init__(self, micSn):
>>>>>>> devCaseCreator
        measurement = ''
        #initiate new Case
        #todo
        self.case = Case()

        #span selector
        self.span = SpanSelector(axSpan, self._onselect, 'horizontal',\
        span_stays=True, useblit = True,
                            rectprops=dict(alpha=0.5, facecolor='red'))
                            
        self.kg_events = []
        #initiate superclass
        super(DetectControlWidget, self).__init__(wavPath, canvas ,t0 = 0,\
        bar = [], parent = None)
        self.setWindowTitle('Create Case')
        hBox = QtGui.QHBoxLayout()
        label = QtGui.QLabel('''Select channel to play, first widget''')
        self.buttonRm = QtGui.QPushButton("delete last event",self)
        self.buttonSave = QtGui.QPushButton("Save Case",self)
        hBox.addWidget(self.buttonLim)
        hBox.addWidget(self.buttonR)
        hBox.addStretch(1)
        self.vBox.addLayout(hBox)
        
        # centralwidget
        centralWidget = QtGui.QWidget()
        centralWidget.setLayout(self.vBox)
        self.setCentralWidget(centralWidget)
        
        # connections
        self.buttonRm.clicked.connect(self.remove_last_event)
        self.buttonSave.clicked.connect(self.save_case)
        
    def _initgraphics(self, micSn):
        #create Graphics
        plt.ioff()
        stftName = micSn.calc_stft(M=1024*4)
        self.canvas = FigureCanvas(plt.subplots(2,sharex=True)[0])
        ax0, axSpan = ca.figure.get_axes()
        micSn.plot_spectrogram(stftName,ax0)
        micSn.plot_spectrogram(stftName,axSpan)    
        #Bar
        self.bar = Bar(ax0)
        
    def _onselect(self, xmin, xmax):
        self.case.add_kg_event()
        self.kg_events.append(axSpan.axvspan(xmin, xmax, facecolor='g', alpha=0.5))
        
    def remove_last_event(self):
        #todo
        pass
        
    def save_case(self):
        #todo
        pass

##

if __name__ == "__main__":
    import pathlib
    sys.path.append('D:\GitHub\myKG')
    from kg.measurement_values import measuredValues
    from kg.time_signal import timeSignal
    #setup measurement
    #mesPath = pathlib.Path('D:\GitHub\myKG\Measurements_example\MBBMZugExample')
    mesPath = pathlib.Path('C:\LucMiaz\KG\Measurements_example\MBBMZugExample')
    mesVal = measuredValues(mesPath.as_posix())
    mesVal.read_variables_values()
    timeSignal.setup(mesPath.as_posix())
    
    mID = 'm_0100'
    ts = timeSignal(mID)
    mic = 1
    ts.read_signal(mic)
    sn = ts.get_signal(mic)
    values = mesVal.get_variables_values(mID, mic, [ 'Tb','Te','Tp_b','Tp_e','LAEQ', 'besch'])
    micSn = MicSignal(sn,mID,mic,values)
    ## Run
    W = DetectControlWidget.from_micSignal(micSn)
    W.show()