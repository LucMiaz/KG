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
import seaborn as sns

#number o cases to prepare
try:
    mesPath = pathlib.Path('C:\lucmiaz\KG_dev_branch\KG\measurements_example\MBBMZugExample')
except PermissionError:
    mesPath = pathlib.Path('d:\github\mykg\measurements_example\MBBMZugExample')
if __name__ == "__main__":  
    # load measured values
    mesVal = measuredValues.from_json(mesPath)
    location =  mesVal.location
    measurement = mesVal.measurement
    
    # setup  measured signal 
    measuredSignal.setup(mesPath)
    
    # setup algorithms
    # todo: parametrize alg parameter in the best possible way 
    algorithm = ZischenDetetkt2(3000,2,0.02)
        
    ##load cases
    
    # todo: if necessary serialize on mesVal
    mesValues = measuredValues.from_json(mesPath)
    casePath1 = mesValues.path.joinpath('test_cases/esr/case_m_0101_4_esr.json')
    case1 = Case.from_JSON(casePath1)
    casePath2 = mesValues.path.joinpath('test_cases/esr/case_m_0100_6_esr.json')
    case2 = Case.from_JSON(casePath2)
    ##
    case = case2
    micSn = MicSignal.from_measurement(mesVal,case.case['mID'],case.case['mic'])
    micSn.calc_kg(algorithm)
    ##
    #sns.color_palette("hls", 4)

    app=QtGui.QApplication()
 ##   
    W = CompareCaseAlgWidget([algorithm],mesVal,case)
    #W=CompareCaseAlgWidget.from_wav(pathlib.Path('C:/lucmiaz/KG_dev_branch/KG/Measurements_example/various_passby/kreischen.wav'), [algorithm])
    W.show()
    


