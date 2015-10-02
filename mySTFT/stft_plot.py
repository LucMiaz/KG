'''
short Time Fourier Transform tools
plots:
- plot PSD
- stft Widget
'''
import sys
import matplotlib
from mpl_toolkits.axes_grid.inset_locator import inset_axes
#import brewer2mpl
import seaborn as sns
sns.set(style='ticks', palette='Set2')
sys.path.append('D:\GitHub\myKG')
import mySTFT
from mySTFT.stft import *


def plot_spectrogram(X, param, ax, colorbar = True, title = 'Spectrogram', dB= True, freqscale = 'log', dBMax = None, scaling = 'density', **kwargs):
    # TODO: correct t axis scala
    """
    plot the spectrogram of a STFT
    """
    sR = param['sR']
    # PSD
    PSD, freq, t_i =  stft_PSD(X, param, scaling = scaling, **kwargs)
    
    if dB:
        Z = 10*np.log10(PSD) - 20*np.log10(2e-5)
    else:
        Z = PSD
    # tempo e frequenza per questo plot é ai bordi
    df, __ = frequency_resolution(param['N'],sR)
    tR = param['R']/sR
    t = np.hstack([t_i[0]-tR/2, t_i + tR/2])
    freq = np.hstack([ freq[0]-df/2, freq + df/2])
    X , Y = np.meshgrid(t , freq)
    
    # plotting
    ax.set_title(title, fontsize = 10)
    #cmap = brewer2mpl.get_map('RdPu', 'Sequential', 9).mpl_colormap
    cmap=['#fff7f3','#fde0dd','#fcc5c0', '#fa9fb5', '#f768a1', '#dd3497', '#ae017e','#7a0177', '#49006a']
    cmap=LinearSegmentedColormap('RdPu',cmap)
    if dBMax==None:
        norm = matplotlib.colors.Normalize(vmin = 0)
    else:
        norm = matplotlib.colors.Normalize(vmin = 0, vmax=dBMax)
    # np.round(np.max(ZdB)-60 ,-1), vmax = np.round(np.max(ZdB)+5,-1), clip = False)
    spect = ax.pcolormesh(X, Y, np.transpose(Z), norm=norm, cmap = cmap)
    #legenda
    if colorbar:
        axcolorbar = inset_axes(ax,
                width="2.5%", # width = 10% of parent_bbox width
                height="100%", # height : 50%
                loc=3,
                bbox_to_anchor=(1.01, 0., 1, 1),
                bbox_transform=ax.transAxes,
                borderpad=0,
                )
        axcolorbar.tick_params(axis='both', which='both', labelsize=8)
        ax.figure.colorbar(spect, cax = axcolorbar)
    #
    if freqscale =='log':
        ax.set_yscale('log')
    else:
        ax.set_yscale('linear')
    ax.xaxis.set_minor_locator(matplotlib.ticker.AutoMinorLocator())
    ax.grid(which= 'both' ,ls="-", linewidth=0.4, color=cmap(0), alpha=0.8)
    ax.set_xlim(t.min(),t.max())
    ax.set_ylim(freq.min(),freq.max())
    if not colorbar:
        return(spect)


def plot_PDD_i(X, param, i , ax, orientation = 'horizontal', dB = True, \
                freqscale = 'log', scaling = 'density',**kwargs):
    """
    plot the spectrogram of a STFT
    """
    # PSD
    PSD, freq, t_i =  stft_PSD(X, param, scaling = scaling,**kwargs)
    PSD_i = PSD[i,:]

    if dB:
        Y = 10*np.log10(PSD_i) - 20*np.log10(2e-5)
    else:
        Y = PSD_i
    # plotting
    if orientation =='horizontal':
        ax.plot(freq,Y)
        if freqscale =='log':
            ax.set_xscale('log')
        else:
            ax.set_xscale('linear')
        ax.xaxis.set_minor_locator(matplotlib.ticker.AutoMinorLocator())
    else:
        ax.plot(Y,freq)
        if freqscale =='log':
            ax.set_yscale('log')
        else:
            ax.set_yscale('linear')
        for tl in ax.xaxis.get_ticklabels():
            tl.set_rotation(90)
            tl.set_fontsize(8)
    ax.grid(True)
    
