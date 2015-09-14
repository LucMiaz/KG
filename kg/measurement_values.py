import scipy as sp
import scipy.io
import numpy as np
import pandas as pd
import copy
import xlrd
import csv
import datetime
import pathlib

class measuredValues():
    def __init__(self, mesPath):
        '''
        handle  the measurement database
        parameters
        ----------
        path: main path of measurement
        
        '''
        self.path = pathlib.Path(mesPath)
        #initiate attributes from Readme.csv
        self.location = None
        self.measurement = None
        self.tables = {}
        self.micValues = {} 
        self.idInfo = {}
        self.mic = []
        #
        vars = ['LOCATION','MEASUREMENT','MIC']
        dicts = ['TABLES','MICVALUES','IDINFO']
        with self.path.joinpath('measurement_info.csv').open('r+') as info:
            reader = csv.reader(info,delimiter=';')
            dict ={}
            var = None
            header = None
            for row in reader:
                if row[0][0][0]=='#':
                    pass
                elif row[0] in dicts:
                    var = row[0]
                    header = row[1:]
                    dict[var] = {}
                elif row[0] in vars:
                    header = None
                    var =row[0]
                elif header == None:
                    dict[var] = row[0]
                else:
                    for i,v in enumerate(row):
                        try:
                            row[i] = int(v)
                        except ValueError:
                            pass
                        if row[i] == '':
                            row[i] = None    
                    dict[var][row[0]] = { h:v for h,v in zip(header,row[1:])}
            #set var and dicts
            self.location, self.measurement, self.mic = (dict[k] for k in vars) 
            self.tables, self.micValues, self.idInfo = (dict[k] for k in dicts)
        #correct mic 
        self.mic = eval(self.mic)
        self.micValues['LAf']['colName'] = eval(self.micValues['LAf']['colName'] )
        #
        self.kgValues ={}
                
    def list_variables(self):
        """
        list all possible variables in data
        """
        var ={'variable':[],'description':[]}
        for k, v in list(self.idInfo.items()) + list(self.micValues.items()):
            var['variable'].append(k)
            var['description'].append(v['description'])
        var = pd.DataFrame(var)
        return(var)
        
    def read_variables_values(self):#,mics, variables = None, all=False):
        '''
        load values of selected variables and mic
        '''
        #if load mic values for interested mic
        tablesPath = self.path.joinpath('measurement_values')
        print('MIC VALUES \n-----------')
        for k,v in self.micValues.items():
            #
            print(k,', ', end='')
            table = self.tables[v['table']]
            wb = xlrd.open_workbook(str(tablesPath.joinpath(table['fileName'])))
            #if Spectrum
            if k == 'LAf':
                S_mic = []
                for mic in self.mic:
                    sN = v['sheet'].replace('_Miki','_Mik'+ str(mic))
                    ws = wb.sheet_by_name(sN)
                    index = []
                    data  = []
                    for row in range(table['skip']+1,ws.nrows):
                        index.append(ws.cell_value(row,0))
                        #terzband spektrum hat 24 werte
                        data.append([ws.cell_value(row,i) for i in range(1,25)])
                    cN = 'mic_'+str(mic)
                    S_mic.append(pd.DataFrame({cN:data}, index = index))
                v['values'] = pd.concat(S_mic, axis=1)
            #if mic single valued value
            else:
                #ID column
                ws = wb.sheet_by_name(v['sheet'])
                #ws starting row number of  
                wsRow0 = table['skip']
                # col names Table in excel ws
                colNames = ws.row_values(wsRow0)
                #index of selectd columns
                cN = [(v['colName']).replace('_i','_'+ str(mic)) for mic in self.mic]
                selectCol = [colNames.index(i) for i in cN] 
                data = []
                index = []
                for row in range(wsRow0+1,ws.nrows):
                    index.append(ws.cell_value(row,0))
                    data.append([ws.cell_value(row,i) for i in selectCol])
                #
                v['values'] = pd.DataFrame(data, index = index, 
                columns = ['mic_' + str(mic) for mic in self.mic])
        #if IDINFO value
        print('\n\nIDINFO \n-----------')        
        for k,v in self.idInfo.items():
            print(k,', ', end='')
            table = self.tables[v['table']]
            wb = xlrd.open_workbook(str(tablesPath.joinpath(table['fileName'])))
            ws = wb.sheet_by_name(v['sheet'])
            # col names Table
            colNames = ws.row_values(table['skip'])
            selectCol = colNames.index(v['colName']) 
            data = []
            index = []
            for row in range(table['skip']+1, ws.nrows):
                index.append(ws.cell_value(row,0))
                data.append(ws.cell_value(row,selectCol))
            v['values'] = pd.DataFrame({k:data}, index = index )
        print('\n\nFinish read values')
    
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
        dict={}
        for var in variables:
            if var in list(self.idInfo.keys()):
                dict[var] =self.idInfo[var]['values'].ix[ID,var]
            elif var in list(self.micValues.keys()):
                values = self.micValues[var]['values']
                if isinstance(mic, list):
                    dict[var] = [values.ix[ID,'mic_'+str(i)] for i in mic] 
                else:
                    dict[var] = values.ix[ID,'mic_'+ str(mic)]
        return(dict)
    
    def set_kg_values(self, calc_id, ID, dspValues ):
        """
        calculated values with dsp are stored in kgValues[calc_id] as dict.
        """
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
        if not calc_id in self.kgValues.keys():
            self.kgValues[calc_id] = {}
        self.kgValues[calc_id]['description'] = algorithmDescription
        self.kgValues[calc_id]['varInfo'] = variableInfo
        
    def export_kg_results(self, calc_id, variables = []):
        '''
        '''
        resultsPath = self.path.joinpath('results')
        KG = self.kgValues[calc_id]
        dateTime =  datetime.datetime.now()
        fileName = 'results_'+ calc_id +'_'+ dateTime.strftime( "%d-%m-%Y_%H-%M-%S")
        resultsPath = resultsPath.joinpath( fileName + '.csv').as_posix()
        #header
        header =   [['# Description' ],
                    ['# This file contains the Results of KG processing'],
                    ['# Measurement and processing informations'],
                    ['date', dateTime.strftime( "%d-%m-%Y")],
                    ['time', dateTime.strftime( "%H:%M:%S")],
                    ['location', self.location],
                    ['measurement', self.measurement],
                    #['measurement date', measuredValues.MES_DATE],
                    ['kg_calc_id',calc_id ],
                    ['algorithm_parameters',KG['description']],
                    ['# table column description']]
        #colnames description
        colNames = [['colName', 'description']]
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
        
    # def plot_spectrum(self, ID, mic, ax, label=None):
    #     ax.set_title('Spectrum', fontsize=12)
    #     freq = np.array(self.micValues['LAf']['colName'])
    #     PS_i = np.array(self.get_variables_values(ID,mic,['LAf'])['LAf'])
    #     if label == None:
    #         label = 'Spectrum_ch_' + str(mic)
    #     ax.plot(freq, PS_i, label = label)
    #     ax.set_xscale('log')
    #     ax.grid(True)
    #     ax.minorticks_off()
    #     ax.set_xticks(freq)
    #     ax.set_xticklabels([ f if  i%3 == 0  else '' for i,f in enumerate(freq) ])
    #     ax.set_xlim([freq.min(),freq.max()])
    #     ax.set_xlabel('f (Hz)', fontsize=10)
    #     ax.set_ylabel(' (dBA)', fontsize=10)
        




