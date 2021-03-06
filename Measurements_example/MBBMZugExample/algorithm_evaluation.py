import sys
sys.path.append('D:\GitHub\myKG')
import os, pathlib
import numpy as np
import itertools
from kg.detect import MicSignal
from kg.algorithm import *
from kg.algorithm import Case
from kg.widgets import *
from kg.measurement_values import measuredValues
from kg.measurement_signal import measuredSignal
#number o cases to prepare

mesPath = pathlib.Path('').absolute()
if __name__ == "__main__":  
    # load measured values
    mesVal = measuredValues.from_json(mesPath)
    location =  mesVal.location
    measurement = mesVal.measurement
    
    # setup  measured signal 
    ##Add other paths here if an other "raw_signal" folder is to be searched (use list). Be sure to put the path where raw_signals_config.json is located in the first index
    Paths=[]
    Paths.append(pathlib.Path('E:/ZugVormessung'))
    Paths.append(pathlib.Path('E:/Biel1Vormessung'))
    
    #graphical selection
    callGUI=False
    if callGUI:
        app=QtGui.QApplication(sys.argv)
        W=QtGui.QMainWindow()
        folderquest = QtGui.QMessageBox.question(W, 'Folder selection', "Would you like to select other pathes to search ?", QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.No)
        if folderquest==QtGui.QMessageBox.Yes:
            numdir, ok=QtGui.QInputDialog.getInt(W, "Number of folders to add", ("Please insert the number of folders you would like to add"),  value=1, min=1, max=10, step=1)
            if ok:
                for i in range(0,numdir):
                    newpath= QFileDialog.getExistingDirectory(W,"Please select path n°"+str(i+1)+" to search (must contain a folder called raw_signals)")
                    if newpath:
                        newpath=pathlib.Path(newpath)
                        Paths.append(newpath)
    print(Paths)
    #measuredSignal.setup(Paths[0])#add other paths here
    
    # setup algorithms
    # todo: parametrize alg parameter in the best possible way 
    FC = [2000,3000,3500,4000,4500]
    Treshold = [13.0]
    DT = [0.02,0.05,0.1]
    algorithms = []
    if len(Treshold)==1:
        threshold=Treshold[0]
        for fc, dt in itertools.product(FC,DT):
            algorithms.append(ZischenDetetkt2(fc,threshold, dt))
    else:
        for fc, threshold, dt in itertools.product(FC,Treshold,DT):
            algorithms.append(ZischenDetetkt2(fc, threshold,dt,Rexport=True))
    
    algorithms=[]
    algorithms.append(ZischenDetetkt2(4500,0.676518927494837,0.02,Rexport=True))
    algorithms.append(ZischenDetetkt2(4500,0.726743716026382,0.1,Rexport=True))
    algorithms.append(ZischenDetetkt2(4500,0.730582921048284,0.05,Rexport=True))
    algorithms.append(ZischenDetetkt2(4000,0.913411063022725,0.02,Rexport=True))
    algorithms.append(ZischenDetetkt2(3500,1.04742936463208,0.02,Rexport=True))
    algorithms.append(ZischenDetetkt2(4000,1.38839908900027,0.05,Rexport=True))
    algorithms.append(ZischenDetetkt2(3000,1.76704138977899,0.02,Rexport=True))
    algorithms.append(ZischenDetetkt2(3500,1.79087764593783,0.05,Rexport=True))
    algorithms.append(ZischenDetetkt2(4000,1.81104574253084,0.1,Rexport=True))
    algorithms.append(ZischenDetetkt2(3500,1.99828945412812,0.1,Rexport=True))
    algorithms.append(ZischenDetetkt2(3000,2.22468607016445,0.05,Rexport=True))
    algorithms.append(ZischenDetetkt2(3000,2.57727672753696,0.1,Rexport=True))
    algorithms.append(ZischenDetetkt2(2000,2.89499961394424,0.02,Rexport=True))
    algorithms.append(ZischenDetetkt2(2000,3.23479771056204,0.05,Rexport=True))
    algorithms.append(ZischenDetetkt2(2000,3.52850682557497,0.1,Rexport=True))
    #load cases
    # todo: if necessary serialize on mesVal
    mesValues = measuredValues.from_json(mesPath)
    casePath = mesValues.path.joinpath('test_cases')
    #collect cases
    cases = []
    for authP in  casePath.iterdir():
        if authP.is_dir():
            print(authP)
            cases.extend([Case.from_JSON(cp) for cp in authP.iterdir()\
                            if cp.match('case_**.json') ])
    notfound=[]
    print('Case cases:')
    print('----------------------')
    for case in cases:
        print(str(case))
        mID = case.case['mID']
        mic = case.case['mic']
        # initaite mic signal
        micSn, mesVal = MicSignal.from_measurement(mID, mic, Paths=Paths)
        if micSn:
            for alg in algorithms:
                print(str(alg),end = ', ')
                alg.test_on_case(case, mesVal, micSn)
                print('.')
        else:
            notfound.append(mID)
            print(mID+" not found. Pass.")
    
    #calc global Rates
    print('Calculate global Rates')
    for alg in algorithms:
        alg.calc_rates()
    # save
    print('save to json')
    for n,alg in enumerate(algorithms):
        filepapth=alg.export_test_results(mesPath)
    print("List of cases not found :"+str(notfound))
    print("Number of analyzed cases : "+str(len(cases)-len(notfound)))
    print(str(filepapth))


