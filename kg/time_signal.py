import os
import pathlib
import scipy as sp
from scipy.io import loadmat, wavfile
import wave
import numpy as np
import pandas as pd
import copy

import csv
import struct
import itertools


class timeSignal():
    """
    import time signal and info from MBBM
    """
    PATH = ''
    SIGNALS = {}

    def __init__(self, ID):
        self.ID = ID
        self.path = timeSignal.PATH
        self.signals = {}
        
    def list_signals(self):
        data = []
        index = []
        for k, v in timeSignal.SIGNALS.items(): 
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
        dataPath = self.path.joinpath('raw_signals')
        if not channel in self.signals.keys():
            signal = timeSignal.SIGNALS[channel]
            time = timeSignal.SIGNALS[signal['time']]
            #load y vector
            path = str(dataPath.joinpath(signal['fileName'])).replace('ID',self.ID)
            arrN = self.ID 
            y = np.ravel(loadmat(path, variable_names = arrN)[arrN])
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
        try:
            s = self.signals[channel]
            info = timeSignal.SIGNALS[channel]
        except KeyError:
            print('Channel '+ str(channel) + ' is not loaded.')
        else:
            info['frames']= len(s['y'])
            info['tmin'] =  s['t'].min()
            return(info)
            
    def get_signal(self, channel):
        """
        return a copy of the signal
        """
        try:
            s = self.signals[channel]
        except KeyError:
            print('Channel '+ str(channel) + ' is not loaded.')
        else:
            return(copy.deepcopy(self.signals[channel]))
    
    @classmethod
    def setup(cls, mesPath):
        mesPath = pathlib.Path(mesPath)
        with mesPath.joinpath('raw_signals_info.csv').open('r+') as info:
            reader = csv.reader(info,delimiter=';')
            header = None
            dict ={}
            for row in reader:
                if row[0][0]=='#':
                    pass
                elif header == None:
                    header = row[1:]
                else:
                    for i,v in enumerate(row):
                        try:
                            row[i] = int(v)
                        except ValueError:
                            pass
                    dict[row[0]] = { h:v for h,v in zip(header,row[1:])}
            #set SIGNAl
            cls.PATH = mesPath
            cls.SIGNALS = dict
        return(cls)
    
##tests 
if __name__ == "__main__":
    #perche 'm1020'noné compreso (tilo), 'm_0119' chefrastuono
    import pathlib
    import matplotlib.pyplot as plt
    timeSignal.setup('D:\GitHub\myKG\Measurements_example\MBBMZugExample')
    #
    ts = timeSignal('m_0101')
    mic=[1,2,4,5,6,7]
    for i,m in enumerate(mic):
        ts.read_signal(m)
