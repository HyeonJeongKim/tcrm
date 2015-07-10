"""
:mod:`figures` -- basic figure elements
=======================================

.. module:: figures
    :synopsis: Basic figure elements for statistical and other plotting
               actions.

.. moduleauthor:: Craig Arthur <craig.arthur@ga.gov.au>

"""

from __future__ import division

import sys
import numpy as np
import scipy.stats as stats
import wind.windmodels as windmodels

from matplotlib import pyplot as plt
from matplotlib.figure import Figure
from matplotlib.artist import setp
from mpl_toolkits.axes_grid1 import make_axes_locatable
from mpl_toolkits.basemap import Basemap

import seaborn as sns
sns.set(style="ticks")

class WindProfileFigure(Figure):

    def __init__(self, lat, lon, eP, cP, rMax, beta, beta1=1.5, beta2=1.4):

        Figure.__init__(self)
        self.R = np.array(range(1, 201), 'f')
        self.lat = lat
        self.lon = lon
        self.rMax = rMax
        self.eP = eP
        self.cP = cP
        self.beta = beta
        self.beta1 = beta1
        self.beta2 = beta2

    def plot(self, profileType=None):
        profiles = []

        if profileType:
            profiles.append(profileType)
        else:
            for p in windmodels.PROFILES:
                profiles.append(p)

        ax = self.add_subplot(1, 1, 1)
        ax.hold(True)
        legend = []

        for name in profiles:
            try:
                cls = windmodels.profile(name)
                params = windmodels.profileParams(name)
                values = [getattr(self, p) for p in params if hasattr(self, p)]
                profile = cls(self.lat, self.lon, self.eP, self.cP,
                              self.rMax, *values)
                V = profile.velocity(self.R)
                ax.plot(self.R, abs(V), linewidth=2)
                legend.append(name.capitalize())
            except TypeError:
                pass

        ax.legend(legend)
        ax.set_xlabel('Radius (km)', fontsize=14)
        ax.set_ylabel('Wind speed (m/s)', fontsize=14)
        ax.set_title((r'$P_c = %d\hspace{0.5}hPa,\hspace{1} P_e' +
                      r'= %d \hspace{0.5} hPa,\hspace{1} R_{max}' +
                      r'= %d \hspace{0.5}km$') %
                    (self.cP / 100., self.eP / 100., self.rMax))

class ScatterHistogramFigure(Figure):

    def __init__(self):
        Figure.__init__(self)

    def plot(self, xdata, ydata):
        i = np.where((xdata < sys.maxint) & (ydata < sys.maxint))[0]
        x = xdata[i]
        y = ydata[i]

        jp = sns.jointplot(x, y, kind='reg',
                           joint_kws={'scatter_kws':{
                                          'color':'slategray',
                                          'alpha':0.5
                                          }
                                      },
                           **kwargs)
        self.tight_layout()


class QuantileFigure(Figure):
    """
    Create a quantile-quantile plot that includes estimated confidence
    intervals for the simulated (or second) dataset.

    """

    def __init__(self):
        Figure.__init__(self)
        self.subfigures = []

    def percentiles(self, data):
        """Calculate percentile values from 1 to 100"""
        per = np.array([stats.scoreatpercentile(data, q)
                        for q in range(1, 101)])
        return per

    def percentilerange(self, data):
        """Calculate a range of percentile values"""
        samples = np.zeros((1000, 100))
        for n in xrange(1000):
            samples[n, :] = np.array([np.random.choice(data)
                                      for _ in xrange(100)])

        dummy = stats.scoreatpercentile(samples, range(1, 101), axis=1)
        upper = stats.scoreatpercentile(dummy, 95, axis=1)
        lower = stats.scoreatpercentile(dummy, 5, axis=1)
        return upper, lower

    def add(self, xdata, ydata, axisrange, xlabel='x', ylabel='y',
            title='Q-Q plot'):
        """Add a subplot to the collection"""
        self.subfigures.append((xdata, ydata, axisrange,
                                xlabel, ylabel, title))

    def formatAxes(self, axes, limits):
        """Format the axes to have the same limits"""
        axes.set_ylim(limits)
        axes.set_xlim(limits)

    def addGrid(self, axes):
        """
        Add a grid to the subplot axes.

        :param axes: `matplotlib.axes` instance

        """
        axes.grid(True)


    def subplot(self, axes, subfigure):
        xdata, ydata, axisrange, xlabel, ylabel, title = subfigure

        xper = self.percentiles(xdata)
        yper = self.percentiles(ydata)

        xupper, xlower = self.percentilerange(xdata)
        yupper, ylower = self.percentilerange(ydata)

        axes.scatter(xper, yper, c='r', marker='o',
                     edgecolor='none', alpha=0.5)

        axes.plot(xupper, ylower, color='0.5', linewidth=1)
        axes.plot(xlower, yupper, color='0.5', linewidth=1)

        axes.set_xlabel(xlabel)
        axes.set_ylabel(ylabel)
        axes.set_title(title)

        xx = np.arange(*axisrange)
        axes.plot(xx, xx, 'b--', linewidth=0.5)

        self.formatAxes(axes, axisrange)
        self.addGrid(axes)
        self.tight_layout()

    def plot(self):
        n = len(self.subfigures)
        r = int(np.ceil(np.sqrt(n)))
        c = int(np.ceil(n / r))
        w, h = self.get_size_inches()
        self.set_size_inches(w * c, r * h)
        for i, subfigure in enumerate(self.subfigures):
            axes = self.add_subplot(r, c, i)
            self.subplot(axes, subfigure)

