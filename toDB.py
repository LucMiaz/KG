import pathlib
import copy
import json
from tqdm import tqdm
import numpy as np
import scipy as sp
import py2neo as pn

#-------------------------------------------------#
#-------------------------------------------------#
#------------VERIFY PATHS TO THE DATA,------------#
#------------TO THE DATABASE AND TO   ------------#
#------------THE EXTERNAL HARDDRIVE   ------------#
#------------CONTAINING THE DATA      ------------#
#------------OBTAINED WITH main_analysis.py ------#
#-------------------------------------------------#
#-------------------------------------------------#


##setting up neo4j:
##Please start a server first and modify the following path accordingly (first is the username:password) (THE DATABASE I MADE IS LIKE THIS neo4j:admin (i.e. neo4j is the username and admin the password)

neopath='http://neo4j:admin@localhost:7474/db/data'
graph=pn.Graph(neopath)


#---------Give the path to the external harddrive that contains the raw data ---------#
pathtoext_withdata=pathlib.Path('E:/')
####


	
#------------------------------------------------------------------------#
#---------Give the paths to the results of main_analysis.py--------------#
#---------THEY MUST BE INSIDE A FOLDER results---------------------------#
#------------------------------------------------------------------------#

Paths=[]
#Paths.append(pathtoext_withdata.joinpath('/Biel1Vormessung/results/results_11-11-2015.json'))
Paths.append(pathtoext_withdata.joinpath('Biel2Vormessung/results/results_11-11-2015.json'))
Paths.append(pathtoext_withdata.joinpath('ZugVormessung/results/results_11-11-2015.json'))

#---------------------------------------------------------------------------------#
#--------Give a list of tuples that gives location and name of the folder---------#
#--------for this location -------------------------------------------------------#
#---------------------------------------------------------------------------------#
ORTS=[['Biel','Biel1Vormessung'], ['Biel2','Biel2Vormessung'],['Zug','ZugVormessung']]#
#-----------------------------------------------------------------------------------------#
#--------Give the name of the variables (they will be taken from MBBM_mes_values.json ----#
#-------- in the path : ------------------------------------------------------------------#
#-------- pathtoext_withdata/ORTS[x][1]/'measurement_values'/MBBM_mes_values.json --------#
#-------- if a variable is not found, it will not be imported and the analysis will go on-#
#-----------------------------------------------------------------------------------------#



listofmicprop={'TEL':'TEL','Tb':'Tb','Te':'Te','Tp_e':'Tp_e','Tp_b':'Tp_b'}#micValues to take from MBBM_mes_values.json 
#idValues to take from MBBM_mes_values.json
listofidprop={'Temperature':'Temp','trainType':'trainType','trainLength':'trainLenght','direction':'direction','rain':'rain','Track':'Gleis','Humidity':'humidity','Wind':'wind','mTime':'mTime','mDate':'mDate','v1':'v1','v2':'v2','axleProLength':'axleProLenght'}
#loads json files for each path in Paths



#------------------THAT'S IT ----------------------------#
#--------------------------------------------------------#
##todo: change this to cope with different algorithms attributes !!!
algparams=['fc','fmax','overlap','dt','threshold','fmin']


