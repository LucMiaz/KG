import sys
sys.path.append('D:\GitHub\myKG')
import os, pathlib
import numpy as np
from kg.measurement_values import measuredValues, read_MBBM_tables
from kg.measurement_signal import measuredSignal


if __name__ == "__main__":
    #Read and save MBBM values
    #mesPath = 'D:\GitHub\myKG\Measurements_example\MBBMZugExample'
    mesPath = pathlib.Path('')
    read_MBBM_tables(mesPath,True)
    
    #load mesVal
    mesVal = measuredValues.from_json(mesPath)