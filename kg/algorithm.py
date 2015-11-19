# import sys
# sys.path.append('D:\GitHub\myKG')
import numpy as np
import pandas as pd
import copy
import datetime
import collections
import json
from PySide import QtGui, QtCore
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt

from kg.mpl_widgets import Bar
from kg.detect import MicSignal
from kg.case import Case
from kg.measurement_values import measuredValues
import math

class Algorithm(object):
    def __init__(self, noiseType, parameter, description ='', Rexport=False):
        self.description = description 
        self.param = parameter
        self.noiseType = noiseType
        self.output = {'t':None, 'result':None, 'dt':None}
        #structure of case_tests {mID:{mic:{author:TP,TN,FP,FN}}}
        self.case_tests = {}
        self.rates={}
        self.Rexport=Rexport
        self.forR=[]
        self.currentauthor=None
        
    def get_info(self):
        return({'class': self.__class__.__name__ , 'noiseType': self.noiseType, \
        'description':self.description, 'param': self.param, 'id':self.get_id(),'prop':self.stringsummary()})
    
    def func(self):
        '''function which implement algorithm'''
        pass
    
    def get_Type(self):
        return None
    
    def test_on_case(self, case, mesValues, micSn = None):
        '''
        test algorithm  on Case
        '''
        loc = mesValues.location
        mes = mesValues.measurement
        assert((case.case['location'] == loc and\
                    case.case['measurement'] == mes))
        mID = case.case['mID']
        mic = case.case['mic']
        self.currentauthor = case.case['author']
        quality = case.case['quality']
        if micSn == None:
            micSn = MicSignal.from_measurement(mesValues, mID, mic)
        else:
            assert((case.case['mID'] == micSn.ID and\
                    case.case['mic'] == micSn.mic))
        #output = self.func(micSn)
        micSn.calc_kg(self)
        output= micSn.get_KG_results(self)['result']
        # compare case and alg results
        comparation, disc = case.compare(output['result'], output['t'],sum =True)

        #fill test cases
        # todo: if ROC evaluation
        # todo: addr BPR vector to case_tests masked in Te Tb
        # todo: add TF vectors
        self.case_tests[str(case)] = {'mic':mic,'mID':mID,'location':loc,\
                                    'measurement':mes,'author':self.currentauthor, \
                                    'quality':quality, 'disc':disc, 'te':case.get_bounds()[1], 'tb':case.get_bounds()[0]}
        #export for R
        if self.Rexport:
            for i in range(0,len(disc)):
                self.forR.append({'mic':mic, 'mID':mID, 'location':loc, 'author':self.currentauthor,'quality':quality, 'BPR':output['BPR'][i], 'time':output['t'][i], 'disc':disc[i], 'NoiseT':self.noiseType, 'Alg':"Z2", 'AlgProp': self.stringsummary()})
            
        self.case_tests[str(case)].update(output)
        self.case_tests[str(case)].update(comparation)
        # add rates
        self.case_tests[str(case)].update(rates(**comparation))
        return(micSn)
        
    def calc_rates(self):
        '''return a dict of the global rates
           {'TPR':,
            'TNR':,
             author:{'TPR':,'TNR':}, 
            'cases':{case:{'TPR':,'TNR':}}}'''
        df = pd.DataFrame( index =list(self.case_tests.keys()),\
                            columns = ['mID','mic','author','TP','TN','FP','FN'])
        #fill df
        col = df.columns

        for case, v in self.case_tests.items():
            for k, v1 in v.items():
                if k in col:
                    df.ix[case][k] = v1
        #calc rates
        col = ['TP','TN','FP','FN']
        # by author
        byAuthor = df.groupby(['author'])[col].aggregate(np.sum).T.to_dict()
        for auth,v in byAuthor.items():
            self.rates[auth] = rates(**v)  
        # global
        self.rates.update(rates(**df[col].sum().to_dict()))
    def stringdefinition(self):
        pass
    def stringsummary(self):
        return "A"
    def export_test_results(self, mesPath):
        '''
        export tests results to json
        '''
        dateTime = datetime.datetime.now()
        fileName = 'test_'+ str(self) +'_'+ dateTime.strftime( "%d-%m-%Y_%H")
        resultsPath = mesPath.joinpath('results').joinpath(fileName + '.json')
        export = collections.OrderedDict()
        export['Description']= '''
                    This file contains the Results of algorithm tests on cases'''
        export.update({'date': dateTime.strftime( "%d-%m-%Y"),
                       'time':dateTime.strftime( "%H-%M-%S")})
        export['algorithm'] = self.get_info()
        export['rates'] = self.rates
        export['case_tests'] = self.case_tests
        export['R']=self.forR
        with resultsPath.open('w+') as file:
            json.dump(export,file, cls=ArrayEncoder, allow_nan=False)
        return resultsPath
        
    def __repr__(self):
        s = '{}\n'.format(self.__class__.__name__)
        s += 'description: {}\n'.format(self.description)
        s += 'parameter:\n{}'.format(self.param)
        return(s)
    def get_id(self):
        """return a short version of class name"""
        return("A")
    @classmethod
    def phony(cls):
        """doesn't create a real algorithm but returns the attributes of the subclass"""
        phony=cls('Z','')
        return (cls.get_id(),cls.stringdefinition())
    @classmethod
    def askforattributes(cls, window):
        """asks for the attributes of the class and return a object with these properties"""
        noiseType, validnt=QtGui.QInputDialog.getItem(window,"Algorithm","Please select noise type", ['Z','K'])
        parameter, validp=QtGui.QInputDialog.getInt(window,"Algorithm", "Please select parameter value",  value=200, min=1, max=10000, step=1)
        if validnt and valip:
            return cls(noiseType, parameter)
        else:
            return None
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
        param = {'fmin':100,'fmax':15000, 'overlap': 4} 
        param['threshold'] = int(threshold)
        param['fc']= int(fc)
        param['dt']= float(dt)
        description = """implement the Algorithm:
        1: stft -> X(k,i)
        2: calculate power per bands for every t_i
        3: build band power ratio (BPR) and compare to threshold for every t_i
        """
        #
        super(ZischenDetetkt1, self).__init__( 'Z', param, description)
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
        output['result'] = 10 * np.log10(1+BPR) > par['threshold']
        output['t'] = t
        output['dt'] = self.param['dt']
        output['BPR'] = BPR
        return(output)
    def stringdefinition(self):
        return 'Z1_fc_threshold_dt'
    def visualize(self,fig, MicSnObj, case = None):
        # todo: improve visualization
        # todo: case.plot() is not shown with spectrogram
        stftName = MicSnObj.get_stft_name(self)
        fig.clf()
        if case is not None:
            ax1= fig.add_subplot(3,1,1)
            ax2= fig.add_subplot(3,1,2,sharex = ax1)
            ax3= fig.add_subplot(3,1,3,sharex = ax1)
        else:
            ax1= fig.add_subplot(2,1,1)
            ax2= fig.add_subplot(2,1,2,sharex = ax1)
        #ax1
        MicSnObj.plot_spectrogram(stftName, ax1) 
        MicSnObj.plot_triggers(ax1)
        MicSnObj.plot_KG(self,ax1,color = 'cyan')
        #ax2
        MicSnObj.plot_triggers(ax2)
        MicSnObj.plot_BPR(self,ax2)
        if case is not None:
            case.plot(ax2,color= 'b')
            
        if case is not None:
            MicSnObj.plot_BPR(self,ax3)
            alg_res = MicSnObj.get_KG_results(self)['result']
            case.plot_compare(ax3, noiseType = self.noiseType , **alg_res)
            return(ax1,ax2,ax3)
        else:
            return(ax1,ax2)

        
    def __str__(self):
        s = '{}_{}s'.format( self.__class__.__name__, self.param['dt'])
        s += '_{}Hz_{}dB'.format(self.param['fc'],self.param['threshold'])
        return(s)
        
    @classmethod
    def from_info(cls):
        pass
    @classmethod
    def phony(cls):
        """doesn't create a real algorithm but returns the attributes of the subclass"""
        phony=cls(10,10,10)
        return (cls.get_id(),cls.stringdefinition())
    @classmethod
    def askforattributes(cls, window):
        """asks for the attributes of the class and return a object with these properties"""
        threshold, validt=QtGui.QInputDialog.getInt(window,"ZischenDetetkt1","Please select threshold",value=3000, min=1, max=10000, step=1)
        parameter, validp=QtGui.QInputDialog.getInt(window,"ZischenDetetkt1", "Please select fc",  value=3000, min=1, max=10000, step=1)
        dt, validdt=QtGui.QInputDialog.getDouble(window,"ZischenDetetkt1", "Please select dt",  value=0.02, min=1, max=1, decimals=2)
        if validt and validdt and validp:
            return cls(fc,threshold,dt)
        else:
            return None