def plot_PDD_k(X, param, k, ax, dB = True, scaling = 'density', **kwargs):
    """
    plot the spectrogram of a STFT
    """
    # PSD
    PSD, freq, t_i =  stft_PSD(X, param, scaling = scaling, **kwargs )
    PSD_k = PSD[:,k]

    if dB:
        Y = 10*np.log10(PSD_k) - 20*np.log10(2e-5)
    else:
        Y = PSD_k
    ax.xaxis.set_minor_locator(matplotlib.ticker.AutoMinorLocator())
    ax.plot(t_i,Y)
    ax.grid(True)

##
from matplotlib.figure import Figure
matplotlib.use('Qt4Agg')
matplotlib.rcParams['backend.qt4']='PySide'
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
from PySide import QtGui, QtCore
                                       
class stftWidget(QtGui.QMainWindow):

    def __init__(self, signal, M, parent = None):
        QtGui.QMainWindow.__init__(self, parent)
        self.setWindowTitle('STFT visualizer')
        # STFT 
        # signal        
        self.signal = signal
        self.lenSn = len(signal['y'])
        # parameter STFT
        self.M = M
        self.N = self.M
        self.overlap = 2
        self.R = self.M/ self.overlap
        self.window = 'hann'
        self.invertible = True
        self.df = self.signal['sR']/self.N
        self.dt = self.R/self.signal['sR']
        # parmeter plot
        self.i = 0 #parameter X[i,:]
        self.k = 0 #parameter X[:,k]
        self.freqscale = 'log'
        self.dB = True
        #stft results
        self.X, self.freq, self.f_i, self.param = None,None,None,None
        
        #gui
        self.main_frame = QtGui.QWidget()
        
        # Create the mpl Figure and FigCanvas objects. 
        self.fig = Figure(figsize = (12,8), dpi= 100)
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setParent(self.main_frame)
        
        gs1 = matplotlib.gridspec.GridSpec(4, 6)
        gs1.update( top = 0.95,bottom = 0.12, wspace=0.1,hspace=0.1)
        
        #spectrum
        self.ax1 = self.fig.add_subplot(gs1[:-1, 0])
        self.ax1.invert_xaxis()
        #sectogram
        self.ax2 = self.fig.add_subplot(gs1[:-1, 1:])
        self.vline = self.ax2.axvline(color = 'b',linewidth = 1,alpha = 1)
        self.hline = self.ax2.axhline(color = 'b',linewidth = 1,alpha = 1)
        #time
        self.ax3 = self.fig.add_subplot(gs1[-1 , 1:],sharex = self.ax2)
        self.fig.subplots_adjust(hspace=0.1, wspace=0.1) 
        #colorbar
        self.axcolorbar = inset_axes(self.ax2,
                width="2.5%", # width = 10% of parent_bbox width
                height="100%", # height : 50%
                loc=3,
                bbox_to_anchor=(1.01, 0., 1, 1),
                bbox_transform=self.ax2.transAxes,
                borderpad=0,
                )

        # Create the navigation toolbar, tied to the canvas
        self.mpl_toolbar = NavigationToolbar(self.canvas, self.main_frame)
        
        #set STFT parm
        groupBoxSTFT = QtGui.QGroupBox("STFT parameters")
        # M
        labelM = QtGui.QLabel('M:')
        self.tboxM = QtGui.QLineEdit()
        self.tboxM.setMinimumWidth(10)
        self.tboxM.editingFinished.connect(self.set_M)
        # R
        labelR = QtGui.QLabel('R:')
        self.tboxR = QtGui.QLineEdit()
        self.tboxR.setMinimumWidth(10)
        self.tboxR.editingFinished.connect(self.set_overlap)
        # N
        labelN = QtGui.QLabel('N:')
        self.tboxN = QtGui.QLineEdit()
        self.tboxN.setMinimumWidth(10)
        self.tboxN.editingFinished.connect(self.set_N)
        # overlap
        labeloverlap = QtGui.QLabel('overlap:')
        self.tboxoverlap = QtGui.QLineEdit()
        self.tboxoverlap.setMinimumWidth(5)
        self.tboxoverlap.editingFinished.connect(self.set_R)
        # COLA normalization checkbox
        self.inverse_cb = QtGui.QCheckBox("COLA normalization")
        self.inverse_cb.setChecked(self.invertible)
        #self.inverse_cb.stateChanged.connect(self.calcSTFT)
        #select window combobox
        labelCombo = QtGui.QLabel('''Select window:''')
        self.combo = QtGui.QComboBox(self)
        for window  in ['hann','triang', 'flattop', 'hamming']:
            self.combo.addItem(window)
        #self.combo.currentIndexChanged.connect(self.calcSTFT)
        #calculate button
        calcB = QtGui.QPushButton("calculate")
        calcB.clicked.connect(self.calcSTFT)
            
        #set plot param
        groupBoxPlot = QtGui.QGroupBox("Plotting parameters")
        # dB Checkbox 
        self.dB_cb = QtGui.QCheckBox("dB")
        self.dB_cb.setChecked(True)
        self.dB_cb.stateChanged.connect(self.set_dB)
        # yScales Checkbox 
        self.freqscales_cb = QtGui.QCheckBox("freqency scale linear")
        self.freqscales_cb.setChecked(False)
        self.freqscales_cb.stateChanged.connect(self.set_freqscale)
        # i
        labeli = QtGui.QLabel('time:')
        self.tboxi = QtGui.QLineEdit()
        self.tboxi.setMinimumWidth(5)
        #self.tboxi.editingFinished.connect(self._plot)
        # k
        labelk = QtGui.QLabel('frequency:')
        self.tboxk = QtGui.QLineEdit()
        self.tboxk.setMinimumWidth(5)
        #self.tboxk.editingFinished.connect(self._plot)
        #plot button
        plotB = QtGui.QPushButton("plot")
        plotB.clicked.connect(self._plot)
    
        # output label
        labelOutput = QtGui.QLabel('parameters:')
        self.tboxOutput = QtGui.QLineEdit()
        self.tboxOutput.setMinimumWidth(100)
        
        # Layout with box sizers
        hbox1 = QtGui.QHBoxLayout()
        for w in [self.dB_cb, self.freqscales_cb, labelk, self.tboxk, labeli,\
                  self.tboxi, plotB]:
             hbox1.addWidget(w)
        hbox1.addStretch(1)
        groupBoxPlot.setLayout(hbox1)
        
        hbox2 = QtGui.QHBoxLayout()
        for w in [labelM, self.tboxM,labelN, self.tboxN,labelR, self.tboxR,\
                   labeloverlap, self.tboxoverlap,labelCombo, self.combo, 
                   self.inverse_cb,calcB]:
             hbox2.addWidget(w)
        hbox2.addStretch(1)
        groupBoxSTFT.setLayout(hbox2)
        
        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(groupBoxSTFT)
        vbox.addWidget(groupBoxPlot)
        vbox.addWidget(self.canvas)
        vbox.addWidget(self.mpl_toolbar)
        vbox.addWidget(self.tboxOutput)
        
        #set main frame 
        self.main_frame.setLayout(vbox)
        self.setCentralWidget(self.main_frame)
        self.calcSTFT()
        self._plot()

    def set_R(self):
        try:
            self.overlap = float(self.tboxoverlap.text())
            self.R = int(self.M / self.overlap)
        except ValueError:
            print('overlap shoud be number')
        self.tboxR.setText(str(self.R))
    
    def set_overlap(self):
        try:
            self.R = int(self.tboxR.text())
        except ValueError:
            print('R should be integer ')
        self.overlap = np.round(self.M / self.R,1)
        self.tboxoverlap.setText(str(self.overlap))
            
    def set_M(self):
        try:
            self.M = int(self.tboxM.text())
        except ValueError:
            print('M should be integer  ')
            
    def set_N(self):
        try:
            self.N = int(self.tboxN.text())
        except ValueError:
            print('N int ')
    
    def set_freqscale(self):
        # set plot param
        self.freqscale = 'linear'  if self.freqscales_cb.isChecked() else 'log'
        self.replot = True
        
    def set_dB(self):
        self.replot = True
    
    def set_stft_param(self):
        # set output
        iter = zip([self.tboxM, self.tboxN, self.tboxR, self.tboxoverlap],\
                   ['M','N','R','overlap'])
        for lineE, par in iter:
            lineE.setText(str(self.param[par]))
        self.tboxOutput.setText('dt (M): ' + str(self.dt) +'\n df: ' + str(self.df))
    
    def set_ik(self):
        try:
            i = np.round(int(self.tboxi.text())/self.dt)
            k = np.round(int(self.tboxk.text())/self.df)
        except ValueError:
            i=0
            k=1
        self.i = i if i in range(0,len(self.f_i)) else 0 
        self.k = k if k in range(1,int(self.N/2)) else 1
        
        
    def calcSTFT(self):
        #read parameters
        self.invertible = self.inverse_cb.isChecked()
        self.window = self.combo.currentText()
        # calc STFT
        self.X, self.freq, self.f_i, self.param = stft( x = self.signal['y'], M = self.M, N = self.N,\
                                    R = self.R, window = self.window,\
                                    sR = self.signal['sR'], invertible = self.invertible)
        self.dt = self.R / self.signal['sR']
        self.df = self.signal['sR']/self.N
        #calc spectrum 
        self.spectrum, _ = stft_spectrum(self.X, self.param)
        self.spectrum = (abs(self.spectrum)**2)[1:self.N//2]
        self.prms, self.t_i = stft_prms(self.X, self.param)
        #set param
        self.set_stft_param()
        #replot needed
        self.replot = True
        
    def _set_limits_tick_labels(self):
        # share axis limits
        self.ax1.set_ybound(self.ax2.get_ybound())
        self.ax3.set_xbound(self.ax2.get_xbound())
        
        #set tick and ticklabels
        for tl in self.ax2.get_xticklabels():
             tl.set_visible(False)
        for tl in self.ax2.get_yticklabels():
             tl.set_visible(False)
             
        self.ax3.yaxis.tick_right()
        for tl in self.ax3.yaxis.get_ticklabels():
            tl.set_fontsize(8)
            
        for tl in  self.axcolorbar.yaxis.get_ticklabels():
            tl.set_fontsize(8)
            
        #labels
        self.ax1.set_ylabel('frequency Hz')
        self.ax3.set_xlabel('time s')
        
    def _plot(self):
        self.dB = self.dB_cb.isChecked()
        self.set_ik()
        
        #ax1 plot spectrum
        self.ax1.cla()
        if self.dB:
            spectrum = 10*np.log10(self.spectrum) - 20*np.log10(2e-5)
            self.ax1.plot(spectrum, self.freq[1:self.N//2], label='total', color = 'r')        
        else:
            self.ax1.plot(self.spectrum, self.freq[1:self.N//2], label='total', color = 'r')
        #frame i
        plot_PDD_i(self.X, self.param, self.i, self.ax1, orientation='vert', \
        dB = self.dB, freqscale = self.freqscale )
                    
        #ax3 plot time
        self.ax3.cla()
        if self.dB:
            prms = 10*np.log10(self.prms) - 20*np.log10(2e-5)
            self.ax3.plot(self.t_i, prms, label='prms', color = 'red')
        else:
            self.ax3.plot(self.prms, prms, label='prms', color = 'red')
        #frame k    
        self.ax3.plot(self.t_i, prms, label='prms', color = 'red')
        plot_PDD_k(self.X, self.param, self.k,\
                    self.ax3, dB = self.dB)
        
        #ax2: plot spectrogram
        if True:#self.replot:
            spect = plot_spectrogram(self.X,self.param, self.ax2,\
                                    colorbar = False, \
                                    dB = self.dB,title='', 
                                    freqscale = self.freqscale )
            self.ax2.figure.colorbar(spect, cax = self.axcolorbar)
            self.replot = False
                    
        #plot i,k lines
        self.vline.set_xdata(self.i*self.dt)
        self.hline.set_ydata(self.k*self.df)
        self.tboxi.setText(str(int(self.i*self.dt)))
        self.tboxk.setText(str(int(self.k*self.df)))
        
        #limits 
        self._set_limits_tick_labels()
        
        #draw canvas
        self.canvas.draw()
