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
     -self signals is a list of signals with key equal channel
    TODO:
    - change init
   
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
    
    def read_signal(self, channel ):
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
    

    def export_to_Wav(self, channel):
        """
        save channel to wav'
        TODO: 
        - don' save if already saved ok
        - return path ok
        """
        wavPath = self.path.joinpath('wav')
        os.makedirs(wavPath.as_posix(), exist_ok = True)
        try:
            s = self.signals[channel]
        except KeyError:
            print('Channel '+ str(channel) + ' is not loaded.')
        else: 
            if timeSignal.SIGNALS[channel]['type'] == 'mic':
                filename = self.ID + '_' + str(channel)+'.wav'
                filePath = wavPath.joinpath(filename)
                if not filename in [p.name for p in wavPath.glob('*.wav')]:
                    sR = s['sR']
                    scaled = np.int16(s['y']/ np.abs(s['y']).max() * 32767)
                    wavfile.write(filePath.as_posix(), sR , scaled)
                return(wavPath.joinpath(filename))
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
        else:
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
            
    def setup( path):
        #set path
        timeSignal.PATH = pathlib.Path(path)
        with timeSignal.PATH.joinpath('raw_signals_info.csv').open('r+') as info:
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
            timeSignal.SIGNALS = dict
    
##tests 
if __name__ == "__main__":
    #perche 'm1020'noné compreso (tilo), 'm_0119' chefrastuono
    import pathlib
    import matplotlib.pyplot as plt
    timeSignal.setup('D:\GitHub\myKG\Measurements_example\MBBMZugExample')
    #
    ts = timeSignal('m_0101')
    mic=[1,2,4,5,6,7]
    f,ax = plt.subplots(len(mic),sharex=True,sharey=True)
    for i,m in enumerate(mic):
        ts.read_signal(m)
        ts.export_to_Wav(m)
        ts.plot_channel(m,ax[i])