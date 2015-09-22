from kg import intervals
import json
import time

class Case(object):
    """
    Defines a case of study
    """
    def __init__(self, ax, data, author):
        """
        Takes a set of data and an axis to display the data on.
        """
        self.measurement=[]
        self.mID=[]
        self.mic=[]
        self.author=author
        self.date=[]
        self.dealingdate=time.strftime('%d.%m.%Y')
        self.tb=0
        self.te=0
        if self.importdata(data):
            self.Set=GraphicalIntervals(ax,displaybutton=False)
        else:
            print("Data could not be imported")
        
        
        
    def importdata(self, data):
        """import the data to Case attributes"""
        ret=True
        try:
            self.case = data['caseID']
        except:
            ret=False
        if ret:
            try:
                self.measurement=data['measurement']
            except:
                ret=False
            if ret:
                try:
                    self.mID=data['mID']
                except:
                    ret=False
                if ret:
                    try:
                        self.mic=data['mic']
                    except:
                        ret=False
                    try:
                        self.tb=data['tb']
                    except:
                        ret=False
                    if ret:
                        try:
                            self.te=data['te']
                        except:
                            ret=False
                        if ret:
                            try:
                                self.date=data['date']
                            except:
                                ret=False
        return ret
        
        def importgraph(self):
            """import and displays the corresponding sound/graphic"""
            
