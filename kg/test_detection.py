# import sys
# sys.path.append('D:\GitHub\myKG')
import os
import pandas as pd
import numpy as np

from kg.measurement_values import measuredValues
from kg.time_signal import timeSignal
from kg.detect import Detect

import datetime
import pickle
import pathlib

class Case(object):
    '''
    A Case object describe the author subjective perception of KG noise
    for a given Microphone passby records.
    self.case['Z'] is a list of intervals where 'zischen' is present
    self.case['K'] is a list of intervals where 'Kreischen' is present
    
    The class contains methods to test a detection algorithm on the case
    '''
    def __init__(self, measurement, caseID, mID, mic, tb, te, author, date = None, \
                    Z = [], K = []):
        self.case = {'caseID': caseID,
                'measurement':measurement, 
                'mID': mID,
                'mic': mic,
                'author':author,
                'date':date ,
                #results
                'tb':tb,
                'te':te,
                'Z':Z,
                'K':K
                }
            
    def add_kg_event(self, t0, t1, noiseType = 'Z'):
        '''
        add intervall where noiseType is present
        '''
        self.case[noiseType].append((t0,t1))
        
    def remove_last_event(self):
        # todo
        pass
        
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
        pickle.dump( self.case, open(casePath.as_posix(), "wb" ))
        
    def _compare(self, detect , noiseType = 'Z' , sum = True):
        '''
        compare detection algorithm results with Case,
        return:
        ------
        true positive, true negative, false positive, false negative
        '''
        detResult = detect['noiseType']
        detTime = detect['t']
        caseResult = np.zeros(len(detTime)).astype('bool')
        #crete array from (union)
        for t0,t1 in self.case[noiseType]:
            i0,i1 = np.searchsorted(t,(t0,t1))
            caseResult[i0:i1] = True
        
        #evaluated interval
        tb = np.max(detect['tb'], self.case['tb'])
        te = np.min(detect['te'], self.case['te'])
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
        
    @classmethod
    def fromfile(cls, casePath):
        return(cls(**pickle.load( open( casePath, "rb" ))))
 
        

    ##
if __name__ == "__main__":
    mesPath = 'D:\GitHub\myKG\Measurements_example\MBBMZugExample' 
    author = 'esr'
    algorithm =  {'name':'Zischen1', 'mesVar':[], 'param': {}}    
    test = DetectionTester(mesPath, author, algorithm)
    test.test_detection()
    test.save_test_results()