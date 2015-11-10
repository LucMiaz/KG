import sys
sys.path.append('Documents/TRAVAIL/SBB_KG/KG')
#sys.path.append('C:/lucmiaz/KG_dev_branch/kg')
#sys.path.append('C:/lucmiaz/KG_dev_branch/Measurements_example')
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
def split_list(alist, wanted_parts=1):
    length = len(alist)
    return [ alist[i*length // wanted_parts: (i+1)*length // wanted_parts] for i in range(wanted_parts) ]

if __name__ == "__main__":
    blocks_size=10#specifies the size of the sublists we want to break validID2 in.
    Paths=[pathlib.Path('E:/Biel1Vormessung'),pathlib.Path('E:/Biel2Vormessung'), pathlib.Path('E:/ZugVormessung')]
    #Paths=[pathlib.Path('E:/Biel1Vormessung')]
    #Paths=[pathlib.Path('Documents/TRAVAIL/SBB_KG/KG/Data/Biel1'),pathlib.Path('Documents/TRAVAIL/SBB_KG/KG/Data/Biel2'),pathlib.Path('Documents/TRAVAIL/SBB_KG/KG/Data/Zug')]
    # setup algorithms
    algorithms =[ZischenDetetkt2(4500,0.7267437,0.1), ZischenDetetkt2(3500,1.0474294,0.02)]
    print(repr(algorithms[0]))
    for path in Paths:
        try:
            path.is_dir()
        except:
            raise('path not found')
    # get list of valid ID
    savingPaths=[]
    #for testing
    # todo: remove it if all signals are in the raw_signal folder
    for mesPath in tqdm(Paths):
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
                file_n, ext=id.name.split('.')
                if ext=='mat':
                    if not id.match('zrd_**'):
                        validID2.append(file_n)
        validID2.sort()
        print(str(validID2[0])+', --- , '+str(validID2[-1])+' : '+str(len(validID2))+' items.')
        clipped = set()
        validID2=validID2[0:30]
        validlength=len(validID2)
        splitvalidID=split_list(validID2,validlength//blocks_size)
		print('Case cases in :')
            print(str(validID2[0])+', --- , '+str(validID2[-1])+' : '+str(len(validID2))+' items.')
            print('----------------------')
        for validIDs in tqdm(splitvalidID):
            for file in tqdm(validIDs):
                ID=file.split('_')[0:-1]
                id=ID[0]
                for i in range(1,len(ID)):
                    id+='_'+ID[i]
                ID=id
                mic=file.split('_')[-1]
                #print('('+ID+', '+str(mic)+')', end = '; ')
                # read the signal
                try:
                    mS = measuredSignal(ID,mic)
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
                else:
                    if mS.is_initialized():
                        y, t, sR = mS.get_signal(mic)
                        ch_info = mS.channel_info(mic)
                        # get the values from measuredValues to initiate MicSignal and Case
                        var = ['Tb','Te','Tp_b','Tp_e','LAEQ']
                        micValues = mesVal.get_variables_values(ID, mic, var)
                        micValues.update(ch_info)
                        # initiate  MicSignal
                        micSn = MicSignal(ID,mic,y,t,sR, micValues)
                        # test if signal is clipped, skip it if True
                        if micSn.clippedtest():
                            clipped.add((ID,mic))
                            print('clipped')
                            continue
                        for alg in algorithms:
                            # calc KG
                            micSn.calc_kg(alg)
                            # set results in mesVal
                            mesVal.set_kg_values(alg,**micSn.get_KG_results(alg))
                    else:
                        try:
                            print('ignoring '+str(ID)+', '+str(mic))
                        except:
                            print('ignoring file')
            mesVal.kg_values_to_json()
    print('\n 100%|----------------------------| Done \n')
    print('Computation done')
    print('Saved in paths :'+str(savingPaths))
    

