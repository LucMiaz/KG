from matplotlib.widgets import AxesWidget
from matplotlib.transforms import blended_transform_factory 
import matplotlib.patches as patches
from matplotlib.patches import Rectangle as Rectangle
import matplotlib.pyplot as plt
import matplotlib

import copy

class _SelectorWidget(AxesWidget):

    def __init__(self, ax, onselect, useblit=False, button=None,
                 state_modifier_keys=None):
        AxesWidget.__init__(self, ax)

        self.visible = True
        self.onselect = onselect
        self.useblit = useblit and self.canvas.supports_blit
        self.connect_default_events()

        self.state_modifier_keys = dict(move=' ', clear='escape',
                                        square='shift', center='control')
        self.state_modifier_keys.update(state_modifier_keys or {})

        self.background = None
        self.artists = []
    
        if isinstance(button, int):
            self.validButtons = [button]
        else:
            self.validButtons = button
    
        # will save the data (position at mouseclick)
        self.eventpress = None
        # will save the data (pos. at mouserelease)
        self.eventrelease = None
        self._prev_event = None
        self.state = set()

    def set_active(self, active):
        AxesWidget.set_active(self, active)
        if active:
            self.update_background(None)

    def update_background(self, event):
        """force an update of the background"""
        # If you add a call to `ignore` here, you'll want to check edge case:
        # `release` can call a draw event even when `ignore` is True.
        if self.useblit:
            self.background = self.canvas.copy_from_bbox(self.ax.bbox)

    def connect_default_events(self):
        """Connect the major canvas events to methods."""
        self.connect_event('motion_notify_event', self.onmove)
        self.connect_event('button_press_event', self.press)
        self.connect_event('button_release_event', self.release)
        self.connect_event('draw_event', self.update_background)
        self.connect_event('key_press_event', self.on_key_press)
        self.connect_event('key_release_event', self.on_key_release)
        self.connect_event('scroll_event', self.on_scroll)

    def ignore(self, event):
        """return *True* if *event* should be ignored"""
        if not self.active or not self.ax.get_visible():
            return True

        # If canvas was locked
        if not self.canvas.widgetlock.available(self):
            return True

        if not hasattr(event, 'button'):
            event.button = None

        # Only do rectangle selection if event was triggered
        # with a desired button
        if self.validButtons is not None:
            if event.button not in self.validButtons:
                return True

        # If no button was pressed yet ignore the event if it was out
        # of the axes
        if self.eventpress is None:
            return event.inaxes != self.ax

        # If a button was pressed, check if the release-button is the
        # same.
        if event.button == self.eventpress.button:
            return False

        # If a button was pressed, check if the release-button is the
        # same.
        return (event.inaxes != self.ax or
                event.button != self.eventpress.button)

    def update(self):
        """draw using newfangled blit or oldfangled draw depending on
        useblit
        """
        if not self.ax.get_visible():
            return False

        if self.useblit:
            if self.background is not None:
                self.canvas.restore_region(self.background)
            for artist in self.artists:
                self.ax.draw_artist(artist)
            self.canvas.update()#use with PyQT
            #self.canvas.blit(ax.bbox) #use with TkAgg
        else:
            self.canvas.draw_idle()
        return False

    def _get_data(self, event):
        """Get the xdata and ydata for event, with limits"""
        if event.xdata is None:
            return None, None
        x0, x1 = self.ax.get_xbound()
        y0, y1 = self.ax.get_ybound()
        xdata = max(x0, event.xdata)
        xdata = min(x1, xdata)
        ydata = max(y0, event.ydata)
        ydata = min(y1, ydata)
        return xdata, ydata

    def _clean_event(self, event):
        """Clean up an event
        Use prev event if there is no xdata
        Limit the xdata and ydata to the axes limits
        Set the prev event
        """
        if event.xdata is None:
            event = self._prev_event
        else:
            event = copy.copy(event)
        event.xdata, event.ydata = self._get_data(event)

        self._prev_event = event
        return event

    def press(self, event):
        """Button press handler and validator"""
        if not self.ignore(event):
            event = self._clean_event(event)
            self.eventpress = event
            self._prev_event = event
            key = event.key or ''
            key = key.replace('ctrl', 'control')
            # move state is locked in on a button press
            if key == self.state_modifier_keys['move']:
                self.state.add('move')
            self._press(event)
            return True
        return False

    def _press(self, event):
        """Button press handler"""
        pass

    def release(self, event):
        """Button release event handler and validator"""
        if not self.ignore(event) and self.eventpress:
            event = self._clean_event(event)
            self.eventrelease = event
            self._release(event)
            self.eventpress = None
            self.eventrelease = None
            self.state.discard('move')
            return True
        return False

    def _release(self, event):
        """Button release event handler"""
        pass

    def onmove(self, event):
        """Cursor move event handler and validator"""
        if not self.ignore(event) and self.eventpress:
            event = self._clean_event(event)
            self._onmove(event)
            return True
        return False

    def _onmove(self, event):
        """Cursor move event handler"""
        pass

    def on_scroll(self, event):
        """Mouse scroll event handler and validator"""
        if not self.ignore(event):
            self._on_scroll(event)

    def _on_scroll(self, event):
        """Mouse scroll event handler"""
        pass

    def on_key_press(self, event):
        """Key press event handler and validator for all selection widgets"""
        if self.active:
            key = event.key or ''
            key = key.replace('ctrl', 'control')
            if key == self.state_modifier_keys['clear']:
                for artist in self.artists:
                    artist.set_visible(False)
                self.update()
                return
            for (state, modifier) in self.state_modifier_keys.items():
                if modifier in key:
                    self.state.add(state)
            self._on_key_press(event)

    def _on_key_press(self, event):
        """Key press event handler - use for widget-specific key press actions.
        """
        pass

    def on_key_release(self, event):
        """Key release event handler and validator"""
        if self.active:
            key = event.key or ''
            for (state, modifier) in self.state_modifier_keys.items():
                if modifier in key:
                    self.state.discard(state)
            self._on_key_release(event)

    def _on_key_release(self, event):
        """Key release event handler"""
        pass

    def set_visible(self, visible):
        """ Set the visibility of our artists """
        self.visible = visible
        for artist in self.artists:
            artist.set_visible(visible)

