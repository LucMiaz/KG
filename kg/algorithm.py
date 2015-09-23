import sys
import numpy as np
import scipy as sp
import pandas as pd
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
    def __init__(self, noiseType, parameter, description =''):
        self.description = description 
        self.param = parameter
        self.noiseType = noiseType
        self.output = {'t':None, 'result':None, 'dt':None}
        #structure of case_tests {mID:{mic:{author:TP,TN,FP,FN}}}
        self.case_tests = {}
        self.rates={'cases':{}}
        
    def get_info(self):
        return({'class': self.__class__.__name__ , 'noiseType': self.noiseType, \
        'description':self.description, 'param': self.param})
    
    def func(self):
        '''function which implement algorithm'''
        pass
    
    def test_on_case(self, case, mesValues):
        '''
        test algorithm  on Case
        '''
        assert(not (case.case['location'] == mesValues.location and\
                    case.case['measurement'] == mesValues.measurement))
                    
        mID = case.case['mID']
        mic = case.case['mic']
        author = case.case['author']
        micSn = MicSignal.from_measurement(mesValues, mID, mic)
        output = self.func(micSn)
        
        comparation = case.compare(output['results'],[min(output['t']),\
                                max(output['t']),output['dt']], sum = True)
        #fill test cases
        dict = {'mic':mic,'mID':mID,'author':author}
        self.case_tests[str(case)]= dict.update(comparation)
    
    def calc_rates(self):
        '''return a dict of the single case and the whole rates
           {'TPR':,
            'TNR':,
             author:{'TPR':,'TNR':}, 
            'cases':{case:{'TPR':,'TNR':}}}'''
        df = pd.DataFrame( columns = ['mID','mic','auth','TP','TN','FP','FN'])
        cols = ['TP','TN','FP','FN']
        #fill df
                            
        def rates(TP,TN,FN,FP,**kwargs):
            return({'TPR':TP/(TP + FN),'TNR':TN/(TN + FP)})
        
        for case, v in self.case_tests.items():
            df.loc(case) = v
            self.rates['cases'][case]= rates(**v)
        #author
        sum = df.groupby(['auth'])[cols].aggregate(np.sum).T.to_dict()
        for auth,v in sum.items():
            self.rates[auth] = rates(**v)
        #whole
        self.rates.update(rates(**df[cols].sum().to_dict()))
        return(rates)
    
    def run_test(self, mesPath, save = True).
        '''
        run test on cases of a mesurement and save results to json
        '''
        mesValues = measuredValues.from_json(mesPath)
        casePath = mesValues.path.joinpath('test_cases')
        #collect cases
        cases = []
        for authP in  casePath.iterdir():
            cases.append([Case.from_json(cp.as_posix()) for cp in auth.iterdir()\
                            if cp.match('case_**.json') ])
        #run test on case
        for case in cases:
            self.test_on_case(case, mesValues)
        self.calc_rates()
        # 
        export to json
        if save:
            fileName = 'case_tests'+ str(self) +'_'+ dateTime.strftime( "%d-%m-%Y_%H-%M-%S")
            casePath = mesValues.path.joinpath('test_cases').joinpath(fileName + '.json')
            export = collections.OrderedDict()
            export['Description']= '''
                        This file contains the Results of algorithm tests on cases'''
            export.update({ 'date': dateTime.strftime( "%d-%m-%Y"),
                            'time':dateTime.strftime( "%H:%M:%S"),
                            'location': mesValues.location,
                            'measurement': mesValues.measurement})
            export['rates'] = copy.deepcopy(self.kgValues)
            export['case_tests'] = copy.deepcopy(self.kgValues))
            with resultsPath.open('w+') as file:
                json.dump(export,file)
        
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
        output['result'] = BPR > par['threshold']
        output['t'] = t
        output['dt'] = self.param['dt']
        output['BPR'] = BPR
        return(output)
        
    def __str__(self):
        s = '{}_{}ms'.format( self.name, self.param['dt'])
        s += '_{}Hz_{}dB'.format(self.param['fc'],self.param['threshold'])
        return(s)
        
    @classmethod
    def from_info(cls):
        pass