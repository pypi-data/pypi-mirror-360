"""Query cassandra by RA and dec. The coords variable should be RA and dec, comma separated with NO SPACE. (To facilitate negative declinations.)

Usage:
  %s <configFile> <coords> [--radius=<radius>] [--coordsfromfile] [--saveresults] [--resultslocation=<resultslocation>] [--number=<number>] [--table=<table>] [--namecolumn=<namecolumn>] [--querycolumns=<querycolumns>] [--nprocesses=<nprocesses>] [--loglocation=<loglocation>] [--logprefix=<logprefix>] [--coldate=<coldate>] [--colmag=<colmag>] [--colmagerr=<colmagerr>] [--colfilter=<colfilter>] [--colra=<colra>] [--coldec=<coldec>] [--colexpname=<colexpname>]

  %s (-h | --help)
  %s --version

Options:
  -h --help                             Show this screen.
  --version                             Show version.
  --coordsfromfile                      Treat the coordinates parameter as a file of coordinates.
  --radius=<radius>                     Cone search radius in arcsec [default: 2].
  --saveresults                         If set, store the results in a file whose prefix starts with this.
  --resultslocation=<resultslocation>   If saveresults is set, store the results in this directory [default: /tmp].
  --number=<number>                     If set and is smaller than the total list, choose a random subset.
  --table=<table>                       Table to search [default: atlas_detections].
  --namecolumn=<namecolumn>             If set, choose this as the name of the result file. Otherwise lc_pid_0000001.csv, etc [default: source_id].
  --querycolumns=<querycolumns>         Grab the selected colums, comma separated, no spaces - instead of everything. Could speed up queries.
  --nprocesses=<nprocesses>             Number of processes to use by default to get/write the results [default: 1]
  --loglocation=<loglocation>           Log file location [default: /tmp/].
  --logprefix=<logprefix>               Log prefix [default: coneSearch].
  --coldate=<coldate>                   The column that represents date [default: mjd].
  --colmag=<colmag>                     The column that represents mag [default: m].
  --colmagerr=<colmagerr>               The column that represents mag error [default: dminst].
  --colfilter=<colfilter>               The column that represents the filter [default: filter].
  --colra=<colra>                       The column that represents the RA [default: ra].
  --coldec=<coldec>                     The column that represents the declination [default: dec].
  --colexpname=<colexpname>             The column that represents the exposure name OR (e.g.) objectId [default: expname].

E.g.
  %s ~/config_cassandra.yaml /tmp/coords.txt --coordsfromfile --table=atlasdophot --nprocesses=4 --number=16 --saveresults
  %s ~/config_cassandra_atlas.yaml 272.40279,-9.97105
  %s ~/config_cassandra_atlas.yaml ~atls/galactic_centre_all_gaia_objects_2degrees_ra_dec_mag_12_19.txt --coordsfromfile --table=atlas_detections --nprocesses=32 --number=10000 --saveresults --resultslocation=/tmp/atlas_lightcurves
  %s ~/config_cassandra.yaml 309.5032775,74.6050893 --table=htmcandidates --coldate=jd --colmag=magpsf --colmagerr=sigmapsf --colfilter=fid --colexpname=objectId
  %s /home/ubuntu/config.yaml /var/lib/cassandra/test/unique_objects_100000_mean_coords.txt --coordsfromfile --table=htmcandidates --coldate=jd --colmag=magpsf --colmagerr=sigmapsf --colfilter=fid --colexpname=objectid --number=1000 --nprocesses=16 --saveresults --resultslocation=/home/ubuntu/coneresults --namecolumn=objectid --querycolumns=objectid,jd,magpsf,sigmapsf,fid,ra,dec
                            

"""
import sys
__doc__ = __doc__ % (sys.argv[0], sys.argv[0], sys.argv[0], sys.argv[0], sys.argv[0], sys.argv[0], sys.argv[0], sys.argv[0])
from docopt import docopt
from gkutils.commonutils import Struct, readGenericDataFile, cleanOptions, parallelProcess, splitList

from gkutils.commonutils import coneSearchHTMCassandra
from cassandra.cluster import Cluster
from cassandra.query import dict_factory
import random
import csv
from datetime import datetime
import os


