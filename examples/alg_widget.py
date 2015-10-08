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
    mesPath = pathlib.Path('C:/lucmiaz/KG_dev_branch/KG')
except:
    mesPath = pathlib.Path('d:\github\mykg')
if __name__ == "__main__":  
    
    
    app=QtGui.QApplication()
    CTW=QtGui.QWidget()
    algorithmclass, valid=QtGui.QInputDialog.getItem(CTW,"Algorithm","Please select an algorithm type", [str(cls.__name__) for cls in vars()['Algorithm'].__subclasses__()])
    if valid:
        print(algorithmclass)
        algorithm=eval(algorithmclass+"askforattributes(CTW)")
    # setup algorithms
    # todo: parametrize alg parameter in the best possible way 
    algorithm = ZischenDetetkt2(3000,2,0.02)
        
    ##load cases
    # load measured values
    jsonpath=mesPath.joinpath(pathlib.Path('measurements_example/MBBMZugExample'))
    mesVal = measuredValues.from_json(jsonpath)
    location =  mesVal.location
    measurement = mesVal.measurement
    
    # setup  measured signal 
    measuredSignal.setup(jsonpath)
    # todo: if necessary serialize on mesVal
    mesValues = measuredValues.from_json(jsonpath)
    casePath1 = mesValues.path.joinpath('test_cases/esr/case_m_0101_4_esr.json')
    case1 = Case.from_JSON(casePath1)
    casePath2 = mesValues.path.joinpath('test_cases/esr/case_m_0100_6_esr.json')
    case2 = Case.from_JSON(casePath2)
    ##
    case = case2
    micSn = MicSignal.from_measurement(mesVal,case.case['mID'],case.case['mic'])
    micSn.calc_kg(algorithm)
    ##

    f,axes = plt.subplots(2,sharex = True)
    ax = axes[0]
    micSn.plot_triggers(ax,color = '#272822',lw=1)
    micSn.plot_BPR(algorithm, ax, color = '#272822', linewidth=1)
    case.plot(ax)
    ax.set_xlim(-0.5,8)
    ymin,ymax = ax.get_ylim()
    ax=axes[1]
    alg_res = micSn.get_KG_results(algorithm)['result']
    micSn.plot_BPR(algorithm, ax, color = '#272822', lw=1)
    case.plot_compare(ax,alg_res['result'], alg_res['t'])
    plt.show()

    
 ##   
    
    #W = CompareCaseAlgWidget.from_measurement(mesVal, [algorithm], case)
    #Q = CompareCaseAlgWidget.from_measurement(mesVal, [algorithm], ID='m_0100',mic=6)
    wavPath = mesPath.joinpath('Measurements_example/various_passby/kreischen.wav')
    R=CompareCaseAlgWidget.from_wav(wavPath,[algorithm])
    #W.show()
    R.show()
    


