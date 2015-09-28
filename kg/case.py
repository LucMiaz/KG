import sys,os,pathlib
import inspect
from kg.intervals import *
from kg.measurement_values import measuredValues
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import json
import time
import numpy as np

##Class Case
class Case(object):
    """
    Defines a case of study
    """
    def __init__(self, location, measurement, mID, mic, Tb, Te, author, **kwargs):
        """
        Takes a set of data as dict and an axis to display the data on.
        """
        self.case = {
                "location":location,
                "measurement": measurement, 
                "mID":  mID,
                "mic":  mic,
                "author": author,
                "date":time.strftime('%d.%m.%Y'),
                "Tb": Tb,
                "Te": Te,
                "KG": SetOfIntervals(), #Kreischen
                "Z": SetOfIntervals() #Zischen
                }
        self.case['caseID'] = str(self)
    
    def compare(self, otherdisc, tmin, tmax, dt, noiseType = 'Z'):
        """Compares the discretization of this case with the one of an algorithm whose results are given in otherdisc. timeparam variable contains the variables for the discretization. Returns a dictionnary with the number of True positives, True negatives, False positives and False negatives"""
        try:
            disc = self.case[noiseType].discretize(tmin, tmax, dt)
        except:
            disc = 0
        assert( len(otherdisc) == len(disc) )
        retTF={'FP':[], 'TP':[], 'FN':[],'TN':[]}
        retTF['TP'] = np.logical_and(otherdisc,disc)
        retTF['TN'] = np.logical_and(np.logical_not(otherdisc), np.logical_not(disc))
        retTF['FP'] = np.logical_and(otherdisc, np.logical_not(disc))
        retTF['FN'] = np.logical_and(np.logical_not(otherdisc),  disc)
        return(retTF)
        
    def save(self, mesPath):
        '''
        save Case to file in mespath\test_cases\author\case_mID_mic_author.json
        '''
        mesPath = pathlib.Path(mesPath)
        casePath = mesPath.joinpath('test_cases').joinpath(self.case['author'])
        os.makedirs(casePath.as_posix(), exist_ok = True)
        name = str(self) + '.json'
        casePath = casePath.joinpath(name)
        self.toJSON(casePath)
        return(casePath.as_posix())
        
    def get_SOI(self, noiseType='Z'):
        return(self.case[noiseType])
    
    def __str__(self):
        """prints the name of the case"""
        return( "case_"+str(self.case['mID'])+"_"+str(self.case['mic'])+'_'+\
        str(self.case['author']))
    
    def __repr__(self):
        """gives a representation of the case"""
        return self.toJSON()

    def toJSON(self,filename = None):
        """returns the essential informations of self, if Pathname or Path is given, save in file."""
        if filename:
            if not isinstance(filename, pathlib.Path):
                fn=pathlib.Path(filename)
            else:
                fn=filename
            with fn.open('w') as fn:
                json.dump(self.case,fn,cls=ComplexEncoder)
        else:
            return json.dumps(self.case, cls= ComplexEncoder)
            
    @classmethod
    def from_JSON(cls, casePath):
        """@classmethod is used to pass the class to the method as implicit argument. Then we open a file in JSON located at casePath and give it to the class with **kwargs (meaning that we pass an arbitrary number of arguments to the class)
        """
        try:
            dict = json.load(open(casePath, 'r'))
        except FileNotFoundError:
            raise Error("The file in path" + casePath + " has not be found.")
        cl = cls(**dict)
        for nT in ['Z']:# todo :'KG' 
            dNT = dict[nT]["SetOfIntervals"]
            set = [[int['xmin'] , int['xmax']] for int in dNT] 
            cl.get_SOI(nT).appendlistofduples(set)
        return(cl)

## Test
if __name__ == "__main__":
    #import prettyplotlib #makes nicer plots
    #import matplotlib.pyplot as plt
    plt.ioff()
    x = np.arange(100)/(79.0)
    y = np.sin(x)
    fig, ax = plt.subplots(1)
    ax.plot(x,y)
    #new = GraphicalIntervals(ax)
    Newcase = Case('Zug','Vormessung','m_0100','1',0,10,'esr')
    ca = FigureCanvas(fig)
    def f1(x1,x2):
        case.case['Z'].append(Interval(x1,x2))
        cs.set
    def f2(x):
        print(x)
    cs= CaseSelector(ax,f1,f2, update_on_ext_event=False)
    ca.show()
    ##save
    mesPath = 'Measurements_example\MBBMZugExample'
    casePath = Newcase.save(mesPath)
    Newcase2 = Case.from_JSON(casePath)
    