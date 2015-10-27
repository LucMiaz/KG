import sys
sys.path.append('D:\GitHub\myKG')
import os, pathlib
import numpy as np
import collections
from PySide import QtGui, QtCore
from PySide.phonon import Phonon
from PySide.QtGui import (QApplication, QMainWindow, QAction, QStyle,
                          QFileDialog)
import matplotlib
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
import pandas as pd
import markdown as md
from pandas.sandbox.qtpandas import DataFrameModel, DataFrameWidget
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
                          
from kg.detect import MicSignal
from kg.mpl_widgets import Bar, CaseSelector
from kg.case import Case
from kg.case import Interval
from kg.measurement_values import measuredValues
from kg.measurement_signal import measuredSignal
from kg.algorithm import *
from scipy.io import wavfile
import random
import json
#import seaborn as sns
#sns.set(style='ticks',palette='Set2')
                          
class DetectControlWidget(QMainWindow):

    def __init__(self, setup = False, **kwargs):
        QMainWindow.__init__(self)
        self.setWindowTitle('listen and detect ;-)')
        #time to syncronize plot and media object
        self.adminsession=False
        self.tShift = None
        self.t = None
        self.mpl = {}
        self.ca_update_handle = []
        self.ca_set_bar_handle = []
        #bools to know if the timer is to be activated
        self.barplay=False
        #refresh timer
        #self.refresh = 30
        #self.timer = QtCore.QTimer()
        #self.timer.setInterval(self.refresh)
        self.savefolder=pathlib.Path("").absolute().parent
        #phonon 
        #the media object controls the playback
        self.media = Phonon.MediaObject(self)
        self.audio_output = Phonon.AudioOutput(Phonon.MusicCategory, self)
        self.seeker = Phonon.SeekSlider(self)
        self.seeker.setFixedHeight(20)
        self.seeker.setMediaObject(self.media)
        self.mediarate='Fairly High 25ms'
        self.media.setTickInterval(25)
        self.comboratedict={'High 15ms':15, 'Fairly High 25ms':25, ' Medium 30ms':30, 'Pretty Low 40ms':40, 'Low 50ms':50, 'Ancient 60ms':60}
        self.comboratelist=['High 15ms', 'Fairly High 25ms', ' Medium 30ms', 'Pretty Low 40ms', 'Low 50ms', 'Ancient60ms']
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
        
        self.menu_bar()
        
        
        
        #layout
        self.vBox = QtGui.QVBoxLayout()
        self.vBox.addWidget(self.seeker)
        self.modifiers= None
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
        
    
        
    def _barplay(self, truth):
        """define what to do when audio is playing/not playing"""
        self.barplay=truth
    def case_down(self):
        pass
    def case_up(self):
        pass
    def chg_folder(self):
        pass
    def change_plot(self):
        pass
    def change_quality(self):
        pass
    def chg_type(self):
        pass
    def chg_typedisplay(self):
        pass
    
    def connections(self):
        # connections
        #self.timer.timeout.connect(self.update_canvas)
        self.media.tick.connect(self.update_time)
        self.media.finished.connect(self.media_finish)
        self.media.stateChanged.connect(self.timer_status)#update timer status on media Statechange
        self._connections()
        #start refresh
        #self.timer.start()
        
    def _connections(self):
        pass
        
    def define_actions(self):
        """define actions for the menu"""
        #exit
        self.exitAction = QtGui.QAction(QtGui.QIcon('exit.png'), '&Exit', self)        
        self.exitAction.setShortcut('Ctrl+Q')
        self.exitAction.setStatusTip('Exit application')
        self.exitAction.triggered.connect(QtGui.qApp.quit)
        #show info
        self.showinfoAction=QtGui.QAction('&Info',self)
        self.showinfoAction.setShortcut('Ctrl+I')
        self.showinfoAction.setStatusTip('Show info')
        self.showinfoAction.triggered.connect(self.show_info)
        #save
        self.saveAction=QtGui.QAction('&Save',self)
        self.saveAction.setShortcut('Ctrl+S')
        self.saveAction.setStatusTip('Save case')
        self.saveAction.triggered.connect(self.save_case)
        #saving folder
        self.changesavingfolderAction=QtGui.QAction('&ChgSFolder',self)
        self.changesavingfolderAction.setShortcut('Ctrl+F')
        self.changesavingfolderAction.setStatusTip('Change saving folder')
        self.changesavingfolderAction.triggered.connect(self.chg_folder)
        #media
        self.playAction = QtGui.QAction('&Play', self)        
        self.playAction.setShortcut('SPACE')
        self.playAction.setStatusTip('Play the audio')
        self.playAction.triggered.connect(self.media.play)
        
        self.stopAction = QtGui.QAction('&Stop', self)        
        self.stopAction.setShortcut('SPACE')
        self.stopAction.setStatusTip('Stop the audio')
        self.stopAction.triggered.connect(self.media.stop)
        
        self.pauseAction = QtGui.QAction('&Pause', self)        
        self.pauseAction.setShortcut('SPACE')
        self.pauseAction.setStatusTip('Pause the audio')
        self.pauseAction.triggered.connect(self.media.pause)
        
        #change cases
        self.nextcaseAction= QtGui.QAction('&Next case', self)        
        self.nextcaseAction.setShortcut('DOWN ARROW')
        self.nextcaseAction.setStatusTip('Move to next case')
        self.nextcaseAction.triggered.connect(self.case_down)
        
        self.prevcaseAction= QtGui.QAction('&Prev case', self)        
        self.prevcaseAction.setShortcut('UP ARROW')
        self.prevcaseAction.setStatusTip('Move to previous case')
        self.prevcaseAction.triggered.connect(self.case_up)
        
    def keyPressEvent(self, event):
        self.modifiers = QtGui.QApplication.keyboardModifiers()#checks on keypress what modifyers there is
        if event.isAutoRepeat():
            return
        if event.key() == QtCore.Qt.Key_D:
            self.set_remove(True)
        elif event.key() == QtCore.Qt.Key_S and not self.modifiers==QtCore.Qt.ControlModifier:
            self.set_int(True)
        elif event.key()== QtCore.Qt.Key_S and self.modifiers==QtCore.Qt.ControlModifier:
            self.media.stop()
            self.save_case()
        elif event.key()==QtCore.Qt.Key_Space:
            if self.modifiers==QtCore.Qt.ControlModifier:#if ctrl pressed, go stops
                self.media_finish()
            else:
                if self.media.state()==1:#if stopped
                    self.media.play()
                elif self.media.state()==4:#if paused
                    self.media.play()
                else:#if playing (2), buffering (3), loading(0) or error(5)
                    self.media.pause()
        elif event.key()==QtCore.Qt.Key_Up or event.key()==QtCore.Qt.Key_Left:
            self.media.stop()
            self.case_up()
        elif event.key()==QtCore.Qt.Key_Down or event.key()==QtCore.Qt.Key_Right:
            self.media.stop()
            self.case_down()
        elif event.key()==QtCore.Qt.Key_Enter:
            self.media.stop()
            if not self.get_quality:
                self.change_quality(1)
            self.save_cases()
            self.case_down()
        elif event.key()==QtCore.Qt.Key_F:
            self.media.stop()
            self.chg_folder()
        elif event.key()==QtCore.Qt.Key_Z:
            self.media.pause()
            self.chg_type()
        elif event.key()==QtCore.Qt.Key_K:
            self.media.pause()
            self.chg_type()
        elif event.key()==QtCore.Qt.Key_T:
            self.media.pause()
            self.chg_type()
        elif event.key()==QtCore.Qt.Key_B:
            self.media.pause()
            self.chg_typedisplay()
        elif event.key()==QtCore.Qt.Key_P:
            self.media.stop()
            self.change_plot()
        elif event.key()==QtCore.Qt.Key_1:
            self.change_quality('bad')
        elif event.key()==QtCore.Qt.Key_2:
            self.change_quality('medium')
        elif event.key()==QtCore.Qt.Key_3:
            self.change_quality('good')
        elif event.key()==QtCore.Qt.Key_U:
            self.update_canvas()
        elif event.key()==QtCore.Qt.Key_R and self.modifiers==QtCore.Qt.ControlModifier:
            text,ok=QtGui.QInputDialog.getItem(self,"Display Quality", "Current quality is "+self.mediarate+"\n Please select an update quality :", self.comboratelist, self.comboratelist.index(self.mediarate))
            if ok:
                self.mediarate=str(text)
                self.media.setTickInterval(self.comboratedict[self.mediarate])
        event.accept()
        
    def keyReleaseEvent(self, event):
        if event.isAutoRepeat():
            return
        if event.key() == QtCore.Qt.Key_D:
            self.set_remove(False)
        elif event.key() == QtCore.Qt.Key_S and not self.modifiers==QtCore.Qt.ControlModifier:
            self.set_int(False)
        event.accept()
    
    def media_finish(self):
        #self.timer.stop()
        self.media.stop()
        self.media.pause()
    
    def menu_bar(self):
        """adds a menu bar"""
        self.define_actions()
        self.statusBar()
        self.Menu = self.menuBar()
        self.fileMenu = self.Menu.addMenu('&File')
        self.fileMenu.addAction(self.showinfoAction)
        self.fileMenu.addAction(self.changesavingfolderAction)
        self.fileMenu.addAction(self.saveAction)
        self.fileMenu.addAction(self.exitAction)
        
        self.mediaMenu=self.Menu.addMenu('&Media')
        self.mediaMenu.addAction(self.playAction)
        self.mediaMenu.addAction(self.pauseAction)
        self.mediaMenu.addAction(self.stopAction)
        
        self.caseMenu=self.Menu.addMenu('&Cases')
        self.caseMenu.addAction(self.nextcaseAction)
        self.caseMenu.addAction(self.prevcaseAction)
        
    def set_int(self, truth):
        pass
    def set_quality(self, val):
        pass
    def set_remove(self, truth):
        pass
    def save_case(self):
        pass
    
    def set_centralWidget(self):
        #centralwidget
        centralWidget = QtGui.QWidget()
        centralWidget.setLayout(self.vBox)
        self.setCentralWidget(centralWidget)
    
    def set_media_source(self, wavPath, t0 = 0, **kwargs):
        self.tShift = t0
        self.t = self.tShift
        self.media.setCurrentSource(Phonon.MediaSource(wavPath))
        self.media.pause()
        
    def set_mpl(self, mpl = {}, **kwargs):
        self.canvas = []
        self.ca_update_handle = []
        self.ca_set_bar_handle = []
        for k, ca in mpl.items():
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
                
    def show_info(self):
        pass
        
    def timer_status(self,newstate, oldstate):
        """changes the timer status according to played audio"""
        if newstate==2:
            #self.timer.start()
            self._barplay(True)
        elif newstate==1:
            #self.timer.stop()
            self._barplay(False)
        elif newstate==4:
            #self.timer.stop()
            self._barplay(False)
    
    def update_time(self,t):
        self.t = t/1000 + self.tShift
        self.update_canvas()

    def update_canvas(self):
        for handle in self.ca_set_bar_handle:
            handle.set_bar_position(self.t)
        for handle in self.ca_update_handle:
            handle.update()
            
        
    @classmethod
    def alg_results(cls, micSn, algorithm):
        wavPath = micSn.export_to_Wav(MESPATH)
        wavPath = MESPATH.joinpath(wavPath)
        #Canvas
        plt.ioff()
        fig = Figure((15,10))
        fig.set_dpi(110)
        ca = FigureCanvas(fig)
        algorithm.visualize(micSn,fig)
        dict = {'animate':True, 'bar':True, 'canvas':ca , \
                'axHandle': [Bar(ax) for ax in fig.get_axes()] }
        return(cls(setup= True, wavPath = wavPath.as_posix(), \
        mpl = {str(algorithm): dict} , t0 = micSn.t.min()))
   

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
    def __init__(self, mesPath, Paths=None):
        #init super
        super(CaseCreatorWidget, self).__init__()
        self.setWindowTitle('Create Case')
        if not Paths:
            self.Paths=[mesPath]
            self.Paths.append(pathlib.Path('E:/ZugVormessung'))
            self.Paths.append(pathlib.Path('E:/Biel1Vormessung'))
        else:
            self.Paths=Paths
        # set the author        
        self.mesPath = mesPath
        self.infofolder=pathlib.Path("").absolute()
        self.minspan = 0.05
        self.PlotTypes=['LAfast', 'Spectogram']
        self.currentplottype=self.PlotTypes[0]
        hBox=self.add_widgets_basic()
        self.set_centralWidget()
        self.author=None
        self.both_visible=True
        #set cases
        self.NoiseTypes = ['Z','KG']
        self.asks_for_info()
        self.asks_for_author()
        if self.author in ['admin','Admin','ADMIN']:
            hBox.addWidget(self.add_widgets_admin())
            self.adminsession=True
        else:
            self.authors=[self.author]
            hBox.addWidget(self.add_widget_extended())
        self.vBox.addLayout(hBox)
        #import cases
        
        #gets number of cases to analyse
        self.asks_for_ncases()
        if not self.adminsession:
            QtGui.QMessageBox.warning(self, 'Audio system', 'Please use hearphones or a good audio system to analyze the signals.')
        self.CaseCombo.addItems(self.casesKeys)
        #removing cases not displayed
        newdictionary={}
        for k in self.casesKeys:
            newdictionary[k]=self.casesToAnalyze[k]
        #select a spare case (just in case ;))
        self.sparecase=None
        for k,v in self.casesToAnalyze.items():
            if k not in self.casesKeys:
                self.sparecase=(k,v)
                break
        self.casesToAnalyze=newdictionary
        self.TurnTheSavedGreen()#set caseCombo
        #add connections
        self.connections()
        self.micSignals={}
    
    def add_new_cases(self):
        """ask for adding a new case"""
        retour,ok=(QtGui.QFileDialog.getOpenFileNames(self, 'Select cases'))
        if ok:
            for file in retour[0]:
                listofpaths.append(pathlib.Path(file))
            if len(listofpaths)>0:
                self.load_cases(listofpaths)
    
    def add_int(self, xmin,xmax):
        self.unsave()
        Int = Interval(xmin,xmax)
        self.SOI.append(Int)
        #print('Add '+ repr(Int))
        self.update_stay_rect()
        if self.barplay==False:
            self.update_canvas()
    
    
    
    def add_widgets_admin(self):
        """add admin tools such as different types of plot, algorithm test and authors browser"""
        #Plots
        groupBox=QtGui.QGroupBox("Admin options")
        self.plotselect=QtGui.QComboBox()
        for type in self.PlotTypes:
            self.plotselect.addItem(type)
        hBox=QtGui.QHBoxLayout()
        labelAuthor=QtGui.QLabel("Plot type")
        hBox.addWidget(labelAuthor)
        hBox.addWidget(self.plotselect)
        
        #Authors
        try:
            authorspath=self.mesPath.joinpath('test_cases')
        except:
            self.authors=['admin']
        else:
            self.authors=os.listdir(authorspath.as_posix())
        
        self.ComboAuthors=QtGui.QComboBox()
        for auth in self.authors:
            self.ComboAuthors.addItem(auth)
        labelAuthor=QtGui.QLabel("Authors")
        hBox.addWidget(labelAuthor)
        hBox.addWidget(self.ComboAuthors)
        
        #algorithms
        self.algorithmsTypes={'Z2':{'classname':'ZischenDetetkt2','attributes':'Z2_fc_threshold_dt'}}
        #for cls in vars()['Algorithm'].__subclasses__():
        #    algid, algdescription=eval(cls.__name__()+".phony()")
        #    self.algorithmsTypes[algid]={'classname':cls.__name__(), 'attributes': algdescription}
        self.Algorithms={}
        self.ComboAlgorithms=QtGui.QComboBox()
        self.asks_for_algorithm()
        self.currentAlgorithm=self.Algorithms[self.ComboAlgorithms.currentText()]
        hBox.addWidget(self.ComboAlgorithms)
        self.buttonCompare=QtGui.QCheckBox('Show algorithm result',self)
        hBox.addWidget(self.buttonCompare)
        groupBox.setLayout(hBox)
        self.author=self.authors[0]
        
        #disable some menu actions
        self.saveAction.setEnabled(False)
        self.changesavingfolderAction.setEnabled(False)
        #add some items to menu
        self.admin_actions()
        self.caseMenu.addAction(self.addcaseAction)
        self.algMenu=self.Menu.addMenu('&Algorithms')
        self.algMenu.addAction(self.addalgAction)
        return groupBox
    
    def add_widgets_basic(self):
        #Figure Canvas
        canvas={}
        plt.ioff()
        fig = Figure((15,10))
        fig.set_dpi(110)#default 110
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
        self.SOIcombo.setItemData(0,QtGui.QColor('#d8b365'),QtCore.Qt.BackgroundRole)#add backgroundcolor of combo Z
        self.SOIcombo.setItemData(0,QtGui.QColor('#f5f5f5'),QtCore.Qt.ForegroundRole)#change text color
        self.SOIcombo.addItem('Kreischen', 'KG')
        self.SOIcombo.setItemData(1,QtGui.QColor('#5ab4ac'),QtCore.Qt.BackgroundRole)#add backgroundcolor of combo K
        self.SOIcombo.setItemData(1,QtGui.QColor('#f5f5f5'),QtCore.Qt.ForegroundRole)#change text color
        hBox1.addWidget(self.SOIcombo)
        # visualize both cb
        self.cb = QtGui.QCheckBox('both visible', self)
        hBox1.addWidget(self.cb)
        groupBox.setLayout(hBox1)
        hBox.addWidget(groupBox)
        hBox.addStretch(1)
        self.vBox.addLayout(hBox)
        # add second row of buttons
        
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
        return hBox
    
    def add_widget_extended(self):
        """add widgets that are not useful when logged as admin"""
        hBox = QtGui.QHBoxLayout()
        # save button
        self.buttonSave = QtGui.QPushButton("save",self)
        hBox.addWidget(self.buttonSave)
        hBox.addStretch()
        # saved data directory group (button to change folder and current folder)
        groupBox=QtGui.QGroupBox("Saving options")
        fm=QtGui.QFontMetrics('HelveticaNeue')
        self.hlab=QtGui.QLabel("Selected directory : "+fm.elidedText(str(self.savefolder),QtCore.Qt.ElideLeft, 250))#crop the displayed path if too long (ElideLeft -> add ... left of the path
        self.buttonChgSave = QtGui.QPushButton("Change folder",self)
        hBox.addWidget(self.hlab)
        hBox.addWidget(self.buttonChgSave)
        
        groupBox.setLayout(hBox)
        #self.vBox.addLayout(hBox)
        #select color of chg saving folder.
        if not self.savefolder:
            self.buttonChgSave.setStyleSheet("background-color: #c2a5cf")
            self.hlab.setText("Selected directory : "+str(self.savefolder))
        else:
            self.buttonChgSave.setStyleSheet("background-color: #a6dba0")
            self.hlab.setText("Selected directory : "+str(self.savefolder))
        return groupBox
    
    def admin_actions(self):
        #algorithms
        self.addalgAction = QtGui.QAction('&Add alg', self)        
        self.addalgAction.setShortcut('Ctrl+A')
        self.addalgAction.setStatusTip('Add algorithm')
        self.addalgAction.triggered.connect(self.asks_for_algorithm)
        #case
        self.addcaseAction = QtGui.QAction('&Add case', self)        
        self.addcaseAction.setShortcut('Ctrl+C')
        self.addcaseAction.setStatusTip('Add case')
        self.addcaseAction.triggered.connect(self.asks_for_case)
    
    def asks_for_algorithm(self):
        """queries the desired algorithms"""
        dialogstring=''
        for alg in self.algorithmsTypes.keys():
            dialogstring+= self.algorithmsTypes[alg]['attributes']
            dialogstring+='\n'
        dialog,ok = QtGui.QInputDialog.getText(self, 'Algorithm input', 'Insert an algorithm description in the following form :\n'+dialogstring,QtGui.QLineEdit.Normal, 'Z2_3000_13.2_0.1')
        try:
            alg,fc,thres,dt=dialog.split('_')
        except:
            return False
        else:
            self.Algorithms[dialog]=(eval(self.algorithmsTypes[alg]['classname']+'('+str(fc)+','+str(thres)+','+str(dt)+')'))
            self.ComboAlgorithms.addItem(dialog)
        
    
    def asks_for_author(self):
        author, ok = QtGui.QInputDialog.getText(self, "Set author", "Please your name : ")
        if ok:
            author = author.replace(' ','_')
            if author=="":
                author='anonymus'
        else:
            author =  'anonymus'
        self.author = author
    
    def asks_for_case(self):
        """asks for new case add"""
        listofpaths=[]
        keeponsasking=True
        while keeponasking:
            retour=(QtGui.QFileDialog.getOpenFileNames(self, 'Select cases'))
            for file in retour[0]:
                listofpaths.append(pathlib.Path(file).absolute())
            ok = QtGui.QMessageBox.question(self,'Done ?',"Have you finished selecting the cases ?", QtGui.QMessageBox.Yes |QtGui.QMessageBox.No, QtGui.QMessageBox.Yes)
            if ok==QtGui.QMessageBox.Yes:
                keeponasking=False
        self.load_cases(listofpaths)
    
    def asks_for_info(self):
        result = QtGui.QMessageBox.question(self, 'Information', "Would you like to see the information page ?", QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.No)
        if result==QtGui.QMessageBox.Yes:
            self.extbrowsercall()
            QtGui.QMessageBox.information(self, 'Proceeding', "Tell me when you are ready to proceed.")
    
    def asks_for_ncases(self):
        """asks for the number of cases to treat from the case_to_json file
        if in admin session, will ask if you want to select the cases yourself. If so, a prompt will ask you to select them. Then the program will load them and add the path to Paths"""
        askforcases=True
        if self.adminsession:
            result =QtGui.QMessageBox.question(self,'Initialization of cases',"Would you like to select the cases yourself?", QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.Yes)
            if result==QtGui.QMessageBox.Yes:
                keeponasking=True
                askforcases=False
            else:
                keeponasking=False
            listofpaths=[]
            while keeponasking:
                retour=(QtGui.QFileDialog.getOpenFileNames(self, 'Select cases'))
                for file in retour[0]:
                    listofpaths.append(pathlib.Path(file).absolute())
                ok = QtGui.QMessageBox.question(self,'Done ?',"Have you finished selecting the cases ?", QtGui.QMessageBox.Yes |QtGui.QMessageBox.No, QtGui.QMessageBox.Yes)
                if ok==QtGui.QMessageBox.Yes:
                    keeponasking=False
                
        if askforcases or len(listofpaths)==0:
            self.import_cases()#import the cases named in caseToAnalyse.json
            self.ncases=len(self.casesKeys)
            #asking for number of cases to treat
            ncases, ok = QtGui.QInputDialog.getInt(self,"Number of cases to analyse", ("Please insert the number of cases \n you would like to analyse.\n \n (You are not forced to do all \n of the proposed cases). \n \n \n Maximum : "+str(self.ncases)+" : "),  value=min(20, self.ncases), min=1, max=self.ncases, step=1)
            if ok and ncases <= self.ncases:
                self.ncases = ncases
                print("Thank you. Preparing "+str(self.ncases)+" cases.")
            else:
                print("Default value, set to maximum : " + str(self.ncases))
                self.ncases=20
            try:
                with open("firstcases.json",'r') as l:
                    firstcaseslist=json.load(l)
            except:
                self.casesKeys=[self.casesKeys[i] for i in range(0,self.ncases)]
            else:
                firstcaseskeys=[('m_'+i[0]+'_'+str(i[1])) for i in firstcaseslist]
                print("first: "+str(firstcaseskeys))
                if self.ncases <len(firstcaseslist)+1:
                    self.casesKeys=[firstcaseskeys[i] for i in range(0,self.ncases)]
                else:
                    self.casesKeys=firstcaseskeys
                    keys=list(self.casesToAnalyze.keys())
                    ncmax=len(keys)
                    while len(self.casesKeys) < min(ncases, ncmax):
                        cas=keys[random.randint(0,ncmax)]
                        if cas not in self.casesKeys:
                            self.casesKeys.append(cas)
        elif len(listofpaths)>0:
            listofcase=[]
            self.casesToAnalyze={}
            self.load_cases(listofpaths)
            
    def _barplay(self, truth):
        """tells what to do if audio is playing or not"""
        super(CaseCreatorWidget, self)._barplay(truth)
        self.CS.setUpdateOnExtEvent(truth)

    def case_down(self):
        """changes case to the next one"""
        index=self.CaseCombo.currentIndex()
        if index<len(self.casesKeys)-1:
            self.change_current_case(index+1)
            self.CaseCombo.setCurrentIndex(index+1)
        else:
            self.change_current_case(0)
            self.CaseCombo.setCurrentIndex(0)
            
    def case_to_analyse(self, ID, mic, mesPath, givenauthor=None):
        """setup the analysed cases from MBBM
        called by load_cases
        """
        # read the signal
        caseDict={}
    
        # initiate  MicSignal
        micSn,micval = load_micSn(ID,mic,mesPath)
        # test if signal is clipped, skipü it if True
        if micSn.clippedtest():
            clipped.add((ID,mic))
            print('clipped')
        # create Wav and add path to caseDict
        caseDict['wavPath'] = str(micSn.export_to_Wav(mesPath, relative=False))
        # initialize empty Case with None author
        caseDict['case']=Case(micval['location'], micval['measurement'],ID, mic,micval['micValues']['Tb'], micval['micValues']['Te'], givenauthor)
        #add tmin tmax
        caseDict['tmin'] = float(micval['t'].min())
        caseDict['tmax'] = float(micval['t'].max())
        caseDict['micSn']=micSn
        # Add data to plot ; key:[t,y] , #key is label of plot
        caseDict['plotData'] = {}
        # first plot prms
        micval['y'],micval['t'],_ = micval['mS'].get_signal('prms' + str(mic))
        caseDict['plotData']['LAfast']=[micval['t'].tolist(),(20*np.log10(micval['y']/(2e-5))).tolist()]
        # second plot prms
        # todo: plot stft band
        # append Case Dict to  dict
        self.casesToAnalyze[ID+'_'+mic]=caseDict
        
    def case_up(self):
        """changes case to the previous one"""
        index=self.CaseCombo.currentIndex()
        if index==0:
            self.change_current_case(-1)
            self.CaseCombo.setCurrentIndex(len(self.casesKeys)-1)   
        else:
            self.change_current_case(index-1)
            self.CaseCombo.setCurrentIndex(index-1)
    
    def change_current_case(self, index):
        key = self.casesKeys[index]
        #self.currentCase.get('saved',False):
        self.set_current_case(key)
        self.update_canvas()
        # else:
        #     QtGui.QMessageBox.warning(self, self.trUtf8("save error"), 
        #      self.trUtf8("Before switching case save it!"))
    
    def change_quality(self, quality):
        if quality in ['good','medium','bad']:
            self.case.set_quality(quality)
            if quality=='good':
                curr=self.Qradios[0].isChecked()
                self.Qradios[0].setChecked(not curr)
            elif quality=='medium':
                curr=self.Qradios[1].isChecked()
                self.Qradios[1].setChecked(not curr)
            else:
                curr=self.Qradios[2].isChecked()
                self.Qradios[2].setChecked(not curr)
    
    def changeplot(self):
        index=self.plotselect.index(self.currentplottype)
        if index+1==len(self.PlotTypes):
            index=0
        else:
            index+=1
        self.plotselect.setCurrentIndex(index)
        self.currentplottype=self.PlotTypes[index]
        
    def chg_folder(self):
        """change the directory where to save the data"""
        newpathlib=str(QFileDialog.getExistingDirectory(self,"Please select a directory where I can save your data."))
        if newpathlib!="":
            self.savefolder=pathlib.Path(newpathlib)
            #select color of chg saving folder.
            if not self.savefolder:
                self.buttonChgSave.setStyleSheet("background-color: #c2a5cf")
            else:
                self.buttonChgSave.setStyleSheet("background-color: #a6dba0")
            fm=QtGui.QFontMetrics(self.hlab.font())
            self.hlab.setText("Selected directory : "+fm.elidedText(str(self.savefolder),QtCore.Qt.ElideLeft, 250))
        else:
            print("Path not modified.")

    def check_rb(self, q):
        self.rbG.setExclusive(True)#allows to choose multiple qualities
        for rb, qb in  zip(self.Qradios, ['good', 'medium', 'bad']):
            rb.setChecked(q==qb)
        self.rbG.setExclusive(True)
        
    def checkSavedCases(self, folder=None):
        """returns the IDs in """
        if folder==None:
            folder=self.savefolder.joinpath(pathlib.Path('test_cases/'+self.author))
        if not isinstance(folder, pathlib.Path):
            folder=pathlib.Path(folder)
        savedIDs=[]
        for cs in folder.iterdir():
            if cs.match('case_**'+self.author+'.json'):
                cx=str(cs).split('\\')[-1]
                mid, mic=cx.split('_')[2:4]
                savedIDs.append('m_'+mid+'_'+mic)
        return(savedIDs)
    
    def chg_type(self):
        """change the noise type to the next one on the list (and back to the first)"""
        current_noise_index= self.NoiseTypes.index(self.current_noise)
        if current_noise_index <len(self.NoiseTypes)-1:
            self.set_noise_type(current_noise_index+1)
            self.SOIcombo.setCurrentIndex(current_noise_index+1)
        else:
            self.set_noise_type(0)
            self.SOIcombo.setCurrentIndex(0)
        self.update_canvas()
    
    def chg_typedisplay(self):
        """toggle between show both and show one"""
        self.both_visible = not self.both_visible
        self.cb.setChecked(self.both_visible)
        self.update_stay_rect
        self.update_canvas()
    
    def _connections(self):
        """connects the buttons/combobox to the methods to be applied"""
        self.SOIcombo.currentIndexChanged.connect(self.set_noise_type)
        self.cb.stateChanged.connect(self.set_both_visible)
        self.CaseCombo.currentIndexChanged.connect(self.change_current_case)
        for rb in self.Qradios:
            rb.clicked.connect(self.set_quality)

        if self.adminsession:
            self.plotselect.currentIndexChanged.connect(self.plotchange)
            self.ComboAuthors.currentIndexChanged.connect(self.load_author)
            self.buttonCompare.stateChanged.connect(self.show_compare)
            self.ComboAlgorithms.currentIndexChanged.connect(self.load_algorithm)
        else:
            self.buttonSave.clicked.connect(self.save_case)
            self.buttonChgSave.clicked.connect(self.chg_folder)
    
    def extbrowsercall(self):
        """call opening info page in external web browser"""
        pathtoinfo=self.infofolder.joinpath('info.html').absolute().as_uri()
        os.startfile(pathtoinfo)
    
    def get_quality(self):
        return(self.currentCase['case'].get('quality',False))
    
    def import_cases(self):
        """performs the basic import of cases"""
        with self.mesPath.joinpath('caseToAnalyze.json').open('r+') as input:
            self.casesToAnalyze = json.load(input)
        for k,v in self.casesToAnalyze.items():
            v['case']['author']=self.author
            v['case']= Case(**v['case'])
        self.casesKeys = sorted(list(self.casesToAnalyze.keys()))#list of name of cases
    
    def load_algorithm(self, index):
        """loads the algorithm selected"""
        self.currentAlgorithm=self.Algorithms[self.ComboAlgorithms.currentText()]
        self.buttonCompare.setCheckState(QtCore.Qt.Unchecked)
        self.plot()
    
    def load_author(self, index):
        """loads the saved intervals of an author"""
        self.author=self.authors[index]
        self.TurnTheSavedGreen()
    
    def load_cases(self, listofpaths):
        """loads the cases given in list of paths to casesToAnalyse
        called by add_case
        and by asks_for_ncases
        """
        for pathtofile in listofpaths:#listofpaths contains Windows paths
            filename, extension =pathtofile.name.split('.')
            filename=filename.split('_')
            gauthor=None
            try:
                int(filename[-1])
            except:
                ID='m_'+filename[-3]
                mic=filename[-2]
                gauthor=filename[-1]
            else:
                ID='m_'+filename[-2]
                mic=filename[-1]
            mesPath=None
            if extension=='json':
                for paths in self.Paths:#find the path to 'raw_signals_config.json'
                    try:
                        listdirs=os.listdir(str(paths.joinpath('raw_signals')))
                    except:
                        pass
                    else:
                        if (ID+'_'+mic+'.mat') in listdirs:
                            mesPath=paths
            elif extension=='mat':
                mesPath=pathtofile.parent.parent
            if mesPath:
                self.case_to_analyse(ID,mic,mesPath, gauthor)
            else:
                print("file not found")
        self.casesKeys = sorted(list(self.casesToAnalyze.keys()))#list of name of cases
    
    def onclick(self,x):
        #remove Interval
        self.remove_int(x)
    
    def onselect(self,xmin,xmax, remove=False):
        #add interval1
        if remove:
            self.remove_int(xmin,xmax)
        else:
            self.add_int(xmin,xmax)
        
    def plot(self):
        self.SelectAxis.cla()
        self.case.plot_triggers(self.SelectAxis)
        if self.currentplottype=='LAfast':
            ymax=0
            for key, pData in self.currentCase['plotData'].items():
                t,y = pData
                self.SelectAxis.plot(t, y , label = key, color='#272822', linewidth=1.)#plot display
                if max(y)>ymax:
                    ymax=max(y)
            tmin = self.currentCase['tmin']
            tmax = self.currentCase['tmax']
            self.SelectAxis.set_xlim(tmin,tmax)
            self.SelectAxis.set_ylabel('LA dB')
            self.SelectAxis.set_xlabel('t (s)')
            self.SelectAxis.set_ylim([0,ymax*1.1])
            self.SelectAxis.legend()
        elif self.currentplottype=='Spectogram':
            if not self.currentCase['case'].get_mIDmic() in self.micSignals.keys():
                micSn=MicSignal.from_wav(self.currentCase['wavPath'])
                if micSn:
                    self.micSignals[self.currentCase['case'].get_mIDmic()]=micSn
                else:
                    print("wav file not found")
                    pass
            self.micSignals[self.currentCase['case'].get_mIDmic()].plot_spectrogram('3930_4096_6',self.SelectAxis)
        for ca in self.canvas:
            ca.draw()
        #update canvas
        self.update_stay_rect()

    def plotchange(self,index):
        """update the plot"""
        self.currentplottype=self.PlotTypes[index]
        self.plot()

    def remove_int(self, xmin, xmax = None):
        self.unsave()
        if xmax == None:
            index = self.SOI.containspoint(xmin)
            if index is not None:
                #print('Remove '+ repr(self.SOI.RangeInter[index]))
                self.SOI.removebyindex(index)
        else:
            self.SOI.remove(Interval(xmin,xmax))
        self.update_stay_rect()
        if self.barplay==False:
            self.update_canvas()

    def save_case(self):
        if self.adminsession:
            QtGui.QMessageBox.warning(self,'Save try','You cannot save a file in admin mode')
        else:
            if self.case.get_quality() == None:
                QtGui.QMessageBox.warning(self, self.trUtf8("save error"), 
                self.trUtf8("Quality of selection has to be set!"))
            else:
                # set the author
                if not self.savefolder:
                    #asks for the folder where to save the datas
                    self.chg_folder()
                #self.case.case['author'] = self.author
                casepath=self.case.save(self.savefolder)
                self.buttonSave.setStyleSheet("background-color: #a6dba0")
                currentIndex= self.casesKeys.index(str(self.CaseCombo.currentText()))
                self.CaseCombo.setItemData(currentIndex,QtGui.QColor('#a6dba0'),QtCore.Qt.BackgroundRole)
                #self.AnalysedCases.append(self.casesKeys[currentIndex])

    def set_both_visible(self, state):
        if state == QtCore.Qt.Checked:
            self.both_visibles= True
        else:
            self.both_visibles= False
        self.update_stay_rect()
    
    def set_current_case(self,key):
        self.releaseKeyboard()
        #self.timer.stop()
        self.media.stop()
        self.currentCase = self.casesToAnalyze[key]
        #attributes
        self.case = self.currentCase['case']
        #update buttons
        self.both_visibles = True
        self.cb.setChecked(self.both_visibles)
        self.current_noise = 'Z'
        self.SOIcombo.setCurrentIndex(self.NoiseTypes.index(self.current_noise))
        if not self.adminsession:
            if self.case.get_saved():
                self.buttonSave.setStyleSheet("background-color: #a6dba0")
            else:
                self.buttonSave.setStyleSheet("background-color: #c2a5cf")
            self.check_rb(self.case.get_quality())
        #set SOI and update Canvas
        self.set_noise_type('Z')
        #plot
        self.plot()
        #Set mediafile
        wavPath = self.mesPath.joinpath(self.currentCase['wavPath'])
        self.set_media_source(str(wavPath), self.currentCase['tmin'])
        #start timer
        #self.timer.start()
        self.grabKeyboard()
        self.set_quality()
    
    def set_int(self,press):
        self.unsave()
        if press:
            self._t_int_min = self.t
            return
        else:
            tmax = self.t
            if abs(tmax-self._t_int_min) > self.minspan:
                self.add_int(self._t_int_min,tmax)
        if self.barplay==False:
            self.update_canvas()
    
    def set_noise_type(self, index):
        if isinstance(index,int):
            self.current_noise = self.NoiseTypes[index]
        else:
            self.current_noise = index
        self.SOI = self.case.get_SOI(self.current_noise)
        self.update_stay_rect()
    
    def set_quality(self):
        for q,rb in zip( ['good','medium','bad'],self.Qradios):
            if rb.isChecked():
                self.case.set_quality(q)

    def set_remove(self,press):
        """removes int while playing audio"""
        self.unsave()
        if press:
            self._t_int_min = self.t
            return
        else:
            tmax = self.t
            if abs(tmax-self._t_int_min) > self.minspan:
                self.remove_int(self._t_int_min,tmax)
        if self.barplay==False:
            self.update_canvas()

    def show_compare(self,state):
        """will show or remove the comparison between current author /current case and the current algorithm"""
        if state==QtCore.Qt.Checked:
            if self.currentCase.get('micSn',False):
                MicSnObj=self.currentCase['micSn']
            else:
                ID=self.currentCase.get_mID()
                mic=self.currentCase.get_mic()
                matPath=self.currentCase.get_mat_path()
                MicSnObj, stftname=load_micSn(ID,mic,matPath, self.currentAlgorithm)
                self.casesToAnalyze[ID+'_'+mic]['micSn']=MicSnObj
                self.casesToAnalyze[ID+'_'+mic]['stftName']=stftname
            MicSnObj.calc_kg(self.currentAlgorithm)
            alg_res = MicSnObj.get_KG_results(self.currentAlgorithm)['result']
            self.case.plot_compare(self.SelectAxis, noiseType = self.currentAlgorithm.noiseType , **alg_res)
        else:
            self.plot()

    def show_info(self):
        self.extbrowsercall()

    def TurnTheSavedGreen(self):
        """
        as its name tells, it turns the saved cases green
        initiates the combobox Casecombo
        it also load the intervals saved
        """
        try:
            sIDs=self.checkSavedCases()
        except:
            print("No saving folder was found")
            self.CaseCombo.setCurrentIndex(0)
            self.set_current_case(self.casesKeys[0])
        else:  
            zind=[i for i in range(0,len(self.casesKeys))]
            for scased in sIDs:
                if scased in self.casesKeys:
                    zind.remove(self.casesKeys.index(scased))
                    currentIndex= self.casesKeys.index(scased)
                    self.CaseCombo.setItemData(currentIndex,QtGui.QColor('#a6dba0'),QtCore.Qt.BackgroundRole)
                    self.casesToAnalyze[scased]['case'].set_saved(True)
                    pathtofile=self.savefolder.joinpath('test_cases/'+self.author+'/case_'+scased+'_'+self.author+'.json')
                    caseinfile=Case.from_JSON(pathtofile)
                    self.casesToAnalyze[scased]['case'].set_quality(caseinfile.get_quality())
                    for type in self.NoiseTypes:
                        self.casesToAnalyze[scased]['case'].set_SOI(caseinfile.get_SOI(type),type)
            if len(zind)==0:
                if self.sparecase and not self.adminsession:
                    k,v = self.sparecase
                    ok=QtGui.QMessageBox.warning(self, "All cases were treated!", "You have already reviewed all the cases. \n I have added the case "+k+" to the list.")
                    self.casesToAnalyze[k]=v
                    self.CaseCombo.addItem(self.sparecase[0])
                    self.casesKeys.append(self.sparecase[0])
                    self.CaseCombo.setCurrentIndex(self.casesKeys.index(k))
                    self.set_current_case(k)
                else:
                    if not self.adminsession:
                        ok=QtGui.QMessageBox.warning(self, "All cases were treated!", "You have already reviewed all the cases.")
                    try:
                        i=self.CaseCombo.currentIndex()
                        firsttime=False
                    except:
                        firsttime=True
                    if not self.adminsession or firsttime:#initialise CaseCombo only if not admin session or firsttime
                        self.CaseCombo.setCurrentIndex(-1)
                        self.current_noise='Z'
                        self.SOI=self.casesToAnalyze[self.casesKeys[0]]['case'].get_SOI()
            else:
                zind=min(zind)
                self.CaseCombo.setCurrentIndex(zind)
                self.set_current_case(self.casesKeys[zind])
     
    def unsave(self):
        """get back to unsaved status"""
        if self.currentCase['case'].get_saved and not self.adminsession:
            self.currentCase['case'].give_saved(False)
            self.buttonSave.setStyleSheet("background-color: #c2a5cf")
            currentIndex= self.casesKeys.index(str(self.CaseCombo.currentText()))
            self.CaseCombo.setItemData(currentIndex,QtGui.QColor('#c2a5cf'),QtCore.Qt.BackgroundRole)
     
    def update_stay_rect(self):
        for index,nT in enumerate(self.NoiseTypes):
            if nT == self.current_noise:
                self.CS.set_stay_rects_x_bounds(self.SOI.tolist(),index)
            elif self.both_visibles:
                self.CS.set_stay_rects_x_bounds(self.case.get_SOI(nT).tolist(), index)
            else:
                self.CS.set_stay_rect_visible(False, index)
    
    @classmethod
    def from_measurement(cls, mesVal, mID, mics, author = None):
        mesPath = mesVal.path.absolute()
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

