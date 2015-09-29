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
from kg.case import *

                          
class DetectControlWidget(QMainWindow):

    def __init__(self,  wavPath, t0 = 0, setup = True, parent = None, **kwargs):
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
#time to syncronize plot and media object
        self.tShift = t0
        self.t = self.tShift
        #layout
        self.vBox = QtGui.QVBoxLayout()
        self.vBox.addWidget(self.seeker)
        #add mpl objects
        self.set_mpl(**kwargs)
        #finish setup
        if setup:
            self.setup(**kwargs)
    
    def setup(self):
        #centralwidget
        centralWidget = QtGui.QWidget()
        centralWidget.setLayout(self.vBox)
        self.setCentralWidget(centralWidget)
        #add connections and star timer
        self.connections()
        
    def set_mpl(self, canvas= {} ,mpl_animated=[],**kwargs):
        self.canvas = canvas
        if mpl_animated == None:
            slef.mpl_animated=[]
        elif isinstance(mpl_animated,list):
            self.mpl_animated = mpl_animated
        else:
            self.mpl_animated = [mpl_animated]
        for k, ca in self.canvas.items():
            self.vBox.addWidget(ca)
            
    def connections(self):
        #refresh timer
        self.timer = QtCore.QTimer()
        # connections
        self.timer.timeout.connect(self.update)
        self.media.tick.connect(self.update_time)
        self._connections()
        #start refresh
        self.timer.start(25)
        
    def _connections(self):
        pass
        
    def update_time(self,t):
        def _update(self,t):
            self.t = t/1000 + self.tShift
            for bar in self.bar:
    
                bar.set_x_position(t/1000 + self.tShift )
        def update(self):
            for mpl_obj in self.mpl_animated:
                mpl_obj.set_bar_position(self.t)
                mpl_obj.update()
            
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
    def __init__(self, case,micSn, author, mesPath):
        #init super
        super(CaseCreatorWidget, self).__init__(str(micSn.export_to_Wav(mesPath)), t0=micSn.t.min(), setup=False)
        self.setWindowTitle('Create Case')
        ###
        plt.ioff()
        #plots
        canvas={}
        # fig, ax = plt.subplots(1, sharex = True)
        # micSn.plot_signal(ax)
        # micSn.plot_triggers(ax)
        # canvas[0] = FigureCanvas(fig)
        # bar.append(Bar(ax))
        # self.ax = ax
        #set Handle
        fig, ax = plt.subplots(1, sharex = True)
        micSn.plot_signal(ax)
        micSn.plot_triggers(ax)
        canvas[1] = FigureCanvas(fig)
        self.HandleAxis = ax
        #case Selector
        self.CS = CaseSelector(self.HandleAxis, self.onselect, self.onclick, 
                                nrect = [20,20], update_on_ext_event = True , 
                                minspan = 0.2 )
        self.set_mpl(canvas, self.CS)
        #
        self.remove = False
        self.both_visibles=True
        #case
        self.case =  case
        self.NoiseTypes = ['Z','KG']
        self.current_noise = 'Z'
        self.set_noise_type('Z')
       
        #add combo box
        hBox = QtGui.QHBoxLayout()
        label = QtGui.QLabel('Noise Type to select ')
        self.SOIcombo = QtGui.QComboBox()
        self.SOIcombo.addItem('Zischen', 'Z')
        self.SOIcombo.addItem('Kreischen', 'KG')
        self.cb = QtGui.QCheckBox('both visible', self)
        self.cb.toggle()
        self.cb.setChecked(True)
        hBox.addWidget(label )
        hBox.addWidget(self.SOIcombo)
        hBox.addWidget(self.cb)
        hBox.addStretch(1)
        self.vBox.addLayout(hBox)
##
        #add buttons
        hBox = QtGui.QHBoxLayout()
        self.buttonNext = QtGui.QPushButton("next",self)
        self.buttonSave = QtGui.QPushButton("save",self)
        hBox.addWidget(self.buttonNext)
        hBox.addWidget(self.buttonSave)
        label = QtGui.QLabel('''Select channel to play, first widget''')
        self.buttonRm = QtGui.QPushButton("delete last event",self)
        self.buttonSave = QtGui.QPushButton("Save Case",self)
        hBox.addWidget(self.buttonLim)
        hBox.addWidget(self.buttonR)
        hBox.addStretch(1)
        self.vBox.addLayout(hBox)
        #finish setup
        self.setup()
    
    def _connections(self):
        #connections
        self.SOIcombo.currentIndexChanged.connect(self.set_noise_type)
        self.cb.stateChanged.connect(self.set_both_visible)
        #self.buttonNext.clicked.connect(self.next_case)
        self.buttonSave.clicked.connect(self.save_case)
    def set_both_visible(self, state):
        if state == QtCore.Qt.Checked:
            self.both_visibles= True
        else:
            self.both_visibles= False
        self.update_stay_rect()
        
    def add_int(self, xmin,xmax):
        Int = Interval(xmin,xmax)
        self.SOI.append(Int)
        print('Add '+ repr(Int))
        self.update_stay_rect()
        
    def set_noise_type(self, index):
        if isinstance(index,int):
            self.current_noise = self.NoiseTypes[index]
        else:
            self.current_noise = index
        self.SOI = self.case.case[self.current_noise]
        self.update_stay_rect()
        
    def remove_int(self,xmin, xmax = None):
        if xmax == None:
            index = self.SOI.containspoint(xmin)
            if index is not None:
                #print('Remove '+ repr(self.SOI.RangeInter[index]))
                self.SOI.removebyindex(index)
        else:
            self.SOI.remove(xmin,xmax)
        self.update_stay_rect()
        
    def update_stay_rect(self):
        for index,nT in enumerate(self.NoiseTypes):
            if nT == self.current_noise:
                self.CS.set_stay_rects_x_bounds(self.SOI.tolist(),index)
            elif self.both_visibles:
                self.CS.set_stay_rects_x_bounds(self.case.case[nT].tolist(), index)
            else:
                self.CS.set_stay_rect_visible(False, index)
        
    def onselect(self,xmin,xmax):
        #add interval1
        if self.remove:
            self.remove_int(xmin,xmax)
            self.remove = False
        else:
            self.add_int(xmin,xmax)
        
    def onclick(self,x):
        #remove Interval
        self.remove_int(x)
        
    def save_case(self):
        self.case.save()
        
    # def next_case(self):
    #     pass
    
    # def keyPressEvent(self, event):
    #     if event.isAutoRepeat():
    #         return
    #     pressed = event.key()
    #     if (pressed in self.keys):
    #         index = self.keys.index(pressed)
    #         self.dots[index] = self.height()+self.upper
    #         self.repaint()
    #     event.accept()
    # def set_tmin(self):
    #     if True:
    #         self.t_int_min = 0
        
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
    