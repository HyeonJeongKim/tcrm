"""
:mod:`plotStats` -- statistical plotting routines
=================================================

.. module:: plotStats
    :synopsis: A collection of statistical plotting routines.

.. moduleauthor:: Craig Arthur <craig.arthur@ga.gov.au>

"""

import sys

from os.path import join as pjoin
import matplotlib.pyplot as plt

from scipy.stats import linregress, probplot, frechet_l
import numpy as np

import seaborn as sns
sns.set_style("ticks")

plt.ioff()

def linreg(data):
    """
    Calculate the linear regression of the data against itself (lag-1)
    Returns the slope, intercept, correlation, two-tailed
    probability and standard error of the estimate.
    """
    tData = np.array([data[1:], data[:-1]])
    i = np.where((tData[0, :] < sys.maxint) & (tData[1, :] < sys.maxint))[0]
    m, c, r, pr, err = linregress(tData[:, i])
    return m, c, r, pr, err


class PlotData(object):
    """
    Base class for plotting summaries of input data.

    """
    def __init__(self, output_path, output_format, context="poster"):
        """
        Initialise statistical plotting routines, fixing the output path and
        the format of all images generated
        """
        self.outpath = output_path
        self.fmt = output_format
        self.fignum = 0
        sns.set_context(context)

    def figurenum(self):
        """
        Increment the figure number and return the new value
        """
        self.fignum += 1
        return self.fignum

    def savefig(self, filename, **kwargs):
        """
        Provide a shortcut to plt.savefig() that adds the output path to the
        filename.
        All keyword args are passed without alteration
        """
        outputfile = ".".join([filename, self.fmt])
        plt.savefig(pjoin(self.outpath, outputfile),
                       format=self.fmt, **kwargs)
        plt.close()

    def scatterHistogram(self, x, y, labels, name, 
                         transform=lambda x: x, **kwargs):
        """
        Create a scatter plot with marginal distributions
        
        :param x: `numpy.ndarray` of x values.
        :param y: `numpy.ndarray` of y values.
        :param list labels: A length-2 list with the x and y labels as strings.
        :param str img_name: Name to use in the file name for saving the 
                             figure.
        
        """

        i = np.where((x < sys.maxint) & (y < sys.maxint))[0]
        xx = transform(x[i])
        yy = transform(y[i])
        jp = sns.jointplot(xx, yy, kind='reg',
                           joint_kws={'scatter_kws':
                                      {'color':'slategray', 
                                       'alpha':0.5}},
                           **kwargs)

        jp.set_axis_labels(*labels)
        plt.tight_layout()

        self.savefig(name)

    def barPlot(self, x, y, name, labels):
        """
        Bar plot, with added trend line or mean line
        
        :param x: `numpy.ndarray` of x-values.
        :param y: `numpy.ndarray` of y-values.
        :param str name: Name of the parameter, which will be used
                         in the filename.
        :param list labels: A list of the x- and y-axis labels to apply.
        """

        f, ax = plt.subplots(1, 1)
        sns.barplot(x, y, ax=ax)
        ax.set_xlabel(labels[0])
        ax.set_ylabel(labels[1])
        ax.axhline(np.mean(y))
        sns.despine()
        f.tight_layout()
        self.savefig(name)

    def plotRegression(self, x, name, labels, transform=lambda x: x):
        """
        A generic function to plot a lag-1 autoregression of the 
        variable, with a joint probability plot including 
        marginal distribution plots.

        :param x: `numpy.ndarray` of the data variable to plot.
        :param str name: Name of the variable. Used for saving the 
                         resulting image.
        :param list labels: A list of the x- and y-axis labels to apply.
        :param func transform: A transform function to apply to 
                               the data. Default is to leave the 
                               data unchanged.
        
        """
        
        f, ax = plt.subplots(1, 1)
        x_t = x[1:]
        x_tm = x[:-1]
        skip = (x_t >= sys.maxint) | (x_tm >= sys.maxint)
        x_t = x_t.compress(skip==False)
        x_tm = x_tm.compress(skip==False)
        
        x_t = transform(x_t)
        x_tm = transform(x_tm)
        
        sns.regplot(x_t, x_tm, fit_reg=True, ax=ax, dropna=True)
        ax.set_xlabel(labels[0])
        ax.set_ylabel(labels[1])
        f.tight_layout()

        self.savefig(name)

        self.scatterHistogram(x_t, x_tm, labels, name+'_scatter')

    
    def plotLonLat(self, lonData, latData, indicator):
        """
        Plot the input lat/lon values lagged against themselves,
        and the same for the changes in lat/lon.

        TODO: 
        """

        plt.figure(self.figurenum(), figsize=(7, 12))

        dlon = lonData[1:] - lonData[:-1]
        dlat = latData[1:] - latData[:-1]
        j = np.where(indicator[1:] == 0)
        dlon = dlon[j]
        dlat = dlat[j]

        # Correct change in longitude where the value jumps across the 180E
        # meridian
        k = np.where(dlon < -180.)
        dlon[k] += 360.

        plt.subplot(211)
        plt.plot(dlon[1:], dlon[:-1], 'k.', markersize=1)
        params = linreg(dlon)
        plt.text(-3, 3, "r = %5.3f"%params[2], ha='center',
                    va='center', color='r', size=14)
        plt.xlim(-4., 4.)
        plt.ylim(-4., 4.)
        plt.xticks(np.arange(-4., 4.1, 1.))
        plt.yticks(np.arange(-4., 4.1, 1.))
        plt.ylabel(r"$\Delta lon (t)$", fontsize=16)
        plt.xlabel(r"$\Delta lon (t-1)$", fontsize=16)
        #plt.grid(True)
        plt.title("Longitude rate of change")

        plt.subplot(212)
        plt.plot(dlat[1:], dlat[:-1], 'k.', markersize=1)
        params = linreg(dlat)
        plt.text(-3, 3, "r = %5.3f"%params[2], ha='center',
                    va='center', color='r', size=14)
        plt.xlim(-4., 4.)
        plt.ylim(-4., 4.)
        plt.xticks(np.arange(-4., 4.1, 1.))
        plt.yticks(np.arange(-4., 4.1, 1.))
        plt.ylabel(r"$\Delta lat (t)$", fontsize=16)
        plt.xlabel(r"$\Delta lat (t-1)$", fontsize=16)
        plt.title("Latitude rate of change")
        plt.tight_layout()
        self.savefig('lonlat_corr')

        labels = [r'$\Delta \phi(t)$', r'$\Delta \phi(t-1)$']
        self.scatterHistogram(dlon[1:], dlon[:-1], labels, 'dlon_scatterHist')
        labels = [r'$\Delta \lambda(t)$', r'$\Delta \lambda(t-1)$']
        self.scatterHistogram(dlat[1:], dlat[:-1], labels, 'dlat_scatterHist')

    def _plotFrequency(self, years, frequency):
        """Plot annual frequency of TCs, plus linear trend line"""

        plt.figure(self.figurenum())
        plt.plot(years[1:-1], frequency[1:-1]) 
        xmax = 5*int((1 + years.max()/5))
        xmin = 5*int((years.min()/5))
        ymax = 5*int(1 + frequency.max()/5)
        plt.xlim(xmin, xmax)
        plt.ylim(0.0, ymax)
        
        plt.xlabel("Year")
        plt.ylabel("Frequency")

        params = linregress(np.array([years, frequency]))
        x = np.arange(xmin, xmax)
        y = params[0]*x + params[1]

        plt.plot(x, y, 'r--')
        plt.title("Annual frequency (%d - %d)"%(years.min(), years.max()))
        self.savefig('frequency')

        return



    def minPressureHist(self, index, pAllData):
        """
        Plot a histogram of the minimum central pressures from the input
        dataset.
        """

        plt.figure(self.figurenum(), figsize=(8, 7))
        plt.clf()
        pcarray = []
        index = index.astype(int)
        for i in range(len(index) - 1):
            if index[i] == 1:
                pcarray.append(pAllData[i])
            else:
                if pAllData[i] is not None:
                    if pAllData[i] < pcarray[-1]:
                        pcarray[-1] = pAllData[i]

        pbins = np.arange(850., 1020., 5)
        pcarray = np.array(pcarray)
        pc = np.take(pcarray, np.where(pcarray<sys.maxint))
        ax = sns.distplot(pc, bins=pbins, fit=frechet_l, 
                          kde_kws={'label':'KDE'},
                          fit_kws={'color':'r',
                                   'label':'Fitted distribution'})

        sns.despine(ax=ax, offset=10, trim=True)
        ax.set_xlabel("Minimum central pressure (hPa)")
        ax.set_ylabel("Probability")
        ax.set_title("Distribution of minimum central pressure")
        ax.legend(loc=0)
        plt.tight_layout()
        self.savefig("min_pressure_hist")

    def plotSpeedBear(self, sAllData, bAllData):
        """
        Plot speed and bearing against each other
        """
        plt.figure(self.figurenum(), figsize=(7, 7))
        plt.subplot(111)
        ii = np.where((sAllData < sys.maxint) & (bAllData < sys.maxint))
        plt.polar((np.pi/2. - np.radians(bAllData[ii])), sAllData[ii],
                     'k.', markersize=2)
        thetalabels = (90 - np.arange(0, 360, 45))
        ii = np.where(thetalabels < 0)
        thetalabels[ii] += 360
        lines, labels = plt.rgrids(np.arange(20., 101., 20.),
                                      labels=None, angle=67.5)
        lines, labels = plt.thetagrids(np.arange(0., 360., 45.),
                                          thetalabels)
        plt.ylim(0, 100.)
        plt.grid(True)
        r = np.corrcoef(bAllData[ii], sAllData[ii])[1, 0]
        plt.text(45, 125, "r = %5.3f"%r, ha='center',
                    va='center', color='r', size=14)
        plt.title("Speed vs bearing")
        self.savefig('spd_bear_corr')

    def quantile(self, data, parameterName, dist='normal'):
        """
        Generate a probability plot of the given data; data should be an
        array of anomalies

        """
        plt.figure(self.figurenum(), figsize=(8, 7))
        plt.clf()
        d = data.compress(data < sys.maxint)
        m = np.average(d)
        sd = np.std(d)
        nd = (d-m)/sd
        (osm, osr), (slope, intercept, r) = probplot(nd, dist=dist, plot=plt)

        plt.ylabel(parameterName)
        plt.title("Q-Q plot - %s" % parameterName)
        plt.xlim((-5, 5))
        plt.ylim((-5, 5))
        pos = (2, -4.8)
        plt.text(2, -4.9, r"$r^2=%1.4f$" % r, fontsize=12)

        self.savefig('qqplot_%s' % parameterName)


