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


Title: HazardInterface.py
Author: Craig Arthur, craig.arthur@ga.gov.au
CreationDate: 2008-01-14
Description: Load maximum wind speed grids and determine hazard levels
             (return periods)
Reference:
SeeAlso: WindfieldInterface
Constraints:

Version: 335

ModifiedBy: Nicholas Summons, nicholas.summons@ga.gov.au
ModifiedDate: 2010-04-30
Modification: Code modified so input files are processed using spatial subsets to prevent
              memory overloading (this allows all wind data for each grid point to
              to processed collectively, rather then resorting to an arbitrary
              averaging process).

ModifiedBy: Nicholas Summons, nicholas.summons@ga.gov.au
ModifiedDate: 2010-07-15
Modification: Implemented GEV distribution fitting using L-moments method (refer to evd.py for more information)

Version: 381
ModifiedBy: Craig Arthur, craig.arthur@ga.gov.au
ModifiedDate: 2010-10-22 11:51:AM
Modification: Uses updated ncSaveGrid, where all output data including
              GEV distribution parameters and return period wind speeds
              are stored in a single netCDF file.
              Made the minimum number of records for calculation of GEV
              distribution configurable. Default value set to 50.

Version: $Rev: 648 $
ModifiedBy: Craig Arthur, craig.arthur@ga.gov.au
ModifiedDate: 2011-04-14 9:01:AM
Modification: Included capacity to calculate confidence interval of
              return period wind speeds. The process uses a bootstrap
              resampling technique to fit a large (default 1000)
              number of GEV distributions. Can be turned on by setting
              'CalculateCI=True' in the HazardInterface section of the
              configuration file.

