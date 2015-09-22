import sys
import os
import pandas as pd
import numpy as np
sys.path.append('D:\GitHub\myKG')
sys.path.append('C:\lucmiaz\KG_dev_branch\KG')
from kg.measurement_values import measuredValues
from kg.time_signal import timeSignal
from kg.detect import Detect
from kg.intervals import *
import datetime
import json
import pathlib
import os

class Case(object):
    '''
    A Case object describe the author subjective perception of KG noise
    for a given Microphone passby records.
    self.case['Z'] is a list of intervals where 'zischen' is present
    self.case['K'] is a list of intervals where 'Kreischen' is present
    
    The class contains methods to test a detection algorithm on the case
    '''
    def __init__(self, measurement, caseID, mID, mic, tb, te, author, date = None, \
                    Z = SetOfIntervals(), K = SetOfIntervals()):
        self.axz=subplot(111,axisbg='#FFFFFF')
        plt.subplots_adjust(bottom=0.2)
        self.axk=subplot(111,axisbg='#FFFFFF')
        plt.subplots_adjust(bottom=0.2)
        self.case = {'caseID': caseID,
                'measurement':measurement, 
                'mID': mID,
                'mic': mic,
                'author':author,
                'date':date ,
                #results
                'tb':tb,
                'te':te,
                'Z':GraphicalIntervals(self.axz,Z),
                'K':GraphicalIntervals(self.axk, K),
                }
        
    def save(self, mesPath):
        '''
        save Case to file
        '''
        mesPath = pathlib.Path(mesPath)
        casePath = mesPath.joinpath('test_cases').joinpath(self.case['author'])
        os.makedirs(casePath.as_posix(), exist_ok = True)
        name = self.case['caseID'] + '.p'
        casePath = casePath.joinpath(name)
        print(casePath)
        #add date
        dateTime =  datetime.datetime.now()
        self.case['date'] = dateTime.strftime( "%d-%m-%Y_%H-%M-%S")
        with open(casePath.as_posix(), 'w') as fp:
            json.dump(self.case, fp)
        
    def _compare(self, detect , noiseType = 'Z' , sum = True):
        '''
        compare detection algorithm results with Case,
        return:
        ------
        true positive, true negative, false positive, false negative
        '''
        detResult = detect['noiseType']
        detTime = detect['t']
        caseResult = self.case[noiseType].discretize(tb,te,detTime)
        #evaluated interval
        mask = np.logical_and(detTime > tb , detTime < te)
        #calculate TP, TN, FP, FN
        out = {}
        out['TP'] = np.logical_and(detResult,caseResult)
        out['TN'] = np.logical_and(np.logical_not(detResult), np.logical_not(caseResult))
        out['FP'] = np.logical_and( detResult, np.logical_not(caseResult))
        out['FN'] = np.logical_and( np.logical_not(detResult),  caseResult)
        # sum 
        if sum:
            for k,v in out.iteritem():
                out[k] = v[mask].sum()
        else:
            out['mask'] = mask
        return(out)
    
    def test(self, algorithm, mesVar, signal = None, sum = True):
        '''
        test algorithm  on Case
        '''
        mID = self.case['mID']
        mic = self.case['mic']
        if(signal is None):
            ts = timeSignal(mID)
            ts.read_signal(mic)
            signal = ts.get_signal(mic)
            
        Det = Detect(signal, mID, mic, **mesVar)
        Det.calc(**algorithm['param'])
        return (self._compare(algorithm['test'],Det.get_results(), sum = sum))
    
    def isemptyZ(self):
        """Tells if the range of Z is empty"""
        return self.Z.isempty()
        
    def isemptyK(self):
        """Tells if the range of K is empty"""
        return self.K.isempty()   
    
    @classmethod
    def fromfile(cls, casePath):
        """@classmethod is used to pass the class to the method as implicit argument. Then we open a file in JSON located at casePath and give it to the class with **kwargs (meaning that we pass an arbitrary number of arguments to the class)
        """
        try:
            return cls(**json.load(open(casePath, 'r')))
        except FileNotFoundError:
            raise Error("The file in path" + casePath + " has not be found.")
 
        
class DetectionTester(object):
    def __init__(self, mesPath, author, algorithm, cases = None ):
        '''
        initiate an algorithm test on the case defined by an author
        '''
        self.mesPath = pathlib.Path(mesPath)
        casePath = self.mesPath.joinpath('test_cases').joinpath(author)
        casePaths = [cp for cp in casePath.iterdir() if cp.match('case_**.p')]
        if cases is not None:
            casePaths = [cp for cp in casePaths if cp.name in cases ]
        self.cases = [Case.open(cp.as_posix()) for cp in casePaths]
        
        self.algorithm = algorithm
        self.mesValues = measuredValues(self.mesPath)
        self.mesValues.read_variables_values()
        #
        self.caseResults = pd.DataFrame(columns = ['TP','TN','FP','FN'])
        self.TPR = None
        self.TNR = None
        
    def test_Detection(self):
        '''
        run the test
        calculate the True Positive Ratio and the True Negative Ratio for the
        algorithm
        '''
        for case in self.cases:
            mesVar = self.mesValues.get_variables_values(mID, mic,\
                                                        self.algorithm['mesVar'])
            
            self.caseResults.loc[case.case['caseID']] = case.test(self.algorithm, mesVar)
        #calc Rates
        Results = self.caseResults.sum(axis = 1)
        # sensitivity
        self.TPR = Results['TP']/(Results['TP'] + Results['FN'])
        # specifity
        self.TNR = Results['TN']/(Results['TN'] + Results['FP'])
    
    def save_test_results(self, path = None):
        dateTime =  datetime.datetime.now()
        TestName = 'test_results_' + self.algorithm['name']+'_'+ \
                    dateTime.strftime( "%d-%m-%Y_%H-%M-%S")
        if path == None:
            path = self.path.parent.joinpath(TestName + ".p")
        else:
            path = pathlib.Path(path).joinpath(TestName + ".p")
        #test results
        testResults = { 'algorithm': self.algorithm,
                        'author':self.author,
                        'caseResults':self.caseResults,
                        'TPR':self.TPR,
                        'TNR':self.TNR
                        }
        pickle.dump( testResults, open( path.as_posix(), "wb" ) )
    ##
if __name__ == "__main__":
    #try:
    #    mesPath = 'D:\GitHub\myKG\Measurements_example\MBBMZugExample' 
    #except:
    mesPath = 'C:\lucmiaz\KG_dev_branch\KG\Measurements_example\MBBMZugExample'
    author = input("Who are you ?   ")
    if not author:
        author="esr"
    #axcomp = plt.axes([0.01, 0.05, 0.1, 0.075])
    #bcomp = matplotlib.widgets.Button(axcomp, 'Compare algorithm')
    #bcomp.on_clicked(test.test_Detection())
    algorithm =  {'name':'Zischen1', 'mesVar':[], 'param': {}}    
    test = DetectionTester(mesPath, author, algorithm)
    #test.save_test_results()