import os
import libpath
import scipy as sp
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
        #falls channel nicht angegeben auswahl aus liste
        if channel in self.signals.keys():
            print( 'channel ' + str(channel) + 'is already loaded.')
        else:
            signal = timeSignal.SIGNALS[channel]
            time = timeSignal.SIGNALS[signal['time']]
            paths = [self.path.joinpath(name).as_posix().replace('ID',self.ID)\
            for names in [signal['fileName'],time['fileName']]]
            #signal values
            for a, path , name in zip([y,t],paths,[self.ID, self.ID + '_X']):
                a = np.ravel(scipy.io.loadmat(path,variable_names = name)[name])
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
                sR = signal['sR']
                data = signal['y']
                scaled = np.int16(data/np.max(np.abs(data)) * 32767)
                sp.io.wavfile.write(filepath, sR, scaled)
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
            
    def setup( path):
        #set path
        timeSignal.PATH = libpath.Path(path)
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
import pathlib
import matplotlib.pyplot as plt
if __name__ == "__main__":
    path = pathlib.Path('D:\GitHub\myKG\Measurements_example\MBBMZugExample')
    timeSignal.setup(path.joinpath('Messdaten_Matlab').as_posix())
    ts = timeSignal('m_0119')
    ts.read_signal(1)
    ts.export_to_Wav(1)
    f,ax = plt.subplots(1)
    ts.plot_channel(1,ax)