import scipy as sp
import scipy.io
import numpy as np
import pandas as pd
import copy
import collections
import xlrd
import csv,json
import datetime
import pathlib
import warnings
import datetime

def read_MBBM_tables(mesPath, save = False):
    '''
    load values of selected variables and mic form MBBM files
    '''
    mesPath = pathlib.Path(mesPath)
    with mesPath.joinpath('measurement_config.json').open('r+') as config:
        CONFIG = json.load(config)
    TABLES = CONFIG['tables']
    MICVALUES = CONFIG['micValues']
    IDVALUES = CONFIG['idValues']
    Mic = CONFIG['microphones']
    tablesPath = mesPath.joinpath('measurement_values')
    print('----------\n')
    print('Read MBBM exel tables \n----------\n\nMIC VALUES \n-----------')
    for k,v in MICVALUES.items():
        print(k,', ', end='')
        table = TABLES[v['table']]
        wb = xlrd.open_workbook(str(tablesPath.joinpath(table['fileName'])))
        #if Spectrum
        if k == 'LAf':
            S_mic = []
            data = {}
            for mic in Mic:
                sN = v['sheet'].replace('_Miki','_Mik'+ str(mic))
                ws = wb.sheet_by_name(sN)
                for row in range(table['skip']+1,ws.nrows):
                    S_mic = [ws.cell_value(row,i) for i in range(1,25)]
                    try:
                        dictID = data[ws.cell_value(row,0)]
                    except KeyError:
                        data[ws.cell_value(row,0)] = {}
                        dictID = data[ws.cell_value(row,0)]
                    dictID[str(mic)] = S_mic
            v['values'] = data
        #if mic single valued value
        else:
            #ID column
            ws = wb.sheet_by_name(v['sheet'])
            #ws starting row number of  
            wsRow0 = table['skip']
            # col names Table in excel ws
            colNames = ws.row_values(wsRow0)
            #index of selectd columns
            cN = [(v['colName']).replace('_i','_'+ str(mic)) for mic in Mic]
            selectCol = [colNames.index(i) for i in cN] 
            data = {}
            for row in range(wsRow0+1,ws.nrows):
                mic_val = {}
                for i,mic in zip(selectCol,Mic):
                    mic_val[str(mic)] = ws.cell_value(row,i) 
                data[ws.cell_value(row,0)] = mic_val
            v['values'] = data
    #if IDVALUES value
    print('\n\nIDVALUES \n-----------')        
    for k,v in IDVALUES.items():
        print(k,', ', end='')
        table = TABLES[v['table']]
        wb = xlrd.open_workbook(str(tablesPath.joinpath(table['fileName'])))
        ws = wb.sheet_by_name(v['sheet'])
        # col names Table
        colNames = ws.row_values(table['skip'])
        selectCol = colNames.index(v['colName']) 
        data = {}
        for row in range(table['skip']+1, ws.nrows):
            data[ws.cell_value(row,0)] = ws.cell_value(row,selectCol)
        v['values'] = data
    print('\n\nFinish read values\n----------\n')
    # return dict
    MBBM_data = collections.OrderedDict()
    MBBM_data['location'] = CONFIG['location']
    MBBM_data['measurement'] = CONFIG['measurement']
    MBBM_data['tables'] = TABLES
    MBBM_data['micValues'] = MICVALUES
    MBBM_data['idValues'] = IDVALUES
    MBBM_data['mic'] = Mic
    if save:
        dataPath = mesPath.joinpath('measurement_values/MBBM_mes_values.json')
        with dataPath.open('w+') as data:
            json.dump(MBBM_data, data)
        print('Data saved to ' + mesPath.as_posix())
    return(MBBM_data)
        

