import numpy as np
class RangeOfIntervals(object):

    def __init__(self):
        self.RangeInter=[]
        self.length=0
        self.sorted=False
    
    def append(self, interv):
        """add a range to the list of intervals.
        need an Interval object"""
        self.sort()
        for i in self.RangeInter:
            if interv.intersect(i):
                a=self.RangeInter.index(i)
                interv.union(i)
                self.RangeInter.pop(a)
                self.length-=1
        self.RangeInter.append(interv)
        self.length+=1
        self.sort()
    
    def sort(self):
        self.RangeInter.sort()
        self.sorted=True
    
    def remove(self, bounds):
        """remove the given interval from the list"""
        self.RangeInter.remove(bounds)
    
    def isin(self, element):
        """Return boolean telling if element is in self"""
        if not self.sorted:
            self.sort()
        continuer=True
        k=-1
        while continuer:
            k+=1
            continuer=(self.RangeInter[k].get_x()[1]<element)
        return (self.RangeInter[k].get_x()[0]< element and k<len(self.RangeInter))

    def discretize(self, zerotime, endtime, deltatime):
        """return the boolean values of the characteristic function of the set RangeInter for the deltatimes from zerotime to endtime (return type numpy array of booleans)"""
        k=zerotime
        ret=[]
        while k<=endtime:
            ret.append(self.isin(k))
            k += deltatime
        return ret
    
    def __repr__(self):
        a=""
        for i in self.RangeInter:
            a=a+" ["+str(i)+"] "
        return a
        
    def __str__(self):
        return "Range of intervals. Number of intervals : "+str(self.length)+"\n"+ self.__repr__()

class Interval(object):
    """create an object of length 2, sorted"""
    def __init__(self, xmin,xmax):
        try: 
            xmin==float(xmin)
        except ValueError:
            raise ValueError("Error while initializing Bounds object : xmin cannot be converted to float")
        try: xmax==float(xmax)
        except:
            raise ValueError("Error while initializing Bounds object : xmax cannot be converted to float")
        self.xmin=min(xmin,xmax)
        self.xmax=max(xmin,xmax)
        
    def get_x(self):
        return self.xmin, self.xmax
        
    #representations, string format
    def __repr__(self):
        return '{}, {}'.format(self.__class__.__name__, self.xmin, self.xmax)
        
    def __str__(self):
        return str(self.xmin) + ', '+ str(self.xmax)
        
    #interval operations
    def intersect(self,other):
        """Tells if intervals are intesecting"""
        return not self != other
        
    def intersection(self, other):
        """Gives the interval intersection"""
        if self.intersect(other):
            self.xmax=min(self.xmax, other.xmax)
            self.xmin=max(self.xmin,other.xmin)
            return self
        else:
            self.xmax=0
            self.xmin=0
            return self
            
    def union(self, other):
        """merge self and other together"""
        self.xmax=max(self.xmax, other.xmax)
        self.xmin=min(self.xmin, other.xmin)
        return self
        
    #sorting definitions
    def __lt__(self, other):
        return self.xmax < other.xmin
        
    def __gt__(self,other):
        return self.xmin>other.xmax
        
    def __eq__(self,other):
        return (self.xmax==other.xmax and self.xmin==other.xmin)
        
    def __ne__(self, other):
        """Intervals are not intersecting"""
        return self < other or self > other
        
    def __le__(self, other):
        return self.xmax <= other.xmax
        
    def __ge__(self,other):
        return self.xmin >= other.xmin
        
