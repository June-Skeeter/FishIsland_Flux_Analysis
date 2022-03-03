from mpl_toolkits.axes_grid1.anchored_artists import AnchoredSizeBar
from matplotlib.patches import BoxStyle
from matplotlib.path import Path

def scalebar(ax,distance=100,label='100 m',scale=5e-2,pos='lower left',Frame=True):
    ax.add_artist(AnchoredSizeBar(ax.transData,
                           distance, label, pos, 
                           pad=0.3,
                           frameon=Frame,
                           size_vertical=distance*scale,
                          ))

class arrow_Box:
    """A simple box."""

    def __init__(self, pad=0.3):
        """
        The arguments must be floats and have default values.

        Parameters
        ----------
        pad : float
            amount of padding
        """
        self.pad = pad
        super().__init__()

    def __call__(self, x0, y0, width, height, mutation_size):
        """
        Given the location and size of the box, return the path of the box
        around it.

        Rotation is automatically taken care of.

        Parameters
        ----------
        x0, y0, width, height : float
            Box location and size.
        mutation_size : float
            Reference scale for the mutation, typically the text font size.
        """
        # padding
        pad = mutation_size * self.pad
        # width and height with padding added
        width = width + 2.*pad
        height = height + 2.*pad
        # boundary of the padded box
        x0, y0 = x0 - pad, y0 - pad
        x1, y1 = x0 + width, y0 + height
        # return the new path
        return Path([(x0, y0),
                     (x1, y0), 
                     (x1, y1),
                     ((x0+x1)/2.,y1+pad*1.5), 
                     (x0, y1),
                     (x0, y0),
                     (x0, y0)],
                    closed=True)


def North_Arrow(ax,fontsize=12,x=0.05,y=0.1):

    BoxStyle._style_list["northarrow"] = arrow_Box  # Register the custom style.

    ax.text(x, y, "N", size=fontsize, va="center", ha="center", rotation=0,transform=ax.transAxes,
            bbox=dict(boxstyle="northarrow,pad=0.13", fc='white',ec='k',lw=1))
    del BoxStyle._style_list["northarrow"]  # Unregister it.
