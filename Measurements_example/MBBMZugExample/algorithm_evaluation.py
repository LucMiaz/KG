import sys
sys.path.append('D:\GitHub\myKG')
import os, pathlib
import numpy as np
import itertools
from kg.detect import MicSignal
from kg.algorithm import *
from kg.algorithm import Case
from kg.widgets import *
from kg.measurement_values import measuredValues
from kg.measurement_signal import measuredSignal

#number o cases to prepare

mesPath = pathlib.Path('').absolute()
if __name__ == "__main__":  
    # load measured values
    mesVal = measuredValues.from_json(mesPath)
    location =  mesVal.location
    measurement = mesVal.measurement
    
    # setup  measured signal 
    measuredSignal.setup(mesPath)
    
    # setup algorithms
    # todo: parametrize alg parameter in the best possible way 
    FC = [3000]
    Treshold = [2]
    DT = [0.02]
    algorithms = []
    for fc, threshold, dt in itertools.product(FC,Treshold,DT):
        algorithms.append(ZischenDetetkt2(fc, dt,threshold))
        
    #load cases
    # todo: if necessary serialize on mesVal
    mesValues = measuredValues.from_json(mesPath)
    casePath = mesValues.path.joinpath('test_cases')
    #collect cases
    cases = []
    for authP in  casePath.iterdir():
        if authP.is_dir():
            print(authP)
            cases.extend([Case.from_JSON(cp) for cp in authP.iterdir()\
                            if cp.match('case_**.json') ])
    
    print('Case cases:')
    print('----------------------')
    for case in cases[1:3]:
        print(str(case))
        mID = case.case['mID']
        mic = case.case['mic']
        # initaite mic signal
        micSn = MicSignal.from_measurement(mesValues, mID, mic)
        for alg in algorithms:
            print(str(alg),end = ', ')
            alg.test_on_case(case, mesVal, micSn)
        print('.')
        
    #calc global Rates
    print('Calculate global Rates')
    for alg in algorithms:
        alg.calc_rates()
    # save
    print('save to json')
    for n,alg in enumerate(algorithms):
        alg.export_test_results(mesPath)


