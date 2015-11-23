"""
STFT
=========

The stft module.

"""
import sys,os
import inspect
#change dir form up/kg/thisfile.py to /up
approot=os.path.dirname(os.path.dirname(inspect.stack()[0][1]))
sys.path.append(approot)
if __name__=='__main__':
    print(approot)
import mySTFT.stft
import mySTFT.stft_plot