class ZischenDetetkt2(Algorithm):
    '''
    implement the Algorithm:
        1: stft -> X(k,i)
        2: calculate power per bands for every t_i
        3: build band power ratio (BPR) 
        4: smooth BPR with simple moving average
        5: compare to threshold for every t_i
    parameter:
        stft Parameter
        cutoff frequency
        threshold
    '''
    def __init__(self, fc, threshold, dt, Rexport=False, fmin=100):
        #
        param = {'fmin': fmin,'fmax': 15000, 'overlap': 6} 
        param['threshold'] = float(threshold)
        param['fc']= int(fc)
        param['dt']= float(dt)
        description = """implement the Algorithm:
        1: stft -> X(k,i)
        2: calculate power per bands for every t_i
        3: build band power ratio (BPR) 
        4: smooth BPR with simple moving average
        5: compare  log10(1+BPR) to threshold for every t_i
        """
        #
        super(ZischenDetetkt2, self).__init__( 'Z', param, description, Rexport)
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
        avBPR = moving_average(bandPower['high']/(1+bandPower['low']))
        decision = 10 * np.log10(1 + avBPR) > par['threshold']
        # at least 1 neighborr has to be 1 
        avDecision = np.logical_and(moving_average(decision) > 0.5 , decision)
        output['result'] = avDecision
        output['t'] = t
        output['dt'] = self.param['dt']
        #output['vBPR']={}
        #output['vBPR']['high']=list(bandPower['high'])
        #output['vBPR']['low']=list(bandPower['low']) #vector BPR
        BPRforR=[]
        for el in avBPR:
            if math.isnan(el):
                BPRforR.append(str("NaN"))
            else:
                BPRforR.append( 10 * np.log10(1 + el))
        output['BPR'] = list(BPRforR)
        output['avBPR']=avBPR
        return(output)
    def plot_spec(self,ax, micSn, decalage=None):
        micSn.calc_kg(self)
        micSn.plot_BPR(self,ax,decalage=decalage,color = '#272822',lw=1)
        
    def stringsummary(self):
        return str(self.param['fc'])+"_"+str(self.param['dt'])
    def stringdefinition(self):
        return 'Z2_fc_threshold_dt'
    def visualize(self,fig, MicSnObj, case = None):
        # todo: improve visualization
        # todo: case.plot() is not shown with spectrogram
        stftName = MicSnObj.get_stft_name(self)
        fig.clf()
        if case is not None:
            ax1= fig.add_subplot(3,1,1)
            ax2= fig.add_subplot(3,1,2,sharex = ax1)
            ax3= fig.add_subplot(3,1,3,sharex = ax1)
        else:
            ax1= fig.add_subplot(2,1,1)
            ax2= fig.add_subplot(2,1,2,sharex = ax1)
        #ax1
        MicSnObj.plot_spectrogram(stftName, ax1) 
        MicSnObj.plot_KG(self,ax1, color = 'cyan')
        #ax2
        MicSnObj.plot_triggers(ax2)
        MicSnObj.plot_signal(ax2)
        #MicSnObj.plot_BPR(self,ax2, color = '#272822',lw=1)
        if case is not None:
            case.plot(ax2, color= 'b')
            
        if case is not None:
            MicSnObj.plot_BPR(self,ax3,color = '#272822',lw=1)
            alg_res = MicSnObj.get_KG_results(self)['result']
            case.plot_compare(ax3, noiseType = self.noiseType , **alg_res)
            return(ax1,ax2,ax3)
        else:
            return(ax1,ax2)
        
    def __str__(self):
        s = '{}_{}s'.format( self.__class__.__name__, self.param['dt'])
        s += '_{}Hz_{}dB'.format(self.param['fc'],self.param['threshold'])
        return(s)
    def get_id(self):
        """return a short version of class name"""
        return("Z2")
    def get_Type(self):
        """returns the type of noise this algorithm is designed to analyze"""
        return 'Z'
    @classmethod
    def from_info(cls):
        pass
    @classmethod
    def phony(cls):
        """doesn't create a real algorithm but returns the attributes of the subclass"""
        phony=cls(10,10,10)
        return (cls.get_id(),cls.stringdefinition())
    @classmethod
    def askforattributes(cls, window):
        """asks for the attributes of the class and return a object with these properties"""
        threshold,validt=QtGui.QInputDialog.getDouble(window,"ZischenDetetkt2","Please select threshold",value=3000, min=1, max=10000, step=0.1)
        fc,validfc=QtGui.QInputDialog.getInt(window,"ZischenDetetkt2", "Please select fc",  value=2, min=0, max=10000, step=1)
        dt,validdt=QtGui.QInputDialog.getDouble(window,"ZischenDetetkt2", "Please select dt",  value=0.02, min=1, max=1, decimals=2, step=0.1)
        if validt and validfc and validdt:
            return cls(fc,threshold, dt)
        else:
            return None
