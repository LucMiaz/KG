import sys
sys.path.append('D:\GitHub\myKG')
import os, pathlib
import numpy as np
from PySide import QtGui, QtCore
import random

from kg.detect import MicSignal
from kg.case import Case
from kg.widgets import CaseCreatorWidget
from kg.measurement_values import measuredValues
from kg.measurement_signal import measuredSignal
from kg.algorithm import ZischenDetetkt1
import itertools


#number o cases to prepare
NCases = 100
setOfCases = {}

if __name__ == "__main__":
    #setup measurement
    mesPath = 'D:\GitHub\myKG\Measurements_example\MBBMZugExample'
    mesVal = measuredValues.from_json(mesPath)
    location =  mesVal.location
    measurement = mesVal.measurement
    # setup  signal 
    measuredSignal.setup(mesPath)
    #
    validID = list(mesVal.get_IDs(True))
    IDxMic = list(itertools.product(validID, mesVal.mic))
    while len(setOfCases) < NCases:
        case_dict={}
        select
        case_n = np.random.randint(len(IDxMic)):
        ID,mic = IDxMic.pop(case_n)
        mS = measuredSignal(ID,mic)
        y,t,sR = mS.get_signal(mic)
        ch_info = mS.channel_info(mic)
        var = ['Tb','Te','Tp_b','Tp_e','LAEQ']
        micValues = mesValues.get_variables_values(ID, mic, var)
        micValues.update(ch_info)
        micSn = MicSignal(ID,mic,y,t,sR, micValues, str(mesValues.path)
        #test if signal is clipped
        if not micSn.clippedtest():
            break
            
        case_dict['wavPath'] = micSn.export_to_wav()
        # initialize empty case
        case_dict['case'] = Case(measurement, location, ID,\
         micValues['Tb'], micValues['Te'], None)
        #graphics
        case_dict['graphics'] = {}
        y,t,_ = ts.get_signal('prms'+str(mic))
        plt.plot(t,np.abs(20*np.log10(y/(2e-5))))
        #append to dict
        setOfCases[ID +'_' + str(mic)] = case_dict
    
    # export to picle 
    
    
    #run if 
    if run:

        W = CaseCreatorWidget.from_measurement(mesVal,mID, mic,'esr')
        W.show()
        sys.exit(app.exec_())
    
    