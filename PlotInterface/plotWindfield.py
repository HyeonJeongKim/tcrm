#!/usr/bin/env python
"""
    Tropical Cyclone Risk Model (TCRM) - Version 1.0 (beta release)
    Copyright (C) 2011  Geoscience Australia

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.


Title: plotWindfield.py - plot a wind field

Author: Craig Arthur
Email: craig.arthur@ga.gov.au
CreationDate: 2006-112-01
Description: Plot a given wind field (in fact any array) over a map,
             given the longitude and latitide grids.


Version: $Rev: 549 $
ModifiedBy: $Author$
ModifiedDate: $Date$
SeeAlso: (related programs)
Constraints:

$Id: plotWindfield.py 549 2007-10-22 01:34:48Z carthur $
"""
import os, sys, pdb, logging

import pylab
from numpy import *
from mpl_toolkits.basemap import Basemap
import Utilities.metutils as metutils


def plotWindfield(xGrid, yGrid, speed, title='Cyclone wind field',
                    xlabel='Longitude', ylabel='Latitude',
                    InfoString='', fileName=None, i=0):
    """
    Plot the wind field for a given grid.
    xGrid, yGrid and speed are arrays of the same size. (xGrid and yGrid
    are typically generated by [xGrid,yGrid] = meshgrid(lon,lat))
    """

    vMax = speed.max()
    InfoString = "%s \nMaximum speed: %2.1f m/s" % (InfoString, vMax)
    pylab.clf()
    dl = 5.
    llLon = min(xGrid[0,:])
    urLon = max(xGrid[0,:])
    llLat = min(yGrid[:,0])
    urLat = max(yGrid[:,0])
    meridians = arange(dl*floor(llLon/dl), dl*ceil(urLon/dl), dl)
    parallels = arange(dl*floor(llLat/dl), dl*ceil(urLat/dl), dl)
    levels = arange(0, 101, 5)

    m = Basemap(projection='cyl',
                resolution='i',
                llcrnrlon=llLon,
                urcrnrlon=urLon,
                llcrnrlat=llLat,
                urcrnrlat=urLat)

    #cs = m.contour(xGrid,yGrid,speed,array(arange(0,90,5)))
    m.contourf(xGrid, yGrid, speed, levels)

    pylab.colorbar()
    pylab.title(title)
    #pylab.figtext(0.175,0.86,InfoString,color='b',horizontalalignment='left',verticalalignment='top',fontsize=10)

    m.drawcoastlines()
    m.drawparallels(parallels, labels=[1,0,0,1], fontsize=9)
    m.drawmeridians(meridians, labels=[1,0,0,1], fontsize=9)
    """
    if cfgPlot['Basemap.fill_continents']:
        m.fillcontinents()
    """

    pylab.grid(True)

    if fileName is not None:
        pylab.savefig(fileName)

def plotPressurefield(xGrid, yGrid, pressure, title='Cyclone pressure field',
                    xlabel='Longitude', ylabel='Latitude',
                    InfoString='', fileName=None, i=0):
    """
    Plot the wind field for a given grid.
    xGrid, yGrid and speed are arrays of the same size. (xGrid and yGrid
    are typically generated by [xGrid,yGrid] = meshgrid(lon,lat))
    """
    pMin = pressure.min()
    if pMin > 8000.:
        pressure = metutils.convert(pressure, 'Pa', 'hPa')
    pylab.clf()
    dl = 5.
    llLon=min(xGrid[0,:])
    urLon=max(xGrid[0,:])
    llLat=min(yGrid[:,0])
    urLat=max(yGrid[:,0])
    meridians=arange(dl*floor(llLon/dl), dl*ceil(urLon/dl), dl)
    parallels=arange(dl*floor(llLat/dl), dl*ceil(urLat/dl), dl)
    levels = array(arange(900, 1020, 5))

    m = Basemap(projection='cyl',
                resolution='i',
                llcrnrlon=llLon,
                urcrnrlon=urLon,
                llcrnrlat=llLat,
                urcrnrlat=urLat)

    m.contourf(xGrid, yGrid, pressure, levels)
    #m.plot(cLon, cLat, 'k.-', markersize=2)

    pylab.colorbar()
    pylab.title(title)

    m.drawcoastlines()
    m.drawparallels(parallels, labels=[1,0,0,1], fontsize=9)
    m.drawmeridians(meridians, labels=[1,0,0,1], fontsize=9)
    """
    if cfgPlot['Basemap.fill_continents']:
        m.fillcontinents()
    """

    pylab.grid(True)

    if fileName is not None:
        pylab.savefig(fileName)
