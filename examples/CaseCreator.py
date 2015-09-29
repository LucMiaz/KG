import sys
sys.path.append('D:\GitHub\myKG')
import os, pathlib
import numpy as np
from PySide import QtGui, QtCore

from kg.detect import MicSignal
from kg.case import Case
from kg.widgets import CaseCreatorWidget
from kg.measurement_values import measuredValues
from kg.measurement_signal import measuredSignal
from kg.algorithm import ZischenDetetkt1

if __name__ == "__main__":
    #setup measurement
    mesPath = 'D:\GitHub\myKG\Measurements_example\MBBMZugExample'
    mesVal = measuredValues.from_json(mesPath)
    measuredSignal.setup(mesPath)
    #algorithm
    #algorithm = ZischenDetetkt1(2000,0,0.1)
    mID = 'm_0100'
    mic = 6
    micSn = MicSignal.from_measurement(mesVal,mID, mic)
    micSn.calc_kg(algorithm)
    #Run Widget
    #W = DetectControlWidget.alg_results(micSn,algorithm)
    caseParam = {'measurement':mesVal.measurement,\
                'location': mesVal.location,
                'mID':mID,'mic':mic,
                'author':'esr'}
    caseParam.update(mesVal.get_variables_values(mID,mic,['Tb','Te']))
    newcase = Case(**caseParam)
    app = QtGui.QApplication(sys.argv)
    W = CaseCreatorWidget(newcase,micSn,'esr',mesVal.path.as_posix())
    W.show()
    sys.exit(app.exec_())
    
    