import sys,os,pathlib
from kg.intervals import *
from kg.measurement_values import measuredValues
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from mpl_toolkits.axes_grid.inset_locator import inset_axes
from matplotlib.font_manager import FontProperties
from matplotlib.colors import LinearSegmentedColormap
from pylab import *
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
                "Z": SetOfIntervals(),#Zischen
                "quality": None, #quality of the detection
                "saved":False,
                }
        self.case['caseID'] = str(self)
    
    def compare(self, result, t , noiseType = 'Z', sum = True, full=True):
        """Compares the discretization of this case with the one of an algorithm whose results are given in otherdisc. timeparam variable contains the variables for the discretization. Returns a dictionnary with the number of True positives, True negatives, False positives and False negatives"""
        #restrict comparation between Tb and Te
        
        otherdisc=result
        try:
            fulldisc=self.case[noiseType].discretize(t)
            intdisc=[int(b) for b in fulldisc]
            assert( len(otherdisc) == len(fulldisc) )
            #assert(not any([i==None for i in disc]))
        except AssertionError:
            print('something wrong in function of ', self)
        if full:
            disc=fulldisc
        else: 
            mask = np.logical_and(t >= self.case['Tb'], t <= self.case['Te'])
            otherdisc = result[mask]
            disc = fulldisc[mask]
            t=t[mask]
        retTF={}
        retTF['TP'] = np.logical_and(otherdisc,disc)
        retTF['TN'] = np.logical_and(np.logical_not(otherdisc), np.logical_not(disc))
        retTF['FP'] = np.logical_and(otherdisc, np.logical_not(disc))
        retTF['FN'] = np.logical_and(np.logical_not(otherdisc),  disc)
        if sum:
            for k, v in retTF.items():
                retTF[k]= int(v.sum())
        else:
            retTF['t'] = t
            retTF['disc'] = disc
        return retTF, intdisc
    
    def discretize(self, noiseType, t):
        """saves a discretization for t and the noiseType"""
        self.case['disc'+noiseType+str(t)] = self.case[noiseType].discretize(t)
        return self.case['disc'+noiseType+str(t)]
    
    def set_quality(self, quality):
        """
        set quality of generated case:
        good: noise events are good to recognize
        medium: it is possible to detect noise events
        bad: noise events almost impossible to detects
        """
        if quality in ['good','medium','bad']:
            self.case['quality'] = quality
        else:
            print('Quality has to be in ' + str(['good','medium','bad']))
        
    def save(self, mesPath):
        '''
        save Case to file in mespath\test_cases\author\case_mID_mic_author.json
        '''
        if self.case['quality']  == None:
            print('Warning: case quality has to be set')
        casePath = mesPath.joinpath('test_cases').joinpath(self.case['author'])
        os.makedirs(casePath.as_posix(), exist_ok = True)
        name = str(self) + '.json'
        casePath = casePath.joinpath(name)
        self.to_JSON(casePath)
        self.case['saved']=True
        return(casePath)
    def set_saved(self, truth):
        if truth in [True, False]:
            self.case['saved']=truth
    def get_SOI(self, noiseType='Z'):
        return(self.case[noiseType])
    def set_SOI(self,listofSOI,noiseType='Z'):
        if isinstance(listofSOI, SetOfIntervals):
            self.case[noiseType]=SetOfIntervals()
            self.case[noiseType].copySOI(listofSOI)
    def get_bounds(self):
        """returns tb and te"""
        return(self.case['Tb'],self.case['Te'])
    def get_mat_path(self, listofpaths):
        """finds the exact path where the file .mat of this case is located relative to at least one of the paths given in listofpaths"""
        for pathtofile in listofpaths:#listofpaths contains Windows paths
            try:
                listfiles= os.listdir(pathtofile.joinpath('raw_signals').as_posix())
            except:
                pass
            else:
                if listfiles.count(self.case['mID']+"_"+str(self.case['mic'])+".mat")>0:
                    return pathtofile.joinpath('raw_signals/'+self.case['mID']+"_"+str(self.case['mic'])+".mat")
    def get_mIDmic(self):
        """returns the mID and mic"""
        return(self.case['mID']+"_"+str(self.case['mic']))
    def get_mID(self):
        """returns the mID of case"""
        return(self.case['mID'])
    def get_mic(self):
        """returns the mci of case"""
        return(self.case['mic'])
    def get_quality(self):
        """returns case quality"""
        return(self.case['quality'])
    def get_saved(self):
        """tells if the case has been saved"""
        return(self.case['saved'])
    def give_saved(self, truthvalue):
        """gives the truthvalue of this case savestate"""
        self.case['saved']=bool(truthvalue)
    def plot_triggers(self, ax, **kwargs):
        """
        Plot evaluation bounds Times as MBBM evaluations
        """
        bounds = ['Tb', 'Te']
        [ax.axvline(self.case[b], **kwargs) for b in bounds]
    
    def plot(self, ax, noiseType='Z',**kwargs):
        #todo: hidden by spectrogram, why?
        """plot the case on axis ax"""
        SOI = self.get_SOI(noiseType)
        ymin, ymax = ax.get_ylim()
        for xmin,xmax in SOI.tolist():
            ax.axvspan(xmin, xmax, ymin, ymax, alpha = 0.2, **kwargs)
            
    def plot_compare(self, ax, result , t , noiseType = 'Z',** kwargs):
        fontP = FontProperties()
        fontP.set_size('small')
        resTF,disc = self.compare(result , t , noiseType, sum=False)
        
        def inter(t,TF):
            x=TF.astype(float)
            dt = t[1]-t[0]
            tint=np.arange(t.min()-dt/2,t.max()+dt,dt/2)
            xint = np.interp(tint,t,x)>=0.5
            return(tint,xint)
        colors = {'TP':'#7de023','TN':'#c8ff96','FP':'#d14316','FN':'#ffac92'}
        ymin,ymax = ax.get_ylim()
        for k in ['TP','TN','FP','FN']:#blue green red yellow
            t,x = inter(resTF['t'], resTF[k])
            ax.fill_between(t,ymin,ymax, where = x,alpha= 0.5, color = colors[k])
        p1 = Rectangle((0, 0), 1, 1, fc=colors['TP'], alpha=0.5)
        p2 = Rectangle((0, 0), 1, 1, fc=colors['TN'],alpha=0.5)
        p3 = Rectangle((0, 0), 1, 1, fc=colors['FP'],alpha=0.5)
        p4 = Rectangle((0,0),1,1,fc=colors['FN'],alpha=0.5)
        ax.legend((p1, p2, p3,p4), ('True positive','True negative','False positive', 'False negative'),loc='upper right', bbox_to_anchor=(0.5, -0.05), fancybox=True, shadow=False, ncol=2, prop=fontP)

    def __str__(self):
        """prints the name of the case"""
        return( "case_"+str(self.case['mID'])+"_"+str(self.case['mic'])+'_'+str(self.case['author']))
    
    def __repr__(self):
        """gives a representation of the case"""
        return self.to_JSON()

    def to_JSON(self, filename = None):
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
    #@relative_to_mesPath("test_cases")
    def from_JSON(cls, casePath,**kwargs):
        """@classmethod is used to pass the class to the method as implicit argument. Then we open a file in JSON located at casePath and give it to the class with **kwargs (meaning that we pass an arbitrary number of arguments to the class)
        """
        if not isinstance(casePath, pathlib.Path):
            casePath=pathlib.Path(casePath)
        with casePath.open('r+') as file:
            dict = json.load(file)
        cl = cls(**dict)
        cl.case['quality'] = dict['quality']
        
        for nT in ['Z','KG']:
            dNT = dict[nT]
            set = [[int['xmin'] , int['xmax']] for int in dNT] 
            cl.get_SOI(nT).appendlistofduples(set)
        return(cl)


