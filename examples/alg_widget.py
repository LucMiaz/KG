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
    textcolor='#f5f5f5'
    axescolor='#f5f5f5'
    axbgcolor='#272822'
    bgcolor='#aaaaaa'
    matplotlib.rcParams['axes.facecolor']=bgcolor
    matplotlib.rcParams['axes.edgecolor']=axescolor
    for i in ['x','y']:
        matplotlib.rcParams['xtick.color']=axescolor
    matplotlib.rcParams['grid.color']=textcolor
    matplotlib.rcParams['ytick.color']=axescolor
    matplotlib.rcParams['figure.edgecolor']=axescolor
    matplotlib.rcParams['patch.linewidth']='0.5'
    matplotlib.rcParams['lines.color']='#7b3294'
    matplotlib.rcParams['lines.linewidth']='0.75'
    matplotlib.rcParams['axes.linewidth']='0.4'
    matplotlib.rcParams['xtick.major.width']='0.4'
    matplotlib.rcParams['ytick.major.width']='0.4'
    matplotlib.rcParams['xtick.minor.width']='0.3'
    matplotlib.rcParams['xtick.minor.width']='0.3'
    matplotlib.rcParams['text.color']=textcolor
    matplotlib.rcParams['axes.labelcolor']='#f5f5f5'
    matplotlib.rcParams['font.family']='HelveticaNeue'
    font={'family':'sans-serif','weight':'regular','size':11}
    matplotlib.rc('font',**font)
    f,axes = plt.subplots(2,sharex = True)
    ax = axes[0]
    micSn.plot_triggers(ax,color = '#f5f5f5',lw=1)
    micSn.plot_BPR(algorithm, ax, color = '#f5f5f5', linewidth=1)
    case.plot(ax)
    ax.set_xlim(-0.5,8)
    ymin,ymax = ax.get_ylim()
    ax=axes[1]
    alg_res = micSn.get_KG_results(algorithm)['result']
    micSn.plot_BPR(algorithm, ax, color = '#f5f5f5', lw=1)
    case.plot_compare(ax,alg_res['result'], alg_res['t'])
    plt.show()
    
 ##   
    W = CompareCaseAlgWidget(mesVal,case,[algorithm])
    W.show()


