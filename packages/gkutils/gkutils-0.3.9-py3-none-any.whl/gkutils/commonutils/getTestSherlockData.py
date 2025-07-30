#!/usr/bin/env python
"""Cone Search against the big tables in the current Sherlock Database for a test list of objects.
The catalogue list should be comma separated with no spaces. Input file should be a (headed)
CSV of coordinates in decimal degrees.

Usage:
  %s <configFile> <inputCoordFile> <catalogueList> [--radius=<radius>]
  %s (-h | --help)
  %s --version

Options:
  -h --help                    Show this screen.
  --version                    Show version.
  --radius=<radius>            Match radius in arcsec [default: 360]

E.g.:
  %s config_pessto.yml /tmp/testObjects.csv tcs_cat_ps1_dr1,tcs_cat_gaia_dr2

  %s sherlock_databases.yml roys_test_data_sample.csv tcs_cat_2mass_psc_final,tcs_cat_gaia_dr1,tcs_cat_gaia_dr2,tcs_cat_guide_star_catalogue_v2_3,tcs_cat_ned_stream,tcs_cat_ps1_dr1,tcs_cat_ps1_ubercal_stars_v1,tcs_cat_sdss_photo_stars_galaxies_dr12 > sherlock_inserts.sql

"""
import sys
__doc__ = __doc__ % (sys.argv[0], sys.argv[0], sys.argv[0], sys.argv[0], sys.argv[0])
from docopt import docopt
import os, MySQLdb, shutil, re
from gkutils.commonutils import dbConnect, Struct, cleanOptions, readGenericDataFile, coords_sex_to_dec, CAT_ID_RA_DEC_COLS, coneSearchHTM, QUICK, FULL


# Add a few extra catalogues from ePESSTO+ crossmatch_catalogues table. Start at 5000 for catalogue ID.
CAT_ID_RA_DEC_COLS['tcs_cat_2mass_psc_final'] = [['id', 'ra', 'decl'],5000]
CAT_ID_RA_DEC_COLS['tcs_cat_gaia_dr1'] = [['id', 'ra', 'dec'],5001]
CAT_ID_RA_DEC_COLS['tcs_cat_gaia_dr2'] = [['source_id', 'ra', 'dec'],5002]
# Note that RightAsc and Declination are in RADIANS for tcs_cat_guide_star_catalogue_v2_3.
CAT_ID_RA_DEC_COLS['tcs_cat_guide_star_catalogue_v2_3'] = [['gsc1ID', 'RightAsc', 'Declination'],5003]
CAT_ID_RA_DEC_COLS['tcs_cat_ned_stream'] = [['ned_name', 'raDeg', 'decDeg', 'redshift'],5004]
CAT_ID_RA_DEC_COLS['tcs_cat_ps1_dr1'] = [['objID', 'raAve', 'decAve'],5005]
CAT_ID_RA_DEC_COLS['tcs_cat_ps1_ubercal_stars_v1'] = [['id', 'RA', 'Decl'],5006]
CAT_ID_RA_DEC_COLS['tcs_cat_sdss_photo_stars_galaxies_dr12'] = [['objID', 'ra', 'dec_'],5007]

# Some tables have "dec" for a column name. It's an SQL keyword and must be backquoted.
def decKey(key):
    if key == 'dec':
        return '`dec`'
    else:
        return key

def nullValue(value):
    if value is None:
        return 'NULL'
    elif not (isinstance(value, int) or isinstance(value, float) or isinstance(value, bool)):
        return ("'%s'" % str(value)) 
    else:
        return str(value)

def doMatch(options):
    import yaml
    with open(options.configFile) as yaml_file:
        config = yaml.load(yaml_file)

    username = config['databases']['catalogues']['username']
    password = config['databases']['catalogues']['password']
    database = config['databases']['catalogues']['database']
    hostname = config['databases']['catalogues']['hostname']

    conn = dbConnect(hostname, username, password, database)
    if not conn:
        print ("Cannot connect to the database")
        return 1

    coords = readGenericDataFile(options.inputCoordFile, delimiter=',')

    queryDict = {}
    for catalogue in options.catalogueList.split(','):

        for row in coords:
            message, results = coneSearchHTM(float(row['ra']), float(row['dec']), float(options.radius), catalogue, queryType = FULL, conn = conn)
            if len(results) > 0:
                for r in results:
                    cols = r[1].keys()
                    vals = r[1].values()
                    sql = "INSERT IGNORE INTO %s (%s) VALUES (%s);" % (catalogue, ",".join([decKey(c) for c in cols]), ",".join([nullValue(x) for x in vals]))
                    print(sql)

    conn.close ()


def main(argv = None):
    opts = docopt(__doc__, version='0.1')
    opts = cleanOptions(opts)

    # Use utils.Struct to convert the dict into an object for compatibility with old optparse code.
    options = Struct(**opts)



    doMatch(options)



if __name__=='__main__':
    main()