class RegressionFigure(Figure):

    def __init__(self):
        Figure.__init__(self)
        self.subfigures = []

    def add(self, xdata, ydata, xlabel='x', ylabel='y',
            title='x', transform=lambda x: x):
        self.subfigures.append((xdata, ydata, xlabel, ylabel, title, transform))

    def prepareData(self, xdata, ydata, transform):
        i = np.where((xdata < sys.maxint) & (ydata < sys.maxint))[0]
        xdata, ydata = transform(xdata), transform(ydata)
        return xdata[i], ydata[i]

    def formatAxes(self, axes, xdata, ydata):
        def filterOutliers(data, m=12.):
            d = np.abs(data - np.median(data))
            mdev = np.median(d)
            s  = d/mdev if mdev else 0
            return data[s < m]

        xmin = filterOutliers(xdata).min()
        xmax = filterOutliers(xdata).max()
        ymin = filterOutliers(ydata).min()
        ymax = filterOutliers(ydata).max()

        axes.set_xlim(xmin, xmax)
        axes.set_ylim(ymin, ymax)
        axes.set_xticks(np.linspace(xmin, xmax, 7))
        axes.set_yticks(np.linspace(ymin, ymax, 7))

        return xmin, xmax

    def subplot(self, axes, subfigure):
        xdata, ydata, xlabel, ylabel, title, transform = subfigure
        color = axes._get_lines.color_cycle

        xdata, ydata = self.prepareData(xdata, ydata, transform)
        k = color.next()
        scatter_kws = {'color':k,
                       'alpha':0.5}
        sns.regplot(xdata, ydata, ax=axes, scatter_kws=scatter_kws)

        xmin, xmax = self.formatAxes(axes, xdata, ydata)
        axes.set_xlabel(xlabel)
        axes.set_ylabel(ylabel)
        axes.set_title(title)

        legend = axes.legend(loc=2)
        legend.get_frame().set_alpha(0.5)

    def plot(self):
        nfig = len(self.subfigures)
        rows = int(np.ceil(np.sqrt(nfig)))
        cols = int(np.ceil(nfig / rows))
        width, height = self.get_size_inches()
        self.set_size_inches(width * cols, rows * height)
        for i, subfigure in enumerate(self.subfigures):
            axes = self.add_subplot(rows, cols, i + 1)
            self.subplot(axes, subfigure)



class LaggedRegressionFigure(RegressionFigure):

    def add(self, data, label='x', title='x', transform=lambda x: x):
        super(LaggedRegressionFigure, self).add(data[1:],
                                                data[:-1],
                                                r'$' + label + r'(t-1)$',
                                                r'$' + label + r'(t)$',
                                                title,
                                                transform)

    def subplot(self, axes, subfigure):
        super(LaggedRegressionFigure, self).subplot(axes, subfigure)
        axes.set_aspect('equal')

class LineRegressionFigure(RegressionFigure):

    def add(self, x, y, xlabel='x', ylabel='y', title='x'):
        super(LineRegressionFigure, self).add(x, y,
                                              xlabel,
                                              ylabel,
                                              title)

    def subplot(self, axes, subfigure):
        xdata, ydata, xlabel, ylabel, title, transform = subfigure
        color = axes._get_lines.color_cycle

        xdata, ydata = self.prepareData(xdata, ydata, transform)

        k = color.next()
        scatter_kws = {'color':k,
                       'alpha':0.5}
        sns.regplot(xdata, ydata, ax=axes, scatter_kws=scatter_kws)

        xmin, xmax = self.formatAxes(axes, xdata, ydata)
        axes.set_xlabel(xlabel)
        axes.set_ylabel(ylabel)
        axes.set_title(title)

        legend = axes.legend(loc=2)
        legend.get_frame().set_alpha(0.5)