$Id: HazardInterface.py 648 2011-10-31 05:34:02Z nsummons $
"""

import os, sys, pdb, logging

from math import *
from numpy import *

import Utilities.nctools as nctools
from Utilities.config import cnfGetIniValue
from Utilities.grid import grdSave, grdRead
import random
from scipy.stats import scoreatpercentile as percentile
from Utilities.progressbar import ProgressBar
import evd

__version__ = "$Id: HazardInterface.py 648 2011-10-31 05:34:02Z nsummons $"

class HazardInterface:

    def __init__(self, configFile='HazardInterface.ini'):
        """
        Initialise HazardInterface module and run internal functions to
        determine return period hazard maps based on wind fields
        generated in WindfieldInterface.
        At this time, I've switched off the sanity checking on the
        return periods that are calculated (i.e. a check that there are
        sufficient years in the windfields to give a 'reliable' estimate
        of the longest return period requested).
        """
        self.pbar = ProgressBar('(5/6) Calculating hazard:    ')
        self.nodata = -9999
        self.configFile = configFile
        self.logger = logging.getLogger()
        self.logger.info("Initiating HazardInterface")
        self.gL = eval(cnfGetIniValue(self.configFile, 'Region', 'gridLimit'))
        self.nsim = cnfGetIniValue(self.configFile, 'HazardInterface', 'NumSim')
        self.calcCI = cnfGetIniValue(self.configFile, 'HazardInterface', 'CalculateCI', False)
        self.inputPath = cnfGetIniValue(self.configFile, 'HazardInterface', 'InputPath',
                                        os.path.join(cnfGetIniValue(self.configFile, 'Output', 'Path'),
                                        'windfield'))
        self.fileList = os.listdir(self.inputPath)

        # Load first windfield file to obtain lat, lon
        inputFile = os.path.join(self.inputPath, self.fileList[0])
        nc_obj = nctools.ncLoadFile(inputFile)
        wf_lon = nctools.ncGetDims(nc_obj, 'lon')
        wf_lat = nctools.ncGetDims(nc_obj, 'lat')
        nc_obj.close()

        # Apply grid limits to obtain valid grid indices
        ii, = ((wf_lon >= self.gL['xMin']) & (wf_lon <= self.gL['xMax'])).nonzero()
        jj, = ((wf_lat >= self.gL['yMin']) & (wf_lat <= self.gL['yMax'])).nonzero()
        self.imin = ii[0]
        self.imax = ii[-1]
        self.jmin = jj[0]
        self.jmax = jj[-1]
        self.lon = wf_lon[self.imin:self.imax+1]
        self.lat = wf_lat[self.jmin:self.jmax+1]
        self.outputPath = os.path.join(cnfGetIniValue(self.configFile, 'Output', 'Path'),
                                       'hazard')
        self.years = array(cnfGetIniValue(self.configFile, 'HazardInterface',
                                          'Years').split(',')).astype('f')
        self.minRecords = cnfGetIniValue(self.configFile, 'HazardInterface',
                                          'MinimumRecords',50)
        self.yrsPerSim = cnfGetIniValue(self.configFile, 'HazardInterface',
                                          'YearsPerSimulation',10)

        # Create dimensions for storing data:
        dimensions = {0:{'name':'years', 'values':self.years, 'dtype':'d', 'atts':{'long_name':'Return period','units':'years'} },
                      1:{'name':'lat', 'values':self.lat, 'dtype':'d', 'atts':{'long_name':'Latitude','units':'degrees_north'} },
                      2:{'name':'lon', 'values':self.lon, 'dtype':'d', 'atts':{'long_name':'Longitude','units':'degrees_east'} } }
        # Create variables:
        variables = {0:{'name':'loc','dims':('lat','lon'),
                        'values':array(self.nodata),'dtype':'d',
                        'atts':{'long_name':'Location parameter for GEV distribution',
                                'units':'m/s'} },
                     1:{'name':'scale','dims':('lat','lon'),
                        'values':array(self.nodata),'dtype':'d',
                        'atts':{'long_name':'Scale parameter for GEV distribution',
                                'units':''} },
                     2:{'name':'shp','dims':('lat','lon'),
                        'values':array(self.nodata),'dtype':'d',
                        'atts':{'long_name':'Shape parameter for GEV distribution',
                                'units':''} },
                     3:{'name':'wspd','dims':('years','lat','lon'),
                        'values':array(self.nodata),'dtype':'d',
                        'atts':{'long_name':'Return period wind speed',
                                'units':'m/s'} },
                     4:{'name':'wspd95','dims':('years','lat','lon'),
                        'values':array(self.nodata),'dtype':'d',
                        'atts':{'long_name':'95th percentile return period wind speed',
                                'units':'m/s'} },
                     5:{'name':'wspd05','dims':('years','lat','lon'),
                        'values':array(self.nodata),'dtype':'d',
                        'atts':{'long_name':'5th percentile return period wind speed',
                                'units':'m/s'} } }

        # Create output file for return-period gust wind speeds and GEV parameters
        self.nc_obj = nctools._ncSaveGrid(os.path.join(self.outputPath,'hazard.nc'),
                                          dimensions, variables, nodata=self.nodata,
                                          writedata=False,dtype='d',keepfileopen=True)

    def calculateWindHazard(self):
        """
        Calculate return wind speeds.
        """
        self.logger.info("Calculating return period wind speeds and GEV distribution parameters" )
        if self.calcCI:
            self.logger.info("Confidence intervals for return period wind speeds will also be calculated")
        x_start, x_end, y_start, y_end = self._return_subset_edges(self.imax - self.imin + 1,
                                                                   self.jmax - self.jmin + 1,
                                                                   x_step=20, y_step=20)

        # Calculate wind hazard in spatial subsets (to prevent memory overload)
        no_subsets = len(x_start)
        percent_complete_last = 0
        self.logger.info("Loading %d data files"%self.nsim)

        loc_varobj = self.nc_obj.variables['loc']
        scale_varobj = self.nc_obj.variables['scale']
        shp_varobj = self.nc_obj.variables['shp']
        windspd_varobj = self.nc_obj.variables['wspd']
        if self.calcCI:
            wspd95_varobj = self.nc_obj.variables['wspd95']
            wspd05_varobj = self.nc_obj.variables['wspd05']

        for k in range(no_subsets):
            i_lim = (self.imin + x_start[k], self.imin + x_end[k])
            j_lim = (self.jmin + y_start[k], self.jmin + y_end[k])
            Vr = self._loadData(i_lim, j_lim)
            Rp,loc2D,scale2D,shp2D = self._calculate(Vr)
            # Calculate confidence interval of return periods:
            if self.calcCI:
                Rp95,Rp05 = self._calculateCI(Vr)

            y1 = int(y_start[k])
            y2 = int(y_end[k] + 1)
            x1 = int(x_start[k])
            x2 = int(x_end[k] + 1)
            loc_varobj[y1:y2, x1:x2] = loc2D
            scale_varobj[y1:y2, x1:x2] = scale2D
            shp_varobj[y1:y2, x1:x2] = shp2D
            windspd_varobj[:, y1:y2, x1:x2] = Rp[:,:,:]
            if self.calcCI:
                wspd95_varobj[:, y1:y2, x1:x2] = Rp95[:,:,:]
                wspd05_varobj[:, y1:y2, x1:x2] = Rp05[:,:,:]

            # Report calculation progress
            percent_complete = int((k / float(no_subsets)) * 10) * 10
            self.pbar.update((k+1) / float(no_subsets))
            if percent_complete != percent_complete_last:
                self.logger.info("Calculating wind hazard: %d percent complete"%percent_complete)
                percent_complete_last = percent_complete

        self.logger.info("Calculating wind hazard: 100 percent complete")

        # Add data range attribute and close output file:
        setattr(windspd_varobj,'actual_range',[windspd_varobj[:].min(), windspd_varobj[:].max()])
        setattr(loc_varobj,'actual_range',[loc_varobj[:].min(), loc_varobj[:].max()])
        setattr(scale_varobj,'actual_range',[scale_varobj[:].min(), scale_varobj[:].max()])
        setattr(shp_varobj,'actual_range',[shp_varobj[:].min(), shp_varobj[:].max()])
        if self.calcCI:
            setattr(wspd95_varobj,'actual_range',[wspd95_varobj[:].min(), wspd95_varobj[:].max()])
            setattr(wspd05_varobj,'actual_range',[wspd05_varobj[:].min(), wspd05_varobj[:].max()])

        self.nc_obj.close()
        self.pbar.update(1.0)

    def _loadData(self, i_lim, j_lim):
        """
        Load all windfield data for each spatial subset into a 3-d array
        """
        Vr = empty((self.nsim, j_lim[1] - j_lim[0] + 1, i_lim[1] - i_lim[0] + 1), dtype='f')
        inputFileList = []
        i = 0

        while len(inputFileList) < self.nsim:
            inputFile = os.path.join(self.inputPath, self.fileList[i])
            if os.path.isfile(inputFile):
                inputFileList.append(inputFile)
                i += 1
            else:
                self.logger.warn("%s does not exist"%inputFile)
                i += 1
                sys.exit( )

        for n in range(self.nsim):
            Vr[n,:,:] = self._loadFile(inputFileList[n], i_lim, j_lim)
        return Vr

    def _loadFile(self, fileName, i_lim, j_lim):
        """
        Internal function to load windfield data from a file for a
        given spatial subset.
        """
        ncobj = nctools.ncLoadFile(fileName)
        ncobj_vmax = nctools.ncGetVar(ncobj, 'vmax')
        data_subset = ncobj_vmax[int(j_lim[0]):int(j_lim[1]+1), 
                                 int(i_lim[0]):int(i_lim[1]+1)]
        ncobj.close()
        return data_subset

    def _calculate(self, Vr):
        """
        Calculate the return period using a simple generalised extreme
        value distribution method.
        Input: array of years to calculate return periods for
        Output: Array of return period wind fields
        """
        Vr_dim = shape(Vr)
        Vr.sort(axis=0)
        Rp = self.nodata*ones((len(self.years), Vr_dim[1], Vr_dim[2]), dtype='f')
        loc2D = self.nodata*ones((Vr_dim[1], Vr_dim[2]), dtype='f')
        scale2D = self.nodata*ones((Vr_dim[1], Vr_dim[2]), dtype='f')
        shp2D = self.nodata*ones((Vr_dim[1], Vr_dim[2]), dtype='f')
        for i in range(Vr_dim[1]):
            for j in range(Vr_dim[2]):
                if Vr[:,i,j].max() > 0:
                    w,loc,scale,shp = evd.estimate_EVD(Vr[:,i,j], self.years,
                                                        self.nodata,self.minRecords,
                                                        self.yrsPerSim)
                    Rp[:,i,j] = w
                    loc2D[i,j] = loc
                    scale2D[i,j] = scale
                    shp2D[i,j] = shp
        return Rp, loc2D, scale2D, shp2D

    def _calculateCI(self, Vr,resamples=200):
        """
        Calculate the confidence interval of the return period using a
        simple generalised extreme value distribution method combined
        with bootstrap sampling.
        Input: array of years to calculate return periods for
        Output: Array of return period wind fields
        """
        #pdb.set_trace()
        Vr_dim = shape(Vr)
        #Vr.sort(axis=0)
        Rp95 = self.nodata*ones((len(self.years), Vr_dim[1], Vr_dim[2]), dtype='f')
        Rp05 = self.nodata*ones((len(self.years), Vr_dim[1], Vr_dim[2]), dtype='f')
        #loc2D = self.nodata*ones((Vr_dim[1], Vr_dim[2]), dtype='f')
        #scale2D = self.nodata*ones((Vr_dim[1], Vr_dim[2]), dtype='f')
        #shp2D = self.nodata*ones((Vr_dim[1], Vr_dim[2]), dtype='f')
        w = zeros((len(self.years),resamples),dtype='f')
        w95 = zeros((len(self.years)),dtype='f')
        w05 = zeros((len(self.years)),dtype='f')
        for i in range(Vr_dim[1]):
            for j in range(Vr_dim[2]):
                if Vr[:,i,j].max() > 0:
                    for n in range(resamples):
                        vn = array([random.choice(Vr[:,i,j]) for _ in Vr[:,i,j] ])
                        vn.sort()
                        w[:,n],loc,scale,shp = evd.estimate_EVD(vn, self.years,
                                                        self.nodata,self.minRecords,
                                                        self.yrsPerSim)
                    for n in range(len(self.years)):
                        w[n,:].sort()
                        w95[n] = percentile(w[n,:],95)
                        w05[n] = percentile(w[n,:],5)

                    Rp95[:,i,j] = w95
                    Rp05[:,i,j] = w05
        return Rp95, Rp05


    def _create_output_files(self, lat, lon):
        """
        Create netcdf output files for entering hazard data.
        Note: this step is required when processing with spatial subsets.
        """
        nc_objs = []
        for (i, y) in enumerate(self.years):
            ncFileName = os.path.join(self.outputPath, "v%d.nc"%(y))
            nc_objs.append(nctools.ncSaveGrid(ncFileName, lon, lat, array(self.nodata), 'windspd', 'm/s', nodata=self.nodata,
                                          writedata=False, keepfileopen=True))
        return nc_objs

    def _return_subset_edges(self, x_dim, y_dim, x_step=10, y_step=10):
        """
        Returns the indices required to subset a 2D array into smaller
        rectangular 2D arrays (of dimension x_step * y_step).  The function
        is used to prevent TCRM from exceeding the available memory when
        calculating wind hazard.
        """
        subset_maxcols = ceil(x_dim/float(x_step))
        subset_maxrows = ceil(y_dim/float(y_step))
        n_subsets = subset_maxcols * subset_maxrows
        x_start = zeros(n_subsets)
        x_end = zeros(n_subsets)
        y_start = zeros(n_subsets)
        y_end = zeros(n_subsets)
        k = 0

        for i in arange(subset_maxcols):
            for j in arange(subset_maxrows):
                x_start[k] = i*x_step
                x_end[k] = min((i+1)*x_step, x_dim)-1
                y_start[k] = j*y_step
                y_end[k] = min((j+1)*y_step, y_dim)-1
                k += 1
        return x_start.astype(int), x_end.astype(int), y_start.astype(int), y_end.astype(int)
