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
from kg.case import Interval, SetOfIntervals
from kg.measurement_values import measuredValues
from kg.measurement_signal import measuredSignal
from kg.algorithm import *
from scipy.io import wavfile
import random
import json
import time
#import seaborn as sns
#sns.set(style='ticks',palette='Set2')
                          
class kgControlWidget(QMainWindow):
    """subclass of QMainWindow that create and destroy subclasses of MainCaseWidget
    """
    def __init__(self, mesPath):
        QMainWindow.__init__(self)
        frm = QtGui.QFrame ()
        w=1200; h=700
        self.mesPath=mesPath
        self.infofolder=pathlib.Path("").absolute()
        self.setWindowTitle('Create Case')
        self.setCentralWidget (frm)
        self.resize(w, h)
        self.CaseWidget=None
        self.session=0
        self.comboratedict={'15ms : High':15, '25ms : Fairly High':25, ' 30ms : Medium ':30, '40ms : Pretty Low ':40, '50ms :Low':50, '60ms : Ancient':60}
        self.menu_bar()
        self.boolaudio=False
        self.initilialized=False
        #self.mainLayout=QtGui.QVBoxLayout()
        
        #TAB
        #self.TabWidget=QtGui.QTabWidget()
        #self.mainTab=QtGui.QWidget()
        #self.vBox = QtGui.QVBoxLayout(self.mainTab)
        #self.TabWidget.addTab(self.mainTab,'Main')
        #self.mainLayout.addWidget(self.TabWidget)
        #self.show_info()
        
        self.vBox=QtGui.QVBoxLayout()
        #self.setLayout(self.mainLayout)
        self.setLayout(self.vBox)
        self.toCleanOnNew=[]
        self.savePlotFolder=pathlib.Path('')
        self.savePlotType='pdf'
        self.savePlotdpi=300
        self.statusBar().setStyleSheet("QStatusBar{padding-left:10px;background:#272822;color:#f5f5f5;font-weight:bold;}")
        
    def add_to_authors(self):
        if self.initilialized:
            try:
                self.ComboAuthors.clear()
            except:
                pass
            for auth in self.CaseWidget.authors:
                try:
                    self.ComboAuthors.addItem(auth)
                except:
                    pass
    
    def add_widgets_admin(self):
        """add admin tools such as different types of plot, algorithm test and authors browser"""
        #Plots
        groupBox=QtGui.QGroupBox("Admin options")
        self.plotselect=QtGui.QComboBox()
        for type in self.CaseWidget.PlotTypes:
            self.plotselect.addItem(type)
        hBox=QtGui.QHBoxLayout()
        labelAuthor=QtGui.QGroupBox("Plot type")
        hpb=QtGui.QHBoxLayout()
        hpb.addWidget(self.plotselect)
        labelAuthor.setLayout(hpb)
        hBox.addWidget(labelAuthor)
        
        #Authors
        try:
            authorspath=self.CaseWidget.mesPath.joinpath('test_cases')
        except:
            self.CaseWidget.authors=['admin']
        else:
            self.CaseWidget.authors=os.listdir(authorspath.as_posix())
        self.CaseWidget.authors.append('admin')
        self.ComboAuthors=QtGui.QComboBox()
        labelAuthor=QtGui.QGroupBox("Authors")
        hcb=QtGui.QHBoxLayout()
        hcb.addWidget(self.ComboAuthors)
        labelAuthor.setLayout(hcb)
        hBox.addWidget(labelAuthor)
        #for cls in vars()['Algorithm'].__subclasses__():
        #    algid, algdescription=eval(cls.__name__()+".phony()")
        #    self.algorithmsTypes[algid]={'classname':cls.__name__(), 'attributes': algdescription}
        self.CaseWidget.Algorithms={}
        self.ComboAlgorithms=QtGui.QComboBox()
        self.CaseWidget.asks_for_algorithm()
        self.CaseWidget.currentAlgorithm=self.CaseWidget.Algorithms[self.ComboAlgorithms.currentText()]
        labelAlg=QtGui.QGroupBox("Algorithms")
        hab=QtGui.QHBoxLayout()
        hab.addWidget(self.ComboAlgorithms)
        labelAlg.setLayout(hab)
        hBox.addWidget(labelAlg)
        groupBox.setLayout(hBox)
        hBox=QtGui.QHBoxLayout()
        hBox.addWidget(groupBox)
        self.CaseWidget.author=self.CaseWidget.authors[0]
        self.toCleanOnNew.append(hBox)
        self.vBox.addLayout(hBox)
    
    def add_widgets_audio(self):
        if not self.boolaudio:
            self.media = Phonon.MediaObject(self)
            self.audio_output = Phonon.AudioOutput(Phonon.MusicCategory, self)
            self.seeker = Phonon.SeekSlider(self)
            self.seeker.setFixedHeight(20)
            self.seeker.setMediaObject(self.media)
            self.mediarate='Fairly High 25ms'
            self.media.setTickInterval(25)
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
            #layout
            self.vBox.addWidget(self.seeker)
            self.modifiers= None
    
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
        self.CaseWidget.CS = CaseSelector(self.SelectAxis, self.CaseWidget.onselect, self.CaseWidget.onclick, 
                                nrect = [50,50], update_on_ext_event = True , 
                                minspan = self.CaseWidget.minspan )
        canvas['selector'] = {'animate':True,'bar':True, 'canvas':ca , 'axHandle': self.CaseWidget.CS}
        
        #set canvas
        self.CaseWidget.set_mpl(canvas)
        
        # add first row of buttons
        CreatorBox = QtGui.QHBoxLayout()
        
        # select case combo 
        groupCaseBox = QtGui.QGroupBox('Select case to analyze ')
        self.CaseCombo = QtGui.QComboBox()
        
        CaseBox = QtGui.QHBoxLayout()
        CaseBox.addWidget(self.CaseCombo)
        groupCaseBox.setLayout(CaseBox)
        
        CreatorBox.addWidget(groupCaseBox)
        # select noise Type
        groupTypeBox = QtGui.QGroupBox('Noise Type to select')
        TypeBox = QtGui.QHBoxLayout()
        # noise Type combo
        self.SOIcombo = QtGui.QComboBox()
        self.SOIcombo.addItem('Zischen', 'Z')
        self.SOIcombo.setItemData(0,QtGui.QColor('#984ea3'),QtCore.Qt.BackgroundRole)#add backgroundcolor of combo Z
        self.SOIcombo.setItemData(0,QtGui.QColor('#f5f5f5'),QtCore.Qt.ForegroundRole)#change text color
        self.SOIcombo.addItem('Kreischen', 'KG')
        self.SOIcombo.setItemData(1,QtGui.QColor('#ffff33'),QtCore.Qt.BackgroundRole)#add backgroundcolor of combo K
        self.SOIcombo.setItemData(1,QtGui.QColor('#272822'),QtCore.Qt.ForegroundRole)#change text color
        TypeBox.addWidget(self.SOIcombo)
        # visualize both cb
        self.cb = QtGui.QCheckBox('both visible', self)
        TypeBox.addWidget(self.cb)
        groupTypeBox.setLayout(TypeBox)

        CreatorBox.addWidget(groupTypeBox)
        # quality radios
        
        groupQualityBox = QtGui.QGroupBox("Select quality: are noise events detectable?")
        self.Qradios = [QtGui.QRadioButton(q) for q in ['good','medium','bad']]
        QualityBox = QtGui.QHBoxLayout()
        self.rbG = QtGui.QButtonGroup()
        for rb in self.Qradios:
            self.rbG.addButton(rb)
            QualityBox.addWidget(rb) 
        groupQualityBox.setLayout(QualityBox)
        CreatorBox.addWidget(groupQualityBox)

        CreatorBox.addStretch(1)
        self.toCleanOnNew.append(CreatorBox)
        self.vBox.addLayout(CreatorBox)
    
    def add_widgets_creator(self):
        """add widgets that are not useful when logged as admin"""
        hBox = QtGui.QHBoxLayout()
        # save button
        self.buttonSave = QtGui.QPushButton("save",self)
        hBox1 = QtGui.QHBoxLayout()
        hBox1.addWidget(self.buttonSave)
        hBox1.addStretch()
        # saved data directory group (button to change folder and current folder)
        groupBox=QtGui.QGroupBox("Saving options")
        fm=QtGui.QFontMetrics('HelveticaNeue')
        self.hlab=QtGui.QLabel("Selected directory : "+fm.elidedText(str(self.CaseWidget.savefolder),QtCore.Qt.ElideLeft, 250))#crop the displayed path if too long (ElideLeft -> add ... left of the path
        self.buttonChgSave = QtGui.QPushButton("Change folder",self)
        hBox1.addWidget(self.hlab)
        hBox1.addWidget(self.buttonChgSave)
        
        groupBox.setLayout(hBox1)
        #self.vBox.addLayout(hBox)
        #select color of chg saving folder.
        if not self.CaseWidget.savefolder:
            self.buttonChgSave.setStyleSheet("background-color: #c2a5cf")
            self.hlab.setText("Selected directory : "+str(self.CaseWidget.savefolder))
        else:
            self.buttonChgSave.setStyleSheet("background-color: #a6dba0")
            self.hlab.setText("Selected directory : "+str(self.CaseWidget.savefolder))
        hBox.addWidget(groupBox)
        self.toCleanOnNew.append(hBox)
        self.vBox.addLayout(hBox)
    
    def admin_actions(self):
        #algorithms
        self.addalgAction = QtGui.QAction('&Add alg', self)        
        self.addalgAction.setShortcut('Ctrl+Shift+A')
        self.addalgAction.setStatusTip('Add algorithm')
        self.addalgAction.triggered.connect(self.CaseWidget.asks_for_algorithm)
        #case
        self.addcaseAction = QtGui.QAction('&Add case', self)        
        self.addcaseAction.setShortcut('Ctrl+Shift+C')
        self.addcaseAction.setStatusTip('Add case')
        self.addcaseAction.triggered.connect(self.CaseWidget.asks_for_case)
        #show compare
        self.compareAction = QtGui.QAction('&Compare',self)
        self.compareAction.setShortcut('Ctrl+Alt+C')
        self.compareAction.setStatusTip('Compare algorithm with case')
        self.compareAction.triggered.connect(self.CaseWidget.show_compare)
        #show author comparison
        self.authorIntAction=QtGui.QAction('&Show author intervals',self)
        self.authorIntAction.setShortcut('Ctrl+Shift+P')
        self.authorIntAction.setStatusTip('Showing author intervals')
        self.authorIntAction.triggered.connect(self.show_author_int)
        
    def admin_actions_disable(self):
        self.basic_action_disable()
        #disable actions
        self.addalgAction.setDisabled(True)
        self.addcaseAction.setDisabled(True)
        self.compareAction.setDisabled(True)
        
    def admin_actions_enable(self):
        #disable actions
        self.basic_action_enable()
        self.addalgAction.setEnabled(True)
        self.addcaseAction.setEnabled(True)
        self.compareAction.setEnabled(True)
        
    def _barplay(self, truth):
        """define what to do when audio is playing/not playing"""
        self.CaseWidget._barplay(truth)
        
    def basic_actions(self):
        #create CaseWidget
        #case creator
        self.createCaseCreatorAction=QtGui.QAction('&CreatorWidget',self)
        #self.createCaseCreatorAction.setShortcuts('Ctrl+C')
        self.createCaseCreatorAction.setStatusTip('Case Creator')
        self.createCaseCreatorAction.triggered.connect(self.NewCaseCreator)
        #case admin
        self.createCaseAdminAction=QtGui.QAction('&AdminWidget',self)
        self.createCaseAdminAction.setStatusTip('Case Creator')
        self.createCaseAdminAction.triggered.connect(self.NewCaseAdmin)
        #show info
        self.showinfoAction=QtGui.QAction('&Info',self)
        self.showinfoAction.setShortcut('Ctrl+I')
        self.showinfoAction.setStatusTip('Show info')
        self.showinfoAction.triggered.connect(self.show_info)
        #media rate
        self.rateActions={}
        for rate in list(self.comboratedict.keys()):
            rAction=QtGui.QAction('& %s' %rate, self)
            rAction.setStatusTip(rate)
            rAction.triggered.connect(lambda: self.change_rate(self.comboratedict[rate]))
            self.rateActions[rate]=rAction
        #save plot
        self.savePlotAction=QtGui.QAction('&SaveImage',self)
        self.savePlotAction.setShortcut('Ctrl+Shift+S')
        self.savePlotAction.setStatusTip('Save current plot and intervals in the save image folder')
        self.savePlotAction.triggered.connect(self.savePlot)
        #change save plot folder
        self.chgSavePlotFolderAction=QtGui.QAction('&Change output folder',self)
        self.chgSavePlotFolderAction.setStatusTip('Change the current folder for saving the Plot')
        self.chgSavePlotFolderAction.triggered.connect(self.chgSavePlotFolder)
        #change save plot type
        self.chgSavePlotTypeAction=QtGui.QAction('&Change output type',self)
        self.chgSavePlotTypeAction.setStatusTip('Change output type : example pdf, svg, png')
        self.chgSavePlotTypeAction.triggered.connect(self.chgSavePlotType)
        self.basic_action_disable()
    
    def basic_action_disable(self):
        self.chgSavePlotTypeAction.setDisabled(True)
        self.chgSavePlotFolderAction.setDisabled(True)
        self.savePlotAction.setDisabled(True)
    
    def basic_action_enable(self):
        self.chgSavePlotTypeAction.setEnabled(True)
        self.chgSavePlotFolderAction.setEnabled(True)
        self.savePlotAction.setEnabled(True)
    
    def chgSavePlotdpi(self):
        retour,ok=QtGui.QInputDialog.getInt(self,'dpi','Please select dot per inch ratio for output')
        if ok:
            self.savePlotdpi=int(retour)
    def chgSavePlotFolder(self):
        retour=(QtGui.QFileDialog.getExistingDirectory(self, 'Please select an output directory.'))
        try:
            pathsave=pathlib.Path(retour).absolute()
        except:
            pass
        else:
            if pathsave.isdir():
                self.savePlotFolder=pathsave
    def chgSavePlotType(self):
        self.releaseKeyboard()
        result,ok=QtGui.QInputDialog.getItem(self,'Image extension','Please select an image type',['png','ps','pdf','svg'])
        if ok:
            self.savePlotType=result
    
    def change_rate(self,rate):
        if self.boolaudio:
            self.mediarate=rate
            self.media.setTickInterval(rate)
    
    def clean_old_Widgets(self):
        for wid in reversed(self.toCleanOnNew):
            self.clearLayout(wid)
        self.toCleanOnNew=[]
    
    def clearLayout(self, layout):
        if layout is not None:
                while layout.count():
                    item = layout.takeAt(0)
                    widget = item.widget()
                    if widget is not None:
                        widget.deleteLater()
                    else:
                        self.clearLayout(item.layout())
    def connections(self):
        self.media.tick.connect(self.update_time)
        self.media.finished.connect(self.media_finish)
        self.media.stateChanged.connect(self.timer_status)#update timer status on media Statechange
        self.SOIcombo.currentIndexChanged.connect(self.CaseWidget.set_noise_type)
        self.cb.stateChanged.connect(self.CaseWidget.set_both_visible)
        self.CaseCombo.currentIndexChanged.connect(self.CaseWidget.change_current_case)
        for rb in self.Qradios:
            rb.clicked.connect(self.CaseWidget.set_quality)
        self.boolaudio=True
    
    def connections_admin(self):
        self.plotselect.currentIndexChanged.connect(self.CaseWidget.plotchange)
        self.ComboAuthors.currentIndexChanged.connect(self.CaseWidget.load_author)
        self.ComboAlgorithms.currentIndexChanged.connect(self.CaseWidget.load_algorithm)
    
    def connections_creator(self):
        self.buttonSave.clicked.connect(self.CaseWidget.save_case)
        self.buttonChgSave.clicked.connect(self.CaseWidget.chg_folder)
    
    def creator_actions(self):
        #save
        self.saveAction=QtGui.QAction('&Save',self)
        self.saveAction.setShortcut('Ctrl+S')
        self.saveAction.setStatusTip('Save case')
        self.saveAction.triggered.connect(self.CaseWidget.save_case)
        #saving folder
        self.changesavingfolderAction=QtGui.QAction('&ChgSFolder',self)
        self.changesavingfolderAction.setShortcut('Ctrl+F')
        self.changesavingfolderAction.setStatusTip('Change saving folder')
        self.changesavingfolderAction.triggered.connect(self.CaseWidget.chg_folder)
        
    def creator_actions_disable(self):
        self.basic_action_disable()
        self.changesavingfolderAction.setDisabled(True)
        self.saveAction.setDisabled(True)
    def creator_actions_enable(self):
        self.basic_action_enable()
        self.changesavingfolderAction.setEnabled(True)
        self.saveAction.setEnabled(True)
    
    def define_actions(self):
        """define actions for the menu"""
        if not self.initilialized:
            #exit
            self.exitAction = QtGui.QAction(QtGui.QIcon('exit.png'), '&Exit', self)        
            self.exitAction.setShortcut('Ctrl+Q')
            self.exitAction.setStatusTip('Exit application')
            self.exitAction.triggered.connect(QtGui.qApp.quit)
            
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
            self.nextcaseAction.setShortcuts(['DOWN', 'ARROW'])
            self.nextcaseAction.setStatusTip('Move to next case')
            self.nextcaseAction.triggered.connect(self.CaseWidget.case_down)
            
            self.prevcaseAction= QtGui.QAction('&Prev case', self)        
            self.prevcaseAction.setShortcuts(['UP','ARROW'])
            self.prevcaseAction.setStatusTip('Move to previous case')
            self.prevcaseAction.triggered.connect(self.CaseWidget.case_up)
            self.creator_actions()
            self.admin_actions()
            self.menu_bar_advanced()
            self.initilialized=True
        self.creator_actions_disable()
        self.admin_actions_disable()
    
    def extbrowsercall(self):
        """call opening info page in external web browser"""
        pathtoinfo=self.infofolder.joinpath('info.html').absolute().as_uri()
        os.startfile(pathtoinfo)
    
    def keyPressEvent(self, event):
        self.modifiers = QtGui.QApplication.keyboardModifiers()#checks on keypress what modifyers there is
        if event.isAutoRepeat():
            return
        if self.session:
            #Any session
            if event.key()==QtCore.Qt.Key_Space:
                if self.modifiers==QtCore.Qt.ControlModifier:#if ctrl pressed, go stops
                    self.CaseWidget.media_finish()
                else:
                    if self.media.state()==1:#if stopped
                        self.CaseWidget.media.play()
                    elif self.media.state()==4:#if paused
                        self.CaseWidget.media.play()
                    else:#if playing (2), buffering (3), loading(0) or error(5)
                        self.CaseWidget.media.pause()
            elif event.key()==QtCore.Qt.Key_Up or event.key()==QtCore.Qt.Key_Left:
                    self.CaseWidget.media.stop()
                    self.CaseWidget.case_up()
            elif event.key()==QtCore.Qt.Key_Down or event.key()==QtCore.Qt.Key_Right:
                    self.CaseWidget.media.stop()
                    self.CaseWidget.case_down()
            elif event.key()==QtCore.Qt.Key_Z:
                self.CaseWidget.media.pause()
                self.CaseWidget.chg_type()
            elif event.key()==QtCore.Qt.Key_K:
                self.CaseWidget.media.pause()
                self.CaseWidget.chg_type()
            elif event.key()==QtCore.Qt.Key_T:
                self.CaseWidget.media.pause()
                self.CaseWidget.chg_type()
            elif event.key()==QtCore.Qt.Key_B:
                self.CaseWidget.media.pause()
                self.CaseWidget.chg_typedisplay()
            elif event.key()==QtCore.Qt.Key_P:
                self.CaseWidget.media.stop()
                self.CaseWidget.change_plot()
            #Creator session
            elif self.session==2: #elements active only if we are in creator session
                if event.key() == QtCore.Qt.Key_D:
                    self.CaseWidget.set_remove(True)
                elif event.key() == QtCore.Qt.Key_S and not self.modifiers==QtCore.Qt.ControlModifier:
                    self.CaseWidget.set_int(True)
                elif event.key()== QtCore.Qt.Key_S and self.modifiers==QtCore.Qt.ControlModifier:
                    self.CaseWidget.media.stop()
                    self.CaseWidget.save_case()
                elif event.key()==QtCore.Qt.Key_Enter:
                    self.CaseWidget.media.stop()
                    if not self.get_quality:
                        self.change_quality(1)
                    self.CaseWidget.save_cases()
                    self.CaseWidget.case_down()
                elif event.key()==QtCore.Qt.Key_F:
                    self.CaseWidget.media.stop()
                    self.CaseWidget.chg_folder()
                elif event.key()==QtCore.Qt.Key_1:
                    self.CaseWidget.change_quality('bad')
                elif event.key()==QtCore.Qt.Key_2:
                    self.CaseWidget.change_quality('medium')
                elif event.key()==QtCore.Qt.Key_3:
                    self.CaseWidget.change_quality('good')
                elif event.key()==QtCore.Qt.Key_U and self.modifiers==QtCore.Qt.ControlModifier:
                    self.CaseWidget.update_canvas()
                elif event.key()==QtCore.Qt.Key_P and self.modifiers==QtCore.Qt.ControlModifier:
                    self.CaseWidget.plot()
        event.accept()
                    
        
    def keyReleaseEvent(self, event):
        if event.isAutoRepeat():
            return
        if self.session==2:
            if event.key() == QtCore.Qt.Key_D:
                self.CaseWidget.set_remove(False)
            elif event.key() == QtCore.Qt.Key_S and not self.modifiers==QtCore.Qt.ControlModifier:
                self.CaseWidget.set_int(False)
        event.accept()
    
    def media_finish(self):
        #self.timer.stop()
        self.media.stop()
        self.media.pause()
        
    def menu_bar(self):
        """adds a menu bar"""
        self.basic_actions()
        self.statusBar()
        self.Menu = self.menuBar()
        self.fileMenu = self.Menu.addMenu('&File')
        self.infoMenu=self.Menu.addMenu('&Info')
        self.infoMenu.addAction(self.showinfoAction)
        self.newCaseMenu= self.fileMenu.addMenu('&New...')
        self.newCaseMenu.addAction(self.createCaseAdminAction)
        self.newCaseMenu.addAction(self.createCaseCreatorAction)
        self.plotMenu=self.Menu.addMenu('&Save Figure')
        self.plotMenu.addAction(self.savePlotAction)
        self.plotMenu.addAction(self.chgSavePlotFolderAction)
        self.plotMenu.addAction(self.chgSavePlotTypeAction)
        
    def menu_bar_advanced(self):
        
        self.fileMenu.addAction(self.changesavingfolderAction)
        self.fileMenu.addAction(self.saveAction)
        self.rateSubMenu=self.fileMenu.addMenu('&Rate')
        self.fileMenu.addAction(self.exitAction)
        self.mediaMenu=self.Menu.addMenu('&Media')
        self.mediaMenu.addAction(self.playAction)
        self.mediaMenu.addAction(self.pauseAction)
        self.mediaMenu.addAction(self.stopAction)
        
        self.caseMenu=self.Menu.addMenu('&Cases')
        self.caseMenu.addAction(self.addcaseAction)
        self.caseMenu.addAction(self.nextcaseAction)
        self.caseMenu.addAction(self.prevcaseAction)
        
        self.adminMenu=self.Menu.addMenu('&Admin')
        self.adminMenu.addAction(self.addalgAction)
        self.adminMenu.addAction(self.compareAction)
        self.adminMenu.addAction(self.authorIntAction)
        
        for rate in sorted(self.comboratedict.keys()):
            self.rateSubMenu.addAction(self.rateActions[rate])
        
    
    def NewCaseAdmin(self):
        newadmin=True
        self.releaseKeyboard()
        if self.boolaudio:
            ok = QtGui.QMessageBox.question(self,'Creating a new admin session',"Creating a new admin session,\n do you want to proceed ?", QtGui.QMessageBox.Yes |QtGui.QMessageBox.No, QtGui.QMessageBox.Yes)
            if not ok==QtGui.QMessageBox.Yes:
                newadmin=False
        if newadmin:
            self.clean_old_Widgets()
            self.CaseWidget=CaseAnalyserWidget(self, self.mesPath)
            self.CaseWidget.basic_widgets()
            self.define_actions()
            self.admin_actions_enable()
            self.connections()
            self.connections_admin()
            self.add_to_authors()
        self.grabKeyboard()
    
    def NewCaseCreator(self):
        newcase=True
        self.releaseKeyboard()
        if self.boolaudio:
            ok = QtGui.QMessageBox.question(self,'Creating a new case creator session',"Creating a new case creator session,\n do you want to proceed ?", QtGui.QMessageBox.Yes |QtGui.QMessageBox.No, QtGui.QMessageBox.Yes)
            if not ok==QtGui.QMessageBox.Yes:
                newcase=False
        if newcase:
            self.clean_old_Widgets()
            self.CaseWidget=CaseCreatorWidget(self, self.mesPath)
            self.CaseWidget.basic_widgets()
            self.define_actions()
            self.creator_actions_enable()
            self.connections()
            self.connections_creator()
        self.grabKeyboard()
        
    def savePlot(self):
        if self.CaseWidget:
            self.set_savefig_params()
            self.statusBar().showMessage('Saving plot')
            name=self.savePlotFolder.absolute().as_posix()+str(self.CaseWidget)+'_'+self.CaseWidget.author+'_'+self.CaseWidget.case.get_mIDmic()+'_'+time.strftime('%d-%m-%Y-%H-%M.')+str(self.savePlotType)
            self.SelectAxis.figure.savefig(name)
            print('Plot saved as '+name)
            self.set_textparam_bw()
            self.statusBar().clearMessage()
            os.startfile(pathlib.Path(name).as_uri())
    
    def set_textparam_bw(self, bw=False):
        """set matplotlib text as black if true, as white if False"""
        if not bw:
            textcolor='#f5f5f5'
            axescolor='#f5f5f5'
            axbgcolor='#272822'
            bgcolor='#aaaaaa'
            matplotlib.rcParams['xtick.color']=axescolor
            matplotlib.rcParams['grid.color']=bgcolor
            matplotlib.rcParams['ytick.color']=axescolor
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
        else:
            textcolor='#272822'
            axescolor='#272822'
            axbgcolor='#f5f5f5'
            bgcolor='#f5f5f5'
            matplotlib.rcParams['xtick.color']=axescolor
            matplotlib.rcParams['grid.color']=bgcolor
            matplotlib.rcParams['ytick.color']=axescolor
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
    
    def set_savefig_params(self, dpi=None, facecolor='#ffffff', edgecolor='white', format=None, bbox='standard', pad_inches=0.1, jpeg_quality=100, transparent=True, bw=True):
        if not dpi:
            dpi=self.savePlotdpi
        matplotlib.rcParams['savefig.dpi']=dpi# figure dots per inch
        matplotlib.rcParams['savefig.facecolor']=facecolor# figure facecolor when saving
        matplotlib.rcParams['savefig.edgecolor']=edgecolor# figure edgecolor when saving
        if not format:
            format=self.savePlotType
        matplotlib.rcParams['savefig.format']=format# png, ps, pdf, svg
        matplotlib.rcParams['savefig.bbox']=bbox# 'tight' or 'standard'.
        matplotlib.rcParams['savefig.pad_inches']=pad_inches# Padding to be used when bbox is set to 'tight'
                                # backends but will workd with temporary file based ones:
                                # e.g. setting animation.writer to ffmpeg will not work,
                                # use ffmpeg_file instead
        if self.savePlotType=='jpeg':
            matplotlib.rcParams['savefig.jpeg_quality']=jpeg_quality #when a jpeg is saved, the default quality parameter.
        if self.savePlotType in ['png','PNG'] and transparent:
            matplotlib.rcParams['savefig.transparent']=True
        else:
            matplotlib.rcParams['savefig.transparent']=False# setting that controls whether figures are saved with a
                                # transparent background by default 
        if bw:
            self.set_textparam_bw(True)
    
    def show_author_int(self):
        self.CaseWidget.plot()
        self.CaseWidget.update_canvas()
    
    def show_info(self):
        self.extbrowsercall()
        #self.infoTab=QtGui.QWidget()
        #self.infoLayout=QtGui.QVBoxLayout(self.infoTab)
        #self.info_view = QtWebKit.QWebView()
        #self.info_view.load(QtCore.QUrl('info.html'))
        #self.infoLayout.addWidget(self.info_view)
        #self.TabWidget.addTab(self.infoTab, 'Information')
        
    
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
        self.CaseWidget.update_time(t)