def palettesimple(chgmatplotlib=True):
    textcolor='#f5f5f5'
    axescolor='#f5f5f5'
    axbgcolor='#272822'
    bgcolor='#aaaaaa'
    palette=QtGui.QPalette()
    palette.setColor(QtGui.QPalette.Window,'#a3a3a3')
    palette.setColor(QtGui.QPalette.Button,textcolor)
    palette.setColor(QtGui.QPalette.ButtonText,axbgcolor)
    palette.setColor(QtGui.QPalette.Text,axbgcolor)
    palette.setColor(QtGui.QPalette.Base,textcolor)
    palette.setColor(QtGui.QPalette.AlternateBase,'#f3f3f3')
    palette.setColor(QtGui.QPalette.WindowText,textcolor)
    palette.setColor(QtGui.QPalette.Highlight, '#c2a5cf')
    palette.setColor(QtGui.QPalette.HighlightedText, axbgcolor)
    palette.setColor(QtGui.QPalette.AlternateBase,axbgcolor)
    palette.setColor(QtGui.QPalette.ToolTipBase, axbgcolor)
    palette.setColor(QtGui.QPalette.Light, axescolor)
    palette.setColor(QtGui.QPalette.Midlight, bgcolor)
    palette.setColor(QtGui.QPalette.Dark, axbgcolor)
    if chgmatplotlib:
        matplotlibsimple()
    return palette
    
