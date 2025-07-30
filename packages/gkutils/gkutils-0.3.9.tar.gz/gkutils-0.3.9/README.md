# gkutils Package #

A collection of useful python methods (some of which should now be replaced by astropy usage), along with some command line utilities.

The command line utilities are:

* coneSearchCassandra (a tool for cone searching inside spatially indexed Cassandra repositories - requires gkhtm and cassandra-driver and access to a Cassandra table with HTM levels 10, 13 and 16 columns.)
* bruteForceConeSearchATLAS (a purely trigonometric tool for searching ATLAS exposure lists to check if they overlap an object of interest)
* getCSVColumnSubset (pull out a subset of colums from a CSV).

There are more potential command line utilities, which will be made available in future versions - e.g. coneSearchMySQL.

