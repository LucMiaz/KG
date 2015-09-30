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
    #
    mID = 'm_0100'
    mic= [1,2,4,5,6]
    app = QtGui.QApplication(sys.argv)
    W = CaseCreatorWidget.from_measurement(mesVal,mID, mic,'esr')
    W.show()
    sys.exit(app.exec_())
    
    