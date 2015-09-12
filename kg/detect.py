import sys
import numpy as np
import scipy as sp
from PySide import QtGui, QtCore
import string
import pandas as pd
import wave
from scipy.io import wavfile
from scipy.fftpack import fft,fftfreq, ifft
from scipy.signal import hamming, hanning, hann,lfilter, filtfilt, decimate
import matplotlib as mpl
import brewer2mpl
from mpl_toolkits.axes_grid.inset_locator import inset_axes
import struct

sys.path.append('D:\GitHub\myKG')
import mySTFT


from pandas.sandbox.qtpandas import DataFrameModel, DataFrameWidget

# todo: phase spectrum
# todo: kg, squeal algorithm
# todo: spectrum spectrum plot

class Detect():
    
    """
    Audio file and the relation for amplitude pressure DV
    
    data attributes:
    - WavData: dict of np arrays containing the time signal
    - Calc: dict of calulated quantity
    - KG: results quantity about Kurvengeräusche  

    methods:
     - 
     - bandpassfilter
     - STFT
     - ISTFT
     - Autocorrelation
     - total time
     - output of time in which condition is present
     - SPL
     - total spectra
     - save as wav
     
    init parameter:
    - filepath, file has to be a 1 channel .wav audio file.
    - filename, string
    
    """    
    def __init__(self, columns = None):
        #dict with all the signals of a given passby to be evaluated
        self.signals = {}
        #dict with all the signals of a given passby to be evaluated
        self.currentSn = 0       
        columns = ['mic', 'tb','te','t1b','t1e','LAEQ', 'besch']
        self.SignalInfo = pd.DataFrame(columns= columns)
        #dict with all calculated stft
        self.STFT = {}
        self.PS = {}
        self.L = {}
        self.KG = {}

     def load_mic_signal(self, signal,ID, vars):
        """
        add a mic signal and its informations
        """
        if not ID in self.signals.keys():
            self.signals[ID]= signal
            try:
                row = [vars[i] for i in self.SignalInfo.columns]
            except KeyError:
                print('vars must contain following variables' + \
                ', '.join(self.SignalInfo.columns))
            #SignalInfo.channel = SignalInfo.channel.astype(int)
            #SignalInfo.mic = self.SignalInfo.mic.astype(int)
            self.SignalInfo.loc[ID] = row
            
    def set_process_mic(self, signalID = None ):
        """
        set signal for the following process
        """
        if signalID == None:
           self.currentSn , ok = QtGui.QInputDialog.getItem( None, 
                                'Select data to process','Data to Process:',
                                 self.SignalInfo.index, 
                                 editable = False 
                                )
        elif signalID in self.signals.keys():
            self.currentSn = signalID
            #print('Signal to processing: '+ str(self.currentSn ))
        else:
            raise(ValueError)
  
    def get_KG_algorithm(self):
        calc_id, algorithmDescription,variableInfo = (1,1,1)
        return(calc_id, algorithmDescription,variableInfo)
        
    def get_KG_results(self):
        '''
        stored values in self.KG
        are returned
        '''
        mic = []
        tpassBy = []
        tsqueal = []
        for id,v in self.KG.items():
            mic.append(self.SignalInfo[id]['mic'])
            tpassBy.append(v['tpassBy'])
            tsqueal.append(v['tsqueal'])
        return({'mic':mic,'tpassBy':tpassBy,'tsqueal':tsqueal })
        
    def calc_stft(self, M , N = None, ola = 2, window = 'hann'):
        signal = self.signals[self.currentSn]
        name = str(M) +'_'+ str(N) +'_'+ str(R)
        X, freq, frame_i, param = mySTFT.stft.stft(signal['y'], M = M, N = N, \
                                                   R = self.R, ola = ola,\
                                                   sR = signal['sR'],\
                                                   window = window,
                                                   invertible = False)
        STFT = {'name': name ,
                'frame_i': frame_i,# centre sample i
                'f': freq,
                'X_i': X, # complex FFT
                'param': param
                }
        try:
            self.STFT[self.currentSn][name] = STFT
        except KeyError:
            self.STFT[self.currentSn] = {name:STFT}
        
    def calc_spectrum_welch(name, tbe = None):
        stft = self.STFT[self.currentSn][name]
        #set interval to evaluate spectrum
        if tb==None:
            tmin,tmax = tbe
        else:
            tmin = self.SignalInfo.ix[self.currentSn]['t1b']
            tmax = self.SignalInfo.ix[self.currentSn]['t1e']
        stft['param']['R']
        kwargs = {
        't0' = 
        'tmin': self.SignalInfo.ix[self.currentSn]['t1b'],
        'tmax': self.SignalInfo.ix[self.currentSn]['t1e'],
        }
        mask = signal['t']
        sectrum ,freq = stft_welch(stft['X_i'], stft['param'],'density', **kwargs):
            
    def calc_SPL(self):
       
        #fill L dict
        self.L[self.currentSn] = { 
        'Leq':Leq,
        'LeqMBBM':snI['LAEQ'],
        'TEL':TEL,
        'LF':{'sR':Fr,'t': sn['t'][0] + tF , 'y':LF},
        'LF2':{'sR':Fr,'t': sn['t'] , 'y':LF2} 
        }
        
    def plot_spectrogram(self, signal, stftName = None, ax, freqscale = 'log', dBMax = 110  ):
        """
        
        """
        #todo
        # datenvorbereitung
        try:
            stft = self.STFT[signal]
        except KeyError:
            print("STFT list has no element " +str(stftNumber))
        if stftName == None:
            stftName == stft.keys()[0]
        stft = stft[stftName]
        kwargs = {
        'fmin': 200,
        'fmax' :10000,
        't0':0
        }
        
        fmax = 10000
        vMax = 110
        plot_spectrogram(stft['X'], stft['param'], ax, dBMax=dBMax, **kwargs )


        
    def plot_PS(self, signal, ax):
        """
        plot power spectra from FFT
        TODO
        """
        #todo
        pass
        
        
    def plot_KG(self, mic, method , ax, type = 'flanging', color='red'):
        """
        TODO label,colors
        mic
        method
        type in ['squeal', 'flanging']
        """
        #todo
        types = {'squeal':'sSqueal', 'flanging':'sFlanging'}
        try:
            KG_mic = self.KG[mic]
        except KeyError as e:
            print('No mic')
            raise(e)
        else:
            try:
                KG = KG_mic[method]
            except KeyError as e:
                print('No method')
                raise(e)
            else:
                try:
                    KG_sn = KG[types[type]]
                    t = KG_sn['t']
                    y = KG_sn['y']
                except (KeyError, ValueError) as e:
                    print('no type')
                    raise(e)
                else:
                    ymin, ymax = ax.get_ylim()
                    ax.fill_between(t, y1 = 130, y2 = 0 , where= y, alpha=0.3, color=color)
                    ax.set_ybound(ymin, ymax)


        
    # def calc_kg1(self, delta = 4,lowcut=4000, highcut=9000):
    #     DT = DSP.DT
    #     micId= self.SignalInfo[self.SignalInfo['type']=='mic'].index.tolist()
    #     # for all signal that are microphpone
    #     for SN in micId:
    #         self.set_process_signal(SN)
    #         self.calc_SPL(A = False, integration_time = DT)
    #         self.calc_STFT()
    #         # signal filtern 
    #         newSn = self.bp_filter(lowcut,highcut)
    #         self.set_process_signal(newSn)
    #         self.calc_SPL(A=False, integration_time = DT)
    #         self.calc_STFT()
    #         # calculate kg 
    #         kg = self.L[SN]['LF2']['y'] - self.L[newSn]['LF2']['y']
    #         # downsampling
    #         R = 32 
    #         t = self.L[SN]['LF2']['t'][:np.floor(len(kg)/R)*R].reshape(-1, R).mean(axis=1)
    #         kg = kg[:np.floor(len(kg)/R)*R].reshape(-1, R).mean(axis=1)
    #         newFr = int(self.L[SN]['LF2']['sR']/R)
    #         #smooth kg 
    #         av_len = int(DT*newFr)
    #         kg = sp.signal.convolve(kg, np.ones(av_len)/av_len, 'same')
    #         kg = (kg.round() <= delta)
    #         # calc kenngrössen 
    #         tpassby = self.SignalInfo.ix[SN]['t1e']-self.SignalInfo.ix[SN]['t1b']
    #         tsqueal = np.sum(kg) / self.L[newSn]['LF2']['sR']
    #         #
    #         self.KG[mic].append({
    #         'method': '1',
    #         'signal': {'samplingRate': newFr, 
    #         't': t,
    #         'y':kg},
    #         'tpassBy':tpassby,
    #         'tsqueal':tsqueal,
    #         'mic':SN,
    #         'snf':newSn
    #         })
    
  
    def calc_kg2(self, DT, delta = 5, highcut=2000):
        method = 'method2'
        micId = self.SignalInfo[self.SignalInfo['type']=='mic'].index.tolist()
        # for all signal that are microphpone
        for SN in micId:
            # SN signal corresponding mic
            mic = self.SignalInfo.ix[SN]['channel']
            self.set_process_signal(SN)
            self.calc_SPL(A = False, integration_time = DT)
            self.calc_STFT()
            
            # signal filtern 
            newSn = self.tp_filter(highcut)
            self.set_process_signal(newSn)
            self.calc_SPL(A=False, integration_time = DT)
            
            # calculate kg 
            flanging = self.L[SN]['LF2']['y'] - self.L[newSn]['LF2']['y']
            # downsampling
            R = 32 
            t = self.L[SN]['LF2']['t'][:np.floor(len(flanging)/R)*R].reshape(-1, R).mean(axis=1)
            flanging = flanging[:np.floor(len(flanging)/R)*R].reshape(-1, R).mean(axis=1)
            newFr = int(self.L[SN]['LF2']['sR']/R)
            
            #smooth kg 
            av_len = int(DT*newFr)
            flanging = sp.signal.convolve(flanging, np.ones(av_len)/av_len, 'same')
            flanging = (flanging.round() >= delta)
            # calc kenngrössen
            tb = self.SignalInfo.ix[SN]['t1b']
            te = self.SignalInfo.ix[SN]['t1e']
            mask = np.all([(t >= tb), (t >= te)], axis=0)
            tPassby = np.sum(mask)/ newFr
            tFlanging = np.sum(flanging[mask]) / newFr
            #Results
            self.KG[mic][method]={
            'method':method,
            'mic': mic,
            'tPassBy':tPassby,
            'tSqueal':None,
            'tFlanging':tFlanging,
            'tKG':None,
            #time signal representation of squel/flanging
            'sSqueal': None,
            'sFlanging': {'samplingRate': newFr, 
            't': t,
            'y':flanging},
            #additional for this method
            'sn': SN,
            'snf': newSn
            }
        #
            
