import sys
sys.path.append('D:\GitHub\myKG')
import os, pathlib
import numpy as np
import random
import pickle
import json

from kg.detect import MicSignal
from kg.case import Case
from kg.measurement_values import measuredValues
from kg.measurement_signal import measuredSignal
import itertools

#number o cases to prepare
NCases = 10
caseToAnalyze = {}
    

if __name__ == "__main__":
    
    mainPath = pathlib.Path('').absolute()
    if len(sys.argv):
        print(sys.argv)
        pass
    mesPath = mainPath.parent
    #setup measurement
    
    mesVal = measuredValues.from_json(mesPath)
    location =  mesVal.location
    measurement = mesVal.measurement
    # setup  signal 
    measuredSignal.setup(mesPath)
    # get list of valid ID
    validID = list(mesVal.get_IDs(True))
    validID2 = []
    #for testing
    for id in ['m_0100','m_0101','m_0102','m_0103','m_0104','m_0105','m_0106','m_0107']:
        if id in validID:
            validID2.append(id)
    clipped= set()
    IDxMic = list(itertools.product(validID2, mesVal.mic))
    print('Random selected cases:')
    print('----------------------')
    while len(caseToAnalyze) < NCases:
        # caseDict to fill
        caseDict={}
        # select randomly a case mic tuple
        case_n = np.random.randint(len(IDxMic))
        ID , mic = IDxMic.pop(case_n)
        print('('+ID+', '+str(mic)+')', end = '; ')
        # read the signal
        mS = measuredSignal(ID,mic)
        y, t, sR = mS.get_signal(mic)
        ch_info = mS.channel_info(mic)
        # get the values from measuredValues to initiate MicSignal and Case
        var = ['Tb','Te','Tp_b','Tp_e','LAEQ']
        micValues = mesVal.get_variables_values(ID, mic, var)
        micValues.update(ch_info)
        # initiate  MicSignal
        micSn = MicSignal(ID,mic,y,t,sR, micValues)
        # test if signal is clipped, skipü it if True
        if micSn.clippedtest():
            clipped.add((ID,mic))
            print('clipped')
            continue
        # create Wav and add path to caseDict
        caseDict['wavPath'] = str(micSn.export_to_Wav(mesPath))
        # initialize empty Case with None author
        caseDict['case'] = {'measurement' : measurement, 'location': location,
         'mID':ID, 'mic':mic,\
         'Tb': micValues['Tb'], 'Te': micValues['Te'], 'author' : None}
        #add tmin tmax
        caseDict['tmin'] = float(t.min())
        caseDict['tmax'] = float(t.max())
        # Add data to plot ; key:[t,y] , #key is label of plot
        caseDict['plotData'] = {}
        # first plot prms
        y,t,_ = mS.get_signal('prms' + str(mic))
        caseDict['plotData']['LAfast']=[t.tolist(),(20*np.log10(y/(2e-5))).tolist()]
        # second plot prms
        # todo: plot stft band
        # append Case Dict to  dict
        caseToAnalyze[ID +'_' + str(mic)] = caseDict
print('')        
print('clipped signals:', clipped)
## export to json
with mainPath.joinpath('caseToAnalyze.json').open('w+') as output:
    json.dump(caseToAnalyze, output)
