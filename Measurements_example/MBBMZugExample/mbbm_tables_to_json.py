import sys
sys.path.append('D:\GitHub\myKG')
import os, pathlib
import numpy as np
from kg.measurement_values import measuredValues, read_MBBM_tables
from kg.measurement_signal import measuredSignal


if __name__ == "__main__":
    #Read and save MBBM values
    mesPath = 'D:\GitHub\myKG\Measurements_example\MBBMZugExample'
    read_MBBM_tables(mesPath,True)
    mesVal = measuredValues.from_json(mesPath)
    ## some tests
    s = mesVal.get_variables_values(ID= ['m_0100','m_0191'], mic= 1,
     variables = ['Tb', 'v1', 'Tp_b', 'Tp_e'])
    print(s)

    ## get evaluated signals
    allID = mesVal.get_IDs(evaluated = False)
    print( 'Total N. of IDs:' , len(allID))
    evalID = mesVal.get_IDs(evaluated = True)
    print( 'evaluated IDs:' , len(evalID))
    nonEvalID = list(set(allID)-set(evalID))
    print(nonEvalID)
    print('m_0120'in allID)