def getLCData(options, session, coordslist):
    table = options.table
    radius = float(options.radius)

    columns = None
    if options.querycolumns:
        columns = options.querycolumns.strip().split(',')

    counter = 0
    for c in coordslist:
        data = coneSearchHTMCassandra(session, c['ra'], c['dec'], radius, table, refineResults = True, columns = columns)
        if data:
            if options.saveresults:
                try:
                    filename = options.resultslocation + '/' + c[options.namecolumn] + '.csv'
                except KeyError as e:
                    filename = options.resultslocation + '/' + 'lc_%d_%07d.csv' % (os.getpid(), counter)
                with open(filename, 'w') as f:
                    w = csv.DictWriter(f, data[0].keys(), delimiter = ',')
                    w.writeheader()
                    for row in data:
                        w.writerow(row)
            else:
                for row in data:

                    #print (row)
                    print (row[options.coldate], "%.2f" % row[options.colmag], "%.2f" % row[options.colmagerr], row[options.colfilter], "%.6f" % row[options.colra], "%.6f" % row[options.coldec], row[options.colexpname])
        # Counter gets incremented regardless of whether there is a result. Means we can
        # map the result number to the input coordinates.
        counter += 1



def worker(num, db, coordslistFragment, dateAndTime, firstPass, miscParameters):
    """thread worker function"""
    # Redefine the output to be a log file.
    options = miscParameters[0]

    pid = os.getpid()
    sys.stdout = open('%s%s_%s_%d_%d.log' % (options.loglocation, options.logprefix, dateAndTime, pid, num), "w")
    cluster = Cluster(db['hostname'])
    session = cluster.connect()
    session.row_factory = dict_factory
    session.set_keyspace(db['keyspace'])


    # This is in the worker function
    getLCData(options, session, coordslistFragment)

    print("Process complete.")
    cluster.shutdown()
    print("Connection Closed - exiting")

    return 0



def main(argv = None):
    opts = docopt(__doc__, version='0.1')
    opts = cleanOptions(opts)

    # Use utils.Struct to convert the dict into an object for compatibility with old optparse code.
    options = Struct(**opts)

    #keyspace = 'atlas'
    #host = ['db0', 'db1', 'db2', 'db3', 'db4']
    
    # random star
    #ra = 83.20546
    #dec = -20.70055
    
    # ATLAS17nij
    #ra = 82.46704
    #dec = -19.52058
    
    # ATLAS20biio
    #ra = 83.24691
    #dec = -19.11739
    
    # ATLAS20bbio - very good!!
    #ra = 81.27903
    #dec = -21.24643
    
    # ATLAS18vre
    #ra = 84.19551
    #dec = -22.41100
    
    # ATLAS19bdbm
    #ra = 85.10436
    #dec = -18.09766
    
    # ATLAS20bbff
    #ra = 86.52075
    #dec = -23.56601
    
    # ATLAS20ymv - THIS IS the CENTRE OBJECT. We did a 10 degree sweep around this.
    #ra = 74.55677
    #dec = -20.35753
    
    # ATLAS17lvn - bright foreground star
    #ra = 68.75953
    #dec = -14.22797
    
    import yaml
    with open(options.configFile) as yaml_file:
        config = yaml.safe_load(yaml_file)

    username = config['cassandra']['local']['username']
    password = config['cassandra']['local']['password']
    keyspace = config['cassandra']['local']['keyspace']
    hostname = config['cassandra']['local']['hostname']

    db = {'username': username,
          'password': password,
          'keyspace': keyspace,
          'hostname': hostname}

    coordslist = []

    if options.coordsfromfile:
        coordslist = readGenericDataFile(options.coords, delimiter=',')
    else:
        coordslist.append({'ra': options.coords.split(',')[0], 'dec': options.coords.split(',')[1]})
    
    if options.number and int(options.number) < len(coordslist):
        coordslist = random.sample(coordslist, int(options.number))

    if int(options.nprocesses) > 1 and len(coordslist) > 1:
        # Do it in parallel!
        currentDate = datetime.now().strftime("%Y:%m:%d:%H:%M:%S")
        (year, month, day, hour, min, sec) = currentDate.split(':')
        dateAndTime = "%s%s%s_%s%s%s" % (year, month, day, hour, min, sec)
        nProcessors, listChunks = splitList(coordslist, bins = int(options.nprocesses), preserveOrder=True)
    
        print("%s Parallel Processing..." % (datetime.now().strftime("%Y:%m:%d:%H:%M:%S")))
        parallelProcess(db, dateAndTime, nProcessors, listChunks, worker, miscParameters = [options], drainQueues = False)
        print("%s Done Parallel Processing" % (datetime.now().strftime("%Y:%m:%d:%H:%M:%S")))
    else:
        cluster = Cluster(db['hostname'])
        session = cluster.connect()
        session.row_factory = dict_factory
        session.set_keyspace(db['keyspace'])

        getLCData(options, session, coordslist)

        cluster.shutdown()

if __name__ == '__main__':
    main()

