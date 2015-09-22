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
        self.kgValues = {}
                
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
        if not isinstance(mic,list):
            mic = [mic] 
        dict={}
        for id in ID: 
            for var in variables:
                if var in self.idValues.keys():
                    try:
                        # if there is id 
                        value = self.idValues[var]['values'][id]
                    except KeyError:
                        value = None
                elif var in self.micValues.keys():
                    try:
                        value = self.micValues[var]['values'][id]
                        value = {m:mv for m,mv in value.items() if int(m) in mic}
                    except KeyError:
                        value = None
                #fill dict
                try:
                    dict[id][var] = value
                except KeyError:
                    dict[id] = {var: value}
        return(dict)
    
    def set_kg_values(self, ID, mic, algorithm, results ):
        """
        calculated values with dsp are stored in kgValues[calc_id] as dict.
        """
        # Todo: algorithm
        try:
            dict = self.kgValues[calc_id]
        except KeyError:
            self.kgValues[calc_id] = {}
            dict = self.kgValues[calc_id]
        #raise error if ID already calculated
        if ID in dict.keys():
           print('ID is alredy calculated')
        else:
            dict[ID] = dspValues
            
    def set_kg_alg_description(self,calc_id, algorithmDescription,variableInfo):
        # Todo: JSON
        if not calc_id in self.kgValues.keys():
            self.kgValues[calc_id] = {}
        self.kgValues[calc_id]['description'] = algorithmDescription
        self.kgValues[calc_id]['varInfo'] = variableInfo
        
    def export_to_json(self, algorithm, variables = []):
        '''
        '''
        # Todo: JSON
        resultsPath = self.path.joinpath('results')
        KG = self.kgValues[algorithm]
        dateTime =  datetime.datetime.now()
        fileName = 'results_'+ calc_id +'_'+ dateTime.strftime( "%d-%m-%Y_%H-%M-%S")
        resultsPath = resultsPath.joinpath( fileName + '.csv').as_posix()
        #header
        header =   {'Description':'''
                    ['# This file contains the Results of KG processing'],
                    ['# Measurement and processing informations']''',
                    'date': dateTime.strftime( "%d-%m-%Y"),
                    'time':dateTime.strftime( "%H:%M:%S"),
                    'location': self.location,
                    'measurement': self.measurement,
                    #['measurement date', measuredValues.MES_DATE],
                    'kg_calc_id':calc_id,
                    'algorithm':algorithm}
        #colnames description
        colNames = ''
        #kgVariables
        colNames += KG['varInfo']
        #
        varInfo = self.list_variables()
        colNames += [[var, varInfo.ix[varInfo.variable =='v1','description']] for var in variables]
        #write to csv
        with open(resultsPath, 'w+', newline='') as file:
            csv_writer = csv.writer(file, delimiter=';')
            for row in header + colNames:
                csv_writer.writerow(row)
            # write table data
            csv_writer.writerow(['## Table with processed data'])
            # table header
            KGColnames = [KGvar[0] for KGvar in KG['varInfo']]
            csv_writer.writerow(['ID']+KGColnames+variables)
            #table data
            IDs = list(KG.keys())
            IDs.remove('varInfo')
            IDs.remove('description')
            for ID in IDs:
                kg = KG[ID]
                for i,mic in enumerate(kg['mic']):
                    row = [ID]
                    row += [kg[col][i] for col in KGColnames]
                    varValues = self.get_variables_values(ID,mic,variables)
                    row+=[varValues[k] for k in variables ]
                    csv_writer.writerow(row) 
            #finish
        print('Values writed to file')
        
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

if __name__ == "__main__":
    #Read and save MBBM values
    mesPath = 'D:\GitHub\myKG\Measurements_example\MBBMZugExample'
    read_MBBM_tables(mesPath,True)
    #getexample
    mesVal = measuredValues.from_json(mesPath)
    s = mesVal.get_variables_values(ID=['m_0100','m_0101'], mic= [1,2], variables=['v2','v1','direction','Ta', 'Te', 'Tp_a', 'Tp_e'])
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

        




