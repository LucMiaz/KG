# import sys
# sys.path.append('D:\GitHub\myKG')
import numpy as np
import pandas as pd
import copy
import datetime
import collections
import json

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt

from kg.mpl_widgets import Bar
from kg.detect import MicSignal
from kg.case import Case
from kg.measurement_values import measuredValues

class Algorithm(object):
    def __init__(self, noiseType, parameter, description =''):
        self.description = description 
        self.param = parameter
        self.noiseType = noiseType
        self.output = {'t':None, 'result':None, 'dt':None}
        #structure of case_tests {mID:{mic:{author:TP,TN,FP,FN}}}
        self.case_tests = {}
        self.rates={}
        
    def get_info(self):
        return({'class': self.__class__.__name__ , 'noiseType': self.noiseType, \
        'description':self.description, 'param': self.param})
    
    def func(self):
        '''function which implement algorithm'''
        pass
    
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
        author = case.case['author']
        quality = case.case['quality']
        if micSn == None:
            micSn = MicSignal.from_measurement(mesValues, mID, mic)
        else:
            assert((case.case['mID'] == micSn.ID and\
                    case.case['mic'] == micSn.mic))
        #output = self.func(micSn)
        micSn.calc_kg(self)
        output = micSn.get_KG_results(self)['result']
        # compare case and alg results
        comparation = case.compare(output['result'], output['t'],sum =True)

        #fill test cases
        # todo: if ROC evaluation
        # todo: addr BPR vector to case_tests masked in Te Tb
        # todo: add TF vectors
        self.case_tests[str(case)] = {'mic':mic,'mID':mID,'location':loc,\
                                    'measurement':mes,'author':author, \
                                    'quality':quality}
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
    
    def export_test_results(self, mesPath):
        '''
        export tests results to json
        '''
        dateTime = datetime.datetime.now()
        fileName = 'test_'+ str(self) +'_'+ dateTime.strftime( "%d-%m-%Y_%H-%M-%S")
        resultsPath = mesPath.joinpath('results').joinpath(fileName + '.json')
        export = collections.OrderedDict()
        export['Description']= '''
                    This file contains the Results of algorithm tests on cases'''
        export.update({'date': dateTime.strftime( "%d-%m-%Y"),
                       'time':dateTime.strftime( "%H:%M:%S")})
        export['algorithm'] = self.get_info()
        export['rates'] = self.rates
        export['case_tests'] = self.case_tests
        with resultsPath.open('w+') as file:
            json.dump(export,file)
        
    def __repr__(self):
        s = '{}\n'.format(self.__class__.__name__)
        s += 'description: {}\n'.format(self.description)
        s += 'parameter:\n{}'.format(self.param)
        return(s)
    
    @classmethod
    def askforattributes(cls, window):
        """asks for the attributes of the class and return a object with these properties"""
        noiseType=QtGui.QInputDialog.getItem(window,"Algorithm","Please select noise type", ['Z','K'])
        parameter=QtGui.QInputDialog.getInt(window,"Algorithm", "Please select parameter value",  value=200, min=1, max=10000, step=1)
        return cls(noiseType, parameter)

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
    def askforattributes(cls, window):
        """asks for the attributes of the class and return a object with these properties"""
        threshold=QtGui.QInputDialog.getInt(window,"ZischenDetetkt1","Please select threshold",value=3000, min=1, max=10000, step=1)
        parameter=QtGui.QInputDialog.getInt(window,"ZischenDetetkt1", "Please select fc",  value=3000, min=1, max=10000, step=1)
        dt=QtGui.QInputDialog.getDouble(window,"ZischenDetetkt1", "Please select dt",  value=0.02, min=1, max=1, decimals=2)
        return cls(fc,threshold,dt)

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
    def __init__(self, fc, threshold, dt):
        #
        param = {'fmin': 100,'fmax': 15000, 'overlap': 6} 
        param['threshold'] = int(threshold)
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
        super(ZischenDetetkt2, self).__init__( 'Z', param, description)
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
        avBPR = moving_average(bandPower['high']/bandPower['low'])
        decision = 10 * np.log10(1 + avBPR) > par['threshold']
        # at least 1 neighborr has to be 1 
        avDecision = np.logical_and(moving_average(decision) > 0.5 , decision)
        output['result'] = avDecision
        output['t'] = t
        output['dt'] = self.param['dt']
        output['BPR'] = avBPR
        return(output)
        
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
        MicSnObj.plot_BPR(self,ax2, color = '#272822',lw=1)
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
        
    @classmethod
    def from_info(cls):
        pass
    @classmethod
    def askforattributes(cls, window):
        """asks for the attributes of the class and return a object with these properties"""
        threshold=QtGui.QInputDialog.getInt(window,"ZischenDetetkt2","Please select threshold",value=3000, min=1, max=10000, step=1)
        parameter=QtGui.QInputDialog.getInt(window,"ZischenDetetkt2", "Please select fc",  value=3000, min=1, max=10000, step=1)
        dt=QtGui.QInputDialog.getDouble(window,"ZischenDetetkt2", "Please select dt",  value=0.02, min=1, max=1, decimals=2)
        return cls(fc,threshold, dt)
        
##functions
def moving_average(a, n=3) :
    a = np.pad(a,(n//2,n//2),mode = 'constant', constant_values=0)
    ret = np.cumsum(a, dtype=float)
    ret[n:] = ret[n:] - ret[:-n]
    return ret[n - 1:] / n
    
def rates(TP,TN,FN,FP,**kwargs):
    '''definition of specifity and sensitivity'''
    if (TP + FN)==0:
        TPR = None
    else:
        TPR = float(TP/(TP + FN))
    #    
    if (TN + FP) == 0:
        TNR = None
    else:
        TNR = float(TN/(TN + FP))
    return({'TPR': TPR,'TNR': TNR})