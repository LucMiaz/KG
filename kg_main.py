import sys
import os
import pandas as pd
import numpy as np
sys.path.append('D:\GitHub\KG')
from kg.measurement_values import measuredValues
from kg.time_signal import *
from kg.dsp import DSP
from kg.grafics import BarCanvas
from kg.audio_visual_app import PlaybackWindow
from PySide import QtGui,QtCore
from pandas.sandbox.qtpandas import DataFrameModel, DataFrameWidget
# todo: analyze non zug signalss

def process_ID( ID, mvalues, method='method2', Mic = None, plot = True):
    """
    canale vedi zeitsignal.list_signals()
    """
    signal = timeSignal(ID)
    dsp = DSP()
        
    # load mic signal and add to dsp
    for mic in Mic:
        signal.load_signal(mic)
        dsp.add_mic_signal(signal = signal.get_signal(mic), type = 'mic', mic = mic, besch =  '...', 
        #pass mValues
        variables=['tb_mic_i', 'te_mic_i', 't1b_mic_i', 't1e_mic_i', 'LAEQ_mic_i', 'v1','v2'],
        vars = mvalues.get_variables_values(ID, mic,variables))

    # select method and calculate KG
    #dsp.calc_kg2(5,highcut= 1500)

    return( signal, dsp)

if __name__ == "__main__":
    #set paths
    timeSignal._setup(path='D:\KurvenK\Messung Zug\data_bsp\Messdaten_Matlab')
    vormessung = measuredValues('D:\KurvenK\Messung Zug\data_bsp')
    # read measurement Values
    vormessung.read_values()
    #set algorithm
    algorithmID = 'alg_1'
    vormessung.set_kg_alg_description(dsp.get_KG_algorithm(algorithmID))
    #select IDs to process
    IDs = ['m_0100']
    for ID in IDs:
        signal, dsp = process_ID(ID ,mvalues = vormessung, method = algorithmID, mics = [6])
        vormessung.set_kg_values(algorithmID, ID, dsp.get_KG_results())
    
    #export data frame (.csv) for further statistical results
    exportVariables = []
    vormessung.export_kg_results(algorithmID, exportVariables)