class PlotPressure(PlotData):

    def plotPressure(self, data):
        labels = [r'$p_c(t)$', r'$p_c(t-1)$']
        self.scatterHistogram(data[1:], data[:-1],
                              labels, 'pressure',
                              xlim=(850, 1020), ylim=(850, 1020))

    def plotPressureRate(self, data):
        labels = [r'$\frac{\delta p_c}{\delta t}(t)$', 
                  r'$\frac{\delta p_c}{\delta t}(t-1)$']
        self.scatterHistogram(data[1:], data[:-1],
                              labels, 'pressure_rate')
        self.quantile(data, 'pressure_rate', 'logistic')

    def plotMinPressure(self, index, pAllData):
        """
        Plot the distribution of minimum central pressure, and 
        include a fitted distribution (presently uses the 
        `scipy.stats.frechet_l` distribution). 

        :param index: `numpy.ndarray` of 1/0 that indicates the start of 
                      separate TC tracks.
        :param pAllData: `numpy.ndarray` of pressure observations from 
                         TC events.

        """
        pcarray = []
        index = index.astype(int)
        for i in range(len(index) - 1):
            if index[i] == 1:
                pcarray.append(pAllData[i])
            else:
                if pAllData[i] is not None:
                    if pAllData[i] < pcarray[-1]:
                        pcarray[-1] = pAllData[i]

        pbins = np.arange(850., 1020., 5)
        pcarray = np.array(pcarray)
        pc = np.take(pcarray, np.where(pcarray<sys.maxint))
        ax = sns.distplot(pc, bins=pbins, fit=frechet_l, 
                          kde_kws={'label':'KDE'},
                          fit_kws={'color':'r',
                                   'label':'Fitted distribution'})

        sns.despine(ax=ax, offset=10, trim=True)
        ax.set_xlabel("Minimum central pressure (hPa)")
        ax.set_ylabel("Probability")
        ax.set_title("Distribution of minimum central pressure")
        ax.legend(loc=0)
        plt.tight_layout()
        self.savefig("min_pressure_hist")

