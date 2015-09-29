import json
class SetOfIntervals(object):
    """
    Defines a class of set of intervals, i.e. a closed of R
    Attribute  | type
    ---------- | ------------
    RangeInter | list of Intervals
    length     | integer
    sorted     | boolean
    
    Method                  | Description              | Return type
    ----------------------- | ------------------------ | -----------
    R.append(a)             | adds Interval `a` to `R` | none
    R.contains(a)           | tests if `a` in `R`      | boolean
    R.discretize(tb,te,dt)  | discretizes `R` in `[tb,te]` step `dt`. Gives $\Xi_{\text{RangeInter}}(\text{Range(tb,te,dt)})$       | list
    R.remove(a)             | removes Interval `a` from `R` | none
    R.removeIntersection(a) | called by `remove()`     | none
    R.haselement(a)         | tests if `a` is an element of the list  R.RangeInter | boolean
    R.sort()                | sorts Intervals in `R.RangeInter` | none
    isempty(self)`          | Tells if self is empty   | boolean
    toJSON(self)`           | returns a JSON serializable representation of self
    fromJSONfile(self, filename)` | adds Intervals to self from a JSON file directly   | boolean
    fromJSON(self, data)`   | append data['SetOfIntervals'] | boolean
    save(self, filename)`   | saves self to filename in json
    """
    
    def __init__(self):
        self.RangeInter=[]
        self.length=len(self.RangeInter)
        self.sorted=False
        self.lastinterval=None
        
    def append(self, interv):
        """adds a range to the list of intervals.
        need an Interval object"""
        self.sort()
        if interv: #check if not None
            if not interv.ispoint():
                self.remove(interv)
                self.RangeInter.append(interv)
                self.length=len(self.RangeInter)
                self.sort()
                self.lastinterval=interv
                return interv
            else:
                return None
        else:
            return None
    
    def appendlistofduples(self,listofduples):
        """adds a list of duples (viewed as an interval) to the SetOfRange. Alternatively one can give a list of lists containg two elements, e.g. [[1.0,2.0],[2.5,3.0],[2.8,4.0]]"""
        try:
            list(listofduples)
        except TypeError:
            print("Please give me a list")
            return False
        if len(listofduples)>0:
            if isinstance(listofduples[0],Interval):
                for inter in range(0,len(listofduples)):
                    self.append(listofduples[inter])
                return True
            else:
                for inter in range(0,len(listofduples)):
                    self.append(Interval(listofduples[inter][0], listofduples[inter][1]))
                return True
        else:
            print("empty list")
            return False
    
    def sort(self):
        """sorts the set of Intervals and union adjacent intervals"""
        self.RangeInter.sort()
        self.length=len(self.RangeInter)
        self.unionize()
        self.unionize()
    
    def remove(self, bounds):
        """removes the given interval from the list"""
        if self.haselement(bounds):
            self.RangeInter.remove(bounds)
        else:
            self.removeIntersection(bounds)
            
    def removebyindex(self, index):
        """removes the interval at index in RangeInter"""
        interv=self.RangeInter[index]
        self.remove(interv)
    
    def tolist(self):
        """returns a list of list representing intervals"""
        a=[]
        for inter in self.RAngeInter:
            a.append(inter.tolist())
        return a
    
    def getRange(self):
        """returns RangeInter"""
        a=[]
        for inter in self.RangeInter:
            a.append(inter.copy())
        return a
    
    def tolistsep(self):
        """returns two lists with xmins and xmaxs"""
        a=[]
        b=[]
        for inter in self.RangeInter:
            l=inter.get_x()
            a.append(l[0])
            b.append(l[1])
        return a,b
    
    def unionize(self):
        """Unions intervals if adjacents"""
        if not self.sorted:
            self.RangeInter.sort()
        if self.length>1:
            for inter in self.RangeInter:
                k = self.RangeInter.index(inter)
                if k < self.length-1:
                    if inter.touch(self.RangeInter[k+1]):
                        new=inter.union(self.RangeInter[k+1])
                        self.RangeInter.remove(self.RangeInter[k+1])
                        self.RangeInter.remove(inter)
                        self.RangeInter.append(new)
                    self.length=len(self.RangeInter)
    
    def removeIntersection(self, bounds):
        """removes the intersection between elements of RangeInter and the Interval bounds"""
        toberemoved=[]
        tobeadded=[]
        for inter in self.RangeInter:
            if inter.intersect(bounds):
                if bounds.contains(inter):
                    toberemoved.append(inter)
                else:
                    toberemoved.append(inter)
                    ret=inter.difference(bounds)
                    if ret[0]:
                        tobeadded.append(ret[0])
                    if ret[1]:
                        tobeadded.append(ret[1])
        for remo in toberemoved:
            self.RangeInter.remove(remo)
        for added in tobeadded:
            self.RangeInter.append(added)
    
    def contains(self, element):
        """returns boolean telling if element is in self"""
        if not self.sorted:
            self.sort()
            continuer=True
            k=-1
            while continuer:
                k+=1
                try:
                    continuer= not (self.RangeInter[k].contains(element)) and k<self.length-1
                    return (self.RangeInter[k].contains(element) and k<self.length)
                except IndexError:
                    print("Empty Range")
                    return False
        elif not element:#check if emptyset
            return True
        else:
            return False
    
    def containspoint(self, flt):
        """checks if the float flt is inside one of the Interval of self.RangeIntervals"""
        ret=None
        for inter in self.RangeInter:
            if inter.containspoint(flt):
                ret=self.RangeInter.index(inter)
        return ret
        
    def haselement(self, element):
        """returns True if element is in self"""
        return bool(self.RangeInter.count(element))
    
    def isempty(self):
        """tells if self is empty"""
        return self.length==0

    def discretize(self, zerotime, endtime, deltatime):
        """returns the characteristic function of the set RangeInter for the deltatimes from zerotime to endtime (return type is a duple of lists)"""
        k=zerotime
        ret=([],[])
        while k<=endtime:
            ret[1].append(self.containspoint(k))
            ret[0].append(k)
            k += deltatime
        return ret
        
    # def changeDiscretizeParameters(self, listofparams):
    #     """method to change the parameters of the discretization (usefull if calling with button)"""
    #     if listofparams:
    #         if len(listofparams)==3:
    #             try:
    #                 self.discargs=tuple(listofparams)
    #                 return True
    #             except:
    #                 print("Could not change discretization parameters : type not convertible to tuple")
    #                 return False
    #         else:
    #             print("Wrong lenth of parameters given for discretization. Default values set : "+str(self.discargs))
    #             return False
    #     else:
    #         print("Empty list of discretization parameters. Default values set : "+str(self.discargs))
    #         return False
    
    def toJSON(self,rounding=4):
        """returns a JSON serializable representation of self, rounding"""
        self.sort()
        a=[]
        for i in self.RangeInter:
            a.append(i.toJSON(rounding))
        return a
    
    def fromJSONfile(self, filename):
        """adds Intervals to self from a JSON file directly"""
        fileJSON=open(filename,'r')
        dataJSON=json.load(fileJSON)
        return self.fromJSON(dataJSON)
    
    def fromJSON(self, data):
        """adds Intervals to self from data (in JSON format). Takes the list of interval from 'SetOfIntervals' index"""
        for i in data['SetOfIntervals']:
            self.append(Interval(i['xmin'],i['xmax']))
        return True
    
    def __repr__(self):
        a=""
        for i in self.RangeInter:
            ind=self.RangeInter.index(i)
            if ind>0:
                a+=','
            a+="["+str(i)+"]"
        return a

    def __str__(self):
        return "Range of intervals. Number of intervals : "+str(self.length)+"\n"+ self.__repr__()
        
    def save(self, filename, rounding=0):
        """saves self to filename in json"""
        try:
            file=open(filename, "w")
            json.dump(self.toJSON(rounding),file)
            print("data written in openned file : "+filename)
        except NameError:
            with open(filename, 'w'):
                print(filename + "openned")
                json.dump(self.toJSON(rounding), filename)
                print("data written in "+filename)