## test

if __name__ == "__main__":
    
    AA = measuredValues('D:\GitHub\myKG\Measurements_example\MBBMZugExample')
    AA.list_variables()
    AA.read_variables_values()
    ##getexample
    s=AA.get_variables_values(ID='m_0100',mic= [1,2], variables=['v2','v1','direction','Ta', 'Te', 'Tp_a', 'Tp_e'])
    print(s)
    
    s=AA.get_variables_values(ID='m_0101',mic= 1, variables=['v2','v1'])
    print(s)
    ## get evaluated signals
    allID = AA.get_IDs(evaluated = False)
    print( 'Total N. of IDs:' , len(allID))
    evalID = AA.get_IDs(evaluated = True)
    print( 'evaluated IDs:' , len(evalID))
    nonEvalID = list(set(allID)-set(evalID))
    print(nonEvalID)
    print('m_0120'in allID)

    ##expot example
    AA.set_kg_alg_description( 'alg1','kkkkkkk',[['var1','aaa'],['var2','bbb'],['mic','micro']])
    AA.set_kg_values('alg1','m_0101',{'mic':[1,2,7],'var1':[22,33,44],'var2':[9,9,9]})
    AA.export_kg_results('alg1',variables= ['Te','v2','mTime'])
    AA.export_kg_results('alg1')

        




