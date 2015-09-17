import sys
import numpy as np
import scipy as sp
import string
import wave
import matplotlib as mpl
import struct
import os

sys.path.append('D:\GitHub\myKG')
from mySTFT.stft import *


class Algorithm(object):
    def __init__(self, name, noiseType, description='', parameter):
        self.name = name
        self.desc = description 
        self.param = parameter
        self.noiseType = noiseType
    
    def get_alg_info(self):
        return({'name':self.name, noiseType: self.noiseType, \
        'description':self.description, 'param': self.param})
    
    def func(self):
        'function which implement algorithm'
        pass
        
    def __repr__(self):
        s = '{} :{}\n'.format(self.__class__.__name__, self.name)
        s += 'description: {}.'.format(self.desc)
        s += 'parameter: {}\n'.format(self.param)
        return(s)

class ZischenDetetkt1(Algorithm):
    '''
    implement the Algorithm:
        1: stft -> X(k,i),t_i
        2: calculate power per bands for every t_i
        3: build band power ratio (BPR) and compare to threshold for every t_i
    parameter:
        stft Parameter
        cutoff frequency
        threshold
    '''
    def __init__(self, fc, threshold, dt):
        #
        fixParam = {'fmin':200,'fmax':12000, 'overlap':2} 
        #
        decription = '''implement the Algorithm:
        1: stft -> X(k,i),t_i
        2: calculate power per bands for every t_i
        3: build band power ratio (BPR) and compare to threshold for every t_i'''
        #
        name = self.__class__.__name__
        super(Algorithm, self).__init__(name , description, 'Z', fixParam)
        for k,v in {'threshold':threshold, 'overlap':overlap, 'fc':fc, 'dt': dt}:
            self.param[k]=v
        self.output = {'t':None, 'result':None,'BPR': None, 'dt':None}
        
    def func(self, MicSnObj):
        par = self.param
        output = copy.deepcopy(self.output)
        # 1: stft
        #todo
        stftParam = {'M' = }
        output['dt']
        stftName = MicSnObj.calc_stft(**stftParam)
        # 2: calculate power per bands
        bands = {'low':(par['fmin'],par['fc']), 'high':(par['fc'],par['fmax'])}
        bandPower = {}
        for k,v in bands.items():
            #todo
            PSD_i, output['t'] = MicSnObj.calc_PSD_i(stftName, tmin=, tmax=, fmin = f0, fmax = f1 )
            bandPower[k]= PSD_i.sum(axis = 0)
        # 3:build ratio and compare to threshold
        BPR = bandPower['high']/bandPower['low']
        output['Results'] = powerRatio > par['threshold']
        output['BPR'] = BPR
        return(output)
        
    def __str__(self):
        s = '{}_{}ms'.format( self.name, self.param['dt'])
        s += '_{}Hz_{}'.format(self.param['fc'],self.param['threshold'])
        return(s)

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
        self.y = signal
        self.t = t
        self.sR = sR
        self.micValues = { 'Tb','Te','Tp_b','Tp_e','LAEQ', 'besch'}
        for k in self.micValues:
            try:
                self.micValues[k] = micValues['k']
            except KeyError:
                Warning('mic value ' + k + 'is initiate as None')
                self.micValues[k] = None
                
        self.wavPath = wavpath
        self.STFT = {}
        self.KG = {'Z':{},'K':{}}
        
    def __str__(self):
        return(self.ID+'_mic' + '_ch_' + str(mic))
        
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
        s = self.signal
        filename = self.ID + '_' + str(self.mic)+'.wav'
        filePath = wavPath.joinpath(filename)
        if not filename in [p.name for p in wavPath.glob('*.wav')]:
            sR = s['sR']
            scaled = np.int16(s['y']/ np.abs(s['y']).max() * 32767)
            wavfile.write(filePath.as_posix(), sR , scaled)
        self.wavPath = wavPath.joinpath(filename)
        return(self.wavPath)
        
    def get_mask(self, tlim = None):
        '''
        calculate mask for time vector according tlim,
        default with MBBM evaluation
        '''
        if tlim == None:
            tb = self.micValues['Tb']
            te = self.micValues['Te']
        else:
            tb,te = tlim
        return(np.logical_and(t >= tb,t >= te)))
    
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
        mask = self.get_mask()
        results['tPassby'] = np.sum(mask)/ newFr
        results['tNoise'] = np.sum(results['results'][mask]) / newFr
        self.KG[algInfo['noiseType']][str(algorithm)] = results
        return(results)
        
    def get_KG_results(self, algorithm = None, noiseType = None):
        '''
        stored values in self.KG
        are returned
        '''
        
        return({'mic':mic,'tpassBy':tpassBy,'tsqueal':tsqueal })
        
    def calc_stft(self, M , N = None, overlap = 2, window = 'hann'):
        X, freq, frame_i, param = mySTFT.stft.stft( self.y, M = M,\
                                                    N = N, \
                                                    overlap = overlap,\
                                                    sR = signal['sR'],\
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
    
    def calc_PSD_i(self, stftName, fmin = 0, fmax = 0tmin = None, tmax = None):
        '''
        calculate PSD for all frames f_i
        '''
        #todo
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
          
        return(stft_PSD(stft['X'], stft['param'], scaling = 'density', **kwargs))

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
        't0': self.tmin,
        'tmin': self.t.min(),
        'tmax': self.t.max()
        }
        mySTFT.stft_plot.plot_spectrogram(stft['X'], stft['param'], ax,\
                                            dBMax=dBMax, **kwargs )
                
    def plot_triggers(self, ax, type ='passby', label=None, lw=1.5 ):
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
            detection = KG[str(algorothm)]
        except KeyError as e:
            print('No calculation for', algorithm)
            raise(e)
        else:
            ymin, ymax = ax.get_ylim()
            ax.fill_between(detection['t'], where = detection['result'] ,\
            y1 = ymin, y2 = ymax, alpha = 0.3, color=color)
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
                
    def plot_prms(self, ax ,label = None):
        pass
        # ax.plot(sn['t'], np.abs(20*np.log10(sn['y']/(2e-5))), label= label)
        
