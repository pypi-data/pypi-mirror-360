#!/usr/bin/env python
"""Is object in the list of ATLAS exposures?

Usage:
  %s <atlasCentresFile> <inputCoordsFile> [--searchradius=<searchradius>] [--footprints] [--red] [--checkmjd] [--mjdtolerance=<mjdtolerance>] [--debug] [--auxparams=<auxparams>]
  %s (-h | --help)
  %s --version

Options:
  -h --help                       Show this screen.
  --version                       Show version.
  --searchradius=<searchradius>   Cone search radius in degrees. [default: 3.86]
  --footprints                    Give me the ATLAS footprints that overlap this RA and Dec. (Otherwise do a cone search.)
  --red                           Give me the full ATLAS reduced file locations.
  --checkmjd                      Only return exposures with MJDs within mjdtolerance.
  --mjdtolerance=<mjdtolerance>   Compare footprint MJD with input MJD (days). [default: 1.0]
  --auxparams=<auxparams>         Spit out some auxiliary parameters from the ATLAS exposures list. Comma separated. No spaces. Ignored if not present.
  --debug                         Spit out some debug.


Example:
   %s all_atlas_exposures.tst eris_coordinates_and_mjds.csv
   %s all_atlas_exposures.tst eris_coordinates_and_mjds.csv --checkmjd
   %s all_atlas_exposures.tst eris_coordinates_and_mjds.csv --checkmjd --red
   %s all_atlas_exposures.tst eris_coordinates_and_mjds.csv --checkmjd --red --footprints
   %s all_atlas_exposures.tst eris_coordinates_and_mjds.csv --checkmjd --red --footprints --mjdtolerance=0.5
   %s ~/atlas/volume_limited_survey/all_co_exposures_20210520_mjd_58940_58969.tst ~/atlas/volume_limited_survey/FakerPositions_10.lis --auxparams=mag5sig --footprints

"""
import sys
__doc__ = __doc__ % (sys.argv[0], sys.argv[0], sys.argv[0], sys.argv[0], sys.argv[0], sys.argv[0], sys.argv[0], sys.argv[0], sys.argv[0])
from docopt import docopt
import os, shutil, re
from gkutils.commonutils import Struct, cleanOptions, readGenericDataFile, coords_sex_to_dec, bruteForceGenericConeSearch, isObjectInsideATLASFootprint

atlas_regex = '(0[1234]a)([56][0-9]{4})o([0-9]{4})([A-Za-z])'
atlas_regex_compiled = re.compile(atlas_regex)


def doRegexMatch(expname):
    match = None
    reSearch = atlas_regex_compiled.search(expname)
    if reSearch:
        camera = reSearch.group(1)
        mjd = reSearch.group(2)
        expno = reSearch.group(3)
        filt = reSearch.group(4)
        match = {}
        match['camera'] = camera
        match['mjd'] = mjd
        match['expno'] = expno
        match['filt'] = filt
    return match

def main(argv = None):
    opts = docopt(__doc__, version='0.1')
    opts = cleanOptions(opts)

    # Use utils.Struct to convert the dict into an object for compatibility with old optparse code.
    options = Struct(**opts)

    auxparams = []
    if options.auxparams:
        auxparams = options.auxparams.split(',')

    atlasCentres = readGenericDataFile(options.atlasCentresFile, delimiter='\t')
    atlasRowLen = len(atlasCentres[0].keys())
    inputCoords = readGenericDataFile(options.inputCoordsFile, delimiter=',')

    radius = 3.86
    try:
        radius = float(options.searchradius)

    except ValueError as e:
        pass

    if options.footprints:
        for row in inputCoords:
            if options.debug:
                print(row)
            try:
                ra = float(row['ra'])
                dec = float(row['dec'])
            except ValueError as e:
                ra, dec = coords_sex_to_dec(row['ra'], row['dec'])

            for r in atlasCentres:
                if isObjectInsideATLASFootprint(ra, dec, float(r['ra']), float(r['dec'])):
                    if options.checkmjd:
                        if abs(float(r['mjd']) - float(row['mjd'])) < float(options.mjdtolerance):
                            matches = doRegexMatch(r['expname'])
                            if matches:
                                red = ''
                                if options.red:
                                    red = '/atlas/red/' + matches['camera'] + '/' + matches['mjd'] + '/' + r['expname'] + '.fits.fz'
                                    print(row['name'], red)
                                else:
                                    print(row['name'], r['expname'])
                            else:
                                print(row['name'], r['expname'])

                    else:
                        matches = doRegexMatch(r['expname'])
                        if matches:
                            red = ''
                            if options.red:
                                red = '/atlas/red/' + matches['camera'] + '/' + matches['mjd'] + '/' + r['expname'] + '.fits.fz'
                                print(row['name'], red)
                            else:
                                try:
                                    if len(auxparams) > 0:
                                        print(row['name'], r['expname'], end = " ")
                                        for param in auxparams:
                                            print(r[param], end = " ")
                                        print()
                                    else:
                                        print(row['name'], r['expname'])
                                except KeyError as e:
                                    print()
                                    #print(row['name'], r['expname'])
                        else:
                            print(row['name'], r['expname'])


    else:
        for row in inputCoords:
            if options.debug:
                print(row)
            try:
                ra = float(row['ra'])
                dec = float(row['dec'])
            except ValueError as e:
                ra, dec = coords_sex_to_dec(row['ra'], row['dec'])

            header, results = bruteForceGenericConeSearch(options.atlasCentresFile, [[ra, dec]], radius*3600.0, raIndex = 'ra', decIndex = 'dec')
            for r in results:
                if options.checkmjd:
                    exps = r.split()
                    if abs(float(exps[3]) - float(row['mjd'])) < float(options.mjdtolerance):
                        matches = doRegexMatch(exps[0])
                        if matches:
                            red = ''
                            if options.red:
                                red = '/atlas/red/' + matches['camera'] + '/' + matches['mjd'] + '/' + exps[0] + '.fits.fz'
                                print (row['name'], red, "%.2f" % (float(exps[atlasRowLen+1])/3600.0))
                            else:
                                print (row['name'], exps[0], "%.2f" % (float(exps[atlasRowLen+1])/3600.0))
                        else:
                            print (row['name'], exps[0], "%.2f" % (float(exps[atlasRowLen+1])/3600.0))
                else:
                    exps = r.split()
                    matches = doRegexMatch(exps[0])
                    if matches:
                        red = ''
                        if options.red:
                            red = '/atlas/red/' + matches['camera'] + '/' + matches['mjd'] + '/' + exps[0] + '.fits.fz'
                            print (row['name'], red, "%.2f" % (float(exps[atlasRowLen+1])/3600.0))
                        else:
                            print (row['name'], exps[0], "%.2f" % (float(exps[atlasRowLen+1])/3600.0))
                    else:
                        print (row['name'], exps[0], "%.2f" % (float(exps[atlasRowLen+1])/3600.0))


if __name__=='__main__':
    main()
    