## decorator to set directory


# def relative_to_mesPath(relPath):
#     mesPath = pathlib.Path('Measurements_example\MBBMZugExample')
#     path = mesPath.joinpath(relPath)
#     def path_decorator(func):
#         def func_wrapper(*args,**kwargs):
#             print(kwargs)
#             author = kwargs['author']
#             mID = kwargs['mID']
#             mic = kwargs['mic']
#             name = "case_"+ mID +"_"+str(mic)+'_'+author +'.json'
#             path2 = path.joinpath(author).joinpath(name)
#             print(path2)
#             return(func( casePath=path, *args,**kwargs))
#         return(func_wrapper)
#     return(path_decorator)
# # 
# def decorator(func):
#     def f(*args,**kwargs):
#         return(Case.from_JSON(func(*args,**kwargs)))
#     return(f)
# 
# @decorator
# def init1(mesPath, author, mID, mic ):
#     name = "case_"+mID +"_"+str(mic)+'_'+author +'.json'
#     casePath = mesPath.joinpath('test_cases').joinpath(author).joinpath(name)
#     print(casePath.absolute())
#     return(casePath)
# #     
# # @decorator
# # def init2( mesPath, author ):
# #     authP = mesPath.joinpath('test_cases').joinpath(author)
# #     #collect cases
# #     casePaths = [ cp  for cp in authP.iterdir() if cp.match('case_**.json') ]
# #     print(casePaths)
# #     return(casePaths[0])
# # 
# # 

## Test
if __name__ == "__main__":
    from kg.detect import MicSignal
    from kg.algorithm import *
    from kg.algorithm import Case
    from kg.widgets import *
    from kg.measurement_values import measuredValues
    from kg.measurement_signal import measuredSignal
    mesPath = pathlib.Path('Measurements_example\MBBMZugExample')
    mesVal = measuredValues.from_json(mesPath)
    measuredSignal.setup(mesPath)
    W = CaseCreatorWidget.from_measurement(mesVal,'m_0100',[6])
    W.show()
##save
    casePath = mesPath.joinpath('test_cases/esr/case_m_0100_6_esr.json').absolute()
    case = Case.from_JSON(casePath)

    