import sys
import numpy as np
import scipy as sp
import string
import wave
from scipy.io import wavfile
import copy 
import struct
import os
import collections
sys.path.append('D:\GitHub\myKG')
from mySTFT.stft import stft, stft_PSD
from mySTFT.stft_plot import plot_spectrogram

class MicSignal(object):
    
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
    def __init__(self, ID, mic, y, t, sR, micValues, wavPath = None):
        self.ID = ID
        self.mic = mic
        self.y = y
        self.t = t
        self.sR = sR
        self.micValues = {}
        for k in ['Tb','Te','Tp_b','Tp_e','LAEQ']:
            try:
                self.micValues[k] = micValues[k]
            except KeyError:
                pass
                #self.micValues[k] = None
                
        self.wavPath = wavPath
        self.STFT = {}
        self.KG = {'Z':{},'K':{}}
        
    def __str__(self):
        return(self.ID +'_mic' + '_ch_' + str(self.mic))
        
    def calc_stft(self, M , N = None, overlap = 2, window = 'hann',**kwargs):
        X, freq, frame_i, param = stft( self.y, M = M,\
                                                N = N, \
                                                overlap = overlap,\
                                                sR = self.sR,\
                                                window = window,\
                                                invertible = True)
        
        name = str(M) +'_'+ str(N) +'_'+ str(overlap)
        self.STFT[name] = { 'name': name ,
                            'frame_i': frame_i,# centre sample i
                            'f': freq,
                            'X': X, # complex FFT
                            'param': param
                            }
        return(name)
    
    def calc_PSD_i(self, stftName, **kwargs):
        '''
        calculate PSD for all frames f_i
        '''
        try:
            stft = self.STFT[stftName]
        except KeyError:
            pass
        else:
            #set interval to evaluate spectrum
            kwargs['t0'] = self.t.min()
        return(stft_PSD(stft['X'], stft['param'], scaling = 'density', **kwargs))
        
    def calc_kg(self, algorithm):
        '''
        run algorithm on MicSignal object
        parameter
        ---------
        algorithm instance
        '''
        #run algorithm
        algInfo = algorithm.get_info()
        results = algorithm.func(self)
        # calc kenngrössen
        mask = self.get_mask(results['t'])
        results['tPassby'] = np.sum(mask)*results['dt']
        results['tNoise'] = np.sum(results['result'][mask]) * results['dt']
        self.KG[algInfo['noiseType']][str(algorithm)] = results
        #return(results)
        
    def calc_spectrum_welch(stftName = None, tint = None):
        try:
            stft = self.STFT[stftName]
        except KeyError:
            pass
        else:
            #set interval to evaluate spectrum
            kwargs = {'t0' : self.t.min()}
            if tlim == None:
                kwargs['tmin'] = self.micValues['Tb']
                kwargs['tmin']= self.micValues['Te']
            else:
                kwargs['tmax'],kwargs['tmin'] = tlim
            sectrum ,freq = stft_welch(stft['X_i'], stft['param'],'density', **kwargs)

    def get_KG_results(self, algorithm):
        '''
        get values in self.KG for algorithm
        return: {'ID':mID, 'mic': mic, 'results':{...}}
        '''
        noiseType = algorithm.noiseType
        ret = collections.OrderedDict()  
        ret['ID'] = self.ID
        ret[str(self.mic)] = {'mic': self.mic}
        ret[self.mic][str(algorithm)] = copy.deepcopy(self.KG[noiseType][str(algorithm)])
        return(ret)
        
    def get_mask(self, t, tlim = None):
        '''
        calculate mask for time vector according tlim,
        default with MBBM evaluation
        '''
        if tlim == None:
            tb = self.micValues['Tb']
            te = self.micValues['Te']
        else:
            tb,te = tlim
        return(np.logical_and(t >= tb,t >= te))
        
    def plot_spectrogram(self, name, ax, freqscale = 'lin', dBMax = 110):
        '''
        plot spectrogram
        '''
        # datenvorbereitung
        try:
            stft = self.STFT[name]
        except KeyError:
            print("STFT dict has no key " + str(name))
        kwargs = {
        'fmin': 200,
        'fmax':10000,
        't0': self.t.min(),
        'tmin': self.t.min(),
        'tmax': self.t.max()
        }
        plot_spectrogram(stft['X'], stft['param'], ax,\
                                            dBMax=dBMax, **kwargs )
        
                
    def plot_triggers(self, ax, type ='eval', label=None, lw=1.5 ):
        """
        type: eval for MBBM evaluations bounds
        type passby passby times
        """
        if type == 'eval':
            bounds = ['Tb', 'Te']
            col= 'R'
        elif type == 'passby':
            bounds = ['Tp_b', 'Tp_e']
            col= 'B'
        [ax.axvline(self.micValues[b], color= col, lw = lw) for b in bounds]
            
    def plot_KG(self, algorithm, ax, color='red'):
        '''
        plot detection results for a given algorithm
        '''
        KG = self.KG[algorithm.noiseType]
        try:
            detection = KG[str(algorithm)]
        except KeyError as e:
            print('No calculation for', algorithm)
            raise(e)
        else:
            ymin, ymax = ax.get_ylim()
            ax.fill_between(detection['t'], where = detection['result'] ,\
            y1 = ymin, y2 = ymax, alpha = 0.3, color=color)
            #ax.set_ybound(ymin, ymax)
            
    def plot_BPR(self, algorithm, ax, color='red'):
        '''
        plot detection results for a given algorithm
        '''
        KG = self.KG[algorithm.noiseType]
        try:
            detection = KG[str(algorithm)]
        except KeyError as e:
            print('No calculation for', algorithm)
            raise(e)
        else:
            ax.plot(detection['t'], 20*np.log10(detection['BPR']), color=color)
            #ax.set_ybound(ymin, ymax)
            
    def plot_signal(self, ax , label = None):
        """
        plot signal
        """
        if label == None:
            label = str(self)
        ax.plot(self.t, self.y, label = label)
            
    def plot_PS(self, ax, label = None):
        '''
        plot power spectra from FFT
        '''
        pass
    def plot_spectrum(self, ID, mic, ax, label=None):
        pass
        # Todo:
    #     ax.set_title('Spectrum', fontsize=12)
    #     freq = np.array(self.micValues['LAf']['colName'])
    #     PS_i = np.array(self.get_variables_values(ID,mic,['LAf'])['LAf'])
    #     if label == None:
    #         label = 'Spectrum_ch_' + str(mic)
    #     ax.plot(freq, PS_i, label = label)
    #     ax.set_xscale('log')
    #     ax.grid(True)
    #     ax.minorticks_off()
    #     ax.set_xticks(freq)
    #     ax.set_xticklabels([ f if  i%3 == 0  else '' for i,f in enumerate(freq) ])
    #     ax.set_xlim([freq.min(),freq.max()])
    #     ax.set_xlabel('f (Hz)', fontsize=10)
    #     ax.set_ylabel(' (dBA)', fontsize=10)
        
                
    def plot_prms(self, ax ,label = None):
        # todo:
        pass
        # ax.plot(sn['t'], np.abs(20*np.log10(sn['y']/(2e-5))), label= label)
        
    def export_to_Wav(self, mesPath):
        """
        Export a .wav file of the signal in mesPath\wav
        
        param
        ------
        mesPath: main measurement path
        
        return
        ------
        libpath Obj: path of wavfile
        """
        wavPath = mesPath.joinpath('wav')
        os.makedirs(wavPath.as_posix(), exist_ok = True)
        filename = self.ID + '_' + str(self.mic)+'.wav'
        filePath = wavPath.joinpath(filename)
        if not filename in [p.name for p in wavPath.glob('*.wav')]:
            scaled = np.int16(self.y/ np.abs(self.y).max() * 32767)
            wavfile.write(filePath.as_posix(), self.sR , scaled)
        self.wavPath = wavPath.joinpath(filename)
        return(self.wavPath)
        
    @ classmethod
    def from_measurement(cls, mesValues, ID, mic):
        mS = measuredSignal(ID,mic)
        y,t,sR = mS.get_signal(mic)
        var = ['Tb','Te','Tp_b','Tp_e','LAEQ', 'besch']
        micValues = mesValues.get_values(ID, mic, var)
        return(cls(ID,mic,y,t,sR,**micValues))
        
        
