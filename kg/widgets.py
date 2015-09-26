# import sys
# sys.path.append('D:\GitHub\myKG')
import os, pathlib
import numpy as np
from PySide import QtGui, QtCore
from PySide.phonon import Phonon
from PySide.QtGui import (QApplication, QMainWindow, QAction, QStyle,
                          QFileDialog)
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
                          
from kg.detect import MicSignal
from kg.mpl_moving_bar import Bar
from kg.case import Case
from kg.intervals import GraphicalIntervalsHandle

                          
class DetectControlWidget(QMainWindow):

    def __init__(self,  wavPath, canvas , t0 = 0, bar = [], parent = None):
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
        fig, axes = plt.subplots(1,sharex=True)
        ax = axes
        micSn.plot_spectrogram(stftName,ax) 
        micSn.plot_triggers(ax)
        ca = FigureCanvas(fig)
        #Bar
        Bars = [Bar(ax) for ax in axes] if isinstance(ax,list) else [Bar(ax)]
        return(cls(wavPath.as_posix(), {1:ca} , micSn.t.min(), Bars))
        
    @classmethod
    def alg_results(cls, micSn, algorithm):
        wavPath = micSn.export_to_Wav()
        #Canvas
        plt.ioff()
        ca, Bars = algorithm.visualize(micSn)
        return(cls(wavPath.as_posix(), {str(micSn):ca} , micSn.t.min(), Bars ))

class CaseCreatorWidget(DetectControlWidget):
    '''
    this is a subclass of DetectControlWidget
    this widget should allow to create cases in GUI style
    kg_ event duration is selected with mouse cursor
    case is saved using a button
    '''

    def __init__(self, case, micSn, author, mesPath):
        plt.ioff()
        self.case =  case
        self.Z = self.case.get_SOI('Z')
        #plots
        canvas={}
        bar = []
        fig, ax = plt.subplots(1, sharex = True)
        micSn.plot_signal(ax)
        micSn.plot_triggers(ax)
        canvas[0] = FigureCanvas(fig)
        bar.append(Bar(ax))
        self.ax = ax
        #set Handle
        fig, ax = plt.subplots(1, sharex = True)
        micSn.plot_signal(ax)
        micSn.plot_triggers(ax)
        canvas[1] = FigureCanvas(fig)
        self.HandleAxis = ax
        self.SOIHandle = GraphicalIntervalsHandle(self.HandleAxis, self.Z)
        #
        t0 = micSn.t.min()
        wavPath = micSn.export_to_Wav(mesPath)
        #init super
        super(CaseCreatorWidget, self).__init__(str(wavPath), canvas, t0, bar )
        self.setWindowTitle('Create Case')
        #
        #initiate superclass
        hBox = QtGui.QHBoxLayout()
        #label = QtGui.QLabel('''Select channel to play, first widget''')
        self.buttonNext = QtGui.QPushButton("next",self)
        self.buttonSave = QtGui.QPushButton("save",self)
        hBox.addWidget(self.buttonNext)
        hBox.addWidget(self.buttonSave)
        hBox.addStretch(1)
        self.vBox.addLayout(hBox)
        # connections
        self.buttonNext.clicked.connect(self.next_case)
        self.buttonSave.clicked.connect(self.save_case)
    
    def next_case(self):
        pass
        
    def save_case(self):
        self.case.save()
        
    @classmethod
    def from_measurement(cls, mesVal,mID,mic):
        case = Case()
        wavPath = micSn.export_to_Wav()
        #Canvas
        plt.ioff()
        ca, Bars = algorithm.visualize(micSn)
        return(cls(wavPath.as_posix(), {str(micSn):ca} , micSn.t.min(), Bars ))
        QMessageBox.information(w, "Message", "An information messagebox @ pythonspot.com ")
        
   
##
if __name__ == "__main__":
    from kg.measurement_values import measuredValues
    from kg.measurement_signal import measuredSignal
    from kg.algorithm import ZischenDetetkt1
    #setup measurement
    mesPath = 'Measurements_example\MBBMZugExample'
    mesVal = measuredValues.from_json(mesPath)
    measuredSignal.setup(mesPath)
    #algorithm
    algorithm = ZischenDetetkt1(2000,0,0.1)
    mID = 'm_0100'
    mic = 6
    micSn = MicSignal.from_measurement(mesVal,mID, mic)
    micSn.calc_kg(algorithm)
    #Run Widget
    #W = DetectControlWidget.alg_results(micSn,algorithm)
    caseParam = {'measurement':mesVal.measurement,\
                'location': mesVal.location,
                'mID':mID,'mic':mic,
                'author':'esr'}
    caseParam.update(mesVal.get_variables_values(mID,mic,['Tb','Te']))
    newcase = Case(**caseParam)
    W = CaseCreatorWidget(newcase,micSn,'esr',mesVal.path.as_posix())
    W.show()
    