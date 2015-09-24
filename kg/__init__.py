"""
KG-Detection
=========

The kg module.

"""
import sys,os
import inspect
#change dir form up/kg/thisfile.py to /up
approot=os.path.dirname(os.path.dirname(inspect.stack()[0][1]))
if __name__=='__main__':
    print(approot)
sys.path.append(approot)
import os,sys
import kg.time_signal
import kg.measurement_values
import kg.mpl_moving_bar
import kg.case
import kg.intervals
import mySTFT.stft
import mySTFT.stft_plot

