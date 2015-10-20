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
    Paths=[mesPath]
    Paths.append(pathlib.Path('E:/ZugVormessung/raw_signals'))
    Paths.append(pathlib.Path('E:/Biel1Vormessung/raw_signals'))
    
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
                    newpath= QFileDialog.getExistingDirectory(W,"Please select path n°"+str(i+1)+" to search (should be named sth like raw_signal)")
                    if newpath:
                        newpath=pathlib.Path(newpath)
                        Paths.append(newpath)
    print(Paths)
    measuredSignal.setup(mesPath)#add other paths here
    
    # setup algorithms
    # todo: parametrize alg parameter in the best possible way 
    FC = [3000]
    Treshold = [2]
    DT = [0.02]
    algorithms = []
    for fc, threshold, dt in itertools.product(FC,Treshold,DT):
        algorithms.append(ZischenDetetkt2(fc, dt,threshold))
        
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
    for case in cases[5:10]:
        print(str(case))
        mID = case.case['mID']
        mic = case.case['mic']
        # initaite mic signal
        micSn = MicSignal.from_measurement(mesValues, mID, mic, multiplePaths=Paths)
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


