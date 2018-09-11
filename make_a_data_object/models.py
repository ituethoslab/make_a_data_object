import logging
import numpy as np
import scipy
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import seaborn as sns
from scipy.interpolate import interp1d
from scipy.ndimage.filters import gaussian_filter
import csv

# This needs to be conditioned. Flask provides logging via app.logger
# logging.basicConfig(filename='debug.log', level=logging.DEBUG)
logger = logging.getLogger()

class Data:
    """Mock data object, a static class. Boo."""
    a = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Phasellus fermentum egestas mauris vel maximus. Pellentesque tortor urna, eleifend in bibendum ac, auctor sed felis. Curabitur vitae suscipit augue. Aenean eu neque at dolor condimentum vehicula. Integer a consequat nulla. Donec malesuada, elit non scelerisque iaculis, purus nibh viverra ipsum, et lacinia libero quam vitae nibh. Phasellus fringilla tempor finibus. Sed tincidunt semper turpis, vel pellentesque mauris tristique non. Pellentesque vel ligula auctor tortor vehicula placerat in vel erat. Cras tincidunt vehicula sapien, eget molestie ex bibendum sed. Morbi sed nulla sed nulla luctus ultrices ac eu neque. Suspendisse non nunc diam. In et suscipit tortor. Nulla gravida malesuada elit. Morbi convallis orci urna, non lobortis nunc mollis eget. Donec gravida felis at neque porta, nec tempus mi dignissim. Nunc porttitor massa justo, vel ultricies neque rhoncus eget. Mauris nec libero eros. Ut tristique interdum odio dapibus vulputate. Quisque sed tortor sed ipsum lacinia consectetur eu in lectus. Nulla ac aliquet metus. Nam turpis augue, interdum eu dictum quis, tincidunt non risus. In hac habitasse platea dictumst. Vestibulum feugiat mauris nec convallis fermentum. Etiam sodales tempus imperdiet."
    p = [3.2, 0, 0, 0, 4.0, 0.2, 3.1]


class DefaultParameters:
    """Default parameters.
    This should be part of the app config, perhaps? And not a silly class.
    """
    smoothing = 5
    filename = 'dataobject.dat'
    limit = None


class Weather:
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


