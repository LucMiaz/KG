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
    
    Paths=[]
    Paths.append(pathlib.Path('E:/ZugVormessung'))
    Paths.append(pathlib.Path('E:/Biel1Vormessung'))
    app=QtGui.QApplication()
    CTW=QtGui.QWidget()
    graphical=False
    if graphical:
        algorithmclass, valid=QtGui.QInputDialog.getItem(CTW,"Algorithm","Please select an algorithm type", [str(cls.__name__) for cls in vars()['Algorithm'].__subclasses__()])
        if valid:
            algorithm=eval(algorithmclass+".askforattributes(CTW)")
    # setup algorithms
    # todo: parametrize alg parameter in the best possible way 
    algorithms = [ZischenDetetkt2(4000,0.79088,0.02)]
    
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
    casePath1 = mesValues.path.joinpath('test_cases/luc/case_m_1656_4_luc.json')
    case1 = Case.from_JSON(casePath1)
    casePath2 = mesValues.path.joinpath('test_cases/luc/case_m_2791_1_luc.json')
    case2 = Case.from_JSON(casePath2)
    ##
    case = case2
    micSn, mesVal = MicSignal.from_measurement(case.case['mID'],case.case['mic'], Paths)
    micSn.calc_kg(algorithms[0])
    ##
    if 2<1:
        f,axes = plt.subplots(2,sharex = True)
        ax = axes[0]
        micSn.plot_triggers(ax,color = '#272822',lw=1)
        micSn.plot_BPR(algorithm, ax, color = '#272822', linewidth=1)
        case.plot(ax)
        ax.set_xlim(-0.5,8)
        ymin,ymax = ax.get_ylim()
        ax=axes[1]
        alg_res = micSn.get_KG_results(algorithm)['result']
        micSn.plot_BPR(algorithms[0], ax, color = '#272822', lw=1)
        case.plot_compare(ax,alg_res['result'], alg_res['t'])
        plt.show()

   
 ##   
    
    W = CompareCaseAlgWidget.from_measurement(mesVal, algorithms, case)
    #Q = CompareCaseAlgWidget.from_measurement(mesVal, [algorithm], ID='m_0100',mic=6)
    #Q.setPalette(palettesimple(True))
    W.setPalette(palettesimple(True))
    #wavPath = mesPath.joinpath('Measurements_example/various_passby/zischen.wav')
    #R=CompareCaseAlgWidget.from_wav(wavPath,[algorithm])
    #R.setPalette(palettesimple(True))
    W.show()
    #R.show()
    #Q.show()


