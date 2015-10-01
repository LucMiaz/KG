import sys
from scipy.io import wavfile # get the api
from scipy.fftpack import fft
import matplotlib

matplotlib.use('Qt4Agg')
matplotlib.rcParams['backend.qt4']='PySide'

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.widgets import *
import matplotlib.patches as patches
from PySide import QtCore, QtGui
import matplotlib.pyplot as plt

def isclipped(xn, K=301, threshold=0.55, displayhist=False, normalizehist=False):
    """
    Tells if the signal xn is clipped or not based on the test by Sergei Aleinik, Yuri Matveev.
    Returns a boolean. 
    Reference: Aleinik S. and Matveev Y. 2014 : Detection of Clipped Fragments in Speech Signals, in International Journal of Electrical, Computer, Energetic, Electronic and Communication Engineering. World Academy of Science, Engineering and Technology, 8, 2, 286--292.
"""
    N=len(xn)
    H=histogram(xn,K,display=displayhist, normalize=normalizehist)
    #Find the very left non-zero k_l histogram bin index
    kl=0
    while H[kl]==0 and kl<=K/2:
        k+=1
    #Find the very right non-zero k_r histogram bin index
    kr=K-1
    while H[kr]==0 and kr>=K/2:
        kr-=1
    #Calculate Denom=k_r-k_l
    Denom=kr-kl
    #sets parameters
    yl0=H[kl]
    yr0=H[kr]
    dl=0
    dr=0
    Dmax=0
    #iteration
    while kr>kl :
        kl+=1
        kr-=1
        if H[kl]<=yl0:
            dl+=1
        else:
            yl0=H[kl]
            dl=0
        if H[kr]<=yr0:
            dr+=1
        else:
            yr0=H[kr]
            dr=0
        Dmax=max(Dmax,dl,dr)
    Rcl=2*Dmax/Denom
    return Rcl>threshold
    
def histogram(xn, K, display=False, normalize=False):
    """returns the function histogram of discrete time signal xn with K bins in histogram"""
    N=len(xn)
    xmin=xn[0]
    xmax=xn[0]
    #find min and max values of signal xn
    for n in range(0,N):
        if xn[n]<xmin:
            xmin=xn[n]
        if xn[n]>xmax:
            xmax=xn[n]
    #setting histogram to 0
    H=[0 for i in range(0,K)]
    for n in range(0,N):
        #calculate y(n)=(x(n)-x_min)/(x_max-x_min)
        yn=((xn[n]-xmin)/(xmax-xmin))#normalize
        #calculate bin index
        k=int(K*yn)
        #add one to the right bin index
        if k<K:
            H[k]+=1
        else:
            H[k-1]+=1
    if normalize:
        maximum=max(H)
        H=[i/maximum for i in H]
    if display:
        plt.bar(range(0,K),H,color='#d8b365')
    return H

fs, data = wavfile.read('C:/lucmiaz/KG_dev_branch/KG/Clipping/n-05-15-src2.wav') # load the data
a = data.T[0] # this is a two channel soundtrack, I get the first track 
#remove [0] if mono file
b=[(ele/2**8.)*2-1 for ele in a] # this is 8-bit track, b is now normalized on [-1,1)
#c = fft(b) # create a list of complex number
#d = len(c)/2  # you only need half of the fft list
def handleButton():
    print("clicked")


app = QtGui.QApplication(sys.argv)
fig = Figure(figsize=(600, 600), dpi=72, facecolor='#1a1a1a', edgecolor=(0,0,0))
win = QtGui.QMainWindow()
canvas = FigureCanvas(fig)

##color properties
fig.set_facecolor('#1a1a1a')
textcolor='#f5f5f5'
axescolor='#f5f5f5'
axbgcolor='#272822'
bgcolor='#aaaaaa'
palette=QtGui.QPalette()
palette.setColor(QtGui.QPalette.Window,axbgcolor)
palette.setColor(QtGui.QPalette.Button,textcolor)
palette.setColor(QtGui.QPalette.ButtonText,axbgcolor)
palette.setColor(QtGui.QPalette.Text,axbgcolor)
palette.setColor(QtGui.QPalette.Base,textcolor)
palette.setColor(QtGui.QPalette.AlternateBase,'#f3f3f3')
palette.setColor(QtGui.QPalette.WindowText,textcolor)
win.setPalette(palette)
ax = fig.add_subplot(111)
for i in ['bottom','top','right','left']:
    ax.spines[i].set_color(axescolor)
for i in ['x','y']:
    ax.tick_params(axis=i,colors=axescolor)
ax.yaxis.label.set_color(textcolor)
ax.xaxis.label.set_color(textcolor)
ax.title.set_color(textcolor)
font={'family':'sans-serif','weight':'regular','size':13}
matplotlib.rc('font',**font)
##

win.setCentralWidget(canvas)

ax.set_axis_bgcolor(axbgcolor)
#btn = QtGui.QPushButton('Test')
#btn.clicked.connect(handleButton)
#win.addDockWidget(core.Qt.LeftDockWidgetArea,btn)
#combo = QtGui.QComboBox()
#plt.plot(abs(c[:(d-1)]), color='#5ab4ac') 
import random
br=[]
for i in range(0,100):
    br.append(random.randint(i,i+10))
ax.plot(br, color='#f5f5f5',zorder=999)
ax.add_patch(patches.Rectangle((1,ax.get_ylim()[0]), 10, ax.get_ylim()[1]-ax.get_ylim()[0], alpha=0.4, facecolor="#d8b365", edgecolor="none"))
ax.add_patch(patches.Rectangle((50,ax.get_ylim()[0]), 15, ax.get_ylim()[1]-ax.get_ylim()[0], alpha=0.4, facecolor="#d8b365", edgecolor="none"))
ax.add_patch(patches.Rectangle((70,ax.get_ylim()[0]), 7, ax.get_ylim()[1]-ax.get_ylim()[0], alpha=0.4, facecolor="#d8b365", edgecolor="none"))
ax.add_patch(patches.Rectangle((20,ax.get_ylim()[0]), 12, ax.get_ylim()[1]-ax.get_ylim()[0], alpha=0.4, facecolor="#5ab4ac", edgecolor="none"))
ax.add_patch(patches.Rectangle((65,ax.get_ylim()[0]), 10, ax.get_ylim()[1]-ax.get_ylim()[0], alpha=0.4, facecolor="#5ab4ac", edgecolor="none"))
#ret=isclipped(b, displayhist=False, normalizehist=False)
#print(ret)
#ax.plot(h,color='#5ab4ac')
#e=a.clip(-6000,6000)
#f=[(ele/2**8.)*2-1 for ele in e]
#☺g=histogram(ts.signals['1']['y'],301, ax, True)
#ret=isclipped(f,displayhist=True, normalizehist=True)
#print(ret)

# add the plot canvas to a window
win.show()
sys.exit(app.exec_())
