import Case
#import kg
import json
import time
import os
import pathlib
from pylab import *
import matplotlib
import prettyplotlib#makes nicer plots
import matplotlib.pyplot as plt
import matplotlib.patches as patches

##Class Case
class Case(object):
    """
    Defines a case of study
    """
    def __init__(self, ax, measurement, mID, mic, author, noiseType):
        """
        Takes a set of data as dict and an axis to display the data on.
        """
        self.case = {
                "measurement": measurement, 
                "mID":  mID,
                "mic":  mic,
                "author":author,
                "date":time.strftime('%d.%m.%Y'),
                "tb": 0.,
                "te": 1.,
                "noiseType":noiseType,
                "Set": SetOfIntervals(),
                }
        self.findtimes()
        self.case.setdefault('caseID',str(self))
        self._update()
    
    def toJSON(self):
        """returns the essential informations of self"""
        return json.dumps(self.case, cls= ComplexEncoder)
    
    def findtimes(self,AA=None,PathToFile='C:\lucmiaz\KG_dev_branch\KG\Measurements_example\MBBMZugExample'):
        """update the times attributes from the given data (mID, mic, measurement) give the measured values if possible (saves about 0.7s)"""
        if not AA:
            AA = measuredValues.from_json(PathToFile)
        self.case['tb']=AA.getVariable(self.case['mID'],self.case['mic'], 'Tb')
        self.case['te']=AA.getVariable(self.case['mID'],self.case['mic'], 'Te')
        
            
    
    def _update(self):
        """runs the initialisation of self.Set"""
        self.case['Set']=GraphicalIntervals(ax,displaybutton=False)
    
    def comparediscretizations(self, otherdisc, timeparam):
        """Compares the discretization of this case with the one of an algorithm whose results are given in otherdisc. timeparam variable contains the variables for the discretization. Returns a dictionnary with the number of True positives, True negatives, False positives and False negatives"""
        
        cont=False
        disc=self.discretize(timeparam, sum=False)
        if disc:
            if len(otherdisc)==len(disc):
                retTF={'FP':[], 'TP':[], 'FN':[],'TN':[]}
                retTF['TP'] = list(np.logical_and(otherdisc,disc))
                retTF['TN'] = list(np.logical_and(np.logical_not(otherdisc), np.logical_not(disc)))
                retTF['FP'] = list(np.logical_and( otherdisc, np.logical_not(disc)))
                retTF['FN'] = list(np.logical_and( np.logical_not(otherdisc),  disc))
                return retTF
            else:
                return None
        else:
            return None
    
    def discretize(self, timeparam):
        """discretize self in respect to parameters timeparam."""
        if self.Set:
            discret=self.Set.discretize(self,timeparam, None, False)#None means the param will not be displayed and the input will not be ordered.
            print("Discretization result : " + discret)
            return discret
        else:
            print("Empty set : no discretization possible")
            return None
    
    def save(self, mesPath):
        '''
        save Case to file
        '''
        mesPath = pathlib.Path(mesPath)
        casePath = mesPath.joinpath('test_cases').joinpath(self.case['author'])
        os.makedirs(casePath.as_posix(), exist_ok = True)
        name = str(self) + '.json'
        casePath = casePath.joinpath(name)
        print(casePath)
        with open(casePath.as_posix(), 'w') as fp:
            json.dump(self.case.__repr__(), fp)
    
    def __str__(self):
        """prints the name of the case"""
        return "case_"+str(self.case['mID'])+"_"+str(self.case['mic'])
    
    def __repr__(self):
        """gives a representation of the case"""
        return self.case.json
    
    @classmethod
    def from_JSON(cls, casePath):
        """@classmethod is used to pass the class to the method as implicit argument. Then we open a file in JSON located at casePath and give it to the class with **kwargs (meaning that we pass an arbitrary number of arguments to the class)
        """
        try:
            return cls(**json.load(open(casePath, 'r')))
        except FileNotFoundError:
            raise Error("The file in path" + casePath + " has not be found.")
            
    def importgraph(self):
        """import and displays the corresponding sound/graphic"""
        if self.case.get('caseId'):
            pass

## Test
if __name__ == "__main__":
    x = arange(100)/(79.0)
    y = sin(x)
    fig = plt.figure()
    ax = subplot(111,axisbg='#FFFFFF')

    ax.plot(x,y)
    plt.tight_layout()
    Newcase=Case(ax,'useful','m_0100','1','luc','Z')