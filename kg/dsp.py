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

sys.path.append('D:\GitHub\KG')

from pandas.sandbox.qtpandas import DataFrameModel, DataFrameWidget

# todo: phase spectrum
# todo: kg, squeal algorithm
# todo: spectrum spectrum plot

class DSP():
    
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
    def __init__(self):
        #pass mic and SPL signals
        self.signals = {}
        self.currentSn = 0
        self.SignalInfo = pd.DataFrame(columns = ['mic','channel','type','tb','te','t1b','t1e','fltPar','LAEQ','besch'])
        self.SignalInfo.channel = self.SignalInfo.channel.astype(int)
        self.SignalInfo.mic = self.SignalInfo.mic.astype(int)
        self.STFT = {}
        self.PS = {}
        self.L = {}
        self.KG = {}

    def add_mic_signal(self, signal, type, mic, besch, vars):
        """
        add a mic signal and its informations
        """
        newID =  len(self.signals)
        #create a new row with mic signal informations on SignalInfo
        SignalInfo = pd.DataFrame(columns = ['mic','channel','type','tb','te','t1b','t1e','fltPar','LAEQ','besch'], 
        data=[[mic, mic , type, vars['tb_mic_i'], vars['te_mic_i'],
        vars['t1b_mic_i'], vars['t1e_mic_i'], None , vars['LAEQ_mic_i'], besch ]],
        index=[newID])
        SignalInfo.channel = SignalInfo.channel.astype(int)
        SignalInfo.mic = self.SignalInfo.mic.astype(int)
        self.SignalInfo = pd.concat([self.SignalInfo,SignalInfo])
        #add signal to signal dict
        self.signals[newID]= signal
        #add empty list to KG evaluation
        self.KG[self.SignalInfo.ix[newID]['channel']] = {}
        
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
    def get_KG_algorithm(self):
        calc_id, algorithmDescription,variableInfo = (1,1,1)
        return(calc_id, algorithmDescription,variableInfo)
        
    def get_KG_results(self):
        '''
        stored values in self.KG
        are returned
        '''
        mic=[]
        tpassBy=[]
        tsqueal=[]
        for id,v in self.KG.items():
            mic.append(self.SignalInfo[id]['mic'])
            tpassBy.append(v['tpassBy'])
            tsqueal.append(v['tsqueal'])
        return({'mic':mic,'tpassBy':tpassBy,'tsqueal':tsqueal })
        
    def set_process_signal(self, signalID = None ):
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
    
        
    def bp_filter(self, lowcut=4000, highcut=9000 , order = 4):
        """
        Add to self.WavData a filtered (butter) np.array.
        np.array key is 'bp_lowcut_highcut'
        parameter: 
        - lowpass frequency
        - highpass frequency
        - order

        """
        signal = self.signals[self.currentSn]
        newSn =  len(self.signals)
        SignalInfo = self.SignalInfo.ix[[self.currentSn]]
        SignalInfo.index = [newSn]
        SignalInfo[['type','besch']] = ['flt','banpassfilter:' + str(lowcut) +'_'+str(highcut) ]
        #
        self.SignalInfo = pd.concat([self.SignalInfo, SignalInfo])
        #
        nyq = 0.5 * signal['sR']
        low = lowcut / nyq
        high = highcut / nyq
        b, a = sp.signal.butter(order, [low, high], btype='band')
        self.signals[newSn] = {'sR':signal['sR'],'t': signal['t'], 'y':sp.signal.lfilter(b, a, signal['y'])}
        return(newSn)
        
    def tp_filter(self, highcut=2000 , order = 4):
        """
        Add to self.WavData a filtered (butter) np.array.
        np.array key is 'bp_lowcut_highcut'
        parameter: 
        - lowpass frequency
        - highpass frequency
        - order

        """
        signal = self.signals[self.currentSn]
        newSn =  len(self.signals)
        SignalInfo = self.SignalInfo.ix[[self.currentSn]]
        SignalInfo.index = [newSn]
        SignalInfo[['type','besch']] = ['flt','lowpassfilter:' + str(highcut) ]
        #
        self.SignalInfo = pd.concat([self.SignalInfo, SignalInfo])
        #filtering
        nyq = 0.5 * signal['sR']
        high = highcut / nyq
        b, a = sp.signal.butter(5, high , btype='lowpass')
        self.signals[newSn] = {'sR':signal['sR'],'t': signal['t'], 'y':sp.signal.lfilter(b, a, signal['y'])}
        return(newSn)
        
    def calc_spectrum():
        signal = self.signals[self.currentSn]
        tb = self.SignalInfo.ix[self.currentSn]['t1b']
        te = self.SignalInfo.ix[self.currentSn]['t1e']
        mask = signal['t']
        
        window = hamming(M) / 1.08
        freq = np.abs(fftfreq(N, 1./signal['sR']))
        X = np.zeros(N*len(frame_i),dtype=np.complex128).reshape(len(frame_i),N)
        #STFT
        for i,frame in enumerate(frame_i):
            X[i,:] = fft( self.__fenster__(M,frame) * window, n = N )* np.exp(- 1j * freq *i)
        
    
    def calc_STFT(self, M = 2**10-1, N = None, ola = 2,window = 'hann'):
        signal = self.signals[self.currentSn]
        name = str(M) +'_'+ str(N) +'_'+ str(R)
        X, freq, frame_i, param = STFT( sn = signal['y'], M = M, N = N,\
                                    ola = ola, R = self.R, window =window,\
                                    sR = signal['sR'])
        #save
        STFT = {'name': name ,
                'frame_i': frame_i,# centre sample i
                'f': freq,
                'X_i': X, # complex FFT
                'param': param
                }
        try:
            self.STFT[self.currentSn].append(STFT)
            
        except KeyError:
            self.STFT[self.currentSn] = [STFT]
            
    def calc_SPL(self, A = True,  integration_time = 0.125):
        """
        http://www.prosoundtraining.com/site/articles/basic-definitions-of-an-integrating-spl-meters/
        and
        FAST= 125ms
        TEL = Schall- und Erschütterungsschutz im Schienenverkehr.
        """
        sn = self.signals[self.currentSn]
        Fr = sn['sR']
        snI = self.SignalInfo.ix[self.currentSn]
        dt = 1 / Fr
        # apply A filter to signal
        if A == True:
            b,a = A_filter(Fr)
            yFlt = lfilter(b, a, sn['y'])
        else:
            yFlt = sn['y']
        # Leq TEL
        # time mask for integration intervall
        tmask = np.all([(sn['t']<= snI['t1e']), (sn['t'] >= snI['t1b'])], axis=0)
        prms2_eq = np.sum(yFlt[tmask]**2)/tmask.sum()
        Leq = 10*np.log10(prms2_eq/(2e-5)**2) 
        TEL = Leq  + 10*np.log10((snI['te']-snI['tb'])/(snI['t1e']-snI['t1b']))
        # integration Filter without  frame loosing
        prms2_F = integrate_flt(yFlt**2, Fr ,integration_time)
        LF2 = 10*np.log10(prms2_F/(2e-5)**2)
        # integration every integration time steps
        tF,LF = time_averaged_sound_level(yFlt, Fr, integration_time)
        #fill L dict
        self.L[self.currentSn] = { 
        'Leq':Leq,
        'LeqMBBM':snI['LAEQ'],
        'TEL':TEL,
        'LF':{'sR':Fr,'t': sn['t'][0] + tF , 'y':LF},
        'LF2':{'sR':Fr,'t': sn['t'] , 'y':LF2} 
        }
        
    def list_SignalInfo(self, PySide = True):
        W = DataFrameWidget(self.SignalInfo)
        W.setWindowTitle('Signal Info')
        return(W)
        
    def plot_STFT_phase(self, signal, ax):
        # datenvorbereitung
        try:
            stft = self.STFT[signal][0]
        except KeyError:
            print("calculate first STFT")
            return()
            
        fmin = 200
        fmax = 10000
        mask = np.all([(stft['freq'] <= fmax), (stft['freq'] >= fmin)], axis=0)
        #first plot
        f= stft['freq'][mask] + stft['df']/2
        TR = stft['R']/(stft['N']*stft['df'])
        t = np.hstack((-TR/2, stft['t_i'] + TR/2))
        # tempo e frequenza per questo plot
        X , Y = np.meshgrid(t , f)
        Z = np.angle(stft['X_i'][:,mask])
        Z = np.transpose(np.unwrap(Z))
        # plotting
        ax.set_title('stft phase:' +str(signal), fontsize=10)
        #cmap = brewer2mpl.get_map('RdPu', 'Sequential', 9).mpl_colormap
        #norm = mpl.colors.Normalize(vmin = 50, vmax=110)
        # np.round(np.max(ZdB)-60 ,-1), vmax = np.round(np.max(ZdB)+5,-1), clip = False)
        spect = ax.pcolormesh(X, Y, Z[1:,:])#, norm = norm, cmap = cmap)
        #legenda
        axins = inset_axes(ax,
                    width="2.5%", # width = 10% of parent_bbox width
                    height="100%", # height : 50%
                    loc=3,
                    bbox_to_anchor=(1.01, 0., 1, 1),
                    bbox_transform=ax.transAxes,
                    borderpad=0,
                    )
        axins.tick_params(axis='both', which='both', labelsize=8)
        ax.figure.colorbar(spect, cax=axins)
        ax.set_yscale('log')
        #ax.grid(True,ls="-", linewidth=0.4, color=cmap(0), alpha=0.8)
        #tiks & labels
        #ax.minorticks_off()
        freqtick = 1000 *(2**(np.arange(-18,13,1)/3)) #center octave bands
        ax.set_yticks(freqtick)
        ax.set_ylim([f.min(),f.max()])
        ax.set_yticklabels(np.array(np.round(freqtick,-1),int))
        ax.set_ylabel('f (Hz)')
        
    def plot_spectrogram(self, signal, ax, stftNumber = 0 ):
        """
        TODO
        """
        # datenvorbereitung
        try:
            stft = self.STFT[signal][stftNumber]
        except KeyError:
            print("STFT list has no element " +str(stftNumber))
            return()
            
        fmin = 200
        fmax = 10000
        vMax= 110
        plot_spectrogram(stft['X'], stft['freq'], stft['frame_i'], signal['sR'],\
                        stft['param'], ax,vMax=110 )
        ax.set_ylim([fmin,fmax])
        ax.set_xlim([t.min(),t.max()])

        
    def plot_PS(self, signal, ax):
        """
        plot power spectra from FFT
        TODO
        """
        pass
        
    def plot_SPL(self, signal, ax, label=None, type = 'LF'):
        """
        plot sound pressure level
        type: FFT or time
        TODO: FFT , label
        """
        if type=='FFT':
            print('not implemented yet')
            return(ax)
        else:
            try:
                L = self.L[signal][type]
                SignalInfo = self.SignalInfo.ix[signal]
            except KeyError:
                print('No signal')
            if label == None:
                label= 'SPL_'+ type +'_sn_' + str(SignalInfo['type'])
            ymin, ymax = ax.get_ylim()
            ax.plot(L['t'], L['y'], label = label)
            Lmax = np.ceil((L['y'].max().max()+1)/5)*5
            if ymax < Lmax:
                ax.set_ylim(40,Lmax)
            ax.set_ylabel('dB')
            #ax.set_xlabel('t (s)')  
        
    def plot_KG(self, mic, method , ax, type= 'flanging', color='red'):
        """
        TODO label,colors
        mic
        method
        type in ['squeal', 'flanging']
        """
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

    
#     #private
#     def __fenster__(self,M,i):
#         """
#         return a window of the np.array self.signal[key] 
#         parameter:
#         - M window length
#         - i center element of the window  if M odd, else shifted forward
#         """
#         signal = self.signals[self.currentSn]
#         nFrames = len(signal['y'])
#         #center element
#         s = int(i + M/2)
#         fenster = np.zeros(M)
#         if(i < nFrames):
#             x = signal['y'][:s+1][-M:]
#             fenster[-len(x):] = x 
#         if(i >= nFrames):  
#             x = signal['y'][s-M+1:]
#             fenster[:len(x)] = x
#         return(fenster)
# ##

