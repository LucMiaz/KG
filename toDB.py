import pathlib
import copy
import json
from tqdm import tqdm
import numpy as np
import scipy as sp
import py2neo as pn
##setting up neo4j:
##Please start a server first and modify the following path accordingly (first is the username:password)
neopath='http://neo4j:admin@localhost:7474/db/data'
graph=pn.Graph(neopath)
pathtoext_withdata=pathlib.Path('/users/lucmiaz/Documents/TRAVAIL/SBB_KG/KG/Data')
####

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
Paths=[pathlib.Path('/Users/lucmiaz/Documents/TRAVAIL/SBB_KG/KG/Data/Biel1Vormessung/results/results_11-11-2015.json'),pathlib.Path('/Users/lucmiaz/Documents/TRAVAIL/SBB_KG/KG/Data/Biel2Vormessung/results/results_11-11-2015.json'),pathlib.Path('/Users/lucmiaz/Documents/TRAVAIL/SBB_KG/KG/Data/ZugVormessung/results/results_11-11-2015.json')]
Result={}
inputname='ResultAggregate.json'
outputname='ResultAggregate_byAlg.json'
listofmicprop={'TEL':'TEL','Tb':'Tb','Te':'Te','Tp_e':'Tp_e','Tp_b':'Tp_b'}#micValues to take from MBBM_mes_values.json 
#idValues to take from MBBM_mes_values.json
listofidprop={'Temperature':'Temp','trainType':'trainType','trainLength':'trainLenght','dir->':'direction','rain':'rain','Platform':'Gleis','Humidity':'humidity','Wind':'wind','mTime':'mTime','mDate':'mDate','v1':'v1','v2':'v2','axleProLength':'axleProLenght'}
outputname='ResultAggregate_byAlg.json'
#loads json files for each path in Paths
neolocations={}
neoalgorithms={}
algorithms={}
mbbm={}
for ort,measurementtype in [['Biel','Vormessung'], ['Biel2','Vormessung'],['Zug','Vormessung']]:
	if ort=='Biel':
		ortd='Biel1'
	else:
		ortd=ort
	pathtoext=pathtoext_withdata.joinpath(ortd+measurementtype+'/measurement_values/MBBM_mes_values.json')
	with open(pathtoext.as_posix(),'r') as mbbmvalues:
		mbbmdict=json.load(mbbmvalues)
	mbbm[ort]=copy.deepcopy(mbbmdict)
neomids={}
neomics={}
for resPath in Paths:
	with open(resPath.as_posix(),'r') as js:
		dictjs=json.load(js)
	location=dictjs['location']
	neolocations[location]=(graph.merge_one('Location',property_key='Name', property_value=location))
	
	for algorithm in dictjs['algorithms'].keys():
		if algorithm not in algorithms.keys():
			algorithms[algorithm]=copy.deepcopy(dictjs['algorithms'][algorithm])
			neoalg=graph.merge_one('Algorithm',property_key='Name',property_value=str(algorithm))
			asc=algorithms[algorithm]
			params=['fc','fmax','overlap','dt','threshold','fmin']
			for par in params:
				neoalg.properties[par]=asc['param'][par]
			neoalg.properties['class']=asc['class']
			neoalg.properties['noiseType']=asc['noiseType']
			neoalgorithms[algorithm]=neoalg
			neoalg.push()
	
	for mid in tqdm(dictjs['results'].keys()):
		ort=dictjs['location']
		#read values from mbbm_mes_values
		dictidvalues={}
		neomid=graph.merge_one('Passing',property_key='id',property_value=mid)
		for idv in listofidprop.keys():
			dictidvalues[str(idv)]=mbbm[ort]['idValues'][listofidprop[idv]]['values'][mid]
			neomid.properties[str(idv)]=dictidvalues[str(idv)]
			if idv=='trainLength':
				dictidvalues[str(idv)]=int(float(mbbm[ort]['idValues'][listofidprop[idv]]['values'][mid])+0.5)
				neomid.properties[str(idv)]=dictidvalues[str(idv)]
				trainLength=dictidvalues[str(idv)]
			elif idv=='trainType':
				dictidvalues[str(idv)]=mbbm[ort]['idValues'][listofidprop[idv]]['values'][mid]
				neomid.properties[str(idv)]=dictidvalues[str(idv)]
				train=dictidvalues[str(idv)]
			else:
				dictidvalues[str(idv)]=mbbm[ort]['idValues'][listofidprop[idv]]['values'][mid]
				neomid.properties[str(idv)]=dictidvalues[str(idv)]
		thistrain=graph.merge_one('Train', property_key='id', property_value=(train+str(trainLength)))
		thistrain.properties['Length']=trainLength
		thistrain.properties['Name']=train
		thistrain.push()
		neomics[mid]={}
		##evaluation of microphones (check path to it)
		maxtN=0
		for alg in algorithms.keys():
			alg_props=algorithms[alg]['id']+algorithms[alg]['prop']
			for mic in dictjs['results'][mid].keys():
				neomics[mid][mic]=graph.merge_one('MicMes', property_key='id',property_value=(mid+'_'+str(mic)+str(alg_props)))
				dictmicvalues={}
				for micv in listofmicprop:
					dictmicvalues[str(micv)]=mbbm[ort]['micValues'][listofmicprop[micv]]['values'][mid][mic]
					neomics[mid][mic].properties[str(micv)]=mbbm[ort]['micValues'][listofmicprop[micv]]['values'][mid][mic]
				t=dictjs['results'][mid][mic][algorithm]['t']['py/numpy.ndarray']['values']
				mask = get_mask(t, (dictmicvalues['Tb'],dictmicvalues['Te']))
				idmicresult=np.array(dictjs['results'][mid][mic][algorithm]['result']['py/numpy.ndarray']['values'], dtype=bool)
				dt=float(dictjs['results'][mid][mic][algorithm]['dt'])
				timenoise=np.sum(idmicresult[mask])*dt
				neomics[mid][mic].properties['tNoise']=np.sum(idmicresult)*dt
				neomics[mid][mic].properties['dt']=dt
				neomics[mid][mic].properties['tNoisemasked']=timenoise
				neomics[mid][mic].properties['micN']=mic
				neomics[mid][mic].push()
				if mic==1 or mic=='1':
					neomid.properties['tEval']= np.sum(mask)*dt
				graph.create(pn.Relationship(neomics[mid][mic],'ISANEVALOF',neomid))
				graph.create(pn.Relationship(neomics[mid][mic],'WASEVALWITH',neoalgorithms[alg]))

		graph.create(pn.Relationship(neomics[mid][mic],'OF',thistrain))
		graph.create(pn.Relationship(neomics[mid][mic],'IN',neolocations[location]))
		neomids[mid]=neomid#store the reference to this node with key id
		neomid.push()
		graph.push()