class _my_SelectorWidget(_SelectorWidget):
    '''
    matplotlib.widgets._SelectorWidget 
    changed update. update has to be called externally
    '''

    def __init__(self, ax, onselect, update_on_ext_event, button=None,
                 state_modifier_keys=None):
        _SelectorWidget.__init__(self, ax, onselect, useblit=True, button=None,
                 state_modifier_keys=None)
        self.update_on_ext_event = update_on_ext_event
        
    def on_key_press(self, event):
        """Key press event handler and validator for all selection widgets"""
        if self.active:
            key = event.key or ''
            key = key.replace('ctrl', 'control')
            if key == self.state_modifier_keys['clear']:
                for artist in self.artists:
                    artist.set_visible(False)
                if not self.update_on_ext_event:
                    self.update()
                return
            for (state, modifier) in self.state_modifier_keys.items():
                if modifier in key:
                    self.state.add(state)
            self._on_key_press(event)

class CaseSelector(_my_SelectorWidget):
    """
    Select a min/max range of the x or y axes for a matplotlib Axes.
    For the selector to remain responsive you much keep a reference to
    it.
    Example usage::
        ax = subplot(111)
        ax.plot(x,y)
        def onselect(vmin, vmax):
            print vmin, vmax
        span = SpanSelector(ax, onselect, 'horizontal')
    *onmove_callback* is an optional callback that is called on mouse
    move within the span range
    """

    def __init__(self, ax, onselect, onclick, minspan = 0.1, nrect = 10, 
                    update_on_ext_event = True,
                    rectprops = None, stay_rectprops = None,lineprops = None, 
                    onmove_callback = None, button = None):
        """
        Create a case selector in *ax*.  When a selection is made, call 
        *onselect* with::
            onselect(vmin, vmax)
        and clear the span.
        *direction* must be 'horizontal' or 'vertical'
        If *minspan* is not *None*, ignore events smaller than *minspan*
        The span rectangle is drawn with *rectprops*; default::
          rectprops = dict(facecolor='red', alpha=0.5)
        Set the visible attribute to *False* if you want to turn off
        the functionality of the span selector
        If *span_stays* is True, the span stays visble after making
        a valid selection.
        *button* is a list of integers indicating which mouse buttons should
        be used for selection.  You can also specify a single
        integer if only a single button is desired.  Default is *None*,
        which does not limit which button can be used.
        Note, typically:
         1 = left mouse button
         2 = center mouse button (scroll wheel)
         3 = right mouse button
        """
        _my_SelectorWidget.__init__(self, ax, onselect, update_on_ext_event, button=button)

        if rectprops is None:
            self.rectprops = dict(facecolor='#f5f5f5', alpha=0.3)
        else:
            self.rectprops = rectprops
        if lineprops is None:
            self.lineprops = dict(color='#e66101',lw = 2)#bar color
        else:
            self.lineprops = lineprops
        
        if not isinstance(nrect,list):
            nrect=[nrect]
        if stay_rectprops is None:
            cc= ['#d8b365','#5ab4ac','#a6dba0','#e66101']#green yellow blue red
            color =[cc[i%len(cc)] for i in range(0,len(nrect))]
            self.stay_rectprops = [dict(facecolor= c, alpha=0.5) for c in color]
        else:
            assert(len(nrect)==len(stay_rectprops))
            self.stay_rectprops = stay_rectprops

        self.pressv = None
        self.onclick = onclick
        self.onmove_callback = onmove_callback
        self.minspan = minspan
        
        # Needed when dragging out of axes
        self.prev = (0, 0)

        # Reset canvas so that `new_axes` connects events.
        self.canvas = None
        self.new_axes(ax, nrect)
    def setUpdateOnExtEvent(self, truth=None):
        """set truthvalue of update_on_ext_event"""
        if truth in [True, False]:
            self.update_on_ext_event=truth
        
    def new_axes(self, ax, nrect):
        self.ax = ax
        if self.canvas is not ax.figure.canvas:
            if self.canvas is not None:
                self.disconnect_events()
            self.canvas = ax.figure.canvas
            self.connect_default_events()
        #span
        trans = blended_transform_factory(self.ax.transData, self.ax.transAxes)
        w, h = 0, 1
        self.rect = Rectangle((0, 0), w, h, transform = trans, visible=False,
                              animated = True, **self.rectprops)
        self.ax.add_patch(self.rect)
        self.artists = [self.rect]
        #stay rect
        self.stay_rects = []
        for set in range(0,len(nrect)):
            self.stay_rects.append([])
            for n in range(0,nrect[set]):
                stay_rect = Rectangle((0, 0), w, h, transform=trans, visible=False,
                                animated = True, **self.stay_rectprops[set])
                self.ax.add_patch(stay_rect)
                self.stay_rects[set].append(stay_rect)
            self.artists.extend(self.stay_rects[set])
        #bar
        self.bar = ax.axvline(0,w,h,visible = False, **self.lineprops)
        self.artists.append(self.bar)
        
    def set_bar_position(self, x):
        self.bar.set_xdata(x)
        self.bar.set_visible(True)
        
    def set_stay_rects_x_bounds(self,xarr, set = 0):
        for n,stay_rect in enumerate(self.stay_rects[set]):
            try:
                xmin, xmax = xarr[n]
            except IndexError:
                stay_rect.set_visible(False)
            else:
                stay_rect.set_x(xmin)
                stay_rect.set_y(self.rect.get_y())
                stay_rect.set_width(abs(xmax-xmin))
                stay_rect.set_height(self.rect.get_height())
                stay_rect.set_visible(True)
                
    def set_stay_rect_visible(self,b=True,set=0):
        for stay_rect in self.stay_rects[set]:
            stay_rect.set_visible(b)

    def ignore(self, event):
        """return *True* if *event* should be ignored"""
        return _SelectorWidget.ignore(self, event) or not self.visible

    def _press(self, event):
        """on button press event"""
        xdata, ydata = self._get_data(event)
        self.pressv = xdata
        return False

    def _release(self, event):
        """on button release event"""
        if self.pressv is None:
            return
        self.buttonDown = False

        self.rect.set_visible(False)
        vmin = self.pressv
        xdata, ydata = self._get_data(event)
        vmax = xdata or self.prev[0]

        if vmin > vmax:
            vmin, vmax = vmax, vmin
        span = vmax - vmin
        if span < self.minspan and event.button==3:#right click to remove span
            self.onclick(vmin)
            return
        elif span> self.minspan and event.button==1:
            self.onselect(vmin, vmax)
            self.pressv = None
            return False
        elif span > self.minspan and event.button==3:
            self.onselect(vmin,vmax, True)
            self.pressv= None
            return False
    
    def simonmove(self):
        """simulates on move"""
        self.update()
            
    def _onmove(self, event):
        self.rect.set_visible(self.visible)
        """on motion notify event"""
        if self.pressv is None:
            return
        x, y = self._get_data(event)
        if x is None:
            return

        self.prev = x, y
        v = x
        minv, maxv = v, self.pressv
        if minv > maxv:
            minv, maxv = maxv, minv
        self.rect.set_x(minv)
        self.rect.set_width(maxv - minv)
        
        if self.onmove_callback is not None:
            vmin = self.pressv
            xdata, ydata = self._get_data(event)
            vmax = xdata or self.prev[0]
        
            if vmin > vmax:
                vmin, vmax = vmax, vmin
            self.onmove_callback(vmin, vmax)
        if not self.update_on_ext_event:
            self.update()
        return False
        