def matplotlibsimple():
    textcolor='#f5f5f5'
    axescolor='#f5f5f5'
    axbgcolor='#272822'
    bgcolor='#aaaaaa'      
    matplotlib.rcParams['axes.facecolor']=axescolor#background of ax   
    matplotlib.rcParams['axes.edgecolor']=axbgcolor
    matplotlib.rcParams['xtick.color']=axescolor
    matplotlib.rcParams['grid.color']=bgcolor
    matplotlib.rcParams['ytick.color']=axescolor
    matplotlib.rcParams['figure.edgecolor']=textcolor
    matplotlib.rcParams['figure.facecolor']='#272822'
    matplotlib.rcParams['patch.linewidth']='0.25'
    matplotlib.rcParams['lines.color']=axbgcolor
    matplotlib.rcParams['lines.linewidth']='0.75'
    matplotlib.rcParams['axes.linewidth']='0.4'
    matplotlib.rcParams['xtick.major.width']='0.4'
    matplotlib.rcParams['ytick.major.width']='0.4'
    matplotlib.rcParams['xtick.minor.width']='0.3'
    matplotlib.rcParams['xtick.minor.width']='0.3'
    matplotlib.rcParams['text.color']=bgcolor#LAFast (on ax)
    matplotlib.rcParams['axes.labelcolor']=axescolor#labels diplayed on the figure (LA, t(s))
    matplotlib.rcParams['font.family']='HelveticaNeue'
    matplotlib.rcParams['grid.linewidth']=0.2
    matplotlib.rcParams['grid.alpha']=0.5
    matplotlib.rcParams['legend.framealpha']=0.4
    matplotlib.rcParams['figure.autolayout']=False
    font={'family':'sans-serif','weight':'regular','size':11}
    matplotlib.rc('font',**font)  