#-------------------------------------------------#
#-------------------------------------------------#
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
Result={}
neolocations={}
neoalgorithms={}
algorithms={}
mbbm={}
log=''
for ort,ortpath in ORTS:
	pathtoext=pathtoext_withdata.joinpath(ortpath+'/measurement_values/MBBM_mes_values.json')
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
	measurement=dictjs['measurement']
	for algorithm in dictjs['algorithms'].keys():
		if algorithm not in algorithms.keys():
			algorithms[algorithm]=copy.deepcopy(dictjs['algorithms'][algorithm])
			neoalg=graph.merge_one('Algorithm',property_key='Name',property_value=str(algorithm))
			asc=algorithms[algorithm]
			for par in algparams:
				neoalg.properties[par]=asc['param'][par]
			neoalg.properties['class']=asc['class']
			neoalg.properties['noiseType']=asc['noiseType']
			neoalgorithms[algorithm]=neoalg
			neoalg.push()
	
	for mid in tqdm(dictjs['results'].keys()):
		ort=dictjs['location']
		#read values from mbbm_mes_values
		dictidvalues={}
		#
		neomid=pn.Node('Passing',Name=mid, Measurement=measurement)
		graph.create(neomid)
		for idv in listofidprop.keys():
			dictidvalues[str(idv)]=mbbm[ort]['idValues'][listofidprop[idv]]['values'][mid]
			if idv=='trainLength':
				dictidvalues[str(idv)]=int(float(mbbm[ort]['idValues'][listofidprop[idv]]['values'][mid])+0.5)
				trainLength=dictidvalues[str(idv)]
			elif idv=='trainType':
				dictidvalues[str(idv)]=mbbm[ort]['idValues'][listofidprop[idv]]['values'][mid]
				train=dictidvalues[str(idv)]
			elif idv=='Track':
				traintrack=mbbm[ort]['idValues'][listofidprop[idv]]['values'][mid]
			elif idv=='mDate':
				mDate=mbbm[ort]['idValues'][listofidprop[idv]]['values'][mid]
				dictidvalues['Day'],dictidvalues['Month'],dictidvalues['Year']=mDate.split('.')
				neomid.properties['Year']=dictidvalues['Year']
				neomid.properties['Month']=dictidvalues['Month']
				neomid.properties['Day']=dictidvalues['Day']
			elif idv=='mTime':
				mTime=mbbm[ort]['idValues'][listofidprop[idv]]['values'][mid]
				#converting time to human readable format
				mHour=int(mTime*24)
				mMinute=int((mTime*24-mHour)*60)
				mSecond=int(((mTime*24-mHour)*60-mMinute)*60)
				dictidvalues['Hour']=mHour
				dictidvalues['Minute']=mMinute
				dictidvalues['Second']=mSecond
				neomid.properties['Hour']=mHour
				neomid.properties['Minute']=mMinute
				neomid.properties['Second']=mSecond
			elif idv=='v1':
				v1=mbbm[ort]['idValues'][listofidprop[idv]]['values'][mid]
			elif idv=='v2':
				v2=mbbm[ort]['idValues'][listofidprop[idv]]['values'][mid]
			else:
				dictidvalues[str(idv)]=mbbm[ort]['idValues'][listofidprop[idv]]['values'][mid]
				neomid.properties[str(idv)]=dictidvalues[str(idv)]
		thistrain=graph.merge_one('TrainType', property_key='Name', property_value=train)
		neomid.push()
		neomics[mid]={}
		##evaluation of microphones (check path to it)
		maxtN=0
		for mic in dictjs['results'][mid].keys():
			neomics[mid][mic]=pn.Node('MicMes', Name=mid+'_'+str(mic))
			graph.create(neomics[mid][mic])
			neomics[mid][mic].properties['micN']=mic
			dictmicvalues={}
			addtEval=True #boolean that says if you have to add the tEval to the mic or if it was already done
			for micv in listofmicprop:
				dictmicvalues[str(micv)]=mbbm[ort]['micValues'][listofmicprop[micv]]['values'][mid][mic]
				neomics[mid][mic].properties[str(micv)]=mbbm[ort]['micValues'][listofmicprop[micv]]['values'][mid][mic]
			tevalmasked=dictmicvalues['Te']-dictmicvalues['Tb']
			tevalmasked_p= dictmicvalues['Tp_e']-dictmicvalues['Tp_b']
			neomics[mid][mic].properties['tEvalmasked']=tevalmasked
			neomics[mid][mic].properties['tEvalmaskedp']=tevalmasked_p
			for alg in algorithms.keys():
				alg_props=algorithms[alg]['id']+algorithms[alg]['prop']
				dt=float(dictjs['results'][mid][mic][alg]['dt'])
				t=dictjs['results'][mid][mic][alg]['t']['py/numpy.ndarray']['values']
				#compute masks
				mask = get_mask(t, (dictmicvalues['Tb'],dictmicvalues['Te']))#first mask on Tb to Te
				mask_p = get_mask(t, (dictmicvalues['Tp_b'],dictmicvalues['Tp_e']))#second mask on Tp_b to Tp_e
				#compute noise time
				idmicresult=np.array(dictjs['results'][mid][mic][alg]['result']['py/numpy.ndarray']['values'], dtype=bool)
				timenoise=float(int(np.sum(idmicresult)*dt*100+0.5)/100)
				timenoisemasked=float(int(np.sum(idmicresult[mask])*dt*100+0.5)/100)
				timenoisemasked_p=float(int(np.sum(idmicresult[mask_p])*dt*100+0.5)/100)
				#compute total time
				teval=len(t)*dt#calc length of full raw signal
				graph.create(pn.Relationship(neomics[mid][mic],'EVALWITH',neoalgorithms[alg],tNoise=timenoise, dt=dt,tNoisemasked=timenoisemasked,
								tNoisemasked_p=timenoisemasked_p))
				if addtEval:
					neomics[mid][mic].properties['tEval']=teval
					addtEval=False
			graph.create(pn.Relationship(neomics[mid][mic],'ISMICOF',neomid))
			neomics[mid][mic].push()
				#graph.create(pn.Relationship(neomics[mid][mic],'OF',thistrain, TrainLength=trainLength, Track=traintrack, Date=mDate, Time=mTime))
		graph.create(pn.Relationship(neomid,'SAW',thistrain,TrainLength=trainLength, V1=v1, V2=v2))
		graph.create(pn.Relationship(neomid,'IN',neolocations[location],Track=traintrack))
		neomids[mid]=neomid#store the reference to this node with key id
		neomid.push()
		graph.push()
