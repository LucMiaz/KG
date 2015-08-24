import os
import scipy as sp
import scipy.io
import numpy as np
import pandas as pd
import copy

import csv
import struct
import xlrd
import wave
import itertools
#visualization panda
from pandas.sandbox.qtpandas import DataFrameModel, DataFrameWidget
from PySide import QtGui, QtCore



def __create_wav__( signal, filepath, resolution = 16):
    """
        create an audio Wav file from signal dict. up to 110dB dynamics
        parameter:
        - signal
        - fileName
        - path
        - resolution in bit 
        TODO:
        - fix resolution
    """
    sR = signal['sR']
    nframes = len(signal['t'])
    sampwidth = int(resolution/8)
    scaling = 2**(resolution-1)/6.32
    # 10^(110/20)*2*10^(-5) = 6.32 Pa is sound Pressure at 110dB 
    wavFile = wave.open(filepath, 'w')
    wavFile.setparams((1, sampwidth, sR, nframes, 'NONE', 'not compressed'))
    #http://zacharydenton.com/generate-audio-with-python/
    DataToSave = np.round(signal['y']*scaling).astype(np.int32)
    wavFile.writeframes(b''.join([struct.pack('h',x) for x in DataToSave ]))
    wavFile.close()
 

class timeSignal():
    """
     -self signals is a list of signals with key equal channel
    TODO:
    - change init
   
    """
    PATH = ''
    SIGNALS = {}

    def __init__(self, ID):
        self.ID = ID
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
    
    def read_signal(self, channel ):
        """
        parameter:Measurement ID (string), channel. If channel is none then input is asked.
        return: dict with time array value array and sampling rate
        """
        #falls channel nicht angegeben auswahl aus liste
        if channel in self.signals.keys():
            print( 'channel ' + str(channel) + 'is already loaded.')
        else:
            signal = timeSignal.SIGNALS[channel]
            time = timeSignal.SIGNALS[signal['time']]
            #signal values
            path = timeSignal.PATH +'\\' + signal['fileName'].replace('ID',self.ID)
            y =  np.ravel(scipy.io.loadmat(path, variable_names = self.ID)[self.ID])
            #time vector for signal
            path = timeSignal.PATH +'\\'+ time['fileName'].replace('ID',self.ID)
            t =  np.ravel(scipy.io.loadmat(path, variable_names = self.ID + '_X')[self.ID + '_X'])
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
    

    def export_to_Wav(self, channel):
        """
        save channel to wav'
        TODO: 
        - don' save if already saved ok
        - return path ok
        """
        try:
            s = self.signals[channel]
        except KeyError:
            print('Channel '+ str(channel) + ' is not loaded.')
        else: 
            if timeSignal.SIGNALS[channel]['type'] =='mic':
                filepath = os.path.dirname(timeSignal.PATH) + '\\audio'
                filename = self.ID+ '_'+str(channel)+'.wav'
                os.makedirs(filepath, exist_ok=True)
                if not filename in os.listdir(filepath):
                    __create_wav__(self.signals[channel], filepath +'\\' + filename)
                    print('salvato: ' + str(channel))
                return(filepath +'\\' + filename)
            else:
                print('Channel'+ str(channel) +'is not a microphone')
        
    def plot_channel(self, channel, ax ,label = None):
        """
        plot signal
        """
        try:
            s = self.signals[channel]
        except KeyError:
            print('Channel '+ str(channel) + ' is not loaded.')
            return
            
        sn = self.signals[channel]
        snInfo = timeSignal.SIGNALS[channel]
        if label == None:
            if snInfo['type'] == 'p_rms':
                label = str(channel)
            else:
                label = snInfo['type'] + '_ch_' + str(channel)
                
        if snInfo['type'] == 'p_rms':
            ax.plot(sn['t'], np.abs(20*np.log10(sn['y']/(2e-5))), label= label)
        else:
            ax.plot(sn['t'], sn['y'], label = label)
            
    def _setup( path):
        #set path
        timeSignal.PATH = path
        with open(timeSignal.PATH+ '\\' + 'Readme.csv', 'r+') as readme:
            reader = csv.reader(readme,delimiter=';')
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
            timeSignal.SIGNALS = dict
    
##tests 

if __name__ == "__main__":
    pass