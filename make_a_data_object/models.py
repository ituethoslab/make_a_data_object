import logging
import numpy as np
import scipy
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import seaborn as sns
from scipy.interpolate import interp1d
from scipy.ndimage.filters import gaussian_filter

# This needs to be conditioned
# logging.basicConfig(filename='debug.log', level=logging.DEBUG)
logger = logging.getLogger()

class Data():
    """Mock data object, a static class. Boo."""
    a = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Phasellus fermentum egestas mauris vel maximus. Pellentesque tortor urna, eleifend in bibendum ac, auctor sed felis. Curabitur vitae suscipit augue. Aenean eu neque at dolor condimentum vehicula. Integer a consequat nulla. Donec malesuada, elit non scelerisque iaculis, purus nibh viverra ipsum, et lacinia libero quam vitae nibh. Phasellus fringilla tempor finibus. Sed tincidunt semper turpis, vel pellentesque mauris tristique non. Pellentesque vel ligula auctor tortor vehicula placerat in vel erat. Cras tincidunt vehicula sapien, eget molestie ex bibendum sed. Morbi sed nulla sed nulla luctus ultrices ac eu neque. Suspendisse non nunc diam. In et suscipit tortor. Nulla gravida malesuada elit. Morbi convallis orci urna, non lobortis nunc mollis eget. Donec gravida felis at neque porta, nec tempus mi dignissim. Nunc porttitor massa justo, vel ultricies neque rhoncus eget. Mauris nec libero eros. Ut tristique interdum odio dapibus vulputate. Quisque sed tortor sed ipsum lacinia consectetur eu in lectus. Nulla ac aliquet metus. Nam turpis augue, interdum eu dictum quis, tincidunt non risus. In hac habitasse platea dictumst. Vestibulum feugiat mauris nec convallis fermentum. Etiam sodales tempus imperdiet."
    p = [3.2, 0, 0, 0, 4.0, 0.2, 3.1]


class Weather():
    """Weather class.

    For now, to be used statistically as a weather factory. Rain is
    not rare in Copenhagen, but it is does not rain particularly much
    at a time, something like <15 mm unless it's a major rain. With
    the weather archice at http://www.dmi.dk/vejr/arkiver/vejrarkiv/,
    let's model it as a random chi-squared distribution.

    """
    precipitation = None

    def __init__(self, precipitation):
        if precipitation:
            self.precipitation = precipitation
        else:
            self.precipitation = self.random_weather()

    def random_weather(self, size=7):
        return np.floor(np.random.chisquare(1, size) * np.random.randint(0, 10))


class DataObject():
    """A data object thing."""
    def __init__(self, abstract, precipitation, size=100, limit=None, alpha=None):
        """The constructor.

        Parameters
        ----------
        size : int
            Size of the object, with equal in two dimensions
        limit : int
            Limit the resolution of the object, the rest of the points
            are interpolated
        alpha : int
            Amount of smoothing. Alpha parameter for gaussian blur
        """
        # X, Y, Z are size in three dimensions
        self.size = size
        self.X = self.Y = size
        self.zscale = self.size / 100 # erm where did this 100 come from again?

        # grid of coordinates
        self.grid = np.mgrid[0:self.X, 0:self.Y]

        # the actually interesting data
        ## numpy.interpolate takes list of new indices, list of old indices,
        ## and list of old values, to calculate new values
        ## Also do scaling for z. 2D inteprolation from scipy would be good

        abstract_v = self.vectorize_abstract(abstract, limit=limit)

        # Intepolation function for vectorized abstract
        self.ai = interp1d([size/len(abstract_v) * i for i, v in enumerate(abstract_v)], abstract_v, bounds_error=False, fill_value=0)
        self.abstract = list(map(self.ai, range(size)))

        # Intepolation function for precipitation
        self.pi = interp1d([size/len(precipitation) * i for i, v in enumerate(precipitation)], precipitation, bounds_error=False, fill_value=0)
        self.precipitation = list(map(self.pi, range(size)))

        # the surface
        self.surface = (size/2) + self.calculate_surface(self.grid,
                                                         self.abstract,
                                                         self.precipitation,
                                                         alpha=alpha) * self.zscale

        logger.debug(self.surface)

    def __repr__(self):
        return "{} with a {} surface".format(self.__class__, self.surface.shape)

    def __str__(self):
        # there is also np.array2string
        return "\n".join(" ".join(str(int(y)) for y in row) for row in self.surface)

    def vectorize_abstract(self, abstract, limit=None):
        lens = list(map(len, abstract.split()[:limit]))
        # av = np.array([10 + (lens[i - 1] - l) for (i, l) in enumerate(lens)])
        av = np.array([np.abs(lens[i - 1] - l) for (i, l) in enumerate(lens)])
        return av

    def outerprod_surface(self, grid, xd, yd):
        """Yet another function. Outputs size * size shaped np.ndarray."""
        # return np.outer(yd, xd) / (np.outer(xd, yd) + 0.00001)
        # return np.outer((yd + 0.1), xd) / np.outer(xd, (yd + 0.1))
        return np.outer(xd, yd)

    def add_surface(self, grid, xd, yd):
        return np.add(xd, yd)

    def calculate_surface(self, grid, xd, yd, alpha=0):
        # return xd + np.outer(xd, yd)
        alpha = alpha or 0
        return gaussian_filter(xd + np.outer(xd, yd), alpha)

    def plot_heatmap(self, **kwargs):
        return sns.heatmap(self.surface, square=True, **kwargs)

    def plot_contourf(self, **kwargs):
        return plt.contourf(self.surface, **kwargs)

    def plot_surface(self, **kwargs):
        fig, ax = plt.subplots(subplot_kw={'projection': '3d'}, **kwargs)
        ax.set_xlim(0, self.size)
        ax.set_ylim(0, self.size)
        ax.set_zlim(0, self.size)
        ax.set_xlabel('abstract')
        ax.set_ylabel('precipitation')
        return fig, ax.plot_surface(*self.grid, self.surface)

    def write(self, filename):
        """Write to file filename."""
        with open(filename, "w") as fd:
            writer = csv.writer(fd, delimiter=" ")
            # fd.write(filename + "\n")
            for row in self.surface:
                # print(row)
                writer.writerow(row)