class PlotBearing(PlotData):

    def plotBearing(self, data):
        labels = [r'$\theta(t)$', r'$\theta(t-1)$']
        def transform(x):
            return np.cos(x/2.)

        self.scatterHistogram(data[1:], data[:-1], labels, 'bearing',
                              transform=transform, xlim=(-1, 1),
                              ylim=(-1, 1))

    def plotBearingRate(self, data):
        labels = [r'$\frac{\delta \theta(t)}{\delta t}$', 
                  r'$\frac{\delta \theta(t-1)}{\delta t}$']
        self.scatterHistogram(data[1:], data[:-1], 
                              labels, 'bearing_rate')
        self.quantile(data, 'bearing_rate', 'logistic')

class PlotSpeed(PlotData):
    
    def plotSpeed(self, data):
        labels = [r'$v (t)$', r'$v (t-1)$']
        self.scatterHistogram(data[1:], data[:-1], labels, 'speed',
                              xlim=(0, 100), ylim=(0, 100))

    def plotSpeedRate(self, data):
        labels = [r'$\frac{\delta v(t)}{\delta t}$', 
                  r'$\frac{\delta v(t-1)}{\delta t}$']
        self.scatterHistogram(data[1:], data[:-1], 
                              labels, 'speed_rate')
        self.quantile(data, 'speed_rate', 'logistic')

