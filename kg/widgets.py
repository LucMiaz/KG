# import sys
# sys.path.append('D:\GitHub\myKG')
import os, pathlib
import numpy as np
import collections
from PySide import QtGui, QtCore
from PySide.phonon import Phonon
from PySide.QtGui import (QApplication, QMainWindow, QAction, QStyle,
                          QFileDialog)
import matplotlib
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
                          
from kg.detect import MicSignal
from kg.mpl_widgets import Bar, CaseSelector
from kg.case import Case
from kg.case import Interval
import seaborn as sns
sns.set(style='ticks', palette='Set2')
                          
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
        self.refresh = 35
        self.timer = QtCore.QTimer()
        self.timer.setInterval(self.refresh)
        self.savefolder=None
        #phonon 
        #the media object controls the playback
        self.media = Phonon.MediaObject(self)
        self.audio_output = Phonon.AudioOutput(Phonon.MusicCategory, self)
        self.seeker = Phonon.SeekSlider(self)
        self.seeker.setFixedHeight(20)
        self.seeker.setMediaObject(self.media)
        self.media.setTickInterval(10)
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
            action = QtGui.QAction(icon, label, self, )
            action.setObjectName(name)
            self.actions.addAction(action)
            action.triggered.connect(getattr(self.media, name))
        self.actions.addSeparator()
        self.actions.addSeparator()
        info = QtGui.QAction( "Info", self)
        self.actions.addAction(info)
        info.triggered.connect(self.show_info)
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

    def set_media_source(self, wavPath, t0 = 0, **kwargs):
        self.tShift = t0
        self.t = self.tShift
        self.media.setCurrentSource(Phonon.MediaSource(wavPath))
        self.media.pause()
        
    def media_finish(self):
        self.media.stop()
        self.media.pause()
        
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
        self.media.finished.connect(self.media_finish)
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
            
    def show_info(self):
        pass
        
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
    case_dicts contains the following attributes:
    mainPath: str
    ccaseDict: dict
    caseDict is a dict with following attr:
    case: Case() instance
    plot: {pName:[t,y],...}
    tmin: flt
    tmax: flt
    wavPath: str
    '''
    def __init__(self, mesPath, casesToAnalyze, author = None):
        #init super
        super(CaseCreatorWidget, self).__init__()
        self.setWindowTitle('Create Case')
        # set the author
        if author == None:
            author, ok = QtGui.QInputDialog.getText(self, "Set author", "Please your name : ")
            if ok:
                author = author.replace(' ','_')
            else:
                author =  'anonymus'
        self.author = author
            
        self.mesPath = mesPath
        self.minspan = 0.05
        self.remove = False
        self.add_widgets()
        self.set_centralWidget()
        #set cases
        self.NoiseTypes = ['Z','KG']
        self.casesToAnalyze = casesToAnalyze        
        self.casesKeys = sorted(list(self.casesToAnalyze.keys()))
        self.CaseCombo.addItems(self.casesKeys)
        #set case
        self.set_current_case(self.casesKeys[0])
        #add connections
        self.connections()
        
    def add_widgets(self):
        #Figure Canvas
        canvas={}
        plt.ioff()
        fig = Figure((15,10))
        fig.set_dpi(110)
        ax = fig.add_subplot(111)
        ca = FigureCanvas(fig)
        self.SelectAxis = ax
        axbgcolor='#272822'
        fig.set_facecolor(axbgcolor)
        #case Selector
        self.CS = CaseSelector(self.SelectAxis, self.onselect, self.onclick, 
                                nrect = [50,50], update_on_ext_event = True , 
                                minspan = self.minspan )
        canvas['selector'] = {'animate':True,'bar':True, 'canvas':ca , 'axHandle': self.CS}
        #set canvas
        self.set_mpl(canvas)
        
        # add first row of buttons
        hBox = QtGui.QHBoxLayout()
        # select case combo 
        groupBox = QtGui.QGroupBox('Select case to analyze ')
        self.CaseCombo = QtGui.QComboBox()
        hbox1 = QtGui.QHBoxLayout()
        hbox1.addWidget(self.CaseCombo)
        groupBox.setLayout(hbox1)
        hBox.addWidget(groupBox)
        # select noise Type
        groupBox = QtGui.QGroupBox('Noise Type to select')
        hBox1 = QtGui.QHBoxLayout()
        # noise Type combo
        self.SOIcombo = QtGui.QComboBox()
        self.SOIcombo.addItem('Zischen', 'Z')
        self.SOIcombo.setItemData(0,QtGui.QColor('#d8b365'),QtCore.Qt.BackgroundRole)#add backgroundcolor to combo Z
        self.SOIcombo.setItemData(0,QtGui.QColor('#f5f5f5'),QtCore.Qt.TextColorRole)#change text color
        self.SOIcombo.addItem('Kreischen', 'KG')
        self.SOIcombo.setItemData(1,QtGui.QColor('#5ab4ac'),QtCore.Qt.BackgroundRole)#add backgroundcolor to combo K
        self.SOIcombo.setItemData(1,QtGui.QColor('#f5f5f5'),QtCore.Qt.TextColorRole)#change text color
        hBox1.addWidget(self.SOIcombo)
        # visualize both cb
        self.cb = QtGui.QCheckBox('both visible', self)
        hBox1.addWidget(self.cb)
        groupBox.setLayout(hBox1)
        hBox.addWidget(groupBox)
        hBox.addStretch(1)
        self.vBox.addLayout(hBox)
        # add second row of buttons
        hBox = QtGui.QHBoxLayout()
        # quality radios
        hBox = QtGui.QHBoxLayout()
        groupBox = QtGui.QGroupBox("Select quality: are noise events detectable?")
        self.Qradios = [QtGui.QRadioButton(q) for q in ['good','medium','bad']]
        hbox1 = QtGui.QHBoxLayout()
        self.rbG = QtGui.QButtonGroup()
        for rb in self.Qradios:
            self.rbG.addButton(rb)
            hbox1.addWidget(rb) 
        groupBox.setLayout(hbox1)
        hBox.addWidget(groupBox)
        # save button
        self.buttonSave = QtGui.QPushButton("save",self)
        hBox.addWidget(self.buttonSave)
        hBox.addStretch()
        # saved data directory group (button to change folder and current folder)
        groupBox2=QtGui.QGroupBox("Saved data directory")
        fm=QtGui.QFontMetrics('HelveticaNeue')
        self.hlab=QtGui.QLabel("Selected directory : "+fm.elidedText(str(self.savefolder),QtCore.Qt.ElideLeft, 250))#crop the displayed path if too long (ElideLeft -> add ... left of the path
        
        
        self.buttonChgSave = QtGui.QPushButton("Change folder",self)
        hBox2=QtGui.QHBoxLayout()
        hBox2.addWidget(self.hlab)
        hBox2.addWidget(self.buttonChgSave)
        groupBox2.setLayout(hBox2)
        hBox.addWidget(groupBox2)
        self.vBox.addLayout(hBox)
        #select color of chg saving folder.
        if not self.savefolder:
            self.buttonChgSave.setStyleSheet("background-color: #c2a5cf")
            self.hlab.setText("Selected directory : "+str(self.savefolder))
        else:
            self.buttonChgSave.setStyleSheet("background-color: #a6dba0")
            self.hlab.setText("Selected directory : "+str(self.savefolder))
        
    def set_current_case(self,key):
        self.releaseKeyboard()
        self.timer.stop()
        self.media.stop()
        self.currentCase = self.casesToAnalyze[key]
        #attributes
        self.case = self.currentCase['case']
        #update buttons
        self.both_visibles = True
        self.cb.setChecked(self.both_visibles)
        self.current_noise = 'Z'
        self.SOIcombo.setCurrentIndex(self.NoiseTypes.index(self.current_noise))
        if self.currentCase.get('saved',False):
            self.buttonSave.setStyleSheet("background-color: #a6dba0")
        else:
            self.buttonSave.setStyleSheet("background-color: #c2a5cf")
        self.check_rb(self.case.case['quality'])
        #set SOI and update Canvas
        self.set_noise_type('Z')
        #plot
        self.plot()
        #Set mediafile
        print('self.mesPath : '+str(self.mesPath))
        wavPath= self.mesPath.joinpath(pathlib.Path("build"))
        wavPath = self.mesPath.joinpath(self.currentCase['wavPath'])
        print("currentCasewavPath : "+str(self.currentCase['wavPath']))
        print("mediafile path : "+str(wavPath))
        self.set_media_source(str(wavPath), self.currentCase['tmin'])
        #start timer
        self.timer.start()
        self.grabKeyboard()
        
    def plot(self):
        self.SelectAxis.cla()
        self.case.plot_triggers(self.SelectAxis)
        for key, pData in self.currentCase['plotData'].items():
            t,y = pData
            self.SelectAxis.plot(t, y , label = key, color='#f5f5f5', linewidth=1.)#plot display
        tmin = self.currentCase['tmin']
        tmax = self.currentCase['tmax']
        self.SelectAxis.set_xlim(tmin,tmax)
        self.SelectAxis.set_ylabel('LA dB')
        self.SelectAxis.set_xlabel('t (s)')
        self.SelectAxis.legend()
        for ca in self.canvas:
            ca.draw()
        #update canvas
        self.update_stay_rect()

    def _connections(self):
        """connects the buttons/combobox to the methods to be applied"""
        self.SOIcombo.currentIndexChanged.connect(self.set_noise_type)
        self.cb.stateChanged.connect(self.set_both_visible)
        self.CaseCombo.currentIndexChanged.connect(self.change_current_case)
        for rb in self.Qradios:
            rb.clicked.connect(self.set_quality)
        self.buttonSave.clicked.connect(self.save_case)
        self.buttonChgSave.clicked.connect(self.chg_folder)
        
    def chg_folder(self):
        """change the directory where to save the data"""
        self.savefolder=pathlib.Path(str(QFileDialog.getExistingDirectory(self,"Please select a directory where I can save your data.")))
        #select color of chg saving folder.
        if not self.savefolder:
            self.buttonChgSave.setStyleSheet("background-color: #c2a5cf")
        else:
            self.buttonChgSave.setStyleSheet("background-color: #a6dba0")
        fm=QtGui.QFontMetrics(self.hlab.font())
        self.hlab.setText("Selected directory : "+fm.elidedText(str(self.savefolder),QtCore.Qt.ElideLeft, self.vBox.sizeHint().width()*0.45))
    
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
        
    def change_current_case(self, index):
        key = self.casesKeys[index]
        if True:#self.currentCase.get('saved',False):
            self.set_current_case(key)
        # else:
        #     QtGui.QMessageBox.warning(self, self.trUtf8("save error"), 
        #      self.trUtf8("Before switching case save it!"))
        
    def set_quality(self):
        for q,rb in zip( ['good','medium','bad'],self.Qradios):
            if rb.isChecked():
                self.case.set_quality(q)
                
    def check_rb(self, q):
        self.rbG.setExclusive(False)#allows to choose multiple qualities
        for rb, qb in  zip(self.Qradios, ['good', 'medium', 'bad']):
            rb.setChecked(q==qb)
        self.rbG.setExclusive(False)
        
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
        if self.case.case['quality'] == None:
            QtGui.QMessageBox.warning(self, self.trUtf8("save error"), 
             self.trUtf8("Quality of selection has to be set!"))
        else:
            # set the author
            if not self.savefolder:
                #asks for the folder where to save the datas
                self.savefolder=pathlib.Path(str(QFileDialog.getExistingDirectory(self,"Please select a directory where I can save your data.")))
            self.case.case['author'] = self.author
            self.case.save(self.savefolder)
            self.currentCase['saved'] = True
            self.buttonSave.setStyleSheet("background-color: #a6dba0")
            currentIndex= self.casesKeys.index(str(self.CaseCombo.currentText()))
            self.CaseCombo.setItemData(currentIndex,QtGui.QColor('#a6dba0'),QtCore.Qt.BackgroundRole)


    def show_info(self):
        information=\
"""With this small Widget is possible to analyze audio signals and create tests cases of curve noise:
----------------------------------------------------------------------
Hear the recorded signal using the media buttons in the toolbar
    - Warning: notebook speakers have poor quality. 
    - Use hearphones or a better audio system to analyze the signal 

We diffentiate between two noise types:
    - Kreischen: Squeal noise
    - Zischen: Flanging Noise

Selection of intervals where noise is present is done by:
    - left mouse button for select span
    - rigth mouse click on a selected span to remove it
    - hold key d and left mouse button to remove span
    - hold key s to select noise while playing

Before saving is important to select quality:
    - good: noise events are good to recognize
    - medium: it is possible to detect noise events
    - bad: noise events almost impossible to detects

Be sure to have analyzed(saved) all the cases before quitting the application. A saved case has a green state.
    
    """
        QtGui.QMessageBox.information(self,"Info", information)
        
    @classmethod
    def from_measurement(cls, mesVal, mID, mics, author = None):
        mesPath = mesVal.path
        ts = measuredSignal(mID,mics)
        case_dict = {}
        for mic in mics:
            micSn = MicSignal.from_measurement(mesVal,mID, mic)
            wavPath = micSn.export_to_Wav(mesPath)
            caseParam = {'measurement':mesVal.measurement,\
                        'location': mesVal.location,
                        'mID':mID,'mic':mic,
                        'author': None}
            caseParam.update(mesVal.get_variables_values(mID, mic, ['Tb','Te']))
            #create case_dict
            y,t,sR = ts.get_signal('prms'+str(mic))
            case_dict[str(micSn)] = {'wavPath': wavPath,
                            'case': Case(**caseParam),
                            'plotData':{'LAf':[t, 20*np.log10(y/(2e-5))]},
                            'tmin':micSn.t.min(),
                            'tmax':micSn.t.max()}
        return(cls( mesPath, case_dict, author))

##
if __name__ == "__main__":
    from kg.measurement_values import measuredValues
    from kg.measurement_signal import measuredSignal
    from kg.algorithm import ZischenDetetkt1
    #setup measurement
    mesPath = pathlib.Path('Measurements_example\MBBMZugExample')
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

    ##
    mic= [1,2,4,5,6]
    W = CaseCreatorWidget.from_measurement(mesVal,mID,mic)
    W.show()
    