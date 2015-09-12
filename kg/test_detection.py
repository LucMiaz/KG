import sys
import os
import pandas as pd
import numpy as np
sys.path.append('D:\GitHub\KG')
from kg.measurement_values import measuredValues
from kg.time_signal import timeSignal, __create_wav__
from kg.dsp import DSP
from kg.grafics import BarCanvas
from kg.audio_visual_app import PlaybackWindow
from PySide import QtGui,QtCore
from pandas.sandbox.qtpandas import DataFrameModel, DataFrameWidget
# todo: function class to create test cases, 
# input: list signals
# output: file with case results
# todo: test class algorithm on cases
# input: test cases (folder/s)
# output: sensitivity(TPR), specificity(TNR), TP, TN, FP, FN 
# visual output

import datetime
import pickle
import glob
import os

class createCases():
    def __init__(self, measurement, cases= [(None,None)], author= None ):
        self.author = author 
        self.cases = cases
        self.mesValues = measuredValues(measurement)
        self.mesValues.read_variables_values()
    
    def save_case(self,mID):
        dateTime =  datetime.datetime.now()
        case = {'caseID':'wavName','measurement', 'mID','mic',\
                'author':'name',
                'date': dateTime.strftime( "%d-%m-%Y_%H-%M-%S"),\
                #results
                'dt': int,
                'tbe':(int,int),
                'Z':np.array([]),
                'K':np.array([])
                }
        try:
            pickle.dump( caseOutput, open( ID + ".p", "wb" ) )
        assert Error:
            pass
        
class testDetection():
    def __init__(self, path, measurement, author, algorithm, cases = None ):
        self.path = pathlib.Path(path)
        self.cases = [x for x in self.path.iterdir() if x.match('case_**.p')]
        if cases is not None:
            self.cases = [x for x in self.cases if x.name in cases ]
        self.author = author
        self.algorithm = algorithm
        self.mesValues = measuredValues(measurement)
        self.mesValues.read_variables_values()
        #
        self.caseResults = pd.DataFrame(columns = ['TP','TN','FP','FN'])
        self.TPR = None
        self.TNR = None
        
    def _compare_X(self, CX, dtC, DX, dtD ):
        
        return(TP, TN, FP, FN)
    
    def _test_case(self,caseResults):
        X = self.algorithm
        mID = caseResults['mID']
        mic = caseResults['mic']
        #todo
        mesVar = self.mesValues.get_variables_values(mID, mic,\
                                                     self.algorithm['mesVar'])
        param = self.algorithm['param']
        signal = timeSignal(mID)  
        Det = Detect(mID, mic, **mesVar, **param)
        # 
        CX = caseResults[X]
        dtC = caseResults['dt']
        DX = Det.KG
        dtD = Det.dtD
        return(_compare_X( CX, dtC, DX, dtD ))    
            
    def test_Detection(self):
        for case in: self.cases
            print(pp.name())
            caseResults = pickle.load( open( case.as_posix(), "rb" ))
            TP, TN, FP, FN = self._test_case(caseResults)
            self.caseResults.loc[caseID] = [TP, TN, FP, FN]
        #calc Rates
        Results = self.caseResults.sum(axis = 1)
        # sensitivity
        self.TPR = Results['TP']/(Results['TP'] + Results['FN'])
        # specifity
        self.TNR = Results['TN']/(Results['TN'] + Results['FP'])
    
    def save_test_results(self, path = None):
        dateTime =  datetime.datetime.now()
        TestName = 'test_results_' + self.algorithm['name']'_'+ \
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
        
    def plot_results(self):
        pass
        
if __name__ == "__main__":
    path = ''
    measurement = '' 
    author = 'esr'
    algorithm =  {'name':'Zischen1', 'mesVar':[], 'param': {}}    
    test = testDetection(path, measurement, author, algorithm)
    test.test_detection()
    test.save_test_results()