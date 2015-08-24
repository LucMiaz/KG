from PySide import QtGui, QtCore
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
matplotlib.use('Qt4Agg')
matplotlib.rcParams['backend.qt4']='PySide'
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from mpl_toolkits.axes_grid.inset_locator import inset_axes
import brewer2mpl

#plt.ioff()

class BarCanvas(FigureCanvas):
    '''
    canvas with moving bar self.bar.
    Two other vertical bar for time tBegin and tEnd
    '''
    def __init__(self, nrow = 1):
        self.figure, self.axes = plt.subplots(nrow,1,sharex=True)
        if nrow == 1:
            self.axes = [self.axes]
        FigureCanvas.__init__(self,self.figure)
        QtGui.QWidget.setSizePolicy(self, QtGui.QSizePolicy.Expanding,
                                            QtGui.QSizePolicy.Expanding)
        #FigureCanvas.updateGeometry(self)
        self.bar = []
        self.x_limits = None
        for ax in self.axes:
            self.bar.append(ax.axvline(linewidth = 1.5, alpha = 0, color='black'))

    def set_initial_figure(self):
        self.x_limits = self.axes[0].get_xlim()
        self.draw()
        self.set_background()

    def set_background(self):
        self.ax_background = []
        for ax in self.axes:
            self.ax_background.append(self.copy_from_bbox(ax.bbox))
        
    def rm_bar(self,alpha=0):
        for bar in self.bar:
            bar.set_alpha(alpha)

    def update_P(self, t):
        '''
        update bar position at time t
        '''
        for bar, ax_b, ax in zip(self.bar, self.ax_background, self.axes):
            bar.set_xdata(t)
            bar.set_alpha(1)
            self.restore_region(ax_b)
            ax.draw_artist(bar)
            self.figure.canvas.blit(self.figure.bbox)
            
    def set_xbounds(self, x_min = None, x_max = None):
        self.rm_bar()
        if x_max == None:
            x_max = self.x_limits[1]
        if x_min == None:
            x_min = self.x_limits[0]
        self.axes[0].set_xbound(x_min, x_max)
        self.draw()
        self.set_background()
        
        
    def resizeEvent(self, e):
        self.rm_bar()
        FigureCanvas.resizeEvent(self,e)
        self.set_background()