class MainCaseWidget():
    def __init__(self, kgControl,mesPath, Paths=None, setup = False, **kwargs):
        #time to syncronize plot and media object
        self.mesPath = mesPath
        if not Paths:
            self.Paths=[mesPath]
            self.Paths.append(pathlib.Path('E:/ZugVormessung'))
            self.Paths.append(pathlib.Path('E:/Biel1Vormessung'))
        else:
            self.Paths=Paths
        self.kgControl=kgControl
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
        self.kgControl.add_widgets_audio()
        #finish setup
        if setup:
            #Set mediafile
            self.kgControl.set_media_source(**kwargs)
            #add mpl objects
            self.kgControl.set_mpl(**kwargs)
            #set and centralWidget
            self.kgControl.set_centralWidget()
            #add connections
            self.connections()
            
        self.kgControl.setWindowTitle('Create Case')
        if not Paths:
            self.Paths=[mesPath]
            self.Paths.append(pathlib.Path('E:/ZugVormessung'))
            self.Paths.append(pathlib.Path('E:/Biel1Vormessung'))
        else:
            self.Paths=Paths
        # set the author        
        self.mesPath = mesPath
        self.minspan = 0.05
        self.PlotTypes=['LAfast', 'Spectogram']
        self.currentplottype=self.PlotTypes[0]
        self.author=None
        self.both_visibles=True
        #set cases
        self.NoiseTypes = ['Z','KG']
        self.current_noise=self.NoiseTypes[0]
        self.SOI=SetOfIntervals()
    
    def add_author(self, ga):
        pass    
    
    def add_new_cases(self):
        """ask for adding a new case"""
        retour,ok=(QtGui.QFileDialog.getOpenFileNames(self.kgControl, 'Select cases'))
        if ok:
            for file in retour[0]:
                listofpaths.append(pathlib.Path(file))
            if len(listofpaths)>0:
                self.load_cases(listofpaths)
                

    def asks_for_algorithm(self):
        pass
        
    def asks_for_case(self):
        """asks for new case add"""
        listofpaths=[]
        keeponasking=True
        self.kgControl.releaseKeyboard()
        while keeponasking:
            retour=(QtGui.QFileDialog.getOpenFileNames(self.kgControl, 'Select cases'))
            for file in retour[0]:
                listofpaths.append(pathlib.Path(file).absolute())
            ok = QtGui.QMessageBox.question(self.kgControl,'Done ?',"Have you finished selecting the cases ?", QtGui.QMessageBox.Yes |QtGui.QMessageBox.No, QtGui.QMessageBox.Yes)
            if ok==QtGui.QMessageBox.Yes:
                keeponasking=False
        self.load_cases(listofpaths)
        self.kgControl.grabKeyboard()
    
    def _barplay(self, truth):
        """define what to do when audio is playing/not playing"""
        self.barplay=truth
    
    def basic_widgets(self):
        self.set_centralWidget()
        self.kgControl.add_widgets_basic()
        self._basic_widgets()
    
    def _basic_widgets(self):
        pass
    
    def case_down(self):
        """changes case to the next one"""
        index=self.kgControl.CaseCombo.currentIndex()
        if index<len(self.casesKeys)-1:
            self.change_current_case(index+1)
            self.kgControl.CaseCombo.setCurrentIndex(index+1)
        else:
            self.change_current_case(0)
            self.kgControl.CaseCombo.setCurrentIndex(0)
        self._on_case_change()
    
    def case_to_analyse(self, ID, mic, matPath, givenauthor=None):
        """setup the analysed cases from MBBM
        called by load_cases
        """
        # read the signal
        caseDict={}
        mesPath=matPath.parent.parent
        # initiate  MicSignal
        micSn,micval = load_micSn(ID,mic,matPath)
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
        self.add_to_author(caseDict['case']['author'])
        
    def case_up(self):
        """changes case to the previous one"""
        index=self.kgControl.CaseCombo.currentIndex()
        if index==0:
            self.change_current_case(-1)
            self.kgControl.CaseCombo.setCurrentIndex(len(self.casesKeys)-1)   
        else:
            self.change_current_case(index-1)
            self.kgControl.CaseCombo.setCurrentIndex(index-1)
        self._on_case_change()
            
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
    def chg_color_on_save(self):
        pass
    def chg_folder(self):
        pass
    
    def change_current_case(self, index):
        key = self.casesKeys[index]
        #self.currentCase.get('saved',False):
        self.set_current_case(key)
        self.update_canvas()
        # else:
        #     QtGui.QMessageBox.warning(self.kgControl, self.trUtf8("save error"), 
        #      self.trUtf8("Before switching case save it!"))
        
    def changeplot(self):
        index=self.kgControl.plotselect.index(self.currentplottype)
        if index+1==len(self.PlotTypes):
            index=0
        else:
            index+=1
        self.kgControl.plotselect.setCurrentIndex(index)
        self.currentplottype=self.PlotTypes[index]
        
    def change_quality(self):
        pass
        
    def chg_type(self):
        """change the noise type to the next one on the list (and back to the first)"""
        current_noise_index= self.NoiseTypes.index(self.current_noise)
        if current_noise_index <len(self.NoiseTypes)-1:
            self.set_noise_type(current_noise_index+1)
            self.kgControl.SOIcombo.setCurrentIndex(current_noise_index+1)
        else:
            self.set_noise_type(0)
            self.kgControl.SOIcombo.setCurrentIndex(0)
        self.update_canvas()
    
    def chg_typedisplay(self):
        """toggle between show both and show one"""
        self.both_visibles=not self.both_visibles
        self.kgControl.cb.setChecked(self.both_visibles)
        self.update_stay_rect
        self.update_canvas()
    
    def connections(self):
        # connections
        #self.timer.timeout.connect(self.update_canvas)

        self._connections()
        #start refresh
        #self.timer.start()
        
    def _connections(self):
        pass
    def deal_with_missing_key(self):
        return(self.kgControl.ComboCase[0])
    def get_quality(self):
        return(self.currentCase['case'].get('quality',False))
    
    def hide_rect(self):
        """hides the rectangles without touching the SOI"""
        self.update_stay_rect(True)
        self.update_canvas()
    
    def import_cases(self):
        """performs the basic import of cases"""
        with self.mesPath.joinpath('caseToAnalyze.json').open('r+') as input:
            self.casesToAnalyze = json.load(input)
        for k,v in self.casesToAnalyze.items():
            v['case']['author']=self.author
            v['case']= Case(**v['case'])
        self.casesKeys = sorted(list(self.casesToAnalyze.keys()))#list of name of cases
    
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
                mesPath=pathtofile
            if mesPath:
                self.case_to_analyse(ID,mic,mesPath, gauthor)
                self.add_to_authors(gauthor)
            else:
                print("file not found")
        self.casesKeys = sorted(list(self.casesToAnalyze.keys()))#list of name of cases
        
    

    
    def _on_case_change(self):
        """defines actions to do when the cases is changed with case_up or case_down"""
        pass
    def onclick(self,x):
        pass
    
    def onselect(self,xmin,xmax, remove=False):
        pass
    def plot(self):
        self.kgControl.SelectAxis.cla()
        self.case.plot_triggers(self.kgControl.SelectAxis)
        if self.currentplottype=='LAfast':
            self.kgControl.statusBar().showMessage("Computing LAfast")
            ymax=0
            for key, pData in self.currentCase['plotData'].items():
                t,y = pData
                self.kgControl.SelectAxis.plot(t, y , label = key, color='#272822', linewidth=1.)#plot display
                if max(y)>ymax:
                    ymax=max(y)
            tmin = self.currentCase['tmin']
            tmax = self.currentCase['tmax']
            self.kgControl.SelectAxis.set_xlim(tmin,tmax)
            self.kgControl.SelectAxis.set_ylabel('LA dB')
            self.kgControl.SelectAxis.set_xlabel('t (s)')
            self.kgControl.SelectAxis.set_ylim([0,ymax*1.1])
            self.kgControl.SelectAxis.legend()
        elif self.currentplottype=='Spectogram':
            self.kgControl.statusBar().showMessage("Computing STFT. Long process, please wait.")
            if not self.currentCase['case'].get_mIDmic() in self.micSignals.keys():
                micSn=MicSignal.from_wav(self.currentCase['wavPath'])
                if micSn:
                    self.micSignals[self.currentCase['case'].get_mIDmic()]=micSn
                    stftName = micSn.get_stft_name(self.currentAlgorithm)
                else:
                    print("wav file not found")
                    pass
            self.micSignals[self.currentCase['case'].get_mIDmic()].plot_spectrogram(stftName,self.kgControl.SelectAxis)
        for ca in self.canvas:
            ca.draw()
        #update canvas
        self.update_stay_rect()
        self.kgControl.statusBar().clearMessage()
    
    def plotchange(self,index):
        """update the plot"""
        self.currentplottype=self.PlotTypes[index]
        self.plot()
        self.update_canvas()
    def __str__(self):
        return('MainCase')
    def save_case(self):
        pass
    def show_compare(self):
        pass
        
    def set_both_visible(self, state):
        if state == QtCore.Qt.Checked:
            self.both_visibles= True
        else:
            self.both_visibles= False
        self.update_stay_rect()
        self.update_canvas()
        
    def set_centralWidget(self):
        #centralwidget
        centralWidget = QtGui.QWidget()
        centralWidget.setLayout(self.kgControl.vBox)
        self.kgControl.setCentralWidget(centralWidget)
        
    def set_current_case(self,key):
        self.kgControl.releaseKeyboard()
        #self.timer.stop()
        self.kgControl.media.stop()
        try:
            self.currentCase = self.casesToAnalyze[key]
        except:
            key=self.deal_with_missing_key()
            self.currentCase=self.casesToAnalyze[key]
        #attributes
        self.case = self.currentCase['case']
        #update buttons
        self.both_visibles = True
        self.kgControl.cb.setChecked(self.both_visibles)
        self.current_noise = 'Z'
        self.kgControl.SOIcombo.setCurrentIndex(self.NoiseTypes.index(self.current_noise))
        self.chg_color_on_save()#changes the color (function active only if it is redefined)
        #set SOI and update Canvas
        self.set_noise_type('Z')
        #plot
        self.plot()
        #Set mediafile
        wavPath = self.mesPath.joinpath(self.currentCase['wavPath'])
        self.set_media_source(str(wavPath), self.currentCase['tmin'])
        #start timer
        #self.timer.start()
        self.kgControl.grabKeyboard()
        self.set_quality()
    
    def set_media_source(self, wavPath, t0 = 0, **kwargs):
        self.tShift = t0
        self.t = self.tShift
        self.kgControl.media.setCurrentSource(Phonon.MediaSource(wavPath))
        self.kgControl.media.pause()
        
    def set_mpl(self, mpl = {}, **kwargs):
        self.canvas = []
        self.ca_update_handle = []
        self.ca_set_bar_handle = []
        hca=QtGui.QHBoxLayout()
        for k, ca in mpl.items():
            ca['canvas'].setParent(self.kgControl)
            self.canvas.append(ca['canvas'])
            hca.addWidget(ca['canvas'])
            handle = ca['axHandle']
            if not isinstance(handle,list):
                handle = [handle]
            if ca['animate']:
                self.ca_update_handle.extend(handle)
            if ca['bar']:
                self.ca_set_bar_handle.extend(handle)
        self.kgControl.toCleanOnNew.append(hca)
        self.kgControl.vBox.addLayout(hca)
                
    def set_noise_type(self, index):
        if isinstance(index,int):
            self.current_noise = self.NoiseTypes[index]
        else:
            self.current_noise = index
        self.SOI = self.case.get_SOI(self.current_noise)
        self.update_stay_rect()
        
    def set_quality(self):
        for q,rb in zip( ['good','medium','bad'],self.kgControl.Qradios):
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
            
    def setup_cases(self):
        """setup cases from the json list. This is the default automatic import"""
        self.import_cases()#import the cases named in caseToAnalyse.json
        self.ncases=len(self.casesKeys)
        #asking for number of cases to treat
        ncases, ok = QtGui.QInputDialog.getInt(self.kgControl,"Number of cases to analyse", ("Please insert the number of cases \n you would like to analyse.\n \n (You are not forced to do all \n of the proposed cases). \n \n \n Maximum : "+str(self.ncases)+" : "),  value=min(20, self.ncases), min=1, max=self.ncases, step=1)
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
                        
                        
    def show_info(self):
        pass

    
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
            self.kgControl.CaseCombo.setCurrentIndex(0)
            try:
                self.set_current_case(self.casesKeys[0])
            except:
                self.kgControl.CaseCombo.setCurrentIndex(-1)
        else:
            zind=[i for i in range(0,len(self.casesKeys))]
            for ucased in self.casesKeys:
                currentIndex=self.casesKeys.index(ucased)
                self.kgControl.CaseCombo.setItemData(currentIndex,QtGui.QColor('#f5f5f5'),QtCore.Qt.BackgroundRole)
            for scased in sIDs:
                if scased in self.casesKeys:
                    zind.remove(self.casesKeys.index(scased))
                    currentIndex= self.casesKeys.index(scased)
                    self.kgControl.CaseCombo.setItemData(currentIndex,QtGui.QColor('#a6dba0'),QtCore.Qt.BackgroundRole)
                    self.casesToAnalyze[scased]['case'].set_saved(True)
                    pathtofile=self.savefolder.joinpath('test_cases/'+self.author+'/case_'+scased+'_'+self.author+'.json')
                    caseinfile=Case.from_JSON(pathtofile)
                    self.casesToAnalyze[scased]['case'].set_quality(caseinfile.get_quality())
                    for type in self.NoiseTypes:
                        self.casesToAnalyze[scased]['case'].set_SOI(caseinfile.get_SOI(type),type)
            
                
            if len(zind)==0:
                self._zind_zero()
            else:
                zind=min(zind)
                self.kgControl.CaseCombo.setCurrentIndex(zind)
                self.set_current_case(self.casesKeys[zind])
        #self.plot()
        #self.update_canvas()

    def update_canvas(self):
        for handle in self.ca_set_bar_handle:
            handle.set_bar_position(self.t)
        for handle in self.ca_update_handle:
            handle.update()
    
    def update_stay_rect(self, hide=False):
        for index,nT in enumerate(self.NoiseTypes):
            if not hide:
                if nT == self.current_noise:
                    self.CS.set_stay_rects_x_bounds(self.SOI.tolist(),index)
                elif self.both_visibles:
                    self.CS.set_stay_rects_x_bounds(self.case.get_SOI(nT).tolist(), index)
                else:
                    self.CS.set_stay_rect_visible(False, index)
            else:
                self.CS.set_stay_rects_x_bounds([], index)
    
    def update_time(self,t):
        self.t = t/1000 + self.tShift
        self.update_canvas()
    def _zind_zero(self):
        """deals with the case where no Case is availaible"""
        pass
    
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

