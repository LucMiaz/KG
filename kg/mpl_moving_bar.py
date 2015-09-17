
import matplotlib
from matplotlib.widgets import *  

class Bar(AxesWidget):
    """
    A horizontal and vertical line span the axes that and move with
    the pointer.  You can turn off the hline or vline spectively with
    the attributes

    and the visibility of the cursor itself with the *visible* attribute.

    For the cursor to remain responsive you much keep a reference to
    it.
    """
    def __init__(self, ax, useblit = True,
                 **lineprops):
        """
        Add a cursor to *ax*.  If ``useblit=True``, use the backend-
        dependent blitting features for faster updates (GTKAgg
        only for now).  *lineprops* is a dictionary of line properties.

        .. plot :: mpl_examples/widgets/cursor.py
        """
        AxesWidget.__init__(self, ax)

        self.connect_event('draw_event', self.clear)

        self.visible = True
        self.useblit = True and self.canvas.supports_blit
        lineprops['animated'] = True
        self.linev = ax.axvline(ax.get_xbound()[0], visible=False, **lineprops)

        self.background = None
        self.needclear = False

    def clear(self, event):
        """clear the cursor"""
        if self.ignore(event):
            return
        self.background = self.canvas.copy_from_bbox(self.ax.bbox)
        self.linev.set_visible(False)

    def set_x_position(self, event):
        self.linev.set_xdata(event)
        self.linev.set_visible(True)
        self._update()

    def _update(self):
        if self.useblit:
            if self.background is not None:
                self.canvas.restore_region(self.background)
            self.ax.draw_artist(self.linev)
            self.canvas.blit(self.ax.bbox)
        else:
            self.canvas.draw_idle()

        return False
