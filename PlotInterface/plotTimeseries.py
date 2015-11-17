"""
:mod:`plotTimeseries` -- plot timeseries data generated by TCRM
===============================================================

.. module:: plotTimeseries
    :synopsis: Load timeseries data generated by TCRM and plot the wind
               speed, component wind speeds and bearing.

.. moduleauthor:: Craig Arthur <craig.arthur@ga.gov.au>

Load timeseries data generated by TCRM and plot the wind
speed, component wind speeds and bearing.

"""

import os
import sys
import logging

from os.path import join as pjoin

import numpy as np
from datetime import datetime

from Utilities.metutils import convert

from timeseries import TimeSeriesFigure, saveFigure

DATEFORMAT = "%Y-%m-%d %H:%M"
INPUT_COLS = ('Station', 'Time', 'Longitude', 'Latitude',
              'Speed', 'UU', 'VV', 'Bearing',
              'Pressure')

INPUT_FMTS = ('|S16', 'object', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8')
INPUT_TITLES = ("Station", "Time", "Longitude", "Latitude", "Wind speed",
                "Eastward wind", "Northward wind", "Wind direction",
                "Sea level pressure")
INPUT_UNIT = ('', '%Y-%m-%d %H:%M', 'degrees', 'degrees', 'm/s',
                'm/s', 'm/s','degrees', 'Pa')
INPUT_CNVT = {
    1: lambda s: datetime.strptime(s.strip(), INPUT_UNIT[1]),
    8: lambda s: convert(float(s.strip() or 0), INPUT_UNIT[8], 'hPa')
    }

def loadTimeseriesData(datafile):
    try:
        return np.genfromtxt(datafile, dtype=INPUT_FMTS, names=INPUT_COLS,
                             comments='#', delimiter=',', skiprows=1,
                             converters=INPUT_CNVT)
    except ValueError:
        return np.empty(0, dtype={
                        'names': INPUT_COLS,
                        'formats': INPUT_FMTS})

def plotTimeseries(inputPath, outputPath, locID=None):
    """
    Load the data and pass it to the :meth:`TimeSeriesFigure.plot` method.

    :param str inputPath: Path to the raw timeseries data.
    :param str outputPath: Path to the location that images should be
                           stored in.
    :param str locID: Unique identifier for a chosen location. If not
                      given, all files in the input path will be processed.

    Example: plotTimeseries('/tcrm/output/timeseries','/tcrm/output/plots')

    """
    if locID:
        # Only plot the data corresponding to the requested location ID:
        inputFile = pjoin(inputPath, 'ts.%s.csv' % (locID))
        outputFile = pjoin(outputPath, 'ts.%s.png' % (locID))
        inputData = loadTimeseriesData(inputFile)

        stnInfo = {'ID': locID, 'lon': inputData['Longitude'][0],
                    'lat': inputData['Latitude'][0]}
        title = 'Station ID: %s (%6.2f, %6.2f)' % (locID,
                                                   inputData['Longitude'][0],
                                                   inputData['Latitude'][0])
        fig = TimeSeriesFigure()
        fig.add(inputData['Time'], inputData['Pressure'],
                [900, 1020], 'Pressure (hPa)', 'Pressure')
        fig.add(inputData['Time'], inputData['Speed'],
                [0, 100], 'Wind speed (m/s)', 'Wind speed')
        fig.add(inputData['Time'], inputData['Bearing'],
                [0, 360], 'Direction', 'Wind direction')

        fig.plot()
        fig.addTitle(title)
        saveFigure(fig, outputFile)

    else:
        files = os.listdir(inputPath)
        inputFileList = [f for f in files if f.startswith('ts.')]
        for f in inputFileList:
            # Here we assume the timeseries files are named ts.<location ID>.dat
            locID = f.rstrip('.csv').lstrip('ts.')
            outputFile = pjoin(outputPath, '%s.png' % f.rstrip('.csv'))
            inputData = loadTimeseriesData(pjoin(inputPath, f))


            stnInfo = {'ID':locID, 'lon':inputData['Longitude'][0],
                        'lat':inputData['Latitude'][0]}
            title = 'Station ID: %s (%6.2f, %6.2f)' % (locID,
                                                       inputData['Longitude'][0],
                                                       inputData['Latitude'][0])


            fig = TimeSeriesFigure()

            fig.add(inputData['Time'], inputData['Pressure'],
                    [900, 1020], 'Pressure (hPa)',
                    'Sea level pressure')
            fig.add(inputData['Time'], inputData['Speed'],
                    [0, 100], 'Wind speed (m/s)', 'Wind speed')
            fig.add(inputData['Time'], inputData['Bearing'],
                    [0, 360], 'Direction', 'Wind direction')
            fig.plot()
            fig.addTitle(title)
            saveFigure(fig, outputFile)


if __name__ == '__main__':
    plotTimeseries(sys.argv[1], sys.argv[2])