class Interval(object):
    """
    Creates an closed interval. It is an object of length 2, sorted\n
    Attribute  | type
    --------   | -------
    xmin       | float
    xmax       | float
    
    Method               | Description                            | Return type
    -------------------- | -------------------------------------- | ------------
    get_x()              | gives xmin,xmax                        | two floats
    intersect(other)     | tests if intersection                  | boolean
    intersection(other)  | gives intesection                      | Interval
    difference(other)    | gives self minus other                 | Interval
    ispoint()            | tests if xmin==xmax                    | boolean
    contains(other)      | Tests if other is in self              | boolean
    isin(other)          | tests if self is contained in other    | boolean
    self < other         | `self.xmax < other.xmin`               | boolean
    self > other         | `self.xmin > other.xmax`               | boolean
    self==other          | same intervals                         | boolean
    self != other        | the two intervals are not intersecting | boolean
    self <= other        | not `self > other`                     | boolean
    self >= other        | not `self < other`                     | boolean
    toJSON(rounding)     | JSON format of Interval, wt rounding   | dict
    """
    def __init__(self, xmin,xmax):
        """initialization of an Interval. Required : two floats"""
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
        """returns xmin and xmax"""
        return self.xmin, self.xmax
        
    #interval operations
    def intersect(self,other):
        """tells if intervals are intesecting"""
        return not self != other
    
    def touch(self,other):
        """tells if intervals touch each other"""
        return (self.xmin==other.get_x()[1] or self.xmax==other.get_x()[0])
        
    def intersection(self, other):
        """gives the interval intersection"""
        if self.intersect(other):
            ret=Interval(max(self.xmin,other.xmin),min(self.xmax, other.xmax))
            if ret.ispoint():
                ret=None
        else:
            ret=None
        return ret
    
    def union(self, other):
        """merges self and other together"""
        self.xmax=max(self.xmax, other.xmax)
        self.xmin=min(self.xmin, other.xmin)
        return self
    
    def difference(self, other):
        """returns self minus intersection with other"""
        if self.contains(other):
            ret1=Interval(self.xmin,other.get_x()[0])
            ret2=Interval(other.get_x()[1],self.xmax)
            if ret1.ispoint():
                if ret2.ispoint():
                    return None, set()
                else:
                    return None, ret2
            else:
                return ret1, ret2
        elif self <= other:
            return Interval(self.xmin, other.get_x()[0]), None
        else:
            return Interval(other.get_x()[1],self.xmax), None
    
    def ispoint(self):
        """checks if interval is only a point"""
        return self.xmin==self.xmax
    
    def contains(self,other):
        """returns True if self contains other"""
        return ((other <= self)and (other >= self))
    
    def isin(self,other):
        """returns True if self is in other"""
        return ((self <= other) and (self >= other))
    
    def containspoint(self, flt):
        """checks if float flt is in the interval self"""
        return self.xmin<=flt and self.xmax>=flt
        
    #sorting definitions
    def __lt__(self, other):
        return self.xmax < other.get_x()[0]
        
    def __gt__(self,other):
        return self.xmin > other.get_x()[1]
        
    def __eq__(self,other):
        return (self.xmax==other.xmax and self.xmin==other.xmin)
        
    def __ne__(self, other):
        """Intervals are not intersecting"""
        return self < other or self > other
        
    def __le__(self, other):
        return self.xmax <= other.get_x()[1]
        
    def __ge__(self,other):
        return self.xmin >= other.get_x()[0]
    
    #representations, string format
    def __repr__(self):
        return '{}: {},{}'.format(self.__class__.__name__, self.xmin, self.xmax)
        
    def __str__(self):
        return str(self.xmin) + ', '+ str(self.xmax)
    
    def toJSON(self, rounding):
        """returns a JSON compatible representation of self, if round==0, then no rounding"""
        if rounding==0:
            return {'xmin':self.xmin, 'xmax':self.xmax}
        else:
            ex=10**rounding
            return {'xmin':int(self.xmin*ex+0.5)/ex, 'xmax':int(self.xmax*ex+0.5)/ex}
    
    def tolist(self):
        """returns a list representing the interval"""
        return [self.xmin, self.xmax]
    
    def copy(self):
        """returns a copy of the interval"""
        return Interval(self.xmin,self.xmax)
        
class ComplexEncoder(json.JSONEncoder):
    def default(self, obj):
        # if isinstance(obj,GraphicalIntervals):
        #     return obj.toJSON()
        if isinstance(obj, SetOfIntervals):
           return obj.toJSON()
        if isinstance(obj, Interval):
            return obj.toJSON()
        # Let the base class default method raise the TypeError
        return json.JSONEncoder.default(self, obj)
### test
if __name__ == "__main__":
    a=SetOfIntervals()
    a.append(Interval(0.,1.))
    a.append(Interval(10.,11.))
    print(a)
