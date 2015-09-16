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
            if interv==i:
                a=self.RangeInter.index(i)
                interv.merge(i)
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
        
    def get_min(self):
        return self.xmin
    def get_max(self):
        return self.xmax
    #representations, string format
    def __repr__(self):
        return '{}, {}'.format(self.__class__.__name__, self.xmin, self.xmax)
    def __str__(self):
        return str(self.xmin) + ', '+ str(self.xmax)
    #sorting definitions
    #== tests if intervals are intersecting, not if they are equals. 
    def __lt__(self, other):
        if self.xmax < other.xmin:
            return True
        else:
            return False
    def __gt__(self,other):
        if self.xmin>other.xmax:
            return True
        else:
            return False
    def __eq__(self,other):
        """Intervals are intesecting"""
        return not self != other
    def __ne__(self, other):
        """Intervals are not intersecting"""
        return self < other or self > other
    def __le__(self, other):
        if self.xmax <= other.xmax:
            return True
        else:
            return False
    def __ge__(self,other):
        if self.xmin >= other.xmin:
            return True
        else:
            return False
    def merge(self, other):
        """merge self and other together"""
        self.xmax=max(self.xmax, other.xmax)
        self.xmin=min(self.xmin, other.xmin)
        return self