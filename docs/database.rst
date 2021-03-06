===============
Hazard database
===============

To make it easier to acess hazard data, and to enable users to link an event to a return period wind speed, TCRM stores information on the individual events, the wind speeds they generate at a set of locations, and the return levels calculated in the :mod:`hazard` module. 

The database is built on the :mod:`sqlite3` module that is part of the standard Python library. Extension to a spatial database system has been identified as an enhancement for future development.

Locations table
---------------

The locations table (*tblLocations*) stores the details of the locations within the model domain. This table has been derived from a (global) listing of WMO-identified weather stations. 

.. tabularcolumns:: |l|c|p{5cm}|
+-------------+----------------------------------+------------+
| Field name  | Field description                | Field type |
+=============+==================================+============+
| locId       | Unique identifier for the        | Text       |
|             | location.                        |            |
+-------------+----------------------------------+------------+
| locName     | Name of the location.            | Text       |
+-------------+----------------------------------+------------+
| locLon      | Longitude of the location, given | Real       |
|             | in geographic coordinates.       |            |
+-------------+----------------------------------+------------+
| locLat      | Latitude of the location, given  | Real       |
|             | in geographic coordinates.       |            |
+-------------+----------------------------------+------------+
| locElev     | Elevation of the location        | Real       |
|             | (in metres)                      |            |
+-------------+----------------------------------+------------+
| locCountry  | Country of the location          | Text       |
+-------------+----------------------------------+------------+