class measuredValues():
    def __init__(self,mesPath, location, measurement, tables, micValues, idValues , mic):
        '''
        handle  the measurement database
        parameters
        ----------
        path: main path of measurement
        
        '''
        self.path = pathlib.Path(mesPath)
        self.location = location
        self.measurement = measurement
        self.tables = tables
        self.micValues = micValues 
        self.idValues = idValues
        self.mic = mic
        self.kgValues = {'algorithms':{},'results':{}}
                
    def list_variables(self):
        """
        list all possible variables in data
        """
        var ={'variable':[],'description':[]}
        for k, v in list(self.idValues.items()) + list(self.micValues.items()):
            var['variable'].append(k)
            var['description'].append(v['description'])
        var = pd.DataFrame(var)
        return(var)

    def get_IDs(self, evaluated = False):
        if not evaluated:
            Index = self.idInfo['mTime']['values'].index.tolist()
        else:
            Index = self.micValues['LAEQ']['values'].index.tolist()
        return(Index)
        
    def get_variables_values(self,ID, mic, variables):
        """
        parameter:
        ----------
        ID: list of ID
        mic: mic list or int
        Variables: list of variables
        return:
        dict of df of the variables
        """
        if not isinstance(ID,list):
            ID =  [ID]
        dict={}
        for id in ID: 
            for var in variables:
                if var in self.idValues.keys():
                    val = self.idValues[var].get('values').get(id)
                    dict.setdefault(id,{})[var] = val
                elif var in self.micValues.keys():
                    val = copy.deepcopy(self.micValues[var].get('values').get(id,{}))
                    if isinstance(mic,list):
                        val = {m:mv for m,mv in val.items() if int(m) in mic}
                    else:
                        val = val[str(mic)]
                    dict.setdefault(id,{})[var] = val
                else:
                    print('Variable '+ var+ ' is not in measurementValue')
        if len(ID)==1:
            return(dict[ID[0]])
        else:
            return(dict)
    
    def set_kg_values(self, algorithm, ID, mic, results ):
        """
        set algorithm information in self.kgValues['algorithm'] 

        set algorithm results in self.kgValues['results'] 
        structure of self.kgValues['results']:
        {ID:{
             'mic':{
                        mic:{
                            str(algorithm):{...}
                            }
                        }
            }
            
        parameter: algorithm, **{'ID':mID, 'mic': mic, 'results':{...}}
        """
        if not str(algorithm) in self.kgValues['algorithms'].keys():
            self.kgValues['algorithms'][str(algorithm)] = algorithm.get_info()
        # add results
        dict = self.kgValues['results'].setdefault(ID,{}).setdefault(mic,{})
        dict[str(algorithm)] = results
        
    def kg_values_to_json(self, variables = []):
        '''
        export kgValues of given algorithm with added variables for R evaluation
        '''
        dateTime =  datetime.datetime.now()
        fileName = 'results_'+ dateTime.strftime( "%d-%m-%Y_%H-%M-%S")
        resultsPath = self.path.joinpath('results').joinpath(fileName + '.json')
        export = collections.OrderedDict()
        export['Description']= '''
                    This file contains the Results of KG processing'''
        export.update({ 'date': dateTime.strftime( "%d-%m-%Y"),
                        'time':dateTime.strftime( "%H:%M:%S"),
                        'location': self.location,
                        'measurement': self.measurement})
        export.update(copy.deepcopy(self.kgValues))
        # Add variables
        # todo : implement
        # for var in variables:
        #     if var in self.micValues.keys():
        #         pass
        #     if var in self.idValues.keys():
        #         pass
        with resultsPath.open('w+') as file:
            json.dump(serialize(export),file)
        
    @classmethod
    def from_json(cls, mesPath):
        dataPath = pathlib.Path(mesPath)
        dataPath = dataPath.joinpath('measurement_values/MBBM_mes_values.json')
        with dataPath.open('r+') as data:
            MBBM_data = json.load(data)
        return(cls(mesPath,**MBBM_data))
        
    @classmethod    
    def from_MBBM(cls, mesPath):
        return(cls(mesPath = mesPath,**read_MBBM_tables(mesPath, save = False)))
        
def serialize(data):
    if isinstance(data, list):
        return [serialize(val) for val in data]
    elif isinstance(data, dict):
        return { serialize(k): serialize(v) for k, v in data.items()}
    elif isinstance(data, np.ndarray):
        return {"py/numpy.ndarray": {
            "values": data.tolist(),
            "dtype":  str(data.dtype)}}
    else:
        return(data)

if __name__ == "__main__":
    
    AA = measuredValues('C:\lucmiaz\KG_dev_branch\KG\Measurements_example\MBBMZugExample')
    AA.list_variables()
    AA.read_variables_values()
    ##getexample
    s=AA.get_variables_values(ID='m_0100',mic= [1,2], variables=['v2','v1','direction','Ta', 'Te', 'Tp_a', 'Tp_e'])
    print(s)
    ##
    
    
    # ## get evaluated signals
    # allID = mesVal.get_IDs(evaluated = False)
    # print( 'Total N. of IDs:' , len(allID))
    # evalID = mesVal.get_IDs(evaluated = True)
    # print( 'evaluated IDs:' , len(evalID))
    # nonEvalID = list(set(allID)-set(evalID))
    # print(nonEvalID)
    # print('m_0120'in allID)

   ##   ##expot example
    # mesVal.set_kg_alg_description( 'alg1','kkkkkkk',[['var1','aaa'],['var2','bbb'],['mic','micro']])
    # mesVal.set_kg_values('alg1','m_0101',{'mic':[1,2,7],'var1':[22,33,44],'var2':[9,9,9]})
    # mesVal.export_kg_results('alg1',variables= ['Te','v2','mTime'])
    # mesVal.export_kg_results('alg1')

        




