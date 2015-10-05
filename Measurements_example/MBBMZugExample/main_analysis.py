import sys
sys.path.append('D:\GitHub\myKG')
import os, pathlib
import numpy as np
import json
import itertools
from kg.detect import MicSignal
from kg.algorithm import *
from kg.measurement_values import measuredValues
from kg.measurement_signal import measuredSignal

#number o cases to prepare
# Todo: craete a log for detecting anomalies
# todo: use try statement in situations where errors can occur. such that evaluation is not stopped
# Todo: separate evaluation in block such thatif analysis stop  the correct we don't lost all the evaluated data
mesPath = pathlib.Path('').absolute()
if __name__ == "__main__":  
    # load measured values
    mesVal = measuredValues.from_json(mesPath)
    location =  mesVal.location
    measurement = mesVal.measurement
    
    # setup  measured signal 
    measuredSignal.setup(mesPath)
    
    # setup algorithms
    algorithms =[ZischenDetetkt2(3000,0,0.02), ZischenDetetkt2(2000,0,0.05)]
    print(repr(algorithms[0]))
    
    # get list of valid ID
    validID = list(mesVal.get_IDs(True))
    validID2 = []
    #for testing
    # todo: remove it if all signals are in the raw_signal folder
    for id in ['m_0100','m_0101','m_0102','m_0103','m_0104','m_0105','m_0106','m_0107']:
        if id in validID:
            validID2.append(id)
        
    clipped = set()
    IDxMic = list(itertools.product(validID2, mesVal.mic))
    print('Case cases:')
    print('----------------------')
    for ID , mic in IDxMic:
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
        for alg in algorithms:
            # calc KG
            micSn.calc_kg(alg)
            # set results in mesVal
            mesVal.set_kg_values(alg,**micSn.get_KG_results(alg))
        #
    print('finish')
    print('save to json')
    mesVal.kg_values_to_json()

