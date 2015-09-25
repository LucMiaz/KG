import os, pathlib
import scipy as sp
from scipy.io import loadmat, wavfile
import wave
import numpy as np
import pandas as pd
import copy
import json

import csv
import struct
import itertools


class measuredSignal():
    """
    import time signal and info from MBBM
    """
    _PATH = ''
    _SIGNALS = {}

    def __init__(self, ID, mic = None):
        self.ID = ID
        self.path = measuredSignal.PATH
        self.signals = {}
        if not mic == None:
            self.read_signal(mic)
        
    def list_signals(self):
        data = []
        index = []
        for k, v in measuredSignal._SIGNALS.items(): 
            df = pd.DataFrame(v, index= [k])
            if k in list(self.signals.keys()):
                df['loaded'] = True
            else:
                df['loaded'] = False
            data.append(df)    
        var = pd.concat(data)
        return(var)
    
    def read_signal(self, channel):
        """
        parameter:Measurement ID (string), channel. If channel is none then input is asked.
        return: dict with time array value array and sampling rate
        """
        channel = str(channel)
        dataPath = self.path.joinpath('raw_signals')
        try:
            signal = measuredSignal._SIGNALS[channel]
        except KeyError:
            print( 'Channel' +channel+ 'is missing')
            raise e
        
        if not channel in self.signals.keys():
            signal = measuredSignal._SIGNALS[channel]
            time = measuredSignal._SIGNALS[str(signal['time'])]
            #load y vector
            path = str(dataPath.joinpath(signal['fileName'])).replace('ID',self.ID)
            arrN = self.ID
            try:
                y = np.ravel(loadmat(path, variable_names = arrN)[arrN])
            except FileNotFoundError as e:
                print(e)
                raise(Exception('Class instance is invalid: ID ' + self.ID + ' is missing'))
            #load t vector
            path = str(dataPath.joinpath(time['fileName'])).replace('ID',self.ID)
            arrN = self.ID + '_X'
            t = np.ravel(loadmat(path, variable_names = arrN)[arrN])
            #calculate the framerate of the signal
            sR =np.round(len(t)/(t[-1] - t[0]))
            self.signals[channel] = {'t': t, 'y':y, 'sR': int(sR) }
    
    def channel_info(self, channel):
        '''
        return data frame with info of signal 
        '''
        channel = str(channel)
        try:
            s = self.signals[channel]
            info = copy.deepcopy(measuredSignal._SIGNALS[channel])
        except KeyError as e:
            print( 'Channel' +channel+ 'is not loaded')
            raise(e)
        else:
            info['frames']= len(s['y'])
            info['tmin'] =  s['t'].min()
            return(info)
            
    def get_signal(self, channel):
        """
        return a copy of the signal
        """
        channel = str(channel)
        try:
            s = self.signals[channel]
        except KeyError:
            print('Channel '+ channel+ ' is not loaded.')
        else:
            signal = copy.deepcopy(self.signals[channel])
        return(signal['y'],signal['t'],signal['sR'],)
    
    @classmethod
    def setup(cls, mesPath):
        mesPath = pathlib.Path(mesPath)
        with mesPath.joinpath('raw_signals_config.json').open('r+') as config:
            cls._SIGNALS = json.load(config)
        cls.PATH = mesPath
        #return(cls)
    
##tests 
if __name__ == "__main__":
    #perché 'm1020'noné compreso (tilo), 'm_0119' chefrastuono
    import matplotlib.pyplot as plt
    measuredSignal.setup('Measurements_example\MBBMZugExample')

    #
    ts = measuredSignal('m_0100')
    mic=[1,2,4,5,6,7]
    for i,m in enumerate(mic):
        ts.read_signal(m)
