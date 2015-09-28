from kg.intervals import *
from matplotlib.widgets import *
import matplotlib.patches as patches 
import matplotlib.pyplot as plt
import json
class GraphicalIntervalsHandle(AxesWidget):
    """
    Graphical support for SetOfIntervals. Have a list called `Rectangles` corresponding to intervals of the class `SetOfIntervals`. This list containts duples : an Interval and a patch (displayed rectangle) linked to an axis (stored in self.ax). This allows to update `Rectangle` from the SetOfInterval attribute `RangeInter` and vice versa, i.e. when we want to delete a displayed patch, we look it up in `Rectangle` (by itering over its second argument), and then we can delete the corresponding `Interval` in `RangeInter`.\n
Method                | Description
--------------------- | ----------
_update()             | updates Rectangles and plot them
on_select(eclick, erelease) | adds the interval selectionned while holding left mouse click
connect(rect)         | connects the rectangle rect to the figure
removerectangle(rect) | removes rect from the figure, from Rectangles list and removes the corresponding interval from RangesInter
on_pick(event)        | removes the interval selectionned while holding right mouse click
toggle_selector(event) | handles key_events
call_discretize(event) | calls the method `discretize` from an event, such as a button
changeDiscretizeParameters(listofparams) | changes the parameters of the discretization (usefull if calling with button). Give list or tuple of length 3
discretize(zerotime, endtime, deltatime, axis=self.axis) | returns the characteristic function of range(zerotime,endtime, deltatime) in respect to RangeInter. Optional argument is the axis where one need to represent the points of the characteristic function. If one does not want any graphical representation, give None as axis
    """
    
    def __init__(self, ax, SetOfInt):#, displaybutton=True, useblit = True):
        """initialisation of object. Needs an axis to be displayed on. Optional SetOfIntervals."""
        #super classes init
        AxesWidget.__init__(self, ax)
        self.Set = SetOfInt
        self.tolerance = 10
        self.rectanglecolor='#c7eae5'
        #attibutes
        self.Rectangles = []
        self.background = None
        self.firsttime=True
        self.ymin= -20
        #last discretization points
        #self.drewdiscpts=None
        #discretization arguments
        #self.discargs=(0.,1.,0.1)
        #connecting
        SpanSelector(ax, self.on_select,'horizontal', useblit=True, rectprops=dict(alpha=0.5,facecolor='red'), minspan=0.01, span_stays=True)
        plt.connect('pick_event', self.on_pick)
        # #adding pre-existing intervals
        # if Range.length>0:
        #     self.RangeInter=Range.RangeInter
        #     self.sort()
        #     print("Imported a Set Of Intervals")
        #     self._update()
        # print("Initialised GraphicalIntervals.")
        # #displaying button for discretization
        # if displaybutton:
        #     axdisc = plt.axes([0.01, 0.05, 0.1, 0.075])
        #     bprev = matplotlib.widgets.Button(axdisc, 'Discretize')
        #     bprev.on_clicked(self.call_discretize)
        # ax.grid(True)

    #operations on rectangles: displaying/removing
    def connect(self,rect):
        """connects rect to figure"""
        cidonpick = rect.figure.canvas.mpl_connect(
            'pick_event', self.on_pick)
        return cidonpick
    
    def sort(self):
        """sorts SetOfIntervals and update self"""
        self.Set.sort()
        self._update()
    
    def _update(self):
        """updates Rectangles and plot them"""
        if self.firsttime:
            self.background = self.ax.figure.canvas.copy_from_bbox(ax.bbox)
        Rrm,Radd= self.compare()#gets rectangles to remove and intervals to add
        for rect in Rrm:
            rect.set_visible(False)
            self.Rectangles.remove(rect)
        self.background=self.ax.figure.canvas.copy_from_bbox(ax.bbox)
        for interv in Radd:
            rect=ax.axvspan(interv.get_x()[0],interv.get_x()[1],-10,10, visible=False, alpha=0.5, facecolor=self.rectanglecolor, picker=self.tolerance)
            self.Rectangles.append(rect)
            self.ax.draw_artist(rect)
            rect.set_visible(True)
        if self.background is not None:
            self.canvas.restore_region(self.background)
        self.canvas.blit(self.ax.bbox)
        
    
    def on_select(self, xmin, xmax):
        """Handles the rectangle selection"""
        interv=Interval(xmin,xmax)
        self.Set.append(interv)
        self._update()
    
    def on_pick(self, event):
        """removes the interval right mouseclicked"""
        if event.mouseevent.button==3:
            self.Set.remove(Interval(event.artist.get_xy()[0][0],event.artist.get_xy()[2][0]))
            self._update()
    
    def compare(self):
        """Compares Rectangles and Set : gives a list of Rectangles to remove, gives a list of Intervals to add."""
        Rrm=[]#list of Intervals to remove from Rectangles
        Radd=self.Set.getRange()#list of ordered duples to add to Rectangles
        if len(Radd)==0:
            for rect in self.Rectangles:
                Rrm.append(Interval(rect.xmin,rect.xmax))
        else:
            for rect in self.Rectangles:
                print(rect.get_xy())
                interrect=Interval(rect.get_xy()[0][0],rect.get_xy()[2][0])
                if self.Set.haselement(interrect):
                    try:
                        Radd.remove(interrect)#the interval is already displayed
                    except ValueError:
                        print("problem removing Interval from Radd, check compare function")
                else:
                    Rrm.append(rect)#the rect needs to be removed from display
        return Rrm, Radd
            
            
        
    #discretization        
    # def call_discretize(self,event):
    #     """calls the method discretize from an event, such as a button"""
    #     self.discretize(self.discargs[0],self.discargs[1],self.discargs[2])
    
    def toJSON(self):
        """Calls toJSON method for self.Set"""
        return self.Set.toJSON()
           
    # def discretize(self, zerotime, endtime, deltatime, axis=1):
    #     """returns the characteristic function of range(zerotime,endtime, deltatime) in respect to RangeInter. Optional argument is the axis where one need to represent the points of the characteristic function. If one does not want any graphical representation, give None as axis"""
    #     if axis==1:
    #         axis=self.ax
    #     if self.length>0:
    #         #first remove the old discretized points
    #         try:
    #             self.drewdiscpts.remove()
    #         except:
    #             print("Empty discretized points : no points removed")
    #         discpts=super(GraphicalIntervals,self).discretize(zerotime,endtime,deltatime)
    #         if axis:
    #             #add the new ones
    #             self.drewdiscpts = axis.scatter(discpts[0],discpts[1], marker='.', s=150, c=discpts[1],linewidths=1, cmap= plt.cm.coolwarm)
    #             print("Drew discretization points")
    #         return discpts
                   
    #string representation
    def __str__(self):
        self.sort()
        return "Graphical representation of : " + SetOfIntervals.__str__(self)

### test
if __name__ == "__main__":
    f,ax = plt.subplots()
    plt.subplots_adjust(bottom=0.2)
    ax.pcolormesh(np.random.random((100, 100)), cmap='gray')
    ax.set_title('Left click to add/drag a point\nRight-click to delete')
    
    Hello = GraphicalIntervalsHandle(ax,SetOfIntervals())