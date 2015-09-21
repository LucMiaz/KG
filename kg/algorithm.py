import sys
import numpy as np
import scipy as sp
import string
import wave
from scipy.io import wavfile
import copy 
import matplotlib as mpl
import struct
import os
sys.path.append('D:\GitHub\myKG')
from mySTFT.stft import stft, stft_PSD
from mySTFT.stft_plot import plot_spectrogram


class Algorithm(object):
    def __init__(self, name, noiseType, parameter, description =''):
        self.name = name
        self.description = description 
        self.param = parameter
        self.noiseType = noiseType
    
    def get_info(self):
        return({'name':self.name, 'noiseType': self.noiseType, \
        'description':self.description, 'param': self.param})
    
    def func(self):
        'function which implement algorithm'
        pass
        
    def __repr__(self):
        s = '{} :{}\n'.format(self.__class__.__name__, self.name)
        s += 'description: {}\n'.format(self.description)
        s += 'parameter:\n{}'.format(self.param)
        return(s)

class ZischenDetetkt1(Algorithm):
    '''
    implement the Algorithm:
        1: stft -> X(k,i)
        2: calculate power per bands for every t_i
        3: build band power ratio (BPR) and compare to threshold for every t_i
    parameter:
        stft Parameter
        cutoff frequency
        threshold
    '''
    def __init__(self, fc, threshold, dt):
        #
        param = {'fmin':200,'fmax':12000, 'overlap':2} 
        param['threshold'] = threshold
        param['fc']= fc
        param['dt']= dt
        description = """implement the Algorithm:
        1: stft -> X(k,i)
        2: calculate power per bands for every t_i
        3: build band power ratio (BPR) and compare to threshold for every t_i
        """
        #
        name = self.__class__.__name__
        super(ZischenDetetkt1, self).__init__( name , 'Z', param, description)
        self.output = {'t':None, 'result':None,'BPR': None, 'dt': self.param['dt']}
        
    def get_stft_param(self,sR):
        '''
        return stft param for a given sampling Rate.
        hoopsize according to dt 
        M according to dt and overlap
        '''
        # hoop according to dt
        R = int(self.param['dt'] * sR)
        M = R * self.param['overlap']
        # 0-pad to next power of two
        N = int(2**np.ceil(np.log2(M)))
        return({'M':M, 'N': N, 'R':R,'overlap': self.param['overlap']})
        
    def func(self, MicSnObj):
        '''
        implement the algorithm
        '''
        par = self.param
        output = copy.deepcopy(self.output)
        # 1: stft
        sR = MicSnObj.sR
        stftName = MicSnObj.calc_stft(**self.get_stft_param(sR))
        # 2: calculate power per bands
        bands = {'low':(par['fmin'],par['fc']), 'high':(par['fc'],par['fmax'])}
        bandPower = {}
        for k,f in bands.items():
            PSD_i, _,t = MicSnObj.calc_PSD_i(stftName, fmin = f[0], fmax = f[1])
            # sum on frequency axis
            bandPower[k]= PSD_i.sum(axis = 1)
        # 3:build ratio and compare to threshold
        BPR = bandPower['high']/bandPower['low']
        output['result'] = BPR > par['threshold']
        output['t'] = t
        output['BPR'] = BPR
        return(output)
        
    def __str__(self):
        s = '{}_{}ms'.format( self.name, self.param['dt'])
        s += '_{}Hz_{}dB'.format(self.param['fc'],self.param['threshold'])
        return(s)