class ZischenDetetkt3(Algorithm):
    '''
    implement the Algorithm:
        1: stft -> X(k,i)
        2: calculate power per bands for every t_i
        3: build band power ratio (BPR) 
        4: smooth BPR with simple moving average
        5: compare to threshold for every t_i
    parameter:
        stft Parameter
        cutoff frequency
        threshold
    '''
    def __init__(self, fc, threshold, dt, Rexport=False, fmin=300):
        #
        param = {'fmin': fmin,'fmax': 15000, 'overlap': 6} 
        param['threshold'] = float(threshold)
        param['fc']= int(fc)
        param['dt']= float(dt)
        description = """implement the Algorithm:
        1: stft -> X(k,i)
        2: calculate power per bands for every t_i
        3: build band power ratio (BPR) 
        4: smooth BPR with simple moving average
        5: compare  log10(1+BPR) to threshold for every t_i
        """
        #
        super(ZischenDetetkt2, self).__init__( 'Z', param, description, Rexport)
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
        avBPR = moving_average(bandPower['high']/(1+bandPower['low']))
        if 2<3:
            pass
        decision = 10 * np.log10(1 + avBPR) > par['threshold']
        # at least 1 neighborr has to be 1 
        avDecision = np.logical_and(moving_average(decision) > 0.5 , decision)
        output['result'] = avDecision
        output['t'] = t
        output['dt'] = self.param['dt']
        #output['vBPR']={}
        #output['vBPR']['high']=list(bandPower['high'])
        #output['vBPR']['low']=list(bandPower['low']) #vector BPR
        BPRforR=[]
        for el in avBPR:
            if math.isnan(el):
                BPRforR.append(str("NaN"))
            else:
                BPRforR.append( 10 * np.log10(1 + el))
        output['BPR'] = list(BPRforR)
        output['avBPR']=avBPR
        return(output)
    def plot_spec(self,ax, micSn, decalage=None):
        micSn.calc_kg(self)
        micSn.plot_BPR(self,ax,decalage=decalage,color = '#272822',lw=1)
        
    def stringsummary(self):
        return str(self.param['fc'])+"_"+str(self.param['dt'])
    def stringdefinition(self):
        return 'Z2_fc_threshold_dt'
    def visualize(self,fig, MicSnObj, case = None):
        # todo: improve visualization
        # todo: case.plot() is not shown with spectrogram
        stftName = MicSnObj.get_stft_name(self)
        fig.clf()
        if case is not None:
            ax1= fig.add_subplot(3,1,1)
            ax2= fig.add_subplot(3,1,2,sharex = ax1)
            ax3= fig.add_subplot(3,1,3,sharex = ax1)
        else:
            ax1= fig.add_subplot(2,1,1)
            ax2= fig.add_subplot(2,1,2,sharex = ax1)
        #ax1
        MicSnObj.plot_spectrogram(stftName, ax1) 
        MicSnObj.plot_KG(self,ax1, color = 'cyan')
        #ax2
        MicSnObj.plot_triggers(ax2)
        MicSnObj.plot_signal(ax2)
        #MicSnObj.plot_BPR(self,ax2, color = '#272822',lw=1)
        if case is not None:
            case.plot(ax2, color= 'b')
            
        if case is not None:
            MicSnObj.plot_BPR(self,ax3,color = '#272822',lw=1)
            alg_res = MicSnObj.get_KG_results(self)['result']
            case.plot_compare(ax3, noiseType = self.noiseType , **alg_res)
            return(ax1,ax2,ax3)
        else:
            return(ax1,ax2)
        
    def __str__(self):
        s = '{}_{}s'.format( self.__class__.__name__, self.param['dt'])
        s += '_{}Hz_{}dB_{}Hz'.format(self.param['fc'],self.param['threshold'],self.param['fmin'])
        return(s)
    def get_id(self):
        """return a short version of class name"""
        return("Z3")
    def get_Type(self):
        """returns the type of noise this algorithm is designed to analyze"""
        return 'Z'
    @classmethod
    def from_info(cls):
        pass
    @classmethod
    def phony(cls):
        """doesn't create a real algorithm but returns the attributes of the subclass"""
        phony=cls(10,10,10)
        return (cls.get_id(),cls.stringdefinition())
    @classmethod
    def askforattributes(cls, window):
        """asks for the attributes of the class and return a object with these properties"""
        threshold,validt=QtGui.QInputDialog.getDouble(window,"ZischenDetetkt3","Please select threshold",value=3000, min=1, max=10000, step=0.1)
        fc,validfc=QtGui.QInputDialog.getInt(window,"ZischenDetetkt3", "Please select fc",  value=2, min=0, max=10000, step=100)
        dt,validdt=QtGui.QInputDialog.getDouble(window,"ZischenDetetkt3", "Please select dt",  value=0.02, min=0, max=1, decimals=2, step=0.1)
        fmin,validfmin=QtGui.QInputDialog.getInt(window,"ZischenDetetkt3", "Please select fmin",  value=300, min=-100, max=fc, step=100)
        if validt and validfc and validdt and validfmin:
            return cls(fc,threshold, dt, fmin)
        else:
            return None
