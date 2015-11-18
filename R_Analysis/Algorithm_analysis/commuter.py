"""Merges the json files produced by algorithm_evaluation.py in one csv file and one json file. This makes the import in R easier."""
import sys
import os,pathlib
import itertools
import json
import math
import csv

def extract_for_R(filespath,listofspec=['BPR'],outputname='Datamaous'):
    """constructs a list of elements for use in R"""
    ## insert folder path
    if not isinstance(filespath,pathlib.Path):
        filespath=pathlib.Path(filespath)
    parentfilepath=filespath.parent
    ## insert possible algorithm specific values (like BPR for Z2)
    listofspec=['BPR']#insert
    #import of the following values
    datamaous=[]
    keys=['mic', 'mID', 'location', 'author','quality', 'time', 'disc', 'NoiseT', 'alg', 'algprop','disct','spec']
    
    qualitydict={'good':3,'medium':2,'bad':1,'NA':0}
    discdict={0:'F',1:'T'}
    with parentfilepath.joinpath(str(outputname)+'.csv').open("w") as ostream:
        writer=csv.DictWriter(ostream, delimiter=',', lineterminator='\n', fieldnames=keys)
        titlerow={}
        for key in keys:
            titlerow[key]=str(key)
        writer.writerow(titlerow)
        for file in filespath.iterdir():
            if file.match("**.json"):#checks if file is a json
                with filespath.joinpath(file).open("r+") as istream:#opens file
                    dictio=json.load(istream)#loads json file
                Cases=dictio['case_tests']#takes the dedicated dictionnary for R
                algorithm=dictio['algorithm']['id']
                algorithmprop=dictio['algorithm']['prop']
                noise=dictio['algorithm']['noiseType']
                for case in Cases:#iterates over cases
                    mID=Cases[case]['mID']
                    mic=Cases[case]['mic']
                    author=Cases[case]['author']
                    quality=qualitydict[Cases[case]['quality']]
                    quality=qualitydict[Cases[case]['quality']]
                    location=Cases[case]['location']
                    for t in Cases[case]['t']:
                        if t>=Cases[case]['tb'] and t<=Cases[case]['te']:
                            i=Cases[case]['t'].index(t)
                            for sp in listofspec:
                                if sp in Cases[case].keys():
                                    ckey=sp
                                    break
                            if not ckey:
                                break
                            else:
                                if not math.isnan(float(Cases[case].get(ckey)[i])):
                                    row={}
                                    row['spec']=Cases[case][ckey][i]
                                    row['disc']=Cases[case]['disc'][i]
                                    row['disct']=discdict[Cases[case]['disc'][i]]
                                    row['mID']=mID
                                    row['mic']=mic
                                    row['author']=author
                                    row['quality']=quality
                                    row['alg']=algorithm
                                    row['algprop']=algorithmprop
                                    row['time']=t
                                    row['location']=location
                                    row['NoiseT']=noise
                                    datamaous.append(row)
                                    writer.writerow(row)
    try:
        os.remove(parentfilepath.joinpath(str(outputname)+'.json'))
    except:
        pass
    with parentfilepath.joinpath(str(outputname)+'.json').open("w+") as ostream:
        json.dump(datamaous,ostream)
def extract_rates(filespath,outputname='Datamaous_2'):
    ## insert folder path
    if not isinstance(filespath,pathlib.Path):
        filespath=pathlib.Path(filespath)
    parentfilepath=filespath.parent
    ## insert possible algorithm specific values (like BPR for Z2)
    listofspec=['BPR']#insert
    #import of the following values
    datamaous={}
    authors=['esr','luc','PHF','PhC']
    keys=['TPR', 'TNR', 'FPR', 'FNR','d_ax','dist_ax']
    fieldnm=list(keys)
    for author in authors:
        for key in keys:
            fieldnm.append(author+'_'+key)
    fieldnm.append('algprop')
    fieldnm.append('thd')
    fieldnm.append('alg')
    with parentfilepath.joinpath(str(outputname)+'.csv').open("w") as ostream:
        writer=csv.DictWriter(ostream, delimiter=',', lineterminator='\n', fieldnames=fieldnm)
        titlerow={}
        for key in keys:
            titlerow[key]=str(key)
        for author in authors:
            for key in keys:
                titlerow[author+'_'+key]=str(author+'_'+key)
        writer.writerow(titlerow)
        for file in filespath.iterdir():
            if file.match("**.json"):#checks if file is a json
                with filespath.joinpath(file).open("r+") as istream:#opens file
                    dictio=json.load(istream)#loads json file
                row={}
                for key in keys:
                    if not (key=='d_ax' or key=='dist_ax'):
                        row[key]=dictio['rates'][key]
                row['d_ax']=(dictio['rates']['TPR']+dictio['rates']['FPR'])/2
                row['dist_ax']=((row['d_ax']-dictio['rates']['TPR'])**2+(row['d_ax']-dictio['rates']['FPR'])**2)**0.5
                for author in authors:
                    for key in keys:
                        if key=='d_ax' or key=='dist_ax':
                            if key=='d_ax':
                                row[author+'_d_ax']=(dictio['rates'][author]['TPR']+dictio['rates'][author]['FPR'])/2
                                row[author+'_dist_ax']=((row[author+'_d_ax']-dictio['rates'][author]['TPR'])**2+(row[author+'_d_ax']-dictio['rates'][author]['FPR'])**2)**0.5
                        else:
                            row[author+'_'+key]=dictio['rates'][author][key]
                        
                row['algprop']=dictio['algorithm']['prop']
                row['thd']=dictio['algorithm']['param']['threshold']
                row['alg']=dictio['algorithm']['id']
                writer.writerow(row)
if __name__=="__main__":
    #extract_for_R("C:/lucmiaz/Algorithms-analysis-report/results")
    extract_rates('C:/lucmiaz/algorithms-analysis-report/WallofFame/results')