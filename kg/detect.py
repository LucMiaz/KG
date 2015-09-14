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

class Algorithm(object):
    pass
    
class KG(object):
    pass
    
class Detect():

class Mic(object):
    
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
    def __init__(self, signal, ID, mic, values):
        #dict with all the signals of a given passby to be evaluated
        self.ID = ID
        self.mic = mic
        self.signal = signal
        self.tmin = self.signal['t'].min()
        self.SignalInfo = {'mic', 'tb','te','t1b','t1e','LAEQ', 'besch'}
        self.STFT = {}
        self.L = {}
        self.KG = {'Z':{},'K':{}}
        
    def export_to_Wav(self,mesPath):
        """
        save channel to wav'
        TODO: 
        - don' save if already saved ok
        - return path ok
        """
        wavPath = mesPath.joinpath('wav')
        os.makedirs(wavPath.as_posix(), exist_ok = True)
        s = self.signal
        filename = self.ID + '_' + str(self.mic)+'.wav'
        filePath = wavPath.joinpath(filename)
        if not filename in [p.name for p in wavPath.glob('*.wav')]:
            sR = s['sR']
            scaled = np.int16(s['y']/ np.abs(s['y']).max() * 32767)
            wavfile.write(filePath.as_posix(), sR , scaled)
        return(wavPath.joinpath(filename))
    
  
    def calc_kg(self, stftParam, highcut = 2000, threshold = 5):
            stftName = self.calc_stft(**stftParam)
            PS = 
            # signal filtern 
            
            
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
  
    def get_KG_algorithm(self):
        calc_id, algorithmDescription,variableInfo = (1,1,1)
        return(calc_id, algorithmDescription,variableInfo)
        
    def get_KG_results(self, short = True):
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
        signal = self.signal
        X, freq, frame_i, param = mySTFT.stft.stft( self.signal['y'], M = M,\
                                                    N = N, \
                                                    ola = ola,\
                                                    sR = signal['sR'],\
                                                    window = window,\
                                                    invertible = False)
        
        name = str(M) +'_'+ str(N) +'_'+ str(ola)
        self.STFT[name] = { 'name': name ,
                            'frame_i': frame_i,# centre sample i
                            'f': freq,
                            'X_i': X, # complex FFT
                            'param': param
                            }
        return(name)
    
    def calcPS_i(self,stftName):
        stft= self.STFT[stftName]
         stft_PSD(stft['X'], stft['param'], scaling = 'density',t0,):
        return()
        

        
    def calc_spectrum_welch(name, tb=None , te = None):
        stft = self.STFT[self.currentSn][name]
        #set interval to evaluate spectrum
        if tb==None:
            tmin,tmax = tb,te
        else:
            tmin = self.SignalInfo.ix[self.currentSn]['t1b']
            tmax = self.SignalInfo.ix[self.currentSn]['t1e']
        kwargs = {
        't0' : 0,
        'tmin': self.SignalInfo.ix[self.currentSn]['t1b'],
        'tmax': self.SignalInfo.ix[self.currentSn]['t1e']
        }
        mask = signal['t']
        sectrum ,freq = stft_welch(stft['X_i'], stft['param'],'density', **kwargs)
            
    def calc_SPL(self):
       
        #fill L dict
        self.L[self.currentSn] = { 
        'Leq':Leq,
        'LeqMBBM':snI['LAEQ'],
        'TEL':TEL,
        'LF':{'sR':Fr,'t': sn['t'][0] + tF , 'y':LF},
        'LF2':{'sR':Fr,'t': sn['t'] , 'y':LF2} 
        }
        
    def plot_spectrogram(self, name, ax, freqscale = 'lin', dBMax = 110  ):
        """
        
        """
        #todo
        # datenvorbereitung
        try:
            stft = self.STFT[name]
        except KeyError:
            print("STFT list has no element " +str(name))
        kwargs = {
        'fmin': 200,
        'fmax':10000,
        't0': self.tmin
        }
        plot_spectrogram(stft['X'], stft['param'], ax, dBMax=dBMax, **kwargs )

    def plot_mic(self, ax ,label = None):
        """
        plot signal
        """
        label = snInfo['type'] + '_ch_' + str(channel)
        ax.plot(sn['t'], sn['y'], label = label)
                
        # def plot_prms(self, ax ,label = None):
        # ax.plot(sn['t'], np.abs(20*np.log10(sn['y']/(2e-5))), label= label)
                
    def plot_triggers(self, ax, type ='passby', label=None, lw=1.5 ):
        """
        type eval for t
        type passby for t
        
        """
        if type == 'eval':
            variables = ['Tb', 'Te']
            col= 'R'
        elif type == 'passby':
            variables = ['Tp_b', 'Tp_e']
            col= 'B'
        t = self.get_variables_values(ID, mic, variables)
        [ax.axvline(x, color= col, lw = lw) for x in t.values()]
            
        
    def plot_PS(self, signal, ax):
        """
        plot power spectra from FFT
        TODO
        """
        #todo
        pass
        
    def plot_KG(self, method , ax, test = 'Z', color='red'):
        """
        TODO label,colors
        mic
        method
        type in ['squeal', 'flanging']
        """
        #todo
        KG = self.KG[test]
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
