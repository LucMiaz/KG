import scipy as sp
import scipy.io
import numpy as np
import pandas as pd
import copy
import xlrd

import csv
import datetime

class measuredValues():
    def __init__(self,path):
        self.path = path
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
        with open(self.path + '\\' + 'Readme.csv', 'r+') as readme:
            reader = csv.reader(readme,delimiter=';')
            dict ={}#{k : None for k in var+dicts}
            var = None
            header = None
            for row in reader:
                if row[0][0]=='#':
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
            self.location, self.measurement,self.mic = (dict[k] for k in vars) 
            self.tables, self.micValues, self.idInfo = (dict[k] for k in dicts)
        #correct mic 
        self.mic = eval(self.mic)
        self.micValues['LPAeqTP_mic_i']['colName'] = eval(self.micValues['LPAeqTP_mic_i']['colName'] )
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
        for k,v in self.micValues.items():
            #
            table = self.tables[v['table']]
            wb = xlrd.open_workbook(self.path +'\\'+ table['fileName'])
            #if Spectrum
            if k == 'LPAeqTP_mic_i':
                S_mic = []
                for mic in self.mic:
                    sN = k.replace('_i','_'+ str(mic))
                    ws = wb.sheet_by_name(sN)
                    index = []
                    data  = []
                    for row in range(table['skip']+1,ws.nrows):
                        index.append(ws.cell_value(row,0))
                        #terzband spektrum hat 24 werte
                        data.append([ws.cell_value(row,i) for i in range(1,25)])
                    S_mic.append(pd.DataFrame({sN:data}, index = index))
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
                columns = [k.replace('_i','_'+ str(mic)) for mic in self.mic])
                
        #if IDINFO value        
        for k,v in self.idInfo.items():
            table = self.tables[v['table']]
            wb = xlrd.open_workbook(self.path +'\\'+ table['fileName'])
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

    def get_variables_values(self,ID, mic, variables):
        """
        parameter:
        ID list of ID
        mic list of mic
        Variables list of variables
        return:
        dict of df of the variables
        """
        dict={}
        for var in variables:
            if var in list(self.idInfo.keys()):
                dict[var] =self.idInfo[var]['values'].ix[ID,var]
            else:
                values = self.micValues[var]['values']
                if isinstance(mic, list):
                    vars = [var.replace('_i','_'+ str(i)) for i in mic]
                    dict[var] = [values.ix[ID,i] for i in vars] 
                else:
                    dict[var] = values.ix[ID,var.replace('_i','_'+ str(mic))]
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
        self.kgValues[calc_id]['description']=algorithmDescription
        self.kgValues[calc_id]['varInfo'] = variableInfo
        
    def export_kg_results(self, calc_id, variables = []):
        '''
        '''
        KG = self.kgValues[calc_id]
        dateTime =  datetime.datetime.now()
        fileName = 'results_'+ calc_id +'_'+ dateTime.strftime( "%d-%m-%Y_%H-%M-%S")
        filePath = self.path + '\\results\\' + fileName + '.csv'
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
        with open(filePath, 'w+', newline='') as file:
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
        
    def plot_spectrum(self, ID, mic, ax, label=None):
        ax.set_title('Spectrum', fontsize=12)
        freq = np.array(self.micValues['LPAeqTP_mic_i']['colName'])
        #mask = np.all([(freq <= fmax), (freq >= fmin)], axis=0)
        PS_i = np.array(self.get_variables_values(ID,[mic],['LPAeqTP_mic_i'])['LPAeqTP_mic_i'])
        if label == None:
            label = 'Spectrum _ch_' + str(mic)
        ax.plot(freq, PS_i, label = label)
        ax.set_xscale('log')
        ax.grid(True)
        ax.minorticks_off()
        ax.set_xticks(freq)
        ax.set_xticklabels([ f if  i%3 == 0  else '' for i,f in enumerate(freq) ])
        ax.set_xlim([freq.min(),freq.max()])
        ax.set_xlabel('f (Hz)', fontsize=10)
        ax.set_ylabel(' (dBA)', fontsize=10)
        
    def plot_times(self, ID, mic, ax, type ='passby', label=None, lw=1.5 ):
        """
        type eval for t
        type passby for t
        
        """
        if type == 'eval':
            variables = ['tb_mic_i', 'te_mic_i']
            col= 'R'
        elif type == 'passby':
            variables = ['t1b_mic_i', 't1e_mic_i']
            col= 'B'
        t = self.get_variables_values(ID, mic, variables)
        [ax.axvline(x, color= col, lw = lw) for x in t.values()]



## test

if __name__ == "__main__":
    
    AA = measuredValues('D:\KurvenK\Messung Zug\data_bsp')
    AA.list_variables()
    AA.read_variables_values()
    ##
    s=AA.get_variables_values(ID='m_0100',mic= [1,2], variables=['v2','direction','tb_mic_i', 'te_mic_i', 't1b_mic_i', 't1e_mic_i'])
    print(s)
    
    s=AA.get_variables_values(ID='m_0100',mic= 1, variables=['te_mic_i','v2','v1'])
    print(s)

    AA.set_kg_alg_description( 'alg1','kkkkkkk',[['var1','aaa'],['var2','bbb'],['mic','micro']])
    AA.set_kg_values('alg1','m_0100',{'mic':[1,2,7],'var1':[22,33,44],'var2':[9,9,9]})
    AA.export_kg_results('alg1',variables= ['t1e_mic_i','v2','mTime'])
    AA.export_kg_results('alg1')

        




