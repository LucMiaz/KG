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
from matplotlib.figure import Figure
                          
from kg.detect import MicSignal
from kg.mpl_widgets import Bar, CaseSelector
from kg.case import Case
from kg.case import Interval
                          
class DetectControlWidget(QMainWindow):

    def __init__(self, setup = False, **kwargs):
        QMainWindow.__init__(self)
        self.setWindowTitle('listen and detect ;-)')
        #time to syncronize plot and media object
        self.tShift = None
        self.t = None
        self.canvas = {}
        self.ca_update_handle = []
        self.ca_set_bar_handle = []
        #refresh timer
        self.refresh = 30
        self.timer = QtCore.QTimer()
        self.timer.setInterval(self.refresh)
        
        #phonon 
        #the media object controls the playback
        self.media = Phonon.MediaObject(self)
        self.audio_output = Phonon.AudioOutput(Phonon.MusicCategory, self)
        self.seeker = Phonon.SeekSlider(self)
        self.seeker.setFixedHeight(20)
        self.seeker.setMediaObject(self.media)
        self.media.setTickInterval(15)
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
        #layout
        self.vBox = QtGui.QVBoxLayout()
        self.vBox.addWidget(self.seeker)
        
        #finish setup
        if setup:
            #Set mediafile
            self.set_media_source(**kwargs)
            #add mpl objects
            self.set_mpl(**kwargs)
            #set and centralWidget
            self.set_centralWidget()
            #add connections
            self.connections()

    def set_media_source(self,wavPath, t0 = 0, **kwargs):
        self.tShift = t0
        self.t = self.tShift
        self.media.setCurrentSource(Phonon.MediaSource(wavPath))
        
    def set_mpl(self, canvas = {}, **kwargs):
        self.canvas = []
        self.ca_update_handle = []
        self.ca_set_bar_handle = []
        for k, ca in canvas.items():
            ca['canvas'].setParent(self)
            self.canvas.append(ca['canvas'])
            self.vBox.addWidget(ca['canvas'])
            handle = ca['axHandle']
            if not isinstance(handle,list):
                handle = [handle]
            if ca['animate']:
                self.ca_update_handle.extend(handle)
            if ca['bar']:
                self.ca_set_bar_handle.extend(handle)
                
    def set_centralWidget(self):
        #centralwidget
        centralWidget = QtGui.QWidget()
        centralWidget.setLayout(self.vBox)
        self.setCentralWidget(centralWidget)
  
            
    def connections(self):
        # connections
        self.timer.timeout.connect(self.update_canvas)
        self.media.tick.connect(self.update_time)
        self.media.finished.connect(self.media.stop)
        self._connections()
        #start refresh
        self.timer.start()
        
    def _connections(self):
        pass
        
    def update_time(self,t):
        self.t = t/1000 + self.tShift

    def update_canvas(self):
        for handle in self.ca_set_bar_handle:
            handle.set_bar_position(self.t)
        for handle in self.ca_update_handle:
            handle.update()
            
    # @classmethod
    # def from_micSignal(cls, micSn, mesPath):
    #     wavPath = micSn.export_to_Wav(mesPath)
    #     #Canvas
    #     plt.ioff()
    #     stftName = micSn.calc_stft(M=1024*4)
    #     fig, axes = plt.subplots(1,sharex=True)
    #     ax = axes
    #     micSn.plot_spectrogram(stftName,ax) 
    #     micSn.plot_triggers(ax)
    #     ca = FigureCanvas(fig)
    #     #Bar
    #     Bars = [Bar(ax) for ax in axes] if isinstance(ax,list) else [Bar(ax)]
    #     return(cls(wavPath.as_posix(), {1:ca} , micSn.t.min(), Bars))
        
    @classmethod
    def alg_results(cls, micSn, algorithm):
        wavPath = micSn.export_to_Wav()
        #Canvas
        plt.ioff()
        canvas = {'Results':algorithm.visualize(micSn)}
        return(cls(setup= True, wavPath = wavPath.as_posix(), canvas = canvas , t0 = micSn.t.min() ))
        

