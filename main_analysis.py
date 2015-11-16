import sys
sys.path.append('/Users/lucmiaz/Documents/TRAVAIL/SBB_KG/KG/Measurements_examples/MBBMZugExample')
import os, pathlib
import numpy as np
import json
import itertools
from kg.detect import MicSignal
from kg.algorithm import *
from kg.measurement_values import measuredValues
from kg.measurement_signal import measuredSignal
from tqdm import tqdm

mesPath = pathlib.Path('').absolute()
def split_list(alist, wanted_parts=1):
    length = len(alist)
    return [ alist[i*length // wanted_parts: (i+1)*length // wanted_parts] for i in range(wanted_parts) ]

if __name__ == "__main__":
    log=''
    blocks_size=1000#specifies the size of the sublists we want to break validID2 in.
	###Choose the Paths to the data
	##1. Make sure that there is a file called 
    #Paths=[pathlib.Path('E:/Biel1Vormessung'),pathlib.Path('E:/Biel2Vormessung'), pathlib.Path('E:/ZugVormessung')]
    #Paths=[pathlib.Path('E:/ZugVormessung')]
    Paths=[pathlib.Path('/Users/lucmiaz/Documents/TRAVAIL/SBB_KG/KG/Data/Biel1'),pathlib.Path('/Users/lucmiaz/Documents/TRAVAIL/SBB_KG/KG/Data/Biel2'),pathlib.Path('/Users/lucmiaz/Documents/TRAVAIL/SBB_KG/KG/Data/Zug')]
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
    npaths=len(Paths)
    cupath=1
    notincluded=[]
    for mesPath in Paths:
        # load measured values
        mesVal = measuredValues.from_json(mesPath)
        location =  mesVal.location
        measurement = mesVal.measurement
        # setup  measured signal 
        measuredSignal.setup(mesPath)
        validID = list(mesVal.get_IDs(True))
        try:
            mbbmids=mesVal.mID
            mbbmmics=mesVal.mic
        except:
            break
        validID2=[]
        for mid in mbbmids:
            if mid[0]=='m':
                for mic in mbbmmics:
                    validID2.append(mid+'_'+str(mic))
        validID2.sort()
        clipped = set()
        validlength=len(validID2)
        log.append(str(validlength))
        nblists=validlength//blocks_size
        splitvalidID=split_list(validID2,nblists)
        log+=('\n'+'Path '+str(cupath)+' of '+str(npaths))
        log+=('\n'+'Case cases in :')
        log+=('\n'+str(validID2[0])+', --- , '+str(validID2[-1])+' : '+str(len(validID2))+' items.')
        log+=('\n'+'----------------------')
        culist=1
        
        for validIDs in splitvalidID:
            log+=('\n'+'list '+str(culist)+' of '+str(nblists)+'\n')
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
                except:
                    log+=('\n'+str(ID)+'_'+str(mic)+'_'+location)
					notincluded.append(str(ID)+'_'+str(mic)+'_'+location)
                else:
                    if mS.is_initialized():
                        y, t, sR = mS.get_signal(mic)
                        ch_info = mS.channel_info(mic)
                        # get the values from measuredValues to initiate MicSignal and Case
                        var = ['Tb','Te','Tp_b','Tp_e','LAEQ']
                        micValues = mesVal.get_variables_values(ID, mic, var)
                        if micValues:
                            micValues.update(ch_info)
                            # initiate  MicSignal
                            micSn = MicSignal(ID,mic,y,t,sR, micValues)
                            # test if signal is clipped, skip it if True
                            if micSn.clippedtest():
                                clipped.add((ID,mic))
                                log+=('\n'+str(ID)+'_'+str(mic)+'_'+location+' is clipped')
                                continue
                            for alg in algorithms:
                                # calc KG
                                micSn.calc_kg(alg)
                                # set results in mesVal
                                mesVal.set_kg_values(alg,**micSn.get_KG_results(alg))
                        else:
                            log+=('\n'+str(ID)+'_'+str(mic)+'_'+location+' was mistakenly taken as mbbmtested\n')
							notincluded.append(str(ID)+'_'+str(mic)+'_'+location)
                    else:
                        try:
                            log+=('\n'+'ignoring '+str(ID)+', '+str(mic))
							notincluded.append(str(ID)+', '+str(mic)+'_'+location)
                        except:
                            log+=('\n'+'ignoring file')
            culist+=1
            mesVal.kg_values_to_json()
        cupath+=1
    log+=('\n 100%|----------------------------| Done \n')
    log+=('\n'+'Computation done')
    log+=('\n'+'Saved in paths :'+str(savingPaths))
	log+=('\n'+'The folloging items where ignored : '+str(notincluded))
	with open('main_analysis.log','w') as logfile:
		logfile.write(str(log))
	if len(notincluded)>0:
		print('\n There were some mID leftout. Please see main_analysis.log for more details')
	print('\n Analysis is over')
	
    

