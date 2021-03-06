# import sys
# sys.path.append('D:\GitHub\myKG')
import sys
import os,pathlib
import numpy as np
import scipy as sp
import string
from scipy.io import wavfile
import copy 
import struct
import matplotlib.pyplot as plt
import collections
import time#to set the ID of MicSignal if created from wav only.
from kg.measurement_signal import measuredSignal
from  mySTFT.stft import stft, stft_PSD
from mySTFT.stft_plot import plot_spectrogram
from kg.measurement_signal import measuredSignal
from kg.measurement_values import measuredValues

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
    def __init__(self, ID, mic, y, t, sR, micValues):

        self.ID = ID
        self.mic = mic
        self.y = y
        self.t = t
        self.sR = sR
        self.micValues = {}
        for k in ['Tb','Te','Tp_b','Tp_e','LAEQ','description','gleis','sec']:
            try:
                self.micValues[k] = micValues[k]
            except KeyError as e:
                raise(Exception('__init__ '+ID+str(mic)+' incomplete'))
                
        self.STFT = {}
        self.KG = {'Z':{},'K':{}}
        self.clippedtest()
        
    def __str__(self):
        return(self.ID +'_mic_' + str(self.mic))
    
    def clippedtest(self,K=301, threshold=0.55, ax=None, normalize=False, overwrite=False, fulllength=False):
        '''
        calls function isclipped on mask tb-te (only if fulllength=False).
        saves the result in self.micValues.
        only process if there isn't already a item 'isclipped' in micValues. To overrule this, pass overwrite=True in method call.
        if an ax is given, the plot of the histogram will be display. if normalize is True, the histogram will be normalizes
        returns boolean
        '''
        if not fulllength:
            xn=self.y[self.get_mask()]
        else:
            xn=self.y
        if overwrite or (not overwrite and 'isclipped' not in self.micValues.keys()):
            ans=isclipped(xn,K,threshold,ax,normalize)
            self.micValues['isclipped']=ans
            return ans
        else:
            return None
            
        
        
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
            STFT = self.STFT[stftName]
        except KeyError:
            pass
        else:
            #set interval to evaluate spectrum
            kwargs['t0'] = self.t.min()
        return(stft_PSD(STFT['X'], STFT['param'], scaling = 'density', **kwargs))

    def calc_kg(self, algorithm, complete = True):
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
        if  complete:
            self.KG[algInfo['noiseType']][str(algorithm)] = results
        else:
            results['tEval'] = np.sum(mask)*results['dt']
            results['tNoise'] = np.sum(results['result'][mask]) * results['dt']
        #return(results)
        
    def calc_spectrum_welch(stftName = None, tint = None):
        try:
            STFT = self.STFT[stftName]
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
            sectrum ,freq = stft_welch(STFT['X_i'], STFT['param'],'density', **kwargs)
    
    def export_to_Wav(self, mesPath, relative=True):
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
        filename = str(self) + '.wav'
        filePath = wavPath.joinpath(filename)
        if not filename in [p.name for p in wavPath.glob('*.wav')]:
            scaled = np.int16(self.y/ np.abs(self.y).max() * 32767)
            wavfile.write(filePath.as_posix(), self.sR , scaled)
        path = filePath.absolute()
        if relative:
            return(path.relative_to(mesPath))
        else:
            return(path)
    
    def get_stft_name(self,algorithm):
        par = algorithm.get_stft_param(self.sR)
        return(str(par['M']) +'_'+ str(par['N']) +'_'+ str(par['overlap']))
        
    def get_stft_keys(self):
        return self.STFT.keys()
    def get_KG_results(self, algorithm):
        '''
        get values in self.KG for algorithm
        return: {'ID':mID, 'mic': mic, 'results':{...}}
        '''
        noiseType = algorithm.noiseType
        ret = collections.OrderedDict()  
        ret['ID'] = self.ID
        ret['mic'] = self.mic
        ret['t']=self.t
        if not self.KG[noiseType].get(str(algorithm),False):
            self.calc_kg(algorithm)
        ret['result'] = copy.deepcopy(self.KG[noiseType][str(algorithm)])
        return(ret)
        
    def get_mask(self, t = None , tlim = None):
        '''
        calculate mask for time vector according tlim,
        default with MBBM evaluation
        '''
        if t is None:
            t = self.t
        if tlim is None:
            tb = self.micValues['Tb']
            te = self.micValues['Te']
        else:
            tb,te = tlim
        return(np.logical_and(t >= tb,t <= te))
  
    def plot_BPR(self, algorithm, ax, label = None, decalage=None,**kwarks):
        '''
        plot detection results for a given algorithm
        '''

        if label==None:
            label = str(algorithm)
        KG = self.KG[algorithm.noiseType]
        try:
            detection = KG[str(algorithm)]
        except KeyError as e:
            print('No calculation for', algorithm)
            raise(e)
        else:
            if decalage:
                t=[]
                for i in detection['t']:
                    t.append(decalage+i)
            else:
                t=detection['t']
            logBPR= 10*np.log10(1+detection['avBPR'])
            l, = ax.plot(t,logBPR,\
                        label=label,**kwarks)
            ax.axhline(algorithm.param['threshold'],lw=1, color = plt.getp(l,'color'))
            ax.set_xlim([min(t),max(t)])
            ax.set_ylabel('BPR')
            ax.set_xlabel('t (s)')
            ax.set_ylim([min(logBPR),max(logBPR)*1.1])
    
    def plot_KG(self, algorithm, ax, **kwargs):
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
            xmin,xmax=ax.get_ylim()
            delta=detection['t'][1]-detection['t'][0]

            #result=[]
            #isany=False
            #for dt in range(xmin,xmax, delta):
            #    t.append(dt)
            #    if dt in detection['t']:
            #        isany=True
            #        result.append(detection['result'][detection['t'].index(dt)])
            #    else:
            #        result.append(False)
            #ax.fill_between(detection['t'], where = detection['result'] ,y1 = ymin, y2 = ymax, alpha = 0.4, **kwargs)
            ax.fill_between(detection['t'], where = detection['result'] ,y1 = ymin, y2 = ymax, alpha = 0.4, **kwargs)
            #ax.set_ybound(ymin, ymax)
    
    def plot_prms(self, ax ,label = None):
        # todo:
        pass
        # ax.plot(sn['t'], np.abs(20*np.log10(sn['y']/(2e-5))), label= label)
    
    def plot_PS(self, ax, label = None):
        '''
        plot power spectra from FFT
        '''
        pass
    
    def plot_signal(self, ax , decalage = None,label = None,**kwargs):
        """
        plot signal
        """
        if label == None:
            label = str(self)
        if decalage:
            t=[]
            for i in self.t:
                t.append(decalage+i)
        else:
            t=self.t
        ax.plot(t, self.y, label = label, **kwargs)
        ax.set_xlim([min(t),max(t)])
        ax.set_ylim([min(self.y)*1.1,max(self.y)*1.1])
            
    def plot_spectrogram(self, name, ax, t0, freqscale = 'lin', **kwargs):
        '''
        plot spectrogram
        '''
        # datenvorbereitung
        print('name in detect' +str(name))
        kwargs = {
        'fmin': 200,
        'fmax':10000,
        't0': t0,
        'tmin':t0
        #'tmin': min(self.t),
        #'tmax': max(self.t),
        }
        try:
            STFT = self.STFT[name]
        except KeyError:
            print("STFT dict has no key " + str(name))
            M, N, overlap = [int(i) for i in name.split('_')]
            print("Computing STFT")
            name = self.calc_stft(M, N, overlap)
            STFT=self.STFT[name]
            
        plot_spectrogram(STFT['X'], STFT['param'], ax, zorder = 1,**kwargs )
           
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
        
    def plot_triggers(self, ax, type ='eval', **kwargs):
        """
        type: eval for MBBM evaluations bounds
        type passby passby times
        """
        if type == 'eval':
            bounds = ['Tb', 'Te']
        elif type == 'passby':
            bounds = ['Tp_b', 'Tp_e']
        [ax.axvline(self.micValues[b], **kwargs) for b in bounds]
            
     
    def visualize_results_widget(self,algorithm):
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
        
                
    
        
    
        
    @ classmethod
    def from_measurement(cls, ID, mic, Paths):
        found=False
        if Paths:
            for p in Paths:
                presults=p.joinpath('raw_signals')
                listfiles= os.listdir(presults.as_posix())
                if listfiles.count(str(ID)+"_"+str(mic)+".mat")>0:
                    measuredSignal.setup(p)
                    pathmes=p
                    found=True
                    print(str(p))
                    break
                
        if not found:
            return None
        mS = measuredSignal(ID,mic)
        if mS.initialized:
            y,t,sR = mS.get_signal(mic)
            ch_info = mS.channel_info(mic)
            var = ['Tb','Te','Tp_b','Tp_e','LAEQ']
            mesValues= measuredValues.from_json(pathmes)
            micValues = mesValues.get_variables_values(ID, mic, var)
            micValues.update(ch_info)
            return(cls(ID,mic,y,t,sR, micValues), mesValues)
        else:#if the signal could not be found return None
            return None
    @classmethod
    def from_wav(cls, wavPath):
        """initialise a MicSignal from a wav file given either as str filename, path to file, or list containing the samplerate and the array"""
        if isinstance(wavPath, str):
            wavPath = pathlib.Path(wavPath).absolute()
        else:
            wavPath = wavPath.absolute()
            
        sR,data = wavfile.read(wavPath.as_posix()) 
        if len(data.shape)>1:#it the input is in stereo
            data = data[0]#takes only one array
        data=data.astype(np.float16, copy=False)
        ID = wavPath.name
        micValues={'Tb':0,'Te':len(data)/sR,'Tp_b':0,'Tp_e':0,'LAEQ':0,'description':0,'gleis':0,'sec':0}
        t = np.linspace(micValues['Tb'],micValues['Te'], len(data))
        return(cls(ID, '' , data, t, sR, micValues))
    
    @classmethod
    def from_wavfolder(cls, ID, mic, Paths):
        found=False
        if Paths:
            for p in Paths:
                if not isinstance(p,pathlib.Path):
                    presults=pathlib.Path(p)
                else:
                    presults=p
                presults=presults.joinpath('wav')
                listfiles= os.listdir(presults.as_posix())
                if listfiles.count(str(ID)+"_mic_"+str(mic)+".wav")>0:
                    try : 
                        measuredSignal.setup(p)
                    except:
                        pass
                    else:
                        pathmes=p
                        found=True
                        print(str(p))
                        break
        if found:
            return cls.from_wav(pathmes.joinpath('wav/'+str(ID)+'_mic_'+str(mic)+'.wav'))
        else:
            return None
        """does the same as from_measurement but calls from_wav to initialise"""
    
        