class CaseAnalyserWidget(MainCaseWidget):
    """
    this is a class designed to compare cases selected by multiple authors and analyse algorithms.
    """
    def __init__(self,kgControl, mesPath, Paths=None):
        super(CaseAnalyserWidget, self).__init__(kgControl, mesPath,Paths)
        self.authors=[]
        self.authors.append('admin')
        #import cases
        #algorithms
        self.algorithmsTypes={'Z2':{'classname':'ZischenDetetkt2','attributes':'Z2_fc_threshold_dt'}}
        #gets number of cases to analyse
        self.asks_for_ncases()
        for dir in os.listdir(mesPath.joinpath('test_cases').as_posix()):
            self.add_to_authors(str(dir))
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
        self.generate_authors()

        self.author=self.authors[0]
        self.casesToAnalyze=self.AuthorCases[self.author]
        #add connections
        self.connections()
        self.micSignals={}
    
    def add_to_authors(self, ga):
        """adds the author ga if it is not already in authors"""
        if ga not in self.authors:
            self.authors.append(ga)
        self.authors.sort()
        self.kgControl.add_to_authors()
    
    def asks_for_algorithm(self):
        """queries the desired algorithms"""
        dialogstring=''
        for alg in self.algorithmsTypes.keys():
            dialogstring+= self.algorithmsTypes[alg]['attributes']
            dialogstring+='\n'
        self.kgControl.releaseKeyboard()
        dialog,ok = QtGui.QInputDialog.getText(self.kgControl, 'Algorithm input', 'Insert an algorithm description in the following form :\n'+dialogstring, QtGui.QLineEdit.Normal, 'Z2_4000_0.706_0.1')
        self.kgControl.grabKeyboard()
        
        try:
            alg,fc,thres,dt=dialog.split('_')
        except:
            print("Could not read your input")
            self.asks_for_algorithm()
        else:
            self.Algorithms[dialog]=(eval(self.algorithmsTypes[alg]['classname']+'('+str(fc)+','+str(thres)+','+str(dt)+')'))
            self.kgControl.ComboAlgorithms.addItem(dialog)
        
    def asks_for_ncases(self):
        result =QtGui.QMessageBox.question(self.kgControl,'Initialization of cases',"Would you like to select the cases yourself?", QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.Yes)
        if result==QtGui.QMessageBox.Yes:
            keeponasking=True
            askforcases=False
        else:
            keeponasking=False
            askforcases=True
        listofpaths=[]
        while keeponasking:
            retour=(QtGui.QFileDialog.getOpenFileNames(self.kgControl, 'Select cases'))
            for file in retour[0]:
                listofpaths.append(pathlib.Path(file).absolute())
            ok = QtGui.QMessageBox.question(self.kgControl,'Done ?',"Have you finished selecting the cases ?", QtGui.QMessageBox.Yes |QtGui.QMessageBox.No, QtGui.QMessageBox.Yes)
            if ok==QtGui.QMessageBox.Yes:
                keeponasking=False
            
        if askforcases or len(listofpaths)==0:
            self.setup_cases()
        elif len(listofpaths)>0:
            listofcase=[]
            self.casesToAnalyze={}
            self.load_cases(listofpaths)
        self.kgControl.grabKeyboard()
    
    def _basic_widgets(self):
        self.kgControl.add_widgets_admin()
        self.load_author(-1)
        ##todo place comboAuthors as Action in the menu and place a label instead.
        self.kgControl.ComboAuthors.setCurrentIndex(-1)
        
    def _connections(self):
        pass
    
    def deal_with_missing_key(self):
        if self.author:
            try:
                self.casesToAnalyze=self.AuthorCases[self.author]
            except:
                self.generate_authors()
                self.casesToAnalyze=self.AuthorCases[self.author]
            return(list(self.casesToAnalyze.keys())[0])
        else:
            try:
                self.author=self.kgControl.ComboAuthors[0]
            except:
                print('No ComboAuthors defined. Problem in deal_with_missing_key function of class CaseAnalyserWidget')
            else:
                self.kgControl.ComboAuthors.setCurrentIndex(0)
                return(self.caseToAnalyze['case'].get_mID())
    
    def generate_authors(self):
        self.AuthorCases={}
        for auth in self.authors:
            if auth=='admin':
                self.AuthorCases['admin']=self.casesToAnalyze
            else:
                self.author=auth
                self.AuthorCases[auth]={}
                try:
                    listofsaved=self.checkSavedCases()
                except:
                    pass
                else:
                    for i in listofsaved:
                        try:
                            self.AuthorCases[auth][i]=copy.deepcopy(self.casesToAnalyze[i])
                        except:
                            pass
    
    def load_algorithm(self, index):
        """loads the algorithm selected"""
        self.currentAlgorithm=self.Algorithms[self.kgControl.ComboAlgorithms.currentText()]
        self.currentplottype=self.PlotTypes[0]
        self.plot()
    
    def load_author(self, index):
        """loads the saved intervals of an author"""
        self.author=self.authors[index]
        self.casesToAnalyze=self.AuthorCases[self.author]
        self.kgControl.CaseCombo.clear()
        self.currentplottype=self.PlotTypes[0]
        self.casesKeys=sorted(list(self.casesToAnalyze.keys()))
        for j in self.casesKeys:
            self.kgControl.CaseCombo.addItem(j)
        self.TurnTheSavedGreen()
        self.chg_type()
        
    def _on_case_change(self):
        self.currentplottype=self.PlotTypes[0]
        self.plot()
        
    def __str__(self):
        return('Analysis')
        
    def show_compare(self):
        """will show or remove the comparison between current author /current case and the current algorithm"""
        if True:
            self.kgControl.statusBar().showMessage("Computing results")
            self.hide_rect()
            if self.currentCase.get('micSn',False):
                MicSnObj=self.currentCase['micSn']
            else:
                ID=self.case.get_mID()
                mic=self.case.get_mic()
                matPath=self.case.get_mat_path(self.Paths)
                if not matPath:
                    print("not matPath found, please connect external Harddrive")
                    return None       
                else:
                    MicSnObj, stftname=load_micSn(ID,mic,matPath, self.currentAlgorithm)
                    self.casesToAnalyze[ID+'_'+str(mic)]['micSn']=MicSnObj
                    self.casesToAnalyze[ID+'_'+str(mic)]['stftName']=stftname
            if MicSnObj:
                MicSnObj.calc_kg(self.currentAlgorithm)
                alg_res = MicSnObj.get_KG_results(self.currentAlgorithm)['result']
                if self.author!='admin':
                    self.case.plot_compare(self.kgControl.SelectAxis, alg_res['result'], alg_res['t'], noiseType = self.currentAlgorithm.noiseType)
                else:
                    MicSnObj.plot_KG(self.currentAlgorithm, self.kgControl.SelectAxis, color = '#984ea3')
                for ca in self.canvas:
                    ca.draw()
            
        else:
            self.plot()
            self.TurnTheSavedGreen()
        self.update_canvas()
        self.kgControl.statusBar().clearMessage()
    
    def _zind_zero(self):
        try:
            i=self.kgControl.CaseCombo.currentIndex()
            firsttime=False
        except:
            firsttime=True
        if firsttime:#initialise CaseCombo only if not admin session or firsttime
            self.kgControl.CaseCombo.setCurrentIndex(-1)
            self.current_noise='Z'
            self.SOI=self.casesToAnalyze[self.casesKeys[0]]['case'].get_SOI()
    
