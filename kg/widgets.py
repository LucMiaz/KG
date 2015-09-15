import sys
import os
import time
import numpy as np
from PySide import QtGui, QtCore
import sys
from PySide.phonon import Phonon
from PySide.QtGui import (QApplication, QMainWindow, QAction, QStyle,
                          QFileDialog)
from pandas.sandbox.qtpandas import DataFrameModel, DataFrameWidget
                          
class PlaybackWindow(QMainWindow):

    # gui messages for different playback states
    STATE_MESSAGES = {
        Phonon.LoadingState: 'Loading {filename}',
        Phonon.ErrorState: 'Error occured: {error}',
        Phonon.PausedState: 'Paused {filename}',
        Phonon.PlayingState: 'Playing {filename}',
        Phonon.StoppedState: 'Stopped {filename}',
        Phonon.BufferingState: 'Buffering'}

    ACTIONS = [
        ('play', 'Play', QStyle.SP_MediaPlay),
        ('pause', 'Pause', QStyle.SP_MediaPause),
        ('stop', 'Stop', QStyle.SP_MediaStop)]

    def __init__(self, canvas, signal, dsp , parent=None):
        QMainWindow.__init__(self, parent)
        self.setWindowTitle('V1')
        #Phonon
        # the media object controls the playback
        self.media = Phonon.MediaObject(self)
        self.audio_output = Phonon.AudioOutput(Phonon.MusicCategory, self)
        self.seeker = Phonon.SeekSlider(self)
        self.seeker.setMediaObject(self.media)
        self.media.setTickInterval(50)
        
        # audio data from the media object goes to the audio output object
        Phonon.createPath(self.media, self.audio_output)
        # set up actions to control the playback
        self.actions = self.addToolBar('Actions')
        for name, label, icon_name in self.ACTIONS:
            icon = self.style().standardIcon(icon_name)
            action = QtGui.QAction(icon, label, self)
            action.setObjectName(name)
            self.actions.addAction(action)
            action.triggered.connect(getattr(self.media, name))
        #Attributes
        #Channels
        self.signal= signal
        self.canvas = canvas
        self.channels = list(self.canvas.keys())
        self.currentCh = None
        self.tShift = None
        #combobox
        hBox = QtGui.QHBoxLayout()
        label = QtGui.QLabel('''Select channel to play, first widget''')
        self.buttonLim = QtGui.QPushButton("x limits",self)
        self.buttonR = QtGui.QPushButton("Results",self)
        self.combo = QtGui.QComboBox(self)
        hBox.addWidget(label)
        hBox.addWidget(self.combo)
        hBox.addWidget(self.buttonLim)
        hBox.addWidget(self.buttonR)
        hBox.addStretch(1)
        
        #stack Widget
        
        self.stack = QtGui.QStackedWidget()
        for k, ca  in self.canvas.items():
            self.combo.addItem('channel ' + str(k))
            ca.setParent(self)
            self.stack.addWidget(ca) 
        
        #layout
        self.vBox = QtGui.QVBoxLayout()
        self.vBox.addWidget(self.seeker)
        self.vBox.addLayout(hBox)
        self.vBox.addWidget(self.stack)
        for k, ca  in self.canvas.items():
            pass
            #self.vBox.addWidget(ca)
        #self.vBox.addSpacing(20)
        
        centralWidget = QtGui.QWidget()
        centralWidget.setLayout(self.vBox)
        self.setCentralWidget(centralWidget)
        # Info
        self.InfoWidget = QtGui.QWidget()
        vBox2 = QtGui.QVBoxLayout()
        self.df = DataFrameWidget(dsp.SignalInfo)
        self.label = QtGui.QLabel()
        self.label.setWindowTitle('Results / Informations')
        self.label.setScaledContents(1)
        self.label.setMargin(20)
        vBox2.addWidget(self.label)
        vBox2.addWidget(self.df)
        self.InfoWidget.setLayout(vBox2)
        
        #Dock
        #label
        # self.dock = QtGui.QDockWidget("Results", self)
        # self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, self.dock)
        # self.dock.setWidget(self.label)
        
        # whenever the playback state changes, show a message to the user
        self.media.stateChanged.connect(self._show_state_message)
        self.combo.currentIndexChanged.connect(self._set_channel)
        self.buttonLim.clicked.connect(self._sharex_input)
        self.buttonR.clicked.connect(self._results)
        self.media.tick.connect(self._update)
        
        #setup
        self._set_channel(0)

        
    def _set_channel(self, i):
        self.stack.setCurrentIndex(i)
        self.currentCh = self.channels[i]
        filename = self.signal.export_to_Wav(self.currentCh)
        self.media.setCurrentSource(Phonon.MediaSource(filename))
        self.tShift = self.signal.channel_info(self.currentCh)['tmin']

    
    def _sharex(self,xmin=None,xmax=None):
        for k,ca in self.canvas.items():
            ca.set_xbounds( xmin , xmax)
            
    def _sharex_input(self):
        x_limits = self.canvas[self.currentCh].x_limits
        text1 =  ';'.join(map(str, np.round(x_limits,2)))
        # get values from dialog
        text, ok = QtGui.QInputDialog.getText(self, 'axes limits',
            'xmin; xmax',QtGui.QLineEdit.Normal,text1)
        if ok:
            if text1 == text:
                self._sharex()
            else:
                try:
                    xmin,xmax =tuple([float(x) for x in text.split(';')])
                except ValueError as e:
                    print('expected xmin and xmax separated by ;')
                    raise(e)
                else:
                    self._sharex(xmin,xmax)
        
    def _update(self,t):
        #t=self.media.currentTime()
        self.canvas[self.currentCh].update_P(t/1000 + self.tShift )
    def _results(self):
        #msgBox = QtGui.QMessageBox()
        #msgBox.setText("The document has been modified.")
        #msgBox.exec_()
        self.label.setText(
        '''
        Questo é un text label.         \n
        Verrano date le informazione sull algoritmo.\n
        Version 1.1
        ''')
        self.InfoWidget.show()

        
        
    def _show_state_message(self, new_state):
        # get the message for the given state and format it
        message = self.STATE_MESSAGES[new_state].format(
            filename=self.media.currentSource().fileName(),
            error=self.media.errorString())
        self.statusBar().showMessage(message)
        # set the file path in the window title bar, if the playback source
        # is a local file
        source = self.media.currentSource()
        filepath = 'No File'
        if source.type() == Phonon.MediaSource.LocalFile:
            filepath = source.fileName()
        self.setWindowFilePath(filepath)

