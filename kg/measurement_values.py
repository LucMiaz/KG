import numpy as np
import pandas as pd
import copy,sys,pathlib
import collections
import xlrd,json
import datetime


def read_MBBM_tables(mesPath, save = False):
    '''
    load values of selected variables and mic form MBBM files
    tables have to be located at \measurement_values relative to mesPath
    need configuration file 'measurement_config.json' located at mesPath
    '''
    mesPath = pathlib.Path(mesPath)
    with mesPath.joinpath('measurement_config.json').open('r+') as config:
        CONFIG = json.load(config)
    TABLES = CONFIG['tables']
    MICVALUES = CONFIG['micValues']
    IDVALUES = CONFIG['idValues']
    Mic = CONFIG['microphones']
    mID= set()
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
                    id = ws.cell_value(row,0)
                    S_mic = [ws.cell_value(row,i) for i in range(1,25)]
                    try:
                        dictID = data[id]
                    except KeyError:
                        data[id] = {}
                        dictID = data[id]
                    mID.add(id)    
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
                id = ws.cell_value(row,0)
                mID.add(id)
                mic_val = {}
                for i,mic in zip(selectCol,Mic):
                    mic_val[str(mic)] = ws.cell_value(row,i) 
                data[id] = mic_val
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
            id = ws.cell_value(row,0)
            data[id] = ws.cell_value(row,selectCol)
            mID.add(id)
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
    MBBM_data['mID'] = list(mID)
    if save:
        dataPath = mesPath.joinpath('measurement_values/MBBM_mes_values.json')
        with dataPath.open('w+') as data:
            json.dump(MBBM_data, data)
        print('Data saved to ' + mesPath.as_posix())
    return(MBBM_data)
        

class measuredValues():
    def __init__(self,mesPath, location, measurement, tables, micValues, idValues , mic, mID):
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
        self.mID = mID
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
        
    def MBBM_valid_id(self,ID):
        """
        If ID is Valid then all the mic are too
        all the ID with calculated LAF
        """
        return(ID in list(self.micValues['LAmax']['values'].keys()))
    def get_path(self):
        try:
            return(self.path.as_posix())
        except:
            try:
                return(str(self.path))
            except:
                return('could not return the path')
    def get_IDs(self, evaluated = False):
        return(list(self.micValues['LAmax']['values'].keys()))
        
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
                    try:
                        values = self.idValues[var].get('values')[id]
                    except KeyError as e:
                        dict[id]=None
                        print('ID '+id +' not found in method get_variable_values of mesurement_values.py in if block.')
                        break
                    dict.setdefault(id,{})[var] = val
                elif var in self.micValues.keys():
                    try:
                        values = self.micValues[var].get('values')[id]
                    except KeyError as e:
                        dict[id]=None
                        print('\n var '+str(var)+' ID '+id +' not found in method get_variable of measurement_values.py in elif block.\n ')
                        break
                    val = copy.deepcopy(values)
                    if isinstance(mic,list):
                        val = {m:mv for m,mv in val.items() if int(m) in mic}
                    else:
                        val = val.get(str(mic))
                    dict.setdefault(id,{})[var] = val
                else:
                    print('Variable '+ var+ ' is not in measurementValue')
        if len(ID)==1:
            return(dict[ID[0]])
        else:
            return(dict)
    
    def set_kg_values(self, algorithm, ID, mic, result, **kwargs ):
        """
        set algorithm information in self.kgValues['algorithm'] 

        set algorithm results in self.kgValues['results'] 
        structure of self.kgValues['results']:
        parameter: algorithm, **{'ID':mID, 'mic': mic, 'results':{...}}
        """
        if not str(algorithm) in self.kgValues['algorithms'].keys():
            self.kgValues['algorithms'][str(algorithm)] = algorithm.get_info()
        # add results
        dict = self.kgValues['results'].setdefault(ID,{}).setdefault(mic,{})
        dict[str(algorithm)] = result
        
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
                        'time':dateTime.strftime( "%H-%M"),
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
    
    def to_db(self, dbname):
        """saves self to the database dbname"""
        from pymongo import MongoClient
        pass
	
    @classmethod
    def from_json(cls, mesPath):
        #dataPath = pathlib.Path(mesPath)
        dataPath = mesPath.joinpath('measurement_values/MBBM_mes_values.json')
        with dataPath.open('r+') as data:
            MBBM_data = json.load(data)
        return(cls(mesPath,**MBBM_data))
        
    @classmethod    
    def from_MBBM(cls, mesPath):
        return(cls(mesPath = mesPath,**read_MBBM_tables(mesPath, save = False)))

def serialize(data):
    '''
    serialize np.array to be saved in .json format
    parameter:
    ----------
    data: nested data of dicts and lists containing np.arrays
    '''
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
    #Read and save MBBM values
    mesPath = pathlib.Path('Measurements_example\MBBMZugExample')
    #read_MBBM_tables(mesPath,True)
    #getexample
    mesVal = measuredValues.from_json(mesPath)
    ##
    s = mesVal.get_variables_values(ID= ['m_01000','m_01091'], mic= 1,
     variables = ['Tb', 'v1', 'Tp_b', 'Tp_e'])
    print(s)

    ## get evaluated signals
    allID = mesVal.get_IDs(evaluated = False)
    print( 'Total N. of IDs:' , len(allID))
    evalID = mesVal.get_IDs(evaluated = True)
    print( 'evaluated IDs:' , len(evalID))
    nonEvalID = list(set(allID)-set(evalID))
    print(nonEvalID)
    print('m_0120'in allID)