class CaseCreatorWidget(MainCaseWidget):
    '''
    this is a subclass of kgControlWidget
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
    def __init__(self, kgControl, mesPath, Paths=None):
        #init super
        super(CaseCreatorWidget, self).__init__(kgControl,mesPath, Paths)
        # set the author  
        self.infofolder=pathlib.Path("").absolute()
        self.minspan = 0.05
        self.PlotTypes=['LAfast', 'Spectogram']
        self.currentplottype=self.PlotTypes[0]
        self.author=None
        self.both_visibles=True
        #set cases
        self.NoiseTypes = ['Z','KG']
        self.asks_for_info()
        self.asks_for_author()
        self.authors=[self.author]
        #add connections
        self.connections()
        self.micSignals={}
    
    def add_int(self, xmin,xmax):
        self.unsave()
        Int = Interval(xmin,xmax)
        self.SOI.append(Int)
        #print('Add '+ repr(Int))
        self.update_stay_rect()
        if self.barplay==False:
            self.update_canvas()

 
    
    def asks_for_author(self):
        author, ok = QtGui.QInputDialog.getText(self.kgControl, "Set author", "Please your name : ")
        if ok:
            author = author.replace(' ','_')
            if author=="":
                author='anonymus'
        else:
            author =  'anonymus'
        self.author = author
    
    def asks_for_info(self):
        result = QtGui.QMessageBox.question(self.kgControl, 'Information', "Would you like to see the information page ?", QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.No)
        if result==QtGui.QMessageBox.Yes:
            self.kgControl.extbrowsercall()
            QtGui.QMessageBox.information(self, 'Proceeding', "Tell me when you are ready to proceed.")
    
    def asks_for_ncases(self):
        """asks for the number of cases to treat from the case_to_json file
        if in admin session, will ask if you want to select the cases yourself. If so, a prompt will ask you to select them. Then the program will load them and add the path to Paths"""
        self.kgControl.releaseKeyboard()
        self.setup_cases()
        self.kgControl.grabKeyboard()
            
    def _barplay(self, truth):
        """tells what to do if audio is playing or not"""
        self.barplay=truth
        self.CS.setUpdateOnExtEvent(truth) 
        
    def _basic_widgets(self):
        self.kgControl.add_widgets_creator()
        #gets number of cases to analyse
        self.asks_for_ncases()
        QtGui.QMessageBox.warning(self.kgControl, 'Audio system', 'Please use hearphones or a good audio system to analyze the signals.')
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
        self.kgControl.CaseCombo.addItems(self.casesKeys)
        self.TurnTheSavedGreen()#set caseCombo
        
    def change_quality(self, quality):
        if quality in ['good','medium','bad']:
            self.case.set_quality(quality)
            if quality=='good':
                curr=self.kgControl.Qradios[0].isChecked()
                self.kgControl.Qradios[0].setChecked(not curr)
            elif quality=='medium':
                curr=self.kgControl.Qradios[1].isChecked()
                self.kgControl.Qradios[1].setChecked(not curr)
            else:
                curr=self.kgControl.Qradios[2].isChecked()
                self.kgControl.Qradios[2].setChecked(not curr)
    
    def chg_color_on_save(self):
        """changes the color of the button save"""
        if self.case.get_saved():
            self.kgControl.buttonSave.setStyleSheet("background-color: #a6dba0")
        else:
            self.kgControl.buttonSave.setStyleSheet("background-color: #c2a5cf")
        self.check_rb(self.case.get_quality())
    
    def chg_folder(self):
        """change the directory where to save the data"""
        newpathlib=str(QFileDialog.getExistingDirectory(self,"Please select a directory where I can save your data."))
        if newpathlib!="":
            self.savefolder=pathlib.Path(newpathlib)
            #select color of chg saving folder.
            if not self.savefolder:
                self.kgControl.buttonChgSave.setStyleSheet("background-color: #c2a5cf")
            else:
                self.kgControl.buttonChgSave.setStyleSheet("background-color: #a6dba0")
            fm=QtGui.QFontMetrics(self.kgControl.hlab.font())
            self.kgControl.hlab.setText("Selected directory : "+fm.elidedText(str(self.savefolder),QtCore.Qt.ElideLeft, 250))
        else:
            print("Path not modified.")

    def check_rb(self, q):
        self.kgControl.rbG.setExclusive(True)#allows to choose multiple qualities
        for rb, qb in  zip(self.kgControl.Qradios, ['good', 'medium', 'bad']):
            rb.setChecked(q==qb)
        self.kgControl.rbG.setExclusive(True)
    
    def _connections(self):
        """connects the buttons/combobox to the methods to be applied"""
        pass
    
    def onclick(self,x):
        #remove Interval
        self.remove_int(x)
    
    def onselect(self,xmin,xmax, remove=False):
        #add interval1
        if remove:
            self.remove_int(xmin,xmax)
        else:
            self.add_int(xmin,xmax)
        
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
            
    def __str__(self):
        return('Creation')
        
    def save_case(self):
        if self.case.get_quality() == None:
            QtGui.QMessageBox.warning(self.kgControl, self.kgControl.trUtf8("save error"), 
            self.kgControl.trUtf8("Quality of selection has to be set!"))
        else:
            # set the author
            if not self.savefolder:
                #asks for the folder where to save the datas
                self.chg_folder()
            #self.case.case['author'] = self.author
            casepath=self.case.save(self.savefolder)
            self.kgControl.buttonSave.setStyleSheet("background-color: #a6dba0")
            currentIndex= self.casesKeys.index(str(self.kgControl.CaseCombo.currentText()))
            self.kgControl.CaseCombo.setItemData(currentIndex,QtGui.QColor('#a6dba0'),QtCore.Qt.BackgroundRole)
            #self.AnalysedCases.append(self.casesKeys[currentIndex])

    def unsave(self):
        """get back to unsaved status"""
        if self.currentCase['case'].get_saved:
            self.currentCase['case'].give_saved(False)
            self.kgControl.buttonSave.setStyleSheet("background-color: #c2a5cf")
            currentIndex= self.casesKeys.index(str(self.kgControl.CaseCombo.currentText()))
            self.kgControl.CaseCombo.setItemData(currentIndex,QtGui.QColor('#c2a5cf'),QtCore.Qt.BackgroundRole)
     
    def _zind_zero(self):
        if self.sparecase:
            k,v = self.sparecase
            ok=QtGui.QMessageBox.warning(self.kgControl, "All cases were treated!", "You have already reviewed all the cases. \n I have added the case "+k+" to the list.")
            self.casesToAnalyze[k]=v
            self.kgControl.CaseCombo.addItem(self.sparecase[0])
            self.casesKeys.append(self.sparecase[0])
            self.kgControl.CaseCombo.setCurrentIndex(self.casesKeys.index(k))
            self.set_current_case(k)
        else:
            ok=QtGui.QMessageBox.warning(self.kgControl, "All cases were treated!", "You have already reviewed all the cases.")
        try:
            i=self.kgControl.CaseCombo.currentIndex()
            firsttime=False
        except:
            firsttime=True
        if firsttime:#initialise CaseCombo only if not admin session or firsttime
            self.kgControl.CaseCombo.setCurrentIndex(-1)
            self.current_noise='Z'
            self.SOI=self.casesToAnalyze[self.casesKeys[0]]['case'].get_SOI()
    
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

class CompareCaseAlgWidget(kgControlWidget):
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
        
        self.kgControl.vBox.addLayout(hBox)
        # Browser
        #todo: add case Info, add alg Info, add test_on_case results
        self.edit = QtGui.QTextBrowser()
        self.kgControl.vBox.addWidget(self.edit)
        self.currentAlg.calc_rates()
        self.edit.setHtml(md.markdown('###TPR :'+str(self.currentAlg.rates['TPR'])+' FPR : '+str(self.currentAlg.rates['FPR'])+ 'TPR-FPR : '+str(self.currentAlg.rates['TPR']-self.currentAlg.rates['FPR'])))
        #set central widget
        self.set_centralWidget()
        
    def set_current_alg(self,index):
        #self.timer.stop()
        self.kgControl.media.stop()
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
        
def load_micSn(ID,mic,matPath, algorithm=None,gvar = ['Tb','Te','Tp_b','Tp_e','LAEQ'] ):
    """loads micSn from the matPath, returns a signal and a stftName"""
    jsonconfigpath=matPath.parent.parent
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
    