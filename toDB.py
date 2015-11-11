import pathlib
import copy
import json
from tqdm import tqdm
import numpy as np
import scipy as sp
def get_mask(t, tlim = None):
	'''
	calculate mask for time vector according tlim,
	default with MBBM evaluation
	'''
	t=np.array(t)
	if tlim is None:
		tb = t[0]
		te = t[-1]
	else:
		tb,te = tlim
	return(np.logical_and(t >= tb,t <= te))
Paths=[pathlib.Path('/Users/lucmiaz/Documents/TRAVAIL/SBB_KG/KG/Data/Biel1/results/results_11-11-2015.json'),pathlib.Path('/Users/lucmiaz/Documents/TRAVAIL/SBB_KG/KG/Data/Biel2/results/results_11-11-2015.json'),pathlib.Path('/Users/lucmiaz/Documents/TRAVAIL/SBB_KG/KG/Data/Zug/results/results_11-11-2015.json')]
Result={}
for resPath in Paths:
	with open(resPath.as_posix(),'r') as js:
		dictjs=json.load(js)
	location=dictjs['location']
	Result[location]={'description':dictjs['Description'],'location':location, 'date_of_comp':dictjs['date'],'algorithms':copy.deepcopy(dictjs['algorithms']), 'measurement':dictjs['measurement'], 'time':dictjs['time']}
	for id in tqdm(dictjs['results'].keys()):
		Result[location][id]={}
		for mic in dictjs['results'][id].keys():
			Result[location][id][mic]={}
			for algorithm in dictjs['algorithms'].keys():
				mask = get_mask(dictjs['results'][id][mic][algorithm]['t']['py/numpy.ndarray']['values'])
				idmicresult=np.array(dictjs['results'][id][mic][algorithm]['result']['py/numpy.ndarray']['values'], dtype=bool)
				dt=float(dictjs['results'][id][mic][algorithm]['dt'])
				timenoise=np.sum(idmicresult[mask])*dt
				Result[location][id][mic][algorithm]={'dt':dt,'tNoise':timenoise}
				Result[location][id]['tEval'] = np.sum(mask)*dt
with open((Paths[0].parent.parent.parent.joinpath('ResultAggregate.json')).as_posix(),'w') as output:
	json.dump(Result,output)
