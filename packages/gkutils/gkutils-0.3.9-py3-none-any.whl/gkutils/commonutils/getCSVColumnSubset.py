"""Write a subset of keys from one CSV to another. Don't use lots of memory.

Usage:
  %s <filename> <outputfile> [--columns=<columns>] [--htm] [--racol=<racol>] [--deccol=<deccol>] [--filtercol=<filtercol>]
  %s (-h | --help)
  %s --version

Options:
  -h --help                    Show this screen.
  --version                    Show version.
  --columns=<columns>          Comma separated (no spaces) columns.
  --htm                        Generate HTM IDs and add to the column subset.
  --racol=<racol>              RA column, ignored if htm not specified [default: ra]
  --deccol=<deccol>            Declination column, ignored if htm not specified [default: dec]
  --filtercol=<filtercol>      Only write the row when this column is not blank.

"""
import sys
__doc__ = __doc__ % (sys.argv[0], sys.argv[0], sys.argv[0])
from docopt import docopt
from gkutils.commonutils import Struct, readGenericDataFile, cleanOptions
import csv
from gkhtm._gkhtm import htmName


def getColumnSubset(options):
    # DictReader doesn't burden the memory - so let's use it to select our column subset.
    data = csv.DictReader(open(options.filename), delimiter=',')

    columns = options.columns.split(',')
    if options.htm:
        columns.append('htm10')
        columns.append('htm13')
        columns.append('htm16')

    with open(options.outputfile, 'w') as f:
        w = csv.DictWriter(f, columns, delimiter = ',')
        w.writeheader()
        for row in data:

            # TO FIX - code is very inefficient. HTMs generated regardless of filtercol. Silly!
            trimmedRow = {key: row[key] for key in options.columns.split(',')}
            if options.htm:
                htm16Name = htmName(16, float(row[options.racol]), float(row[options.deccol]))
                trimmedRow['htm10'] = htm16Name[0:12]
                trimmedRow['htm13'] = htm16Name[12:15]
                trimmedRow['htm16'] = htm16Name[15:18]

            try:
                if options.filtercol:
                    if trimmedRow[options.filtercol] and trimmedRow[options.filtercol] != 'null':
                        w.writerow(trimmedRow)
                else:
                    w.writerow(trimmedRow)
            except KeyError as e:
                w.writerow(trimmedRow)

    return

def main(argv = None):
    opts = docopt(__doc__, version='0.1')
    opts = cleanOptions(opts)

    # Use utils.Struct to convert the dict into an object for compatibility with old optparse code.
    options = Struct(**opts)

    getColumnSubset(options)


if __name__ == '__main__':
    main()

