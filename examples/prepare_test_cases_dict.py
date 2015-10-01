import sys
sys.path.append('D:\GitHub\myKG')
import os, pathlib
import numpy as np
import random
import pickle
from PySide import QtGui, QtCore


from kg.detect import MicSignal
from kg.case import Case
from kg.widgets import CaseCreatorWidget
from kg.measurement_values import measuredValues
from kg.measurement_signal import measuredSignal
from kg.algorithm import ZischenDetetkt1
import itertools


#number o cases to prepare
NCases = 100
caseToAnalyze = {}

if __name__ == "__main__":
    #setup measurement
    mesPath = 'D:\GitHub\myKG\Measurements_example\MBBMZugExample'
    mesVal = measuredValues.from_json(mesPath)
    location =  mesVal.location
    measurement = mesVal.measurement
    # setup  signal 
    measuredSignal.setup(mesPath)
    # get list of valid ID
    validID = list(mesVal.get_IDs(True))
    IDxMic = list(itertools.product(validID, mesVal.mic))
    while len(setOfCases) < NCases:
        # caseDict to fill
        caseDict={}
        # select randomly a case mic tuple
        case_n = np.random.randint(len(IDxMic)):
        ID , mic = IDxMic.pop(case_n)
        # read the signal
        mS = measuredSignal(ID,mic)
        y, t, sR = mS.get_signal(mic)
        ch_info = mS.channel_info(mic)
        # get the values from measuredValues to initiate MicSignal and Case
        var = ['Tb','Te','Tp_b','Tp_e','LAEQ']
        micValues = mesValues.get_variables_values(ID, mic, var)
        micValues.update(ch_info)
        # initiate  MicSignal
        micSn = MicSignal(ID,mic,y,t,sR, micValues, str(mesValues.path)
        # test if signal is clipped, skipü it if True
        if not micSn.clippedtest():
            clipped.add((ID,mic))
            continue
        # create Wav and add path to caseDict
        caseDict['wavPath'] = micSn.export_to_wav()
        # initialize empty Casewith None author
        caseDict['case'] = Case(measurement, location, ID,\
         micValues['Tb'], micValues['Te'], None)
        # Add data to plot ; key:[t,y] , #key is label of plot
        caseDict['plotData'] = {}
        # first plot prms
        y,t,_ = ts.get_signal('prms' + str(mic))
        caseDict['plotData']['LAfast']=[t,np.abs(20*np.log10(y/(2e-5))))]
        
        # second plot prms
        y,t,_ = ts.get_signal('prms' + str(mic))
        caseDict['plotData']['LAfast']=[t,np.abs(20*np.log10(y/(2e-5))))]
        # append Case Dict to  dict
        caseToAnalyze[ID +'_' + str(mic)] = caseDict
        
# export to pikle