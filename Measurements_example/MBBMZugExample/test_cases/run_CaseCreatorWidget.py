import sys
sys.path.append('D:\GitHub\myKG')
import os, pathlib
import numpy as np
import json
from PySide import QtGui, QtCore

from kg.case import Case
from kg.widgets import CaseCreatorWidget
import itertools


if __name__ == "__main__":
    #import
    mainPath = pathlib.Path('').absolute()
    mesPath = mainPath.parent
    with mainPath.joinpath('caseToAnalyze.json').open('r+') as input:
        caseToAnalyze = json.load(input)
    for k,v in caseToAnalyze.items():
        v['case'] = Case(**v['case'])

    app = QtGui.QApplication(sys.argv)
    W = CaseCreatorWidget(mesPath, caseToAnalyze)
    W.show()
    sys.exit(app.exec_())
    

