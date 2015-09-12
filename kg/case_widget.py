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

    ACTIONS = [
        ('play', 'Play', QStyle.SP_MediaPlay),
        ('pause', 'Pause', QStyle.SP_MediaPause),
        ('stop', 'Stop', QStyle.SP_MediaStop)]

    def __init__(self, canvas, signal,dsp=None, parent=None):
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
        self.df = DataFrameWidget(pd.DataFrame([1,2,3]))#dsp.SignalInfo)
        self.label = QtGui.QLabel()
        self.label.setWindowTitle('Results / Informations')
        self.label.setScaledContents(1)
        self.label.setMargin(20)
        vBox2.addWidget(self.label)
        vBox2.addWidget(self.df)
        self.InfoWidget.setLayout(vBox2)
        
        # whenever the playback state changes, show a message to the user
        #self.media.stateChanged.connect(self._show_state_message)
        self.combo.currentIndexChanged.connect(self._set_channel)
        self.buttonLim.clicked.connect(self._sharex_input)
        self.buttonR.clicked.connect(self._results)
        self.media.tick.connect(self._update)
        #setup
        self._set_channel(0)
        
    def _set_channel(self, i):
        self.stack.setCurrentIndex(i)
        self.currentCh = self.channels[i]
        filename = self.signal.export_to_Wav(self.currentCh).as_posix()
        self.media.setCurrentSource(Phonon.MediaSource(filename))
        self.tShift = self.signal.channel_info(self.currentCh)['tmin']
        print(self.tShift)

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
        
    ##
def onselect(xmin, xmax):
    print(xmin,xmax)

if __name__ == "__main__":
    import sys
    import os
    import pandas as pd
    import numpy as np
    sys.path.append('D:\GitHub\myKG')
    from kg.measurement_values import *
    from kg.time_signal import *
    # from kg.dsp import DSP
    from kg.grafics import BarCanvas
    # from kg.audio_visual_app import PlaybackWindow
    from PySide import QtGui,QtCore
    from pandas.sandbox.qtpandas import DataFrameModel, DataFrameWidget
    #perche 'm1020'noné compreso (tilo), 'm_0119' chefrastuono
    import pathlib
    import matplotlib.pyplot as plt
    from matplotlib.widgets import SpanSelector
##    
    timeSignal.setup('D:\GitHub\myKG\Measurements_example\MBBMZugExample')
    mesValues = measuredValues('D:\GitHub\myKG\Measurements_example\MBBMZugExample')
    mesValues.list_variables()
    mesValues.read_variables_values()
    ##
    ID = 'm_0119'
    ts = timeSignal(ID)
    mic=[1,2,4,5,6,7]
    for i,m in enumerate(mic):
        ts.read_signal(m)
        ts.export_to_Wav(m)
    canvas = BarCanvas()


    # set useblit True on gtkagg for enhanced performance
    span = SpanSelector(canvas.axes[0], onselect, 'horizontal', useblit=True,
                        rectprops=dict(alpha=0.5, facecolor='red') )
                        
    ts.plot_channel(1,canvas.axes[0])
    canvas.set_initial_figure()
    W = PlaybackWindow({1:canvas},ts)
    W.show()