##functions
def isclipped(xn, K=301, threshold=0.55, axdisplay=None, normalizehist=False):
    """
    Tells if the signal xn is clipped or not based on the test by Sergei Aleinik, Yuri Matveev.
    Returns a boolean. 
    Reference: Aleinik S. and Matveev Y. 2014 : Detection of Clipped Fragments in Speech Signals, in International Journal of Electrical, Computer, Energetic, Electronic and Communication Engineering. World Academy of Science, Engineering and Technology, 8, 2, 286--292.
"""
    N=len(xn)
    H=histogram(xn,K,display=axdisplay, normalize=normalizehist)
    #Find the very left non-zero k_l histogram bin index
    if not H:
        return None
    kl=0
    while H[kl]==0 and kl<=K/2:
        k+=1
    #Find the very right non-zero k_r histogram bin index
    kr=K-1
    while H[kr]==0 and kr>=K/2:
        kr-=1
    #Calculate Denom=k_r-k_l
    Denom=kr-kl
    #sets parameters
    yl0=H[kl]
    yr0=H[kr]
    dl=0
    dr=0
    Dmax=0
    #iteration
    while kr>kl :
        kl+=1
        kr-=1
        if H[kl]<=yl0:
            dl+=1
        else:
            yl0=H[kl]
            dl=0
        if H[kr]<=yr0:
            dr+=1
        else:
            yr0=H[kr]
            dr=0
        Dmax=max(Dmax,dl,dr)
    Rcl=2*Dmax/Denom
    return Rcl>threshold
    
def histogram(xn, K, display=None, normalize=False):
    """returns the function histogram of discrete time signal xn with K bins in histogram"""
    N=len(xn)
    xmin=min(xn)
    xmax=max(xn)
    #find min and max values of signal xn
    #for n in range(0,N):
    #    if xn[n]<xmin:
    #        xmin=xn[n]
    #    if xn[n]>xmax:
    #        xmax=xn[n]
    if xmax==xmin:
        print("xmin=xmax")
        return None
    #setting histogram to 0
    H=[0 for i in range(0,K)]
    for n in range(0,N):
        #calculate y(n)=(x(n)-x_min)/(x_max-x_min)
        yn=((xn[n]-xmin)/(xmax-xmin))#normalize
        #calculate bin index
        k=int(K*yn)
        #add one to the right bin index
        if k<K:
            H[k]+=1
        else:
            H[k-1]+=1
    if normalize:
        maximum=max(H)
        H=[i/maximum for i in H]
    if display:
        display.bar(range(0,K),H,color='#d8b365')
    return H

