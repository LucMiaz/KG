import sys, inspect
import os, pathlib
import numpy as np
import json
from PySide import QtGui, QtCore

from kg.case import Case
from kg.widgets import *
import itertools
import matplotlib
from matplotlib.font_manager import FontProperties


if __name__ == "__main__":
    #import
    mainPath = pathlib.Path('').absolute()
    #mesPath = mainPath.parent
    mesPath = pathlib.Path('').absolute()
    #color Choice
    changecolors=True
    if changecolors:
        textcolor='#f5f5f5'
        axescolor='#f5f5f5'
        axbgcolor='#272822'
        bgcolor='#aaaaaa'
        textcolor='#aaaaaa'
        axescolor='#f4f4f4'
        axbgcolor='#272822'
        bgcolor='#aaaaaa'
        palette=QtGui.QPalette()
        palette.setColor(QtGui.QPalette.Window,'#4a4944')
        palette.setColor(QtGui.QPalette.Button,textcolor)
        palette.setColor(QtGui.QPalette.ButtonText,axbgcolor)
        palette.setColor(QtGui.QPalette.Text,axbgcolor)
        palette.setColor(QtGui.QPalette.Base,textcolor)
        palette.setColor(QtGui.QPalette.AlternateBase,'#f3f3f3')
        palette.setColor(QtGui.QPalette.WindowText,textcolor)
        palette.setColor(QtGui.QPalette.Highlight, '#c2a5cf')
        palette.setColor(QtGui.QPalette.HighlightedText, axbgcolor)
        palette.setColor(QtGui.QPalette.AlternateBase,axescolor)
        palette.setColor(QtGui.QPalette.ToolTipBase, axescolor)
        palette.setColor(QtGui.QPalette.Light, axescolor)
        palette.setColor(QtGui.QPalette.Midlight, textcolor)
        palette.setColor(QtGui.QPalette.Dark, axbgcolor)
        matplotlib.rcParams['axes.facecolor']=axescolor#background of ax   
        matplotlib.rcParams['axes.edgecolor']=axbgcolor
        matplotlib.rcParams['xtick.color']=textcolor
        matplotlib.rcParams['grid.color']=bgcolor
        matplotlib.rcParams['ytick.color']=textcolor
        matplotlib.rcParams['figure.edgecolor']=textcolor
        matplotlib.rcParams['figure.facecolor']='#eeee00'
        matplotlib.rcParams['patch.linewidth']='0.25'
        matplotlib.rcParams['lines.color']=axbgcolor
        matplotlib.rcParams['lines.linewidth']='0.75'
        matplotlib.rcParams['axes.linewidth']='0.4'
        matplotlib.rcParams['xtick.major.width']='0.4'
        matplotlib.rcParams['ytick.major.width']='0.4'
        matplotlib.rcParams['xtick.minor.width']='0.3'
        matplotlib.rcParams['xtick.minor.width']='0.3'
        matplotlib.rcParams['text.color']=textcolor#LAFast (on ax)
        matplotlib.rcParams['axes.labelcolor']=textcolor#labels diplayed on the figure (LA, t(s))
        matplotlib.rcParams['font.family']='Georgia'
        matplotlib.rcParams['grid.linewidth']=0.2
        matplotlib.rcParams['grid.alpha']=0.8
        matplotlib.rcParams['legend.framealpha']=0.4
        matplotlib.rcParams['figure.autolayout']=True

    app=QtGui.QApplication(sys.argv)
    W = kgControlWidget(mesPath)
    if changecolors:
        W.setPalette(palette)
        W.setFont(QtGui.QFont('HelveticaNeue',11))
    W.show()
    #sys.exit(app.exec_())