# """
# ##
# if __name__ == "__main__":
#         """
#         mask = np.all([(freq <= fmax), (freq >= fmin)], axis=0)
#         f= freq[mask]
#         meanFilter=np.array([1]*5)/5
#         y= PS_i
#         for i in range(0,len(y[:,0])):
#             y[i,:] = sp.signal.convolve(y[i,:],meanFilter,mode= 'same')
#         y= y[:,mask]
#         """ / df per normalizzare 
#         l'energia per frequenzband, vale sum PS df = prms^2  """
#         
#         PSS= self.PS(self.Calc['STFT_8192'])
#         Ntot = self.param['nFrames']
#         Fs = self.param['sR']
#         dt = 1/Fs
#         N = PSS['N']
#         print("N: ",N)
#         TR = PSS['TR']
#         print("Etot: ", np.sum(self.WavData['original']**2)*dt )
#         #
#         print("E_tot da SP_i: ", np.sum(np.sum(PSS['PS_i'],1))* TR)
#         #
#         #         prms_k1 = self.Calc[fft]['welch'][3]['prms_i']**2
#         #         print("E_tot da prms welch 1", np.sum(prms_k1 )*T/2 ,"len",len(prms_k1))
#         #         print("E_tot da SP_k1: ", np.sum(np.sum(self.Calc[fft]['welch'][3]['PS_i'],0))*T/2    )