class PlotFrequency(PlotData):
    
    def plotFrequency(self, years, frequency):
        """
        Plot annual count of events within the domain.
        
        TODO: Automatically adjust the x-tickmarks to be spaced
              nicely (i.e. no overlap of labels).
              Offer option of drawing the mean value (using 
              `axes.axhline`) or a linear trend line.
        """
        labels = ["Year", "Number"]
        self.barPlot(years.astype(int), frequency, "frequency", labels)

class PlotDays(PlotData):
    
    def plotJulianDays(self, julianDayObs, julianDayGenesis):
        """
        Plot bar graphs of the number of TC observations per day of year 
        and genesis events per day of year.
        
        TODO: Format the tick marks to represent monthly intervals.
              Add a KDE over both bar plots.
        """
        f, (ax1, ax2) = plt.subplots(2, 1, sharex=True)
        
        sns.barplot(julianDayObs[:, 0], julianDayObs[:, 1], ax=ax1)
        ax1.set_xlim((1, 365))
        ax1.set_ylabel('Observations')
        ax1.set_xticks(np.arange(1, 365, 30))

        sns.barplot(julianDayGenesis[:, 0], julianDayGenesis[:, 1], ax=ax2)
        ax2.set_xlim((1, 365))
        ax2.set_xlabel('Day of year')
        ax2.set_ylabel('Genesis events')

        ax2.set_xticks(np.arange(1, 365, 30))
        ax2.set_xticklabels(np.arange(1, 365, 30,dtype=int))
        self.savefig("julian_day")


if __name__ == "__main__":
    """
    import Utilities.config as config
    configFile = sys.argv[1]
    dataPath = config.cnfGetIniValue(configFile, 'Output', 'Path', os.getcwd())
    inputPath = pjoin(dataPath, 'process')
    outputPath = pjoin(dataPath, 'plots')
    plt.rcParams['figure.figsize'] = (7, 12)

    pRateData = files.flLoadFile(pjoin(inputPath, 'pressure_rate'))
    pAllData = files.flLoadFile(pjoin(inputPath, 'all_pressure'))
    bRateData = files.flLoadFile(pjoin(inputPath, 'bearing_rate'))
    bAllData = files.flLoadFile(pjoin(inputPath, 'all_bearing'))
    sRateData = files.flLoadFile(pjoin(inputPath, 'speed_rate'))
    sAllData = files.flLoadFile(pjoin(inputPath, 'all_speed'))
    freq = files.flLoadFile(pjoin(inputPath, 'frequency'))
    years = freq[:, 0]
    frequency = freq[:, 1]

    plotting = PlotData(outputPath, "png")
    plotting.plotPressure(pAllData, pRateData)
    plotting.plotBearing(bAllData, bRateData)
    plotting.plotSpeed(sAllData, sRateData)
    plotting.plotFrequency(years, frequency)
    plotting.plotSpeedBear(sAllData, bAllData)
    """
