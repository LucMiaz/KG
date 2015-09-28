from matplotlib.widgets import AxesWidget
import matplotlib.patches as patches
from matplotlib.patches import Rectangle as Rectangle
import matplotlib.pyplot as plt
import matplotlib
blended_transform_factory= matplotlib.transforms.blended_transform_factory 
import copy


class _SelectorWidget(AxesWidget):

    def __init__(self, ax, onselect, button=None, state_modifier_keys=None):
        AxesWidget.__init__(self, ax)

        self.visible = True
        self.onselect = onselect
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

    def _update(self):
        """draw using newfangled blit or oldfangled draw depending on
        useblit
        """
        if not self.ax.get_visible():
            return False
        
        if self.background is not None:
            self.canvas.restore_region(self.background)
        for artist in self.artists:
            self.ax.draw_artist(artist)
        self.canvas.blit(self.ax.bbox)

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
            #self.update()
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
                #self.update()
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

class SpanSelector2(_SelectorWidget):
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

    def __init__(self, ax, onselect, onclick, minspan= 0.1,
                 rectprops=None, onmove_callback=None, span_stays = True, nrect=10,
                 button=None):
        """
        Create a span selector in *ax*.  When a selection is made, clear
        the span and call *onselect* with::
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
        _SelectorWidget.__init__(self, ax, onselect, button=button)

        if rectprops is None:
            rectprops = dict(facecolor='red', alpha=0.5)
        
        rectprops['animated'] = True

        self.rect = None
        self.pressv = None
        
        self.onclick = onclick
        self.rectprops = rectprops
        self.onmove_callback = onmove_callback
        self.minspan = minspan
        self.span_stays = span_stays

        # Needed when dragging out of axes
        self.prev = (0, 0)

        # Reset canvas so that `new_axes` connects events.
        self.canvas = None
        self.new_axes(ax)

    def new_axes(self, ax):
        self.ax = ax
        if self.canvas is not ax.figure.canvas:
            if self.canvas is not None:
                self.disconnect_events()

            self.canvas = ax.figure.canvas
            self.connect_default_events()

        trans = blended_transform_factory(self.ax.transData,
                                              self.ax.transAxes)
        w, h = 0, 1
        self.rect = Rectangle((0, 0), w, h,
                              transform=trans,
                              visible=False,
                              **self.rectprops)
        self.ax.add_patch(self.rect)
        self.artists = [self.rect]
        if self.span_stays:
            self.stay_rects = []
            for i in range(1,nrect):
                stay_rect = Rectangle((0, 0), w, h,
                                       transform=trans,
                                       visible=False,
                                       **self.rectprops)
                self.ax.add_patch(stay_rect)
                self.stay_rects.append(stay_rect)
            self.artists.extend(self.stay_rects)
        
        #bar
        self.bar = ax.axvline(ax.get_xbound()[0], visible=False)
        self.artists.append(self.bar)

        
    def set_bar_position(self, t):
        self.bar.set_xdata(t)
        self.bar.set_visible(True)
        
    def set_stay_rects_x(self,xarr):
        if self.span_stays:
            for n,stay_rect in enumerate(self.stay_rects):
                try:
                    xmin,xmax = xarr[n]
                except IndexError:
                    stay_rect.set_visible(False)
                else:
                    stay_rect.set_x(xmin)
                    stay_rect.set_y(self.rect.get_y())
                    stay_rect.set_width(abs(xmax-xmin))
                    stay_rect.set_height(self.rect.get_height())
                    stay_rect.set_visible(True)

    def ignore(self, event):
        """return *True* if *event* should be ignored"""
        return _SelectorWidget.ignore(self, event) or not self.visible

    def _press(self, event):
        """on button press event"""
        #self.rect.set_visible(self.visible)
        #if self.span_stays:
        #    self.stay_rect.set_visible(False)

        xdata, ydata = self._get_data(event)
        self.pressv = xdata
        return False

    def _release(self, event):
        """on button release event"""
        if self.pressv is None:
            return
        self.buttonDown = False

        self.rect.set_visible(False)

        #self.canvas.draw()
        vmin = self.pressv
        xdata, ydata = self._get_data(event)
        vmax = xdata or self.prev[0]

        if vmin > vmax:
            vmin, vmax = vmax, vmin
        span = vmax - vmin
        if span < self.minspan:
            self.onclick(vmin)
            return
        else:
            self.onselect(vmin, vmax)
            self.pressv = None
            return False

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
        #self.update()
        return False


# class GraphicalIntervalsHandle(AxesWidget):
#     """
#     Set of intervals with graphical support. Add a list called `Rectangles` to the class `SetOfIntervals`. This list containts duples : an Interval and a patch (displayed rectangle) linked to an axis (stored in self.ax). This allows to update `Rectangle` from the SetOfInterval attribute `RangeInter` and vice versa, i.e. when we want to delete a displayed patch, we look it up in `Rectangle` (by itering over its second argument), and then we can delete the corresponding `Interval` in `RangeInter`.\n
# Method                | Description
# --------------------- | ----------
# _update()             | updates Rectangles and plot them
# on_select(eclick, erelease) | adds the interval selectionned while holding left mouse click
# connect(rect)         | connects the rectangle rect to the figure
# removerectangle(rect) | removes rect from the figure, from Rectangles list and removes the corresponding interval from RangesInter
# on_pick(event)        | removes the interval selectionned while holding right mouse click
# toggle_selector(event) | handles key_events
# call_discretize(event) | calls the method `discretize` from an event, such as a button
# changeDiscretizeParameters(listofparams) | changes the parameters of the discretization (usefull if calling with button). Give list or tuple of length 3
# discretize(zerotime, endtime, deltatime, axis=self.axis) | returns the characteristic function of range(zerotime,endtime, deltatime) in respect to RangeInter. Optional argument is the axis where one need to represent the points of the characteristic function. If one does not want any graphical representation, give None as axis
#     """
#     
#     def __init__(self, ax, SetOfInt):#, displaybutton=True, useblit = True):
#         """initialisation of object. Needs an axis to be displayed on. Optional SetOfIntervals."""
#         super classes init
#         AxesWidget.__init__(self, ax)
#         handle
#         self.Set = SetOfInt
#         attibutes
#         self.Background = None 
#         self.ymin = -20
#         self.Rectangles =[]
#         for n in range(0,10):
#             rect = ax.axvspan(0,0,-10,10,visible=False,alpha=0.5)
#             self.Rectangles.append(rect)
#         spanselector
#         SpanSelector(ax, self.on_select, 'horizontal', useblit=True,minspan=0.01, rectprops=dict(alpha=0.5, facecolor='red'))
#         connections
#         self.connect_event('draw_event', self.clear)
#         plt.connect('button_press_event', self.on_click)
#     
#     def _update(self):
#         """updates Rectangles and plot them"""
#         for n,vspan in enumerate(self.Rectangles):
#             try:
#                 int = self.Set.RangeInter[n]
#             except IndexError:
#                 vspan.set_visible(False)
#             else:
#                 vspan.set_visible(True)
#                 xmin,xmax = int.get_x()
#                 vspan.set_xy([[xmin,-10],[xmax,-10],[xmax,10],[xmin,10]])
#                 self.ax.draw_artist(vspan)
#         if self.background is not None:
#             self.canvas.restore_region(self.background)
#         self.canvas.blit(self.ax.bbox)
#         return False
#         
#     def clear(self, event):
#         """clear the cursor"""
#         self.background = self.canvas.copy_from_bbox(self.ax.bbox)
#         for rect in self.Rectangles:
#             rect.set_visible(False)
#         
#     def on_select(self, xmin, xmax):
#         """adds the interval selectionned while holding left mouse click"""
#         int = Interval(xmin,xmax)
#         self.Set.append(int)
#         print("Added interval ["+ str(int)+"]")
#         self._update()
#     
#     def on_click(self, event):
#         """removes the interval mouseclicked"""
#         self.remove_int(event.xdata)
#         self._update()
#             
#     def remove_int(self, x):
#         """removes the object rect from Rectangle list and the corresponding Interval in RangeInter"""
#         for int in self.Set.RangeInter:
#             xmin,xmax = int.get_x()
#             if x>=xmin and  x<=xmax:
#                 self.Set.RangeInter.remove(int)
#                 break
#  
#  
#  
# def calc_fill_between_args(ymin):
#     x = []
#     y1 = []
#     for interval in self.RangeInter:
#         xmin,xmax = interval.get_x()
#         x.extend([xmin,xmin,xmax,xmax])
#         y1.extend([ymin,-ymin,-ymin,ymin])
#     return(x,y1,ymin)
##
if __name__ == "__main__":
    import numpy as np
    #import prettyplotlib #makes nicer plots
    #import matplotlib.pyplot as plt
    def onselect(x1,x2):
        print(x1,x2)
        
    x = np.arange(100)/(79.0)
    y = np.sin(x)
    fig, ax = plt.subplots(1)
    ax.plot(x,y)
    SpanSelector2(ax,onselect,'horizontal')
    
    
    
    