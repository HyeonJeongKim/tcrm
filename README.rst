The Tropical Cyclone Risk Model
===============================

The **Tropical Cyclone Risk Model** is a stochastic tropical cyclone
model developed by `Geoscience Australia <http://www.ga.gov.au>`_ for
estimating the wind hazard from tropical cyclones.

Due to the relatively short record of quality-controlled, consistent
tropical cyclone observations, it is difficult to estimate average
recurrence interval wind speeds ue to tropical cyclones. To overcome
the restriction of observed data, TCRM uses an autoregressive model to
generate thousands of years of events that are statistically similar
to the historical record. To translate these events to estimated wind
speeds, TCRM applies a parametric windfield and boundary layer model
to each event. Finally an extreme value distribution is fitted to the
aggregated windfields at each grid point in the model domain to
provide ARI wind speed estimates.


Features
--------
* **Multi-platform**: TCRM can run on desktop machines through to massively-parallel systems (tested on Windows XP/Vista/7, \*NIX);
* **Multiple options for wind field & boundary layer models**: A number of radial profiles and simple boundary layer models have been included to allow users to test sensitivity to these options.
* **Globally applicable**: Users can set up a domain in any TC basin in the globe. The model is not tuned to any one region of the globe. Rather, the model is designed to draw sufficient information from best-track archives;
* **Evaluation metrics**: Offers capability to run objective evaluation of track model metrics (e.g. landfall rates);
* **Single scenarios**: Users can run a single TC event (e.g. using a b-deck format track file) at high temporal resolution and extract time series data at chosen locations;

Branch
------

This development branch (`visuals`) is developing the visualisations
of output (statistical and hazard levels).

**NOTE**: Because some dependencies are built only for Python 2.7,
 this branch is not backward compatible with Python 2.6.

Dependencies
------------

TCRM requires:

 * `Python 2.7 <https://www.python.org/>`_;
 * `numpy <http://www.numpy.org/>`_; 
 * `scipy <http://www.scipy.org/>`_;
 * `matplotlib 1.4.3 <http://matplotlib.org/>`_; 
 * `Basemap 1.0.8 <http://matplotlib.org/basemap/index.html>`_; 
 * `netcdf4-python <https://code.google.com/p/netcdf4-python/>`_; 
 * `pandas <http://pandas.pydata.org/>`_; 
 * `Shapely <https://github.com/Toblerity/Shapely>`_; 
 * `seaborn 0.5.1 <http://stanford.edu/~mwaskom/software/seaborn/index.html>`_;
 * and `gcc`.  

For parallel execution, `Pypar <http://github.com/daleroberts/pypar>`_ is required;

Status
------

.. image:: https://travis-ci.org/GeoscienceAustralia/tcrm.svg?branch=visuals
    :target: https://travis-ci.org/GeoscienceAustralia/tcrm
    :alt: Build status


.. image:: https://coveralls.io/repos/GeoscienceAustralia/tcrm/badge.svg?branch=visuals
  :target: https://coveralls.io/r/GeoscienceAustralia/tcrm?branch=visuals
  :alt: Test coverage

    
.. image:: https://landscape.io/github/GeoscienceAustralia/tcrm/visuals/landscape.svg?style=flat
    :target: https://landscape.io/github/GeoscienceAustralia/tcrm/visuals
    :alt: Code Health

Contributing to TCRM
--------------------

If you would like to take part in TCRM development, take a look at `docs/contributing.rst <https://giihub.com/GeoscienceAustralia/tcrm/blob/master/docs/contributing.rst>`_.

License information
-------------------

See the file `LICENSE.rst <https://github.com/GeoscienceAustralia/tcrm/blob/master/LICENCE.rst>`_ 
for information on the history of this software, terms and conditions for usage, 
and a DISCLAIMER OF ALL WARRANTIES.

Screenshot
----------

.. image:: https://rawgithub.com/GeoscienceAustralia/tcrm/master/docs/screenshot.png