class Bar(AxesWidget):
    """
    A vertical line span the axes that and move with
    the pointer.  You can turn off the hline or vline spectively with
    the attributes

    and the visibility of the cursor itself with the *visible* attribute.

    For the cursor to remain responsive you much keep a reference to
    it.
    """
    def __init__(self, ax, lineprops=None, **kwargs):
        """
        Add a bar to *ax*.  *lineprops* is a dictionary of line properties.
        """
        AxesWidget.__init__(self, ax)
        if lineprops is None:
            lineprops = dict(color='#e66101',lw = 2)

        self.linev = ax.axvline(0, 0, 1 , visible=False, **lineprops)
        self.background = None
        self.needclear = False
        self.connect_event('draw_event', self.clear)

    def clear(self, event=None):
        """clear the cursor"""
        if event:
            if self.ignore(event):
                return

            self.background = self.canvas.copy_from_bbox(self.ax.bbox)
            self.linev.set_visible(False)
        else:
            self.background = self.canvas.copy_from_bbox(self.ax.bbox)
            self.linev.set_visible(False)

    def set_bar_position(self, x):
        #self.clear()
        self.linev.set_visible(False)
        self.linev.set_xdata(x)
        self.linev.set_visible(True)

    def update(self):
        if self.background is not None:
            self.canvas.restore_region(self.background)
        self.ax.draw_artist(self.linev)
        self.canvas.blit(self.ax.bbox)
        return False

    