class DataObject:
    """A data object thing."""
    def __init__(self, abstract, precipitation, daylength, size=450, base=50, border=25, limit=None, alpha=None):
        """The constructor.

        Parameters
        ----------
        abstract : string
            Abstract for the visit or presentation or something
        precipitation : list of numbers
            Precipitation data
        daylength : int
            Day length in hours
        size : int
            Size of the object, with equal in two dimensions (default 450)
        base : int
            Base height (default 50)
        border : int
            Border width per side (default 25)
        limit : int
            Limit the resolution of the object, the rest of the points
            are interpolated
        alpha : int
            Amount of smoothing. Alpha parameter for gaussian blur
        """
        # Sanity checks for arguments. Type checking could be fun
        assert isinstance(abstract, str)
        assert isinstance(precipitation, list)
        assert all(isinstance(p, (int, float)) for p in precipitation)
        assert isinstance(size, int) and size > 1
        assert isinstance(border, (type(None), int))  # and border >= 0
        assert isinstance(limit, (type(None), int))  # and limit > 0
        assert isinstance(alpha, (type(None), int))  # and alpha > 0
        assert size - border * 2 > 0

        self.size = size
        self.base = base
        self.border = border
        # self.zscale = self.size / 100 # erm where did this constant come from again?
        self.zscale = self.size / 25
        self.data_size = self.size - 2 * self.border

        # grid of coordinates
        self.grid = np.mgrid[0:self.size, 0:self.size]

        # the actually interesting data
        # numpy.interpolate takes list of new indices, list of old indices,
        # and list of old values, to calculate new values
        # Also do scaling for z. 2D inteprolation from scipy would be good

        abstract_v = self.vectorize_abstract(abstract, limit=limit)

        # Intepolation function for vectorized abstract
        self.ai = interp1d(
            np.linspace(0, self.data_size, len(abstract_v)),
            abstract_v)
        self.abstract = list(map(self.ai, range(self.data_size)))

        # Intepolation function for precipitation
        self.pi = interp1d(
            np.linspace(0, self.data_size, len(precipitation)),
            precipitation)
        self.precipitation = list(map(self.pi, range(self.data_size)))
        # Let's add a constant 1 to the precipitation to bring it up from 0
        self.precipitation = list(np.add(self.precipitation, 1))

        # Let's add sun to the precipitation
        # self.precipitation = list(np.add(self.precipitation, sun))
        # way sketchy here...
        self.daylength = daylength
        sun_for_a_day = list(map(lambda t: self.sun(t, self.daylength), np.linspace(0, 24, num=int(len(self.precipitation) / 7))))
        # Pad to length of the precipitation after possible rounding artefacts
        sun_for_a_week = sun_for_a_day * 7 + [0] * (len(self.precipitation) - len(sun_for_a_day * 7))

        self.precipitation = np.add(
            self.precipitation,
            list(map(lambda t: self.sun(t, self.daylength), sun_for_a_week)))

        # the surface
        self.surface = self.base + self.calculate_surface(self.border,
                                                          self.abstract,
                                                          self.precipitation,
                                                          alpha=alpha) * self.zscale
        # Clip it. Crude. Refactor this
        self.surface = np.clip(self.surface, self.base, self.size - self.base)

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

    def sun(self, t, dayhours):
        """This return -1 to 1, how high up in the sky is the sun.
            Not really accurate as sun reaches the same peak throughout the year."""
        # assert t >= 0
        assert t <= 24
        assert dayhours >= 0
        assert dayhours <= 24
        if t < dayhours:
            # return np.sin(np.pi / (dayhours / t))
            return np.sin(np.pi * t / dayhours)
        else:
            return -np.sin(np.pi * (24-t) / (24-dayhours))

    def outerprod_surface(self, xd, yd):
        """Yet another function. Outputs size * size shaped np.ndarray."""
        # return np.outer(yd, xd) / (np.outer(xd, yd) + 0.00001)
        # return np.outer((yd + 0.1), xd) / np.outer(xd, (yd + 0.1))
        return np.outer(xd, yd)

    def add_surface(self, xd, yd):
        return np.add(xd, yd)

    def calculate_surface(self, border, xd, yd, alpha=0):
        """Calculate a surface.

        Return a surface, which conceptually matches
        the surface function in OpenSCAD

        Parameters
        ----------
        border : int
            Border width, which is applied to all sides
        xd : np.array
            Numpy array of data for first edge of the matrix
        yd : np.array
            Numpy array of data for the second of the matrix
        alpha : int
            Amount of smoothing, alpha parameter for Gaussian blurr

        Returns
        -------
        np.array
            2-D matrix, size len(xd) + 2*border on each side
        """
        alpha = alpha or 0
        assert len(xd) == len(yd), "both vectors (yd={}, xd={}) must be same size".format(len(xd), len(yd))
        # Pad xd and yd with the border, and construct the matrix
        # using nympy.pad would be wise
        surface = gaussian_filter(
            np.outer(
                np.concatenate((np.zeros(border), xd, np.zeros(border))),
                np.concatenate((np.zeros(border), yd, np.zeros(border)))),
            alpha)
        # Smoothing overflows onto the border. Compensate by pulling it to zero
        if border:
            surface[0:border, :] = 0
            surface[-border:, :] = 0
            surface[:, 0:border] = 0
            surface[:, -border:] = 0

        return surface

    def plot_heatmap(self, **kwargs):
        return sns.heatmap(self.surface, square=True, **kwargs)

    def plot_contourf(self, **kwargs):
        return plt.contourf(self.surface, **kwargs)

    def plot_surface(self, **kwargs):
        if 'ax' not in kwargs:
            fig, ax = plt.subplots(subplot_kw={'projection': '3d'}, **kwargs)
        else:
            ax = kwargs['ax']
        ax.set_xlim(0, self.size)
        ax.set_ylim(0, self.size)
        ax.set_zlim(0, self.size)
        ax.set_xlabel('abstract')
        ax.set_ylabel('precipitation')
        return ax.plot_surface(self.grid[0], self.grid[1], self.surface)

    def get_inverse(self):
        # A number of issues to consider here, namely rotation, flipping
        # and the fact that the base needs to be in the middle of the item
        # of course, not as low as 50 units (mm) for a 500 unit (5cm) item
        raise NotImplementedError("Design TBD")
        # return self.size - self.surface

    def write(self, filename):
        """Write to file filename."""
        with open(filename, "w") as fd:
            writer = csv.writer(fd, delimiter=" ")
            # fd.write(filename + "\n")
            for row in self.surface:
                # print(row)
                writer.writerow(row)


class AdditiveDataObject(DataObject):
    """A Data object which has an additive surface, ie. less pronounced
    variation in z.
    """
    def __init__(self, abstract, precipitation, daylength, size=450, base=50, border=25, limit=None, alpha=None):
        super().__init__(abstract, precipitation, daylength, size, base, border, limit, alpha)

    def calculate_surface(self, border, xd, yd, alpha=0):
        alpha = alpha or 0
        assert len(xd) == len(yd), "both vectors (yd={}, xd={}) must be same size".format(len(xd), len(yd))
        # Pad xd and yd with the border, and construct the matrix
        # using nympy.pad would be wise
        surface = gaussian_filter(
            np.add(
                np.concatenate((np.zeros(border), xd, np.zeros(border))).reshape(self.size, 1),
                np.concatenate((np.zeros(border), yd, np.zeros(border)))),
            alpha)

        # Smoothing overflows onto the border. Compensate by pulling it to zero
        if border:
            surface[0:border, :] = 0
            surface[-border:, :] = 0
            surface[:, 0:border] = 0
            surface[:, -border:] = 0

        return surface