class CompareCaseAlgWidget(DetectControlWidget):
    #todo: improve graphical quality
    
    def __init__(self, wavPath, algorithms, micSn, case = None):
        #init super
        super(CompareCaseAlgWidget, self).__init__()
        self.resize(1300, 900)
        self.case = case
        self.micSn = micSn
        #set algorithms
        self.algorithms = algorithms
        self.currentAlg = self.algorithms[0]
        self.wavPath = wavPath#this wav path is indipendent of micSn if initiated from wav
        print(wavPath)
        self.set_media_source(str(self.wavPath), self.micSn.t.min())
        self.add_widgets()
        self.connections()
        self.palette=True
        
    def add_widgets(self):
        """initialise the graphical output"""
        self.setWindowTitle('Compare Case and Algorithm ')
        if self.palette:
            matplotlibsimple()
        #add canvas
        plt.ioff()
        self.fig = Figure((17,15))
        self.fig.set_dpi(110)
        ca = FigureCanvas(self.fig)
        # plot
        self.canvas = [ca]
        self.plot()
        # set canvas
        self.set_mpl({1:{'animate':True,'bar':True, 'canvas': ca , 
        'axHandle': [Bar(ax) for ax in self.axes]}})
        # add first row of buttons
        hBox = QtGui.QHBoxLayout()
        # select alg combo 
        groupBox = QtGui.QGroupBox('Select Algorithm ')
        self.algCombo = QtGui.QComboBox()
        for alg in self.algorithms:
            self.algCombo.addItem(str(alg))
        hbox1 = QtGui.QHBoxLayout()
        hbox1.addWidget(self.algCombo)
        groupBox.setLayout(hbox1)
        hBox.addWidget(groupBox)
        hBox.addStretch(1)
        # groupBox2 = QtGui.QGroupBox('Plotting')
        # hbox2=QtGui.QHBoxLayout()
        # self.buttonplot=QtGui.QPushButton('Draw')
        # hbox2.addWidget(self.buttonplot)
        # groupBox2.setLayout(hbox2)
        # hBox.addWidget(groupBox2)
        # hBox.addStretch(1)
        
        self.vBox.addLayout(hBox)
        # Browser
        #todo: add case Info, add alg Info, add test_on_case results
        self.edit = QtGui.QTextBrowser()
        self.vBox.addWidget(self.edit)
        self.currentAlg.calc_rates()
        self.edit.setHtml(md.markdown('###TPR :'+str(self.currentAlg.rates['TPR'])+' FPR : '+str(self.currentAlg.rates['FPR'])+ 'TPR-FPR : '+str(self.currentAlg.rates['TPR']-self.currentAlg.rates['FPR'])))
        #set central widget
        self.set_centralWidget()
        
    def set_current_alg(self,index):
        #self.timer.stop()
        self.media.stop()
        self.currentAlg = self.algorithms[index]
        self.plot()
        #start timer
        #self.timer.start()
        self.currentAlg.calc_rates()
        self.edit.setHtml(md.markdown('###TPR :'+str(self.currentAlg.rates['TPR'])+' FPR : '+str(self.currentAlg.rates['FPR'])+ 'TPR-FPR : '+str(self.currentAlg.rates['TPR']-self.currentAlg.rates['FPR'])))
        
    def plot(self):
        self.axes = self.currentAlg.visualize(self.fig, self.micSn, self.case)
        self.canvas[0].draw()

    def _connections(self):
        self.algCombo.currentIndexChanged.connect(self.set_current_alg)
        #self.buttonplot.clicked.connect(self.callTrueFalse)
  
    def show_info(self):
        pass
    
    # def callTrueFalse(self):
    #     """plot the true/false positive/negative plots"""
    #     if self.case: 
    #         f,axes = plt.subplots(2,sharex = True)
    #         ax = axes[0]
    #         self.micSn.plot_triggers(ax,color = '#272822',lw=1)
    #         self.micSn.plot_BPR(self.currentAlg, ax, color = '#272822', linewidth=1)
    #         self.case.plot(ax)
    #         ax.set_xlim(-0.5,8)
    #         ymin,ymax = ax.get_ylim()
    #         ax=axes[1]
    #         alg_res = self.micSn.get_KG_results(self.currentAlg)['result']
    #         self.micSn.plot_BPR(self.currentAlg, ax, color = '#272822', lw=1)
    #         self.case.plot_compare(ax,alg_res['result'], alg_res['t'])
    #         plt.show()

    @classmethod
    def from_measurement(cls , mesVal, algorithms, case = None, ID = None, mic = None):
        """initiate from measurement"""
        mesPath = mesVal.path.absolute()
        if case is not None:
            ID = case.case['mID']
            mic = case.case['mic']
        elif mic is None or ID is None:
            raise(ValueError)
        #initiate micSn    
        measuredSignal.setup(mesPath)
        mS = measuredSignal(ID,mic)
        y,t,sR = mS.get_signal(mic)
        ch_info = mS.channel_info(mic)
        var = ['Tb','Te','Tp_b','Tp_e','LAEQ']
        micValues = mesVal.get_variables_values(ID, mic, var)
        micValues.update(ch_info)
        micSn = MicSignal(ID,mic,y,t,sR, micValues)
        #calculations
        if not isinstance(algorithms,list):
            algorithms = [algorithms]
        for n,alg in enumerate(algorithms):
            #calculate algorithms on case
            if case is not None:
                alg.test_on_case(case, mesVal, micSn)
                alg.calc_rates()
            #calculate kg on micSn
            else:
                micSn.calc_kg(alg)
        wavPath = micSn.export_to_Wav(mesPath)
        return cls(mesPath.joinpath(wavPath),  algorithms,micSn, case)
    
    @classmethod
    def from_wav(cls, wavPath, algorithms):
        """configures a CompareCaseAlgWidget from a wav (file or path) and an algorithm"""
        micSn = MicSignal.from_wav(wavPath)
        if not isinstance(algorithms,list):
            algorithms = [algorithms]
        for alg in algorithms:
            micSn.calc_kg(alg)
        return cls(wavPath, algorithms, micSn)
        