class PressureFigure(LaggedRegressionFigure):

    def plot(self, pressures, pressureRates):
        self.add(pressures, 'p', 'Pressure')
        self.add(pressureRates, r'\Delta p', 'Pressure rate of change')
        super(PressureFigure, self).plot()


class SpeedFigure(LaggedRegressionFigure):

    def plot(self, speeds, speedRates):
        self.add(speeds, 'v', 'Speed')
        self.add(speedRates, r'\Delta v', 'Speed rate of change (Acceleration)')
        super(SpeedFigure, self).plot()


class BearingFigure(LaggedRegressionFigure):

    def plot(self, bearings, bearingRates):
        def transform(z):
            return np.cos(np.radians(z))
        self.add(bearings, r'\cos(\theta)', 'Bearing', transform)
        self.add(bearingRates, r'\Delta\theta',
                 'Bearing rate of change')
        super(BearingFigure, self).plot()


class FrequencyFigure(LineRegressionFigure):

    def plot(self, years, frequency):
        self.add(np.array(years[1:-1], int), frequency[1:-1], 'Year',
                 'Frequency', 'Annual Frequency')
        super(FrequencyFigure, self).plot()


def saveFigure(figure, filename):
    from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
    canvas = FigureCanvas(figure)
    canvas.print_figure(filename)


def saveWindProfilesFigure(lat, lon, eP, cP, rMax, beta,
                           filename='docs/windprofiles.png'):
    fig = WindProfileFigure(lat, lon, eP, cP, rMax, beta)
    fig.plot()
    saveFigure(fig, filename)


def savePressureFigure(pressures, pressureRates,
                       filename='docs/prs_corr.png'):
    fig = PressureFigure()
    fig.plot(pressures, pressureRates)
    saveFigure(fig, filename)
    fig = ScatterHistogramFigure()
    fig.plot(pressures[1:], pressures[:-1])
    saveFigure(fig, 'docs/pressuresh.png')
    fig = ScatterHistogramFigure()
    fig.plot(pressureRates[1:], pressureRates[:-1])
    saveFigure(fig, 'docs/pressureratesh.png')


def saveSpeedFigures(speeds, speedRates):
    fig = SpeedFigure()
    fig.plot(speeds, speedRates)
    saveFigure(fig, 'docs/spd_corr.png')
    fig = ScatterHistogramFigure()
    fig.plot(speeds[1:], speeds[:-1])
    saveFigure(fig, 'docs/speedsh.png')
    fig = ScatterHistogramFigure()
    fig.plot(speedRates[1:], speedRates[:-1])
    saveFigure(fig, 'docs/speedratesh.png')

def saveBearingFigure(bearings, bearingRates):
    fig = BearingFigure()
    fig.plot(bearings, bearingRates)
    saveFigure(fig, 'docs/bear_corr.png')
    fig = ScatterHistogramFigure()
    fig.plot(bearings[1:], bearings[:-1])
    saveFigure(fig, 'docs/bearingsh.png')
    fig = ScatterHistogramFigure()
    fig.plot(bearingRates[1:], bearingRates[:-1])
    saveFigure(fig, 'docs/bearingratesh.png')



def saveFrequencyFigure(years, frequency, filename='docs/freq_corr.png'):
    fig = FrequencyFigure()
    fig.plot(years, frequency)
    saveFigure(fig, filename)


def main():
    import Utilities.files as files
    from os.path import join as pjoin, dirname, normpath
    baseDir = normpath(pjoin(dirname(__file__), '..'))
    inputPath = pjoin(baseDir, 'output', 'process')

    saveWindProfilesFigure(-12., 130., 100700., 95000., 30., 1.6)

    pressureRates = files.flLoadFile(pjoin(inputPath, 'pressure_rate'))
    pressures = files.flLoadFile(pjoin(inputPath, 'all_pressure'))
    savePressureFigure(pressures, pressureRates)

    speedRates = files.flLoadFile(pjoin(inputPath, 'speed_rate'))
    speeds = files.flLoadFile(pjoin(inputPath, 'all_speed'))
    saveSpeedFigures(speeds, speedRates)

    bearingRates = files.flLoadFile(pjoin(inputPath, 'bearing_rate'))
    bearings = files.flLoadFile(pjoin(inputPath, 'all_bearing'))
    saveBearingFigure(bearings, bearingRates)

    freq = files.flLoadFile(pjoin(inputPath, 'frequency'))
    saveFrequencyFigure(np.array(freq[:,0],int), freq[:,1])

if __name__ == "__main__":
    main()
