import matplotlib
from matplotlib.widgets import *  
from pylab import *

class SetOfIntervals(object):
    """Define a class of set of intervals, i.e. a closed of R"""
    def __init__(self):
        self.RangeInter=[]
        self.length=len(self.RangeInter)
        self.sorted=False
        self.lastinterval=None
        
    def append(self, interv):
        """add a range to the list of intervals.
        need an Interval object"""
        self.sort()
        if interv: #check if not None
            self.remove(interv)
            self.RangeInter.append(interv)
            self.length=len(self.RangeInter)
            self.sort()
            self.lastinterval=interv
            return interv
        else:
            return None
    
    def sort(self):
        """Sort the set of Intervals and union adjacent intervals"""
        self.RangeInter.sort()
        self.length=len(self.RangeInter)
        self.unionize()
        self.unionize()
    
    def remove(self, bounds):
        """remove the given interval from the list"""
        if self.haselement(bounds):
            self.RangeInter.remove(bounds)
        else:
            self.removeIntersection(bounds)
    
    def unionize(self):
        """Union intervals if adjacents"""
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
        """remove the intersection between elements of RangeInter and the Interval bounds"""
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
    
    def __repr__(self):
        a=""
        for i in self.RangeInter:
            a=a+" ["+str(i)+"] "
        return a

    def __str__(self):
        return "Range of intervals. Number of intervals : "+str(self.length)+"\n"+ self.__repr__()

class GraphicalIntervals(SetOfIntervals, AxesWidget):
    """Set of interval with graphical support"""
    def __init__(self, ax, useblit = True, **lineprops):
        """
        Add intervals to *ax*.  If ``useblit=True``, use the backend-
        dependent blitting features for faster updates (GTKAgg
        only for now).  *lineprops* is a dictionary of line properties.

        .. plot :: mpl_examples/widgets/cursor.py
        """
        AxesWidget.__init__(self, ax)
        SetOfIntervals.__init__(self)
        self.Rectangles=[]
        self.addremove=True
        toggle_selector.RS = RectangleSelector(ax, self.on_select, drawtype='line',button=1)
        connect('key_press_event', self.toggle_selector)
        connect('pick_event', self.on_pick)
        print("initialised")
    
    def _update(self):
        """update Rectangles and plot them"""
        for rect in self.Rectangles:
            rect[1].remove()
        self.Rectangles=[]
        for inter in self.RangeInter:
            coord=inter.get_x()
            rect=ax.add_patch(patches.Rectangle((coord[0],self.ax.get_xlim()[0]), coord[1]-coord[0], self.ax.get_ylim()[1], alpha=0.4, facecolor="#c7eae5", edgecolor="none"))
            self.Rectangles.append((inter,rect))
        self.ax.figure.canvas.draw()
    
    def on_select(self, eclick, erelease):
        """add the interval selectionned while holding left mouse click"""
        self.LastInterval=Interval(eclick.xdata,erelease.xdata)
        if not self.LastInterval.ispoint():
            self.append(self.LastInterval)
        print(self.LastInterval)
        self._update()
    
    def on_pick(self, event):
        """remove the interval selectionned while holding right mouse click"""
        print(str(event.artist))
        print("here")
        #self._update()  
        

    def toggle_selector(self, event):
        if event.key in ['Q', 'q'] and toggle_selector.RS.active:
            toggle_selector.RS.set_active(False)
            print("Key "+event.key+" pressed")
        if event.key in ['A', 'a'] and not toggle_selector.RS.active:
            toggle_selector.RS.set_active(True)
            print("Key "+event.key+" pressed")
        if event.key in ['\b'] and self.lastinterval:
            self.remove(self.lastinterval)
        if event.key in ['r','R']:
            print("Key "+str(event.key)+" pressed")
            self.LastInterval.remove()
            if self.addremove:
                print("Adding intervals")
            else:
                print("Removing intervals")
        if event.key in ['u','U']:
            print("Key "+event.key+" pressed")
            self.update()
                
    def __str__(self):
        self.sort()
        return "Graphical representation of : " + SetOfIntervals.__str__(self)

class Interval(object):
    """Create an closed interval. It is an object of length 2, sorted"""
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
        return '{}: {},{}'.format(self.__class__.__name__, self.xmin, self.xmax)
        
    def __str__(self):
        return str(self.xmin) + ', '+ str(self.xmax)
        
    #interval operations
    def intersect(self,other):
        """Tells if intervals are intesecting"""
        return not self != other
    
    def touch(self,other):
        """Tells if intervals touch each other"""
        return (self.xmin==other.get_x()[1] or self.xmax==other.get_x()[0])
        
    def intersection(self, other):
        """Gives the interval intersection"""
        if self.intersect(other):
            ret=Interval(max(self.xmin,other.xmin),min(self.xmax, other.xmax))
            if ret.ispoint():
                ret=None
        else:
            ret=None
        return ret
    
    def difference(self, other):
        """Return self minus intersection with other"""
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
        """check if interval is only a point"""
        return self.xmin==self.xmax
    
    def contains(self,other):
        """Return True if self contains other"""
        return ((other <= self)and (other >= self))
    
    def isin(self,other):
        """Return True if self is in other"""
        return ((self <= other) and (self >= other))
        
    def union(self, other):
        """merge self and other together"""
        self.xmax=max(self.xmax, other.xmax)
        self.xmin=min(self.xmin, other.xmin)
        return self
        
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
    
x = arange(100)/(79.0)
y = sin(x)
fig = figure
ax = subplot(111)
ax.plot(x,y)

Hello=GraphicalIntervals(ax)
show()
