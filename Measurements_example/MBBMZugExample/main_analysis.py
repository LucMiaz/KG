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
from tqdm import tqdm
#number o cases to prepare
# Todo: craete a log for detecting anomalies
# todo: use try statement in situations where errors can occur. such that evaluation is not stopped
# Todo: separate evaluation in block such thatif analysis stop  the correct we don't lost all the evaluated data
mesPath = pathlib.Path('').absolute()
if __name__ == "__main__":  
    Paths=[pathlib.Path('E:/Biel1Vormessung'),pathlib.Path('E:/Biel2Vormessung'), pathlib.Path('E:/ZugVormessung')]
    #Paths=[pathlib.Path('E:/Biel1Vormessung')]
    
    # setup algorithms
    algorithms =[ZischenDetetkt2(4500,0.7267437,0.1), ZischenDetetkt2(3500,1.0474294,0.02)]
    print(repr(algorithms[0]))
    
    # get list of valid ID
    savingPaths=[]
    #for testing
    # todo: remove it if all signals are in the raw_signal folder
    npaths=len(Paths)
    cupath=1
    for mesPath in Paths:
        print(str(cupath)+'/'+str(npaths))
        
        # load measured values
        mesVal = measuredValues.from_json(mesPath)
        location =  mesVal.location
        measurement = mesVal.measurement
        # setup  measured signal 
        measuredSignal.setup(mesPath)
        validID = list(mesVal.get_IDs(True))
        validID2 = []
        for id in mesPath.joinpath('raw_signals').iterdir():
            if id.is_file():
                file_n, ext=id.as_posix().split('.')
                if ext=='mat':
                    if file_n.split('/')[-1][0]!='zrd':
                        file=file_n.split('/')[-1]
                        validID2.append(file)
        
        clipped = set()
        print('Case cases:')
        print('----------------------')
        for file in tqdm(validID2):
            try:
                ID=file.split('_')[0:-1]
                id=ID[0]
                for i in range(1,len(ID)):
                    id+='_'+ID[i]
                ID=id
                mic=file.split('_')[-1]
                #print('('+ID+', '+str(mic)+')', end = '; ')
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
            except KeyError:
                print('Key not found : ')
                try:
                    print(str(file))
                except:
                    print('Not able to print file name')
            except:
                try:
                    mesVal.kg_values_to_json()
                except:
                    try:
                        print(str(mesVal))
                    except:
                        print('Could not save to json')
        print(str(cupath)+'/'+str(npaths)+'100%| Done')
        print('saving to json')
        mesVal.kg_values_to_json()
        try:
            print('saved at : '+str(cupath)+' of '+str(npaths))
            print('in file '+mesVal.get_path())
            savingPaths.append(mesVal.get_path())
        except:
            print('saved. No more info could be printed')
        cupath+=1
    print('Computation done')
    print('Saved in paths :'+str(savingPaths))
    

