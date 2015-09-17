<<<<<<< HEAD
import numpy as np
class SetOfIntervals(object):
=======
class RangeOfIntervals(object):
>>>>>>> master

    def __init__(self):
        self.RangeInter=[]
        self.length=0
        self.sorted=False
    
    def append(self, interv):
        """add a range to the list of intervals.
        need an Interval object"""
        self.sort()
<<<<<<< HEAD
        try:
            interv.get_x()
            test=True
        except AttributeError:
            test= False
        if test:
            for i in self.RangeInter:
                if interv.intersect(i):
                    a=self.RangeInter.index(i)
                    interv.union(i)
                    self.RangeInter.pop(a)
                    self.length-=1
            self.RangeInter.append(interv)
            self.length+=1
            self.sort()
        return test
=======
        for i in self.RangeInter:
            if interv.intersect(i):
                a=self.RangeInter.index(i)
                interv.union(i)
                self.RangeInter.pop(a)
                self.length-=1
        self.RangeInter.append(interv)
        self.length+=1
        self.sort()
>>>>>>> master
    
    def sort(self):
        self.RangeInter.sort()
        self.sorted=True
    
    def remove(self, bounds):
        """remove the given interval from the list"""
<<<<<<< HEAD
        if self.haselement(bounds):
            self.RangeInter.remove(bounds)
        else:
            self.removeIntersection(bounds)
        
    def removeIntersection(self, bounds):
        """remove the intersection between elements of RangeInter and the Interval bounds)"""
        a=0
        for inter in self.RangeInter:
            if inter.intersect(bounds):
                self.RangeInter.remove(inter)
                ret=inter.difference(bounds)
                self.RangeInter.append(ret[0])
                self.RangeInter.append(ret[1])
                a+=1
    
    def contains(self, element):
        """Return boolean telling if element is in self"""
        if not self.sorted:
            self.sort()
            continuer=True
            k=-1
            while continuer:
                k+=1
                continuer= not (self.RangeInter[k].contains(element)) and k<self.length-1
                return (self.RangeInter[k].contains(element) and k<self.length)
        elif not element:#check if emptyset
            return True
        else:
            return False
    
    def haselement(self, element):
        """Return True if element is in self"""
        return bool(self.RangeInter.count(element))

    def discretize(self, zerotime, endtime, deltatime):
        """return the boolean values of the characteristic function of the set RangeInter for the deltatimes from zerotime to endtime (return type numpy array of booleans)"""
        k=zerotime
        ret=[]
        while k<=endtime:
            ret.append(self.contains(k))
            k += deltatime
        return ret
=======
        self.RangeInter.remove(bounds)
>>>>>>> master
    
    def __repr__(self):
        a=""
        for i in self.RangeInter:
            a=a+" ["+str(i)+"] "
        return a
<<<<<<< HEAD
        
=======
>>>>>>> master
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
        
<<<<<<< HEAD
    def get_x(self):
        return self.xmin, self.xmax
        
    #representations, string format
    def __repr__(self):
        return '{}: {},{}'.format(self.__class__.__name__, self.xmin, self.xmax)
        
    def __str__(self):
        return str(self.xmin) + ', '+ str(self.xmax)
        
=======
    def get_min(self):
        return self.xmin
    def get_max(self):
        return self.xmax
    #representations, string format
    def __repr__(self):
        return '{}, {}'.format(self.__class__.__name__, self.xmin, self.xmax)
    def __str__(self):
        return str(self.xmin) + ', '+ str(self.xmax)
>>>>>>> master
    #interval operations
    def intersect(self,other):
        """Tells if intervals are intesecting"""
        return not self != other
<<<<<<< HEAD
        
    def intersection(self, other):
        """Gives the interval intersection"""
        if self.intersect(other):
            ret=Interval(max(self.xmin,other.xmin),min(self.xmax, other.xmax))
        else:
            ret=set()
        return ret
    
    def difference(self, other):
        """Return self minus intersection with other"""
        if self.contains(other):
            ret1=Interval(self.xmin,other.get_x()[0])
            ret2=Interval(other.get_x()[1],self.xmax)
            if ret1.ispoint():
                if ret2.ispoint():
                    return set(), set()
                else:
                    return set(), ret2
            else:
                return ret1, ret2
        elif self <= other:
            return Interval(self.xmin, other.get_x()[0]), set()
        else:
            return Interval(other.get_x()[1],self.xmax), set()
    
    def ispoint(self):
        """check if interval is only a point"""
        return self.xmin==self.xmax
    
    def contains(self,other):
        """Return True if self contains other"""
        return ((other <= self)and (other >= self))
    
    def isin(self,other):
        """Return True if self is in other"""
        return ((self <= other) and (self >= other))
        
=======
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
>>>>>>> master
    def union(self, other):
        """merge self and other together"""
        self.xmax=max(self.xmax, other.xmax)
        self.xmin=min(self.xmin, other.xmin)
        return self
<<<<<<< HEAD
        
    #sorting definitions
    def __lt__(self, other):
        return self.xmax <= other.get_x()[0]
        
    def __gt__(self,other):
        return self.xmin >= other.get_x()[1]
        
    def __eq__(self,other):
        return (self.xmax==other.xmax and self.xmin==other.xmin)
        
    def __ne__(self, other):
        """Intervals are not intersecting"""
        return self <= other or self >= other
        
    def __le__(self, other):
        return self.xmax <= other.get_x()[1]
        
    def __ge__(self,other):
        return self.xmin >= other.get_x()[0]
    
R=SetOfIntervals()
a=Interval(0,1)
b=Interval(3,4)
c=Interval(2,2.5)
d=Interval(2.5,3.5)
e=Interval(0,1)
f=Interval(3.6,3.7)
R.append(a)
R.append(b)
=======
    #sorting definitions
    def __lt__(self, other):
        return self.xmax < other.xmin:
    def __gt__(self,other):
        return self.xmin>other.xmax:
    def __eq__(self,other):
        return 
    def __ne__(self, other):
        """Intervals are not intersecting"""
        return self < other or self > other
    def __le__(self, other):
        return self.xmax <= other.xmax:
    def __ge__(self,other):
        return self.xmin >= other.xmin:
>>>>>>> master
