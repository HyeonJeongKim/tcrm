"""
:mod:`tracks` -- plot TC tracks
===================================

.. module:: tracks
    :synopsis: Plot TC tracks on a map.

.. moduleauthor:: Craig Arthur <craig.arthur@ga.gov.au>

"""
import sys
import logging as log

import numpy as np

from matplotlib.collections import LineCollection
from matplotlib.colors import Normalize, BoundaryNorm, ListedColormap
from matplotlib.cm import get_cmap

import Utilities.shptools as shptools

from maps import MapFigure, saveFigure

def make_segments(x, y):
    """
    Create a list of line segments from x,y coordinates, in the 
    correct format for LineCollection.

    :param x: :class:`numpy.ndarray` of x-coordinates.
    :param y: :class:`numpy.ndarray` of y-coordinates.
    """

    points = np.array([x, y]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)

    return segments



class TrackMapFigure(MapFigure):
    """
    Base class for plotting track maps.
    """

    def colorline(self, x, y, z=None, linewidth=1.0, alpha=1.0):
        """
        Create and add line collections to an axes instance, using 
        an optional magnitude value to colourize the line segments.

        :param x: :class:`numpy.ndarray` of x-coordinates for lines.
        :param y: :class:`numpy.ndarray` of y-coordinates for lines.
        :param z: (Optional) :class:`numpy.ndarray` of magnitudes to 
                  colourize the line segments. 
        :param float linewidth: Line width of the line segments to plot.
        :param float alpha: Transparency level of the line segments.

        """

        if z is None:
            z = np.linspace(0.0, 1.0, len(x))

        if not hasattr(z, '__iter__'):
            z = np.array([z])

        z = np.asarray(z)

        segments = make_segments(x, y)
        cmap = ListedColormap(['0.75', '#0FABF6', '#0000FF',
                                '#00FF00', '#FF8100', '#ff0000'])
        norm = BoundaryNorm([0, 17.5, 24.5, 32.5, 44.2, 55.5, 1000], cmap.N)
        lc = LineCollection(segments, array=z, cmap=cmap, 
                            norm=norm, linewidth=linewidth, alpha=alpha)
        
        ax = self.gca()
        ax.add_collection(lc)

        
    def add(self, tracks, xgrid, ygrid, title, map_kwargs):
        self.subfigures.append((tracks, xgrid, ygrid, title, map_kwargs))

    def subplot(self, axes, subfigure):
        tracks, xgrid, ygrid, title, map_kwargs = subfigure
        mapobj, mx, my = self.createMap(axes, xgrid, ygrid, map_kwargs)

        for track in tracks:
            mlon, mlat = mapobj(track.Longitude, track.Latitude)
            self.colorline(mlon, mlat, track.WindSpeed, 
                           linewidth=1, alpha=0.75)
        axes.set_title(title)
        self.labelAxes(axes)
        self.addGraticule(axes, mapobj)
        self.addCoastline(mapobj)
        self.fillContinents(mapobj)
        self.addMapScale(mapobj)

class SingleTrackMap(TrackMapFigure):

    def plot(self, tracks, xgrid, ygrid, title, map_kwargs):
        self.add(tracks, xgrid, ygrid, title, map_kwargs)
        super(SingleTrackMap, self).plot()


def saveTrackMap(tracks, xgrid, ygrid, title, map_kwargs, filename):
    fig = SingleTrackMap()
    fig.plot(tracks, xgrid, ygrid, title, map_kwargs)
    saveFigure(fig, filename)

def main(configFile):
    from Utilities.loadData import loadTrackFile
    from Utilities.config import ConfigParser
    from os.path import join as pjoin, normpath, dirname
    baseDir = normpath(pjoin(dirname(__file__), '..'))
    inputPath = pjoin(baseDir, 'input')
    config = ConfigParser()
    config.read(configFile)

    inputFile = config.get('DataProcess', 'InputFile')
    source = config.get('DataProcess', 'Source')

    gridLimit = config.geteval('Region', 'gridLimit')

    xx = np.arange(gridLimit['xMin'], gridLimit['xMax'] + .1, 0.1)
    yy = np.arange(gridLimit['yMin'], gridLimit['yMax'] + .1, 0.1)

    xgrid, ygrid = np.meshgrid(xx, yy)

    if len(dirname(inputFile)) == 0:
        inputFile = pjoin(inputPath, inputFile)

    try:
        tracks = loadTrackFile(configFile, inputFile, source)
    except (TypeError, IOError, ValueError):
        log.critical("Cannot load historical track file: {0}".format(inputFile))
        raise

    title = source
    outputPath = config.get('Output', 'Path')
    outputPath = pjoin(outputPath, 'plots','stats')
    outputFile = pjoin(outputPath, 'tctracks.png')

    map_kwargs = dict(llcrnrlon=xgrid.min(),
                      llcrnrlat=ygrid.min(),
                      urcrnrlon=xgrid.max(),
                      urcrnrlat=ygrid.max(),
                      projection='merc',
                      resolution='i')

    figure = TrackMapFigure()
    figure.add(tracks, xgrid, ygrid, title, map_kwargs)
    figure.plot()
    saveFigure(figure, outputFile)

if __name__ == "__main__":
    configFile = sys.argv[1]
    main(configFile)
