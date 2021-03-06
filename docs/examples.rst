Examples
========

Full TCRM hazard simulation
---------------------------

An example configuration file is provided with the code to provide
users a starting point for testing the installation, and for setting
up their own simulation. The example simulation is centred on Port
Hedland, Australia (118.6E, 20.3S), which has experienced numerous
severe tropical cyclones.

Once the model has been :ref:`installed <installation>` and tested,
the example simulation can be run as follows::
    
    $ python tcrm.py -c example/port_hedland.ini

The model will automatically create output folders to store the
results in, as well as a log file that provides details on the
progress of the model. The simulation will process the input track
database (IBTrACS v03r05), run the statistical interface, generate
1000 simulated years of TC events, the wind swaths associated with
those simulated years, calculate the hazard (return period wind
speeds) for the region and plot the output as maps and a return period
curve for Port Hedland. The hazard data are also stored in netCDF
(version 4) files.

.. figure:: hazard_example.png
     :align: center
     :alt: 100-year return period wind speed near Port Hedland,
           Australia.
     :figclass: align-center

     100-year return period wind speed near Port Hedland,
     Australia. Wind speeds represent a 3-second gust wind speed, 10
     metres above ground level in open, flat terrain.

.. figure:: hazard_curve.png
    :align: center
    :alt: Example hazard curve for Port Hedland, Australia.
    :figclass: align-center
    
    Hazard curve for Port Hedland, Australia, based on 1000 years of
    synthetic tropical cyclone events. The grey shading indicates the
    90th percentile range, based on a bootstrap resampling procedure.

Running in an MPI environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
For a multiprocessor environment using MPI and Pypar, the example can
be run with::

    $ mpirun -np 16 python tcrm.py -c example/port_hedland.ini

This will execute TCRM across 16 CPUs (if available). 

TCRM has been tested on systems up to 256 CPUs. Testing with moderate
event sets (4000 events) indicate > 23 times speedup when run across
32 CPUs.

Scenario simulation
-------------------

An example scenario is also included with the code to demonstrate an
individual event simulation. This uses Tropical Cyclone *Tracy*, which
impacted Darwin, Australia in 1974. The example simulation uses the
best track data captured in the IBTrACS dataset, with the radius to
maximum winds sourced from JTWC. TC *Tracy* struck Darwin early on
Christmas Morning (1974), and resulted in 68 deaths and the largest
peacetime evacuation of a city in Australia's history. A more detailed
simulation of TC Tracy using TCRM is given in Schofield *et al.*
(2009).


