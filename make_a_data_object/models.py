import logging
import numpy as np
import scipy
from scipy.interpolate import interp1d

class Data():
    """Mock data object, a static class. Boo."""
    a = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Phasellus fermentum egestas mauris vel maximus. Pellentesque tortor urna, eleifend in bibendum ac, auctor sed felis. Curabitur vitae suscipit augue. Aenean eu neque at dolor condimentum vehicula. Integer a consequat nulla. Donec malesuada, elit non scelerisque iaculis, purus nibh viverra ipsum, et lacinia libero quam vitae nibh. Phasellus fringilla tempor finibus. Sed tincidunt semper turpis, vel pellentesque mauris tristique non. Pellentesque vel ligula auctor tortor vehicula placerat in vel erat. Cras tincidunt vehicula sapien, eget molestie ex bibendum sed. Morbi sed nulla sed nulla luctus ultrices ac eu neque. Suspendisse non nunc diam. In et suscipit tortor. Nulla gravida malesuada elit. Morbi convallis orci urna, non lobortis nunc mollis eget. Donec gravida felis at neque porta, nec tempus mi dignissim. Nunc porttitor massa justo, vel ultricies neque rhoncus eget. Mauris nec libero eros. Ut tristique interdum odio dapibus vulputate. Quisque sed tortor sed ipsum lacinia consectetur eu in lectus. Nulla ac aliquet metus. Nam turpis augue, interdum eu dictum quis, tincidunt non risus. In hac habitasse platea dictumst. Vestibulum feugiat mauris nec convallis fermentum. Etiam sodales tempus imperdiet."
    p = [3.2, 0, 0, 0, 4.0, 0.2, 3.1]


class DataObject():
    """A data object thing."""
    size = None
    X = Y = Z = None
    scale = 1
    grid = (None, None)
    surface = None
    abstract = None
    precipitation = None
    
    def __init__(self, abstract, precipitation, size=100, limit=None):
        """The constructor"""
        # X, Y, Z are size in three dimensions
        self.size = size
        self.X = self.Y = size
        
        # grid of coordinates
        self.grid = np.mgrid[0:self.X, 0:self.Y]
        
        # the actually interesting data
        ## numpy.interpolate takes list of new indices, list of old indices,
        ## and list of old values, to calculate new values
        ## Also do scaling for z. 2D inteprolation from scipy would be good
        self.scale = size/min(len(abstract), len(precipitation))
        
        abstract_v = self.vectorize_abstract(abstract, limit=limit)
        
        self.ai = interp1d(np.arange(len(abstract_v)),
                                             abstract_v, kind='cubic')
        self.abstract = np.interp(np.linspace(0, len(abstract_v), size),
                                  np.arange(len(abstract_v)),
                                  self.ai(abstract_v))
        
        self.pi = interp1d(np.arange(len(precipitation)),
                                             precipitation, kind='cubic')
        self.precipitation = np.interp(np.linspace(0, len(precipitation), size),
                                       np.arange(len(precipitation)),
                                       self.pi(precipitation))
        
        logging.debug(self.grid)
        
        # the surface
        self.surface = (size/2) + self.outerprod_surface(self.grid,
                                                         self.abstract,
                                                         self.precipitation) # * self.scale
        
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

    def heatmap(self, **kwargs):
        return sns.heatmap(self.surface, square=True, **kwargs)
    
    def contourf(self, **kwargs):
        return plt.contourf(self.surface, **kwargs)

    def write(self, filename):
        """Write to file filename."""
        with open(filename, "w") as fd:
            writer = csv.writer(fd, delimiter=" ")
            # fd.write(filename + "\n")
            for row in self.surface:
                # print(row)
                writer.writerow(row)