def load_micSn(ID,mic,matPath, gvar = ['Tb','Te','Tp_b','Tp_e','LAEQ'], algorithm=None):
    """loads micSn from the matPath, returns a signal and a stftName"""
    jsonconfigpath=matPath
    mesVal = measuredValues.from_json(jsonconfigpath)
    location =  mesVal.location
    measurement = mesVal.measurement
    measuredSignal.setup(jsonconfigpath)
    mS = measuredSignal(ID,mic)
    y, t, sR = mS.get_signal(mic)
    ch_info = mS.channel_info(mic)
    # get the values from measuredValues to initiate MicSignal and Case
    var = gvar
    micValues = mesVal.get_variables_values(ID, mic, var)
    micValues.update(ch_info)
    # initiate  MicSignal
    MicSnObj = MicSignal(ID,mic,y,t,sR, micValues)
    if algorithm:
        stftName = MicSnObj.get_stft_name(algorithm)
        return MicSnObj, stftName
    else:
        return MicSnObj, {'location':location,'measurement':measurement, 'micValues':micValues,'t':t,'y':y,'sR':sR, 'mS':mS}

##
if __name__ == "__main__":
    from kg.measurement_values import measuredValues
    from kg.measurement_signal import measuredSignal
    from kg.algorithm import ZischenDetetkt1
    #setup measurement
    
    mesPath = pathlib.Path('').absolute().joinpath('Measurements_example\MBBMZugExample')
    MESPATH = mesPath
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
    #W = CaseCreatorWidget.from_measurement(mesVal,mID,mic)
    #W=CaseCreatorWidget.from_wav('C:\lucmiaz\KG_dev_branch\Measurements_example\various_passby\kreischen.wav')
    W.show()
    