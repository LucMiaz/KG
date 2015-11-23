'''
short Time Fourier Transform tools
plots:
- plot PSD
- stft Widget
'''
import sys
import matplotlib
from mpl_toolkits.axes_grid.inset_locator import inset_axes
from matplotlib.colors import LinearSegmentedColormap
#import seaborn as sns
import brewer2mpl
#sns.set(style='ticks', palette='Set2')
sys.path.append('D:\GitHub\myKG')
import mySTFT
from mySTFT.stft import *


def plot_spectrogram(X, param, ax, colorbar = False, title = 'Spectrogram', dB= True, freqscale = 'log', dBMax = None, scaling = 'density', **kwargs):
    # TODO: correct t axis scala
    """
    plot the spectrogram of a STFT
    """
    sR = param['sR']
    # PSD
    PSD, freq, t_i =  stft_PSD(X, param, scaling = scaling, **kwargs)
    if dB:
        Z = 10*np.log10(PSD) - 20*np.log10(2e-5)
    else:
        Z = PSD
    # tempo e frequenza per questo plot é ai bordi
    df, __ = frequency_resolution(param['N'],sR)
    tR = param['R']/sR
    t = np.hstack([t_i[0]-tR/2, t_i + tR/2])
    freq = np.hstack([ freq[0]-df/2, freq + df/2])
    X , Y = np.meshgrid(t , freq)
    
    # plotting
    ax.set_title(title, fontsize = 10)
    #cmap = brewer2mpl.get_map('RdPu', 'Sequential', 9).mpl_colormap
    colormap=['#fff7f3','#fde0dd','#fcc5c0','#fa9fb5','#f768a1','#dd3497','#ae017e','#7a0177','#49006a']
    cmap=LinearSegmentedColormap.from_list('YeOrRe',colormap)
    
    #cmap=LinearSegmentedColormap('RdPu',cmap)
    if dBMax==None:
        norm = matplotlib.colors.Normalize(vmin = 0)
    else:
        norm = matplotlib.colors.Normalize(vmin = 0, vmax=dBMax)
    # np.round(np.max(ZdB)-60 ,-1), vmax = np.round(np.max(ZdB)+5,-1), clip = False)
    spect = ax.pcolormesh(X, Y, np.transpose(Z), norm=norm, cmap = cmap)
    #legenda
    if colorbar:
        axcolorbar = inset_axes(ax,
                width="2.5%", # width = 10% of parent_bbox width
                height="100%", # height : 50%
                loc='upper left',
                bbox_to_anchor=(1.01, 0., 1, 1),
                bbox_transform=ax.transAxes,
                borderpad=0,
                )
        axcolorbar.tick_params(axis='both', which='both', labelsize=8)
        ax.figure.colorbar(spect, cax = axcolorbar)
    #
    if freqscale =='log':
        ax.set_yscale('log')
    else:
        ax.set_yscale('linear')
    ax.xaxis.set_minor_locator(matplotlib.ticker.AutoMinorLocator())
    ax.grid(which= 'both' ,ls="-", linewidth=0.15, color='#aaaaaa', alpha=0.3)
    ax.set_xlim(t.min(),t.max())
    ax.set_ylim(freq.min(),freq.max())
    if not colorbar:
        return(spect)


def plot_PDD_i(X, param, i , ax, orientation = 'horizontal', dB = True, \
                freqscale = 'log', scaling = 'density',**kwargs):
    """
    plot the spectrogram of a STFT
    """
    # PSD
    PSD, freq, t_i =  stft_PSD(X, param, scaling = scaling,**kwargs)
    PSD_i = PSD[i,:]

    if dB:
        Y = 10*np.log10(PSD_i) - 20*np.log10(2e-5)
    else:
        Y = PSD_i
    # plotting
    if orientation =='horizontal':
        ax.plot(freq,Y)
        if freqscale =='log':
            ax.set_xscale('log')
        else:
            ax.set_xscale('linear')
        ax.xaxis.set_minor_locator(matplotlib.ticker.AutoMinorLocator())
    else:
        ax.plot(Y,freq)
        if freqscale =='log':
            ax.set_yscale('log')
        else:
            ax.set_yscale('linear')
        for tl in ax.xaxis.get_ticklabels():
            tl.set_rotation(90)
            tl.set_fontsize(8)
    ax.grid(True)
    
def plot_PDD_k(X, param, k, ax, dB = True, scaling = 'density', **kwargs):
    """
    plot the spectrogram of a STFT
    """
    # PSD
    PSD, freq, t_i =  stft_PSD(X, param, scaling = scaling, **kwargs )
    PSD_k = PSD[:,k]

    if dB:
        Y = 10*np.log10(PSD_k) - 20*np.log10(2e-5)
    else:
        Y = PSD_k
    ax.xaxis.set_minor_locator(matplotlib.ticker.AutoMinorLocator())
    ax.plot(t_i,Y)
    ax.grid(True)

##