class CaseCreatorWidget(DetectControlWidget):
    '''
    this is a subclass of DetectControlWidget
    this widget should allow to create cases in GUI style
    kg_ event duration is selected with mouse cursor
    case is saved using a button
    '''
    def __init__(self, cases_dict):
        #init super
        super(CaseCreatorWidget, self).__init__()
        self.setWindowTitle('Create Case')
        self.minspan = 0.1
        self.remove = False
        self.add_widgets()
        self.set_centralWidget()
        #set case
        self.NoiseTypes = ['Z','KG']
        self.cases_dict = cases_dict
        self.mainPath = self.cases_dict['mainPath']
        self.cases_keys = list(cases_dict.keys())
        self.cases_keys.remove('mainPath')
        self.CaseCombo.addItems(self.cases_keys)
        self.set_case(0)
        #add connections
        self.connections()
        
    def add_widgets(self):
        canvas={}
        fig = Figure()
        fig.set_dpi(150)
        ax = fig.add_subplot(111)
        ca = FigureCanvas(fig)
        bar = Bar(ax) 
        canvas['spectrogram'] = {'animate':True,'bar':True, 'canvas':ca , 'axHandle': bar}
        self.ax = ax
        fig = Figure()
        fig.set_dpi(150)
        ax = fig.add_subplot(111)
        ca = FigureCanvas(fig)
        ax.set_xlim(self.ax.get_xlim())
        self.SelectAxis = ax
        #case Selector
        self.CS = CaseSelector(self.SelectAxis, self.onselect, self.onclick, 
                                nrect = [50,50], update_on_ext_event = True , 
                                minspan = self.minspan )
        canvas['selector'] = {'animate':True,'bar':True, 'canvas':ca , 'axHandle': self.CS}
        #set canvas
        self.set_mpl(canvas)
        #add combo box
        hBox = QtGui.QHBoxLayout()
        label = QtGui.QLabel('Noise Type to select ')
        self.SOIcombo = QtGui.QComboBox()
        self.SOIcombo.addItem('Zischen', 'Z')
        self.SOIcombo.addItem('Kreischen', 'KG')
        self.cb = QtGui.QCheckBox('both visible', self)
        self.cb.toggle()
        hBox.addWidget(label )
        hBox.addWidget(self.SOIcombo)
        hBox.addWidget(self.cb)
        hBox.addStretch(1)
        self.vBox.addLayout(hBox)
        #add buttons
        hBox = QtGui.QHBoxLayout()
        label = QtGui.QLabel('Select case to analyze ')
        self.CaseCombo = QtGui.QComboBox()
        self.buttonSave = QtGui.QPushButton("save",self)
        hBox.addWidget(label)
        hBox.addWidget(self.CaseCombo)
        hBox.addWidget(self.buttonSave)
        hBox.addStretch(1)
        self.vBox.addLayout(hBox)
        
    def set_case(self,case_index):
        # todo: add not possible
        self.releaseKeyboard()
        self.timer.stop()
        self.media.stop()
        self.currentCase = self.cases_dict[self.cases_keys[case_index]]
        #attributes
        self.case = self.currentCase['case']
        micSn = self.currentCase['micSn']
        #update buttons
        self.both_visibles=True
        self.cb.setChecked(self.both_visibles)
        self.current_noise = 'Z'
        self.SOIcombo.setCurrentIndex(self.NoiseTypes.index(self.current_noise))
        #set SOI and update Canvas
        self.set_noise_type('Z')
        #plot
        # todo: rm ax add prms and band
        #ax
        self.ax.cla()
        stftN = list(micSn.STFT.keys())[0]
        micSn.plot_spectrogram(stftN,self.ax)
        micSn.plot_triggers(self.ax)
        #SelectAxis
        self.SelectAxis.cla()
        micSn.plot_signal(self.SelectAxis)
        micSn.plot_triggers(self.SelectAxis)
        self.SelectAxis.set_xlim(self.ax.get_xlim())
        for ca in self.canvas:
            ca.draw()
        #update canvas
        self.update_stay_rect()

        #self.update_canvas()
        #Set mediafile
        wavPath = self.currentCase['wavPath']
        self.set_media_source(wavPath ,micSn.t.min())
        #start timer
        self.timer.start()
        self.grabKeyboard()

    def _connections(self):
        # connections
        self.SOIcombo.currentIndexChanged.connect(self.set_noise_type)
        self.cb.stateChanged.connect(self.set_both_visible)
        self.CaseCombo.currentIndexChanged.connect(self.set_case)
        self.buttonSave.clicked.connect(self.save_case)
    
    def set_noise_type(self, index):
        if isinstance(index,int):
            self.current_noise = self.NoiseTypes[index]
        else:
            self.current_noise = index
        self.SOI = self.case.case[self.current_noise]
        self.update_stay_rect()
        
    def set_both_visible(self, state):
        if state == QtCore.Qt.Checked:
            self.both_visibles= True
        else:
            self.both_visibles= False
        self.update_stay_rect()
        
    def add_int(self, xmin,xmax):
        Int = Interval(xmin,xmax)
        self.SOI.append(Int)
        #print('Add '+ repr(Int))
        self.update_stay_rect()
        
    def remove_int(self, xmin, xmax = None):
        if xmax == None:
            index = self.SOI.containspoint(xmin)
            if index is not None:
                #print('Remove '+ repr(self.SOI.RangeInter[index]))
                self.SOI.removebyindex(index)
        else:
            self.SOI.remove(Interval(xmin,xmax))
        self.update_stay_rect()
        
    def set_int(self,press):
        if press:
            self._t_int_min = self.t
            return
        else:
            tmax = self.t
            if abs(tmax-self._t_int_min) > self.minspan:
                self.add_int(self._t_int_min,tmax)
        
    def onselect(self,xmin,xmax):
        #add interval1
        if self.remove:
            self.remove_int(xmin,xmax)
        else:
            self.add_int(xmin,xmax)
        
    def onclick(self,x):
        #remove Interval
        self.remove_int(x)
        
    def keyPressEvent(self, event):
        if event.isAutoRepeat():
            return
        if event.key() == QtCore.Qt.Key_D:
            self.remove = True
        elif event.key() == QtCore.Qt.Key_S:
            self.set_int(True)
        event.accept()
        
    def keyReleaseEvent(self, event):
        if event.isAutoRepeat():
            return
        if event.key() == QtCore.Qt.Key_D:
            self.remove = False
        elif event.key() == QtCore.Qt.Key_S:
            self.set_int(False)
        event.accept()
        
    def update_stay_rect(self):
        for index,nT in enumerate(self.NoiseTypes):
            if nT == self.current_noise:
                self.CS.set_stay_rects_x_bounds(self.SOI.tolist(),index)
            elif self.both_visibles:
                self.CS.set_stay_rects_x_bounds(self.case.case[nT].tolist(), index)
            else:
                self.CS.set_stay_rect_visible(False, index)
    
    def save_case(self):
        self.case.save(self.mainPath)
        #index = self.cases_keys.index(self.currentCase)
        # todo: 
        self.CaseCombo.model().item(2).setForeground(QtGui.QColor('red'))
        
    @classmethod
    def from_measurement(cls, mesVal, mID, mics, author):
        mesPath = str(mesVal.path)
        case_dict = {'mainPath' : mesPath}
        for mic in mics:
            micSn = MicSignal.from_measurement(mesVal,mID, mic)
            wavPath = micSn.export_to_Wav(mesPath)
            micSn.calc_stft(1024*4)
            caseParam = {'measurement':mesVal.measurement,\
                        'location': mesVal.location,
                        'mID':mID,'mic':mic,
                        'author':author}
            caseParam.update(mesVal.get_variables_values(mID,mic,['Tb','Te']))
            #create case_dict
            case_dict[str(micSn)] = {'wavPath': str(wavPath),
                            'case': Case(**caseParam),'micSn':micSn}
        return(cls(case_dict))

##
if __name__ == "__main__":
    from kg.measurement_values import measuredValues
    from kg.measurement_signal import measuredSignal
    from kg.algorithm import ZischenDetetkt1
    #setup measurement
    mesPath = 'Measurements_example\MBBMZugExample'
    mesVal = measuredValues.from_json(mesPath)
    measuredSignal.setup(mesPath)
    ##
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
    ##
    mic= [1,2,4,5,6]
    W = CaseCreatorWidget.from_measurement(mesVal,mID, mic,'esr')
    W.show()
    