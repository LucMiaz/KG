import sys
import os
import pandas as pd
import numpy as np
sys.path.append('D:\GitHub\KG')
from kg.measurement_values import measuredValues
from kg.time_signal import timeSignal, __create_wav__
from kg.dsp import DSP
from kg.grafics import BarCanvas
from kg.audio_visual_app import PlaybackWindow
from PySide import QtGui,QtCore
from pandas.sandbox.qtpandas import DataFrameModel, DataFrameWidget


def process_ID( ID, mvalues, method='method2', Mic = None, plot = True):
    """
    canale vedi zeitsignal.list_signals()
    """
    signal = timeSignal(ID)
    dsp = DSP()
    canvas = {}
    
    # load mic signal and add to dsp
    for mic in Mic:
        signal.load_signal(mic)
        dsp.add_mic_signal(signal = signal.get_signal(mic), type = 'mic', 
        mic = mic, 
        besch =  '...', 
        #pass measuredValues
        vars = mvalues.get_values(ID= ID, mic= [mic], 
        variables=['tb_mic_i', 'te_mic_i', 't1b_mic_i', 't1e_mic_i','LAEQ_mic_i','v1','v2']))
    
    # select method and calculate KG
    dsp.calc_kg2(5,highcut= 1500)
        
    # prepare Plots
    if plot:
        for mic,kg in dsp.KG.items():            
            #get signals
            kg= kg[method]
            sn = kg['sn']
            snf = kg['snf']
            bc = BarCanvas(nrow=2)
            bc.figure.suptitle('Mic '+ str(mic), fontsize=10, fontweight='bold')

            #ax0
            dsp.plot_SPL(snf, bc.axes[0], type= 'LF2')
            dsp.plot_SPL(sn, bc.axes[0], type= 'LF2')
            dsp.plot_KG(mic,method, bc.axes[0], type='flanging')
            #signal.load_signal('prms'+ str(mic))
            bc.axes[0].grid()
            bc.axes[0].legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
            ncol=3, mode="expand", borderaxespad=0.)
            #ax1
            dsp.plot_spectrogram(sn,bc.axes[1])
            bc.axes[1].set_xlabel('t (s)')
            #all
            for axis in bc.axes:
                mvalues.plot_times(ID, mic, axis)
                mvalues.plot_times(ID, mic, axis, type = 'eval')
            bc.set_initial_figure()
            canvas[mic] = bc
    
    return(canvas,signal, dsp)

if __name__ == "__main__":
    #set paths
    measuredValues.PATH = 'D:\KurvenK\Messung Zug\data_bsp'
    timeSignal.PATH = 'D:\KurvenK\Messung Zug\data_bsp\Messdaten_Matlab'
    vormessung = measuredValues()
    Var = vormessung.list_variables()
    Var = DataFrameWidget(Var)
    Var.show()
    vormessung.set_variables(all=True)
    vormessung.set_mic([1,2,4,5,6,7])
    vormessung.read_values()
    
    #list of ID to process
    for ID in ['m_0100']:
        canvas, signal, dsp = process_ID(ID , method='method2', mvalues = vormessung, Mic = [6])
        vormessung.set_DSP_values(dsp.get_KG_results())
    #export data frame (.csv) for further statistical results    
##

    W = PlaybackWindow(canvas, signal=signal, dsp=dsp )
    W.show()

    