##functions
def moving_average(a, n=3) :
    a = np.pad(a,(n//2,n//2),mode = 'constant', constant_values=0)#adds n//2 values 0 to the left and right of a
    ret = np.cumsum(a, dtype=float)#returns i-th entry as (a_0+a_1+...+a_i)
    ret[n:] = ret[n:] - ret[:-n]
    return(ret[n-1:]/n)
        
def rates(TP,TN,FN,FP,**kwargs):
    '''definition of specifity and sensitivity'''
    if (TP + FN)==0:
        TPR = None
    else:
        TPR = float(TP/(TP + FN))
        FNR = float(FN/(TP+FN))
    #    
    if (TN + FP) == 0:
        TNR = None
    else:
        TNR = float(TN/(TN + FP))
        FPR = float(FP/(TN+FP))
    if FPR and TPR:
        d_ax=(TPR+FPR)/2#nearest point on the diagonal
        dist_ax=((d_ax-TPR)**2+(d_ax-FPR)**2)**0.5#euclidean distance to d_ax
    return({'TPR': TPR,'TNR': TNR, 'FPR': FPR, 'FNR':FNR, 'd_ax':d_ax,'dist_ax':dist_ax})
    
class ArrayEncoder(json.JSONEncoder):
    def default(self, obj):
        # if isinstance(obj,GraphicalIntervals):
        #     return obj.toJSON()
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, bool):
            return str(int(obj))
        return json.JSONEncoder.default(self, obj)
