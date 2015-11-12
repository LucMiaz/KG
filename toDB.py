import pathlib
import copy
import json
from tqdm import tqdm
import numpy as np
import scipy as sp
import py2neo as pn
##setting up neo4j:
##Please start a server first and modify the following path accordingly (first is the username:password)
neopath='http://neo4j:zivi@localhost:7474/db/data'
graph=pn.Graph(neopath)

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
Paths=[pathlib.Path('/Users/lucmiaz/Documents/TRAVAIL/SBB_KG/KG/Data/Biel1/results/results_11-11-2015.json'),pathlib.Path('/Users/lucmiaz/Documents/TRAVAIL/SBB_KG/KG/Data/Biel2/results/results_11-11-2015.json'),pathlib.Path('/Users/lucmiaz/Documents/TRAVAIL/SBB_KG/KG/Data/Zug/results/results_11-11-2015.json')]
Result={}
inputname='ResultAggregate.json'
outputname='ResultAggregate_byAlg.json'
listofmicprop={'TEL':'TEL','Tb':'Tb','Te':'Te','Tp_e':'Tp_e','Tp_b':'Tp_b'}#micValues to take from MBBM_mes_values.json 
#idValues to take from MBBM_mes_values.json
listofidprop={'°C':'Temp','trainType':'trainType','trainLen':'trainLenght','dir->':'direction','rain':'rain','Platform':'Gleis','Humidity':'humidity','Wind':'wind','mTime':'mTime','mDate':'mDate','v1':'v1','v2':'v2','axleProLength':'axleProLenght'}
outputname='ResultAggregate_byAlg.json'
#loads json files for each path in Paths
neolocations={}
neoalgorithms={}
algorithms={}
graph.schema.create_uniqueness_constraint("Train", "nom")
graph.schema.create_uniqueness_constraint("Passing", "mID")
graph.schema.create_uniqueness_constraint("Location","Name")
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
	neolocations[location]=(pn.merge_one('Location',property_key='Name', property_value=location))
	
	for algorithm in dictjs[location]['algorithms'].keys():
		if algorithm not in algorithms.keys():
			algorithms[algorithm]=copy.deepcopy(dictjs[location]['algorithms'])
			neoalg=pn.merge_one('Algorithm',property_key='Name',property_value=str(algorithm))
			asc=algorithms[algorithm]
			params=['fc','fmax','overlap','dt','threshold','fmin']
			for par in params:
				neoalg.properties[par]=asc['param'][par]
			neoalg.properties['class']=asc['class']
			neoalg.properties['noiseType']=asc['noiseType']
			neoalgorithms[algorithm]=neoalg
	
	for id in dictjs['results'].keys():
		ort=dictjs['results'][id]['location']
		#read values from mbbm_mes_values
		dictidvalues={}
		for idv in listofidprop.keys():
			dictidvalues[str(idv)]=mbbmdict['idValues'][listofidprop[idv]]['values'][mid]
		neomid=graph.merge_one('Passing',property_key='id',property_value=mid)
		neomid.properties=dictidvalues
		neomics[mid]={}
		##evaluation of microphones (check path to it)
		maxtN=0
		for alg in algorithms:
			alg_props=alg['description']['id']+alg['description']['prop']
			for mic in dictjs['results'][mid][mics].keys():
				neomics[mid][mic]=graph.merge_one('MicMes', property_key='id',property_value=(mid+'_'+str(mic)+str(alg_props)))
				dictmicvalues={}
				for micv in listofmicprop:
					dictmicvalues[str(micv)]=mbbmdict['micValues'][listofmicprop[micv]]['values'][mid][mic]
					neomics[mid][mic].properties[str(micv)]=mbbmdict['micValues'][listofmicprop[micv]]['values'][mid][mic]
				t=dictjs['results'][id][mic][algorithm]['t']['py/numpy.ndarray']['values']
				mask = get_mask(t, (dictmicvalues['Tb'],dictmicavlues['Te']))
				idmicresult=np.array(dictjs['results'][id][mic][algorithm]['result']['py/numpy.ndarray']['values'], dtype=bool)
				dt=float(dictjs['results'][id][mic][algorithm]['dt'])
				timenoise=np.sum(idmicresult[mask])*dt
				neomic[mid][mic].properties['tNoise']=np.sum(idmicresult)*dt
				neomic[mid][mic].properties['dt']=dt
				neomic[mid][mic].properties['tNoisemasked']=timenoise
				neomic[mid][mic].properties['micN']=mic
				if mic==1 or mic=='1':
					neomid.properties['tEval']= np.sum(mask)*dt
				graph.create(pn.Relationship(neomic[mid][mic],'ISANEVALOF',neomid)
				graph.create(pn.Relationship(neomic[mid][mic],'WASEVALWITH',neoalgorithms[alg])
		train=neomid.properties['trainType']
		trainLength=int(neomid.properties['trainLenght']+0.5)###check spelling in json
		thistrain=graph.merge_one('Train', property_name='id', property_value=(train+str(trainLength)))
		thistrain.properties['Length']=trainLength
		thistrain.properties['Name']=train
		graph.create(pn.Relationship(neomic[mid][mic],'OF',thistrain)
		graph.create(pn.Relationship(neomic[mid][mic],'IN',neolocations[location])
		neomids[id]=neomid#store the reference to this node with key id