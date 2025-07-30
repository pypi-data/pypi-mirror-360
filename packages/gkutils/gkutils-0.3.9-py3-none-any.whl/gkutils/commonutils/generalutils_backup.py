# encoding: utf-8
"""
*General utilities file.*

:Author:
    Ken W. Smith
"""

# Utilities file.  The following import are used so often I've placed them at
# the top of the file.  Other imports are executed only when needed.

import time
import os, sys
from datetime import datetime
import math
import warnings
import re
from operator import itemgetter
from functools import reduce

warnings.filterwarnings('ignore', '.*the sets module is deprecated.*', DeprecationWarning, 'MySQLdb')

FLAGS = {'orphan':          1,
         'variablestar':    2,
         'nt':              4,
         'agn':             8,
         'sn':             16,
         'miscellaneous':  32,
         'tde':            64,
         'lens':          128,
         'mover':         256,
         'bright':        512,
         'kepler':       1024}


def dbConnect(lhost, luser, lpasswd, ldb, lport=3306, quitOnError=True):
    """Create a MySQL database connection.

    Args:
        lhost: hostname
        luser: username
        lpasswd: password
        ldb: database name
        lport: port if not the default one
        quitOnError:

    Returns:
        conn: A database connection object
    """
    import MySQLdb

    try:
        conn = MySQLdb.connect (host = lhost,
                                user = luser,
                              passwd = lpasswd,
                                  db = ldb,
                                port = lport)
    except MySQLdb.Error as e:
        print("Error %d: %s" % (e.args[0], e.args[1]))
        if quitOnError:
            sys.exit (1)
        else:
            conn=None

    return conn

# 2014-07-29 KWS Setup a Logger. Fed up with trawling through print files!! Based on Dave's code.

def setupLogger(yamlConfigFile):
    """Create a Logger object.

    Args:
        yamlConfigFile: The YAML config file

    Returns:
        logger: A logger object
    """
    import logging
    import logging.config
    import yaml

    # IMPORT CUSTOM HANDLER THAT ALLOWS GROUP WRITING
    #handlers.GroupWriteRotatingFileHandler = GroupWriteRotatingFileHandler

    stream = file(yamlConfigFile, 'r')
    yamlContent = yaml.load(stream)
    stream.close()

    # use the logging settings section of the dictionary file if there is one
    # - otherwise assume the file contains only logging settings
    if "logging settings" in yamlContent:
        yamlContent = yamlContent["logging settings"]
        yamlContent["version"] = 1

    logging.config.dictConfig(yamlContent) # Python 2.7-ism.

    logger = logging.getLogger(__name__)

    return logger


def getDSS2Image (ra, dec, x, y):
    """Old code to get a DSS2 Image.

    Args:
        ra:
        dec:
        x:
        y:

    Returns:
        soup: A BeautifulSoup object
    """
    from BeautifulSoup import BeautifulSoup
    import urllib.request, urllib.error, urllib.parse
    import urllib.request, urllib.parse, urllib.error
    import urllib.parse

    baseurl = 'http://archive.eso.org'
    url = baseurl + '/dss/dss/image'
    values = {'ra' : ra,
              'dec' : dec,
              'name' : '',
              'x' : x,
              'y' : y,
              'Sky-Survey' : 'DSS-2-red',
              'equinox' : 'J2000' }

    data = urllib.parse.urlencode(values)
    req = urllib.request.Request(url, data)
    response = urllib.request.urlopen(req)
    the_page = response.read()
    soup = BeautifulSoup(BeautifulSoup(the_page).prettify())
    for a in soup.findAll('a'):
        if not a['href'].startswith("http"):
           a['href'] = urllib.parse.urljoin(baseurl, a['href'])

    for img in soup.findAll('img'):
        if not img['src'].startswith("http"):
           img['src'] = urllib.parse.urljoin(baseurl, img['src'])

    return soup


def bin(x, digits=0):
    """Get the binary for a decimal input.

    Args:
        x: Decimal input
        digits: Number of digits for padding.

    Returns:
        A binary string, padded if necessary.
    """
    # 2020-10-13 KWS Python 3 returns octal numbers with a prefix of 'o'. Need to remove this.
    oct2bin = ['000','001','010','011','100','101','110','111']
    binstring = [oct2bin[int(n)] for n in oct(x).replace('L','').replace('o','')]
    return ''.join(binstring).lstrip('0').zfill(digits)


# 2015-03-18 KWS Added ability to add extra decimal places of precision
#               (min = 2, max = 4)
#               Note - do NOT use 'round' function. This creates a whole
#               world of pain of having to propagate the rounding upwards
#               through the coordinate.  You want accuracy - just request
#               more digits.
def ra_to_sex (ra, delimiter = ':', decimalPlaces = 2):
   """Decimal RA to Sexagesimal converter.

   Args:
        ra: Right Ascension
        delimiter: Optional delimiter - assumed to be colon by default
        decimalPlaces: Number of decimal places to calculate onto returned result.

   Returns:
        RA string in sexagesimal
   """

   if decimalPlaces < 2:
      decimalPlaces = 2

   if decimalPlaces > 4:
      decimalPlaces = 4

   accuracy = 10**decimalPlaces

   # Calculation from Decimal Degrees:
   # 2013-09-17 KWS We're getting occasional RAs with negative values.
   #                I've assumed that we can just add 360.0 to these.

   if ra < 0.0:
      ra = ra + 360.0

   ra_hh   = int(ra/15)
   ra_mm   = int((ra/15 - ra_hh)*60)
   ra_ss   = int(((ra/15 - ra_hh)*60 - ra_mm)*60)
   ra_ff  = int((((ra/15 - ra_hh)*60 - ra_mm)*60 - ra_ss)*accuracy)

   return ('%02d' %ra_hh + delimiter + '%02d' %ra_mm + delimiter + '%02d' %ra_ss + '.' + '%0*d' % (decimalPlaces, ra_ff))


# 2015-03-18 KWS Added ability to add extra decimal places of precision
#               (min = 1, max = 3)
#               Note - do NOT use 'round' function. This creates a whole
#               world of pain of having to propagate the rounding upwards
#               through the coordinate.  You want accuracy - just request
#               more digits.
def dec_to_sex (dec, delimiter = ':', decimalPlaces = 1):
   """dec_to_sex.

   Args:
        dec:
        delimiter:
        decimalPlaces:
   """

   if decimalPlaces < 1:
      decimalPlaces = 1

   if decimalPlaces > 3:
      decimalPlaces = 3

   accuracy = 10**decimalPlaces

   if (dec >= 0):
      hemisphere = '+'
   else:
      # Unicode minus sign - should be treated as non-breaking by browsers
      hemisphere = '-'
      dec *= -1

   dec_deg = int(dec)
   dec_mm  = int((dec - dec_deg)*60)
   dec_ss  = int(((dec - dec_deg)*60 - dec_mm)*60)
   dec_f  = int(((((dec - dec_deg)*60 - dec_mm)*60) - dec_ss)*accuracy)

   return (hemisphere + '%02d' %dec_deg + delimiter + '%02d' %dec_mm + delimiter + '%02d' %dec_ss + '.' + '%0*d' % (decimalPlaces, dec_f))


def coords_dec_to_sex (ra, dec, delimiter = ':', decimalPlacesRA = 2, decimalPlacesDec = 1):
   """coords_dec_to_sex.

   Args:
        ra:
        dec:
        delimiter:
        decimalPlacesRA:
        decimalPlacesDec:
   """

   return(ra_to_sex(ra,delimiter, decimalPlaces = decimalPlacesRA), dec_to_sex(dec,delimiter, decimalPlacesDec))


# 2015-03-18 KWS Added N and E offset calculator (thanks Dave)
def getOffset(ra1, dec1, ra2, dec2):
   '''Work out N-S, E-W separations (object 1 relative to 2)'''

   if ':' in str(ra1):
      ra1 = sexToDec(ra1, ra=True)
   if ':' in str(dec1):
      dec1 = sexToDec(dec1, ra=False)
   if ':' in str(ra2):
      ra2 = sexToDec(ra2, ra=True)
   if ':' in str(dec2):
      dec2 = sexToDec(dec2, ra=False)

   # 2013-10-20 KWS Always make sure that the ra and dec values are floats

   ra1 = float(ra1)
   ra2 = float(ra2)
   dec1 = float(dec1)
   dec2 = float(dec2)

   north = -(dec1 - dec2) * 3600.0
   east = -(ra1 - ra2) * math.cos(math.radians((dec1 + dec2)) / 2.) * 3600.0
   offset = {'N': north, 'E': east}

   return offset

def ra_in_decimal_hours(ra):
   """ra_in_decimal_hours.

   Args:
        ra:
   """

   return(ra/15.0)

# Base-26 converter - for local QUB PS1 IDs
def baseN(num, base=26, numerals="abcdefghijklmnopqrstuvwxyz"):
   """baseN.

   Args:
        num:
        base:
        numerals:
   """
   if num == 0:
       return numerals[0]

   if num < 0:
       return '-' + baseN((-1) * num, base, numerals)

   if not 2 <= base <= len(numerals):
       raise ValueError('Base must be between 2-%d' % len(numerals))

   left_digits = num // base
   if left_digits == 0:
       return numerals[num % base]
   else:
       return baseN(left_digits, base, numerals) + numerals[num % base]

# Base 26 number padded with base 26 zeroes (a)
def base26(num):
   """base26.

   Args:
        num:
   """
   if num < 0:
      raise ValueError('Number must be positive or zero')

   return baseN(num).rjust(3,'a')


# 2013-02-27 KWS Added converter to get base 10 number back from base 26
def base26toBase10(b26number):
    """Convert from Base 26 to Base 10. Only accept lowercase letters"""
    numerals="abcdefghijklmnopqrstuvwxyz"
    import re
    if re.search('^[a-z]+$', b26number):
        b26number = b26number[::-1]
        b10number = 0
        for i in range(len(b26number)):
            b10number += numerals.index(b26number[i])*(26 ** i)
    else:
        return -1

    return b10number

# 2022-12-28 KWS Added two new Base 26 encode/decode functions. These are
#                aimed at the Pan-STARRS nameserver where we start with
#                single letters, then progress to two letters, etc. I
#                may eventually use this for ATLAS as well.
def base26Encode(number, alphabet="abcdefghijklmnopqrstuvwxyz"):
    """Converts an integer to an alphabet equivilent"""
    if not isinstance(number, (int)):
        raise TypeError("number must be an integer")

    if number <= 0:
        return None

    if 1 <= number - 1 < len(alphabet):
        return alphabet[number - 1]

    base = ''
    while number != 0:
        number, r = divmod(number, len(alphabet))
        if r == 0:
            number = number - 1
        base = alphabet[r - 1] + base
    return base


def base26Decode(value, alphabet="abcdefghijklmnopqrstuvwxyz"):
    """Decodes alphabet letters to integers"""
    if not value.isalpha():
        return None
    value = value.lower()[::-1]
    number = 0
    for i in range(len(value)):
        number = ((len(alphabet) ** i) * (alphabet.index(value[i]) + 1)) + number
    return number


class DictLookup(dict):
   """
   a dictionary which can lookup value by key, or keys by value
   """
   def __init__(self, items=[]):
      """items can be a list of pair_lists or a dictionary"""
      dict.__init__(self, items)

   def get_key(self, value):
      """find the key(s) as a list given a value"""
      return [item[0] for item in list(self.items()) if item[1] == value]

   def get_value(self, key):
      """find the value given a key"""
      return self[key]


def getFlagDefs(flags, dictionary, delimiter = ' + '):
   """getFlagDefs.

   Args:
        flags:
        dictionary:
        delimiter:
   """
   flagDefs = []

   lookup = DictLookup(dictionary)

   # It's an 8 bit flag at the moment, and we only
   # use 6 bits.  Cycle through the flags and concatenate
   # the keys.
   for i in range(16):
      mask = (1<<15) >>i
      try:
         if flags & mask:
            flagDefs.append(''.join(lookup.get_key(flags & mask)))
      except TypeError:
         # We got a None (i.e. NULL) value
         return ''

   return delimiter.join(flagDefs)

# 2017-04-24 KWS We need to keep track of leap seconds.
#                Stub code installed here.
def getLeapSeconds(dateTime):
   """getLeapSeconds.

   Args:
        dateTime:
   """
   leapSeconds = 0
   return leapSeconds

def getCurrentMJD():
   """getCurrentMJD.
   """
   jd = time.time()/86400.0+2440587.5
   mjd = jd-2400000.5
   return mjd

def getCurrentJD():
   """getCurrentJD.
   """
   jd = time.time()/86400.0+2440587.5
   return jd

def getJDfromMJD(mjd):
   """getJDfromMJD.

   Args:
        mjd:
   """
   jd = mjd + 2400000.5
   return jd
   

def getDateFromMJD(mjd, fitsFormat=False):
   """getDateFromMJD.

   Args:
        mjd:
        fitsFormat:
   """
   unixtime = (mjd + 2400000.5 - 2440587.5) * 86400.0;
   theDate = datetime.utcfromtimestamp(unixtime)
   stringDate = theDate.strftime("%Y-%m-%d %H:%M:%S")
   if fitsFormat == True:
      stringDate = stringDate.replace(' ','T')

   return stringDate


# 2012-03-26 KWS Added function to convert from date to MJD
def getMJDFromSqlDate(sqlDate):
   """getMJDFromSqlDate.

   Args:
        sqlDate:
   """
   mjd = None

   try:
      year, month, day = sqlDate[0:10].split('-')
      hours, minutes, seconds = sqlDate[11:19].split(':')
      t = (int(year), int(month), int(day), int(hours), int(minutes), int(seconds), 0, 0, 0)
      unixtime = int(time.mktime(t))
      mjd = unixtime/86400.0 - 2400000.5 + 2440587.5
   except ValueError as e:
      mjd = None
      print("String is not in SQL Date format.")

   return mjd

def getUnixTimeFromSQLDate(sqlDate):
   """getUnixTimeFromSQLDate.

   Args:
        sqlDate:
   """
   unixTime = None

   try:
      year, month, day = sqlDate[0:10].split('-')
      hours, minutes, seconds = sqlDate[11:19].split(':')
      t = (int(year), int(month), int(day), int(hours), int(minutes), int(seconds), 0, 0, 0)
      unixTime = int(time.mktime(t))
   except ValueError as e:
      unixTime = None
      print("String is not in SQL Date format.")

   return unixTime

def getSQLDateFromUnixTime(unixTime):
   """getSQLDateFromUnixTime.

   Args:
        unixTime:
   """
   sqlDate = None
   try:
      sqlDate = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(unixTime)))
   except ValueError as e:
      sqlDate = None
      print("Unix time must be an integer.")
   return sqlDate

def getDateFractionMJD(mjd, delimiter = ' ', decimalPlaces = 2):
   """getDateFractionMJD.

   Args:
        mjd:
        delimiter:
        decimalPlaces:
   """
   floatWidth = decimalPlaces + 3 # always have 00.00 or 00.000 or 00.0000, etc
   unixtime = (mjd + 2400000.5 - 2440587.5) * 86400.0;
   theDate = datetime.utcfromtimestamp(unixtime)
   dateString = theDate.strftime("%Y:%m:%d:%H:%M:%S")
   (year, month, day, hour, min, sec) = dateString.split(':')
   dayFraction = int(day) + int(hour)/24.0 + int(min)/(24.0 * 60.0) + int(sec)/(24.0 * 60.0 * 60.0)
   dateFraction = "%s%s%s%s%0*.*f" % (year, delimiter, month, delimiter, floatWidth, decimalPlaces, dayFraction)
   return dateFraction


def sexToDec (sexv, ra = False, delimiter = ':'):
   """sexToDec.

   Args:
        sexv:
        ra:
        delimiter:
   """
   # Note that the approach below only works because there are only two colons
   # in a sexagesimal representation.
   degrees = 0
   minutes = 0
   seconds = 0
   decimalDegrees = None
   sgn = 1

   try:
      # Look for a minus sign.  Note that -00 is the same as 00.

      (degreesString, minutesString, secondsString) = sexv.split(delimiter)

      if degreesString[0] == '-':
         sgn = -1
      else:
         sgn = 1

      degrees = abs(float(degreesString))
      minutes = float(minutesString)
      seconds = float(secondsString)
      if ra:
         degrees *= 15.0
         minutes *= 15.0
         seconds *= 15.0

      decimalDegrees = (degrees + (minutes / 60.0) + (seconds / 3600.0)) * sgn
      if not ra and (decimalDegrees < -90.0 or decimalDegrees > 90.0):
         decimalDegrees = None
      elif ra and (decimalDegrees < 0.0 or decimalDegrees > 360.0):
         decimalDegrees = None
   except ValueError:
      # Just in case we're passed a dodgy string
      decimalDegrees = None

   return decimalDegrees


def coords_sex_to_dec (ra, dec, delimiter = ':'):
   """coords_sex_to_dec.

   Args:
        ra:
        dec:
        delimiter:
   """

   return(sexToDec(ra, ra=True ,delimiter=delimiter), sexToDec(dec, ra=False, delimiter=delimiter))


# A wrapper for the C++ ConeSearch utility.  In lieu of creating a pure Python facility.
# Note that this is desiged to lookup IDs that are INTEGERS.
def wrapConeSearch(dbuser, dbpass, dbname, dbhost, tablename, ra, dec, radius):
   """wrapConeSearch.

   Args:
        dbuser:
        dbpass:
        dbname:
        dbhost:
        tablename:
        ra:
        dec:
        radius:
   """
   if dbpass == "":
      dbpass = """ "" """

   cmd = "ConeSearch " + dbuser + " " + dbpass + " " + dbname + " " + dbhost + " quick " + tablename + " "  + str(ra) + " " + str(dec) + " " + str(radius)
   #print cmd
   cmdout= os.popen(cmd)
   result= cmdout.readlines()
   if cmdout.close() != None:
      print("Problem with command")
      return -1

   numberOfMatches = 0
   matchedRowNumberLinePrefix = "Number of matched rows = "

   resultSetSortedBySep = []

   if len(result) == 1:
      # We probably got no matches
      #if result[0].startswith("No matches from "):
      #   print "No results"
      #else:
      #   print "Something went wrong..."
      pass
   else:
      resultSet = []
      for line in result:
         if line.startswith(matchedRowNumberLinePrefix):
            #print line.replace(matchedRowNumberLinePrefix,"").rstrip()
            numberOfMatches = int(line.replace(matchedRowNumberLinePrefix,"").rstrip())
         else:
            #print line.rstrip().lstrip().rstrip('"').lstrip("ID: ").replace(" Separation = ", "")
            (id, separation) = line.rstrip().lstrip().rstrip('"').lstrip("ID: ").replace(" Separation = ", "").split(',')
            keyvaluepair = {"id": int(id), "separation": float(separation)}
            resultSet.append(keyvaluepair)

      resultSetSortedBySep = sorted(resultSet, key=lambda k: k['separation'])

   return numberOfMatches, resultSetSortedBySep



def calculate_cartesians(ra, dec):
   """calculate_cartesians.

   Args:
        ra:
        dec:
   """
   ra = math.radians(ra)
   dec = math.radians(dec)
   cos_dec = math.cos(dec)
   cx = math.cos(ra) * cos_dec
   cy = math.sin(ra) * cos_dec
   cz = math.sin(dec)

   cartesians = (cx, cy, cz)
   return cartesians


pi = (4*math.atan(1.0))
DEG_TO_RAD_FACTOR = pi/180.0
RAD_TO_DEG_FACTOR = 180.0/pi

def getAngularSeparation(ra1, dec1, ra2, dec2):
   """
   Calculate the angular separation between two objects.  If either set of
   coordinates contains a colon, assume it's in sexagesimal and automatically
   convert into decimal before doing the calculation.
   """

   angularSeparation = None

   if ra1 is None or ra2 is None or dec1 is None or dec2 is None:
      # Angular separation can't be calculated.
      return angularSeparation

   if ':' in str(ra1):
      ra1 = sexToDec(ra1, ra=True)
   if ':' in str(dec1):
      dec1 = sexToDec(dec1, ra=False)
   if ':' in str(ra2):
      ra2 = sexToDec(ra2, ra=True)
   if ':' in str(dec2):
      dec2 = sexToDec(dec2, ra=False)

   # 2013-10-20 KWS Always make sure that the ra and dec values are floats

   ra1 = float(ra1)
   ra2 = float(ra2)
   dec1 = float(dec1)
   dec2 = float(dec2)


   if ra1 is not None and ra2 is not None and dec1 is not None and dec2 is not None:

      aa  = (90.0-dec1)*DEG_TO_RAD_FACTOR
      bb  = (90.0-dec2)*DEG_TO_RAD_FACTOR
      cc  = (ra1-ra2)*DEG_TO_RAD_FACTOR
      one = math.cos(aa)*math.cos(bb)
      two = math.sin(aa)*math.sin(bb)*math.cos(cc)

      # Because acos() returns NaN outside the ranges of -1 to +1
      # we need to check this.  Double precision decimal places
      # can give values like 1.0000000000002 which will throw an
      # exception.

      three = one+two

      if (three > 1.0):
         three = 1.0
      if (three < -1.0):
         three = -1.0

      angularSeparation = math.acos(three)*RAD_TO_DEG_FACTOR*3600.0

   return angularSeparation


# 2012-02-29 KWS Python Cone Search code - depends on new htmCircle Python/C++ module.
QUICK = 1
FULL  = 2
COUNT = 3

# Hash of table names.  Produces list containing list of columns and table id.
# 2012-08-01 KWS Added tables for PESSTO lookups
CAT_ID_RA_DEC_COLS = {
   'tcs_transient_objects': [['id', 'ra_psf', 'dec_psf'],0],
   'tcs_2mass_psc_cat': [['designation', 'ra', 'decl'],1],
   'tcs_cat_v_2mass_psc_noextended': [['designation', 'ra', 'decl'],1],
   'tcs_2mass_xsc_cat': [['designation', 'ra', 'decl'],2],
   'tcs_guide_star_cat': [['hstID', 'RightAsc', 'Declination'],3], # Remember that RA and DEC are in RADIANS here
   'tcs_cat_v_guide_star_ps': [['hstID', 'RightAsc', 'Declination'],3], # Remember that RA and DEC are in RADIANS here
   'tcs_ned_cat': [['Object_Name', 'RA_deg', 'DEC_deg', 'Redshift_1'],4],
   'tcs_cat_v_ned_not_gal_qso': [['Object_Name', 'RA_deg', 'DEC_deg', 'Redshift_1'],4], # This and the following 3 views given same catalogue ID as base NED catalogue
   'tcs_cat_v_ned_qsos': [['Object_Name', 'RA_deg', 'DEC_deg', 'Redshift_1'],4],
   'tcs_cat_v_ned_xrays': [['Object_Name', 'RA_deg', 'DEC_deg', 'Redshift_1'],4],
   'tcs_cat_v_ned_galaxies': [['Object_Name', 'RA_deg', 'DEC_deg', 'Redshift_1'],4],
   'tcs_sdss_galaxies_cat': [['Objid', 'ra', 'dec_', 'z'],5],
   'tcs_cat_v_sdss_galaxies_notspec': [['Objid', 'ra', 'dec_', 'z'],5], # Not spectroscopic galaxies
   'tcs_sdss_spect_galaxies_cat': [['Objid', 'ra', 'dec_', 'z'],6],
   'tcs_sdss_stars_cat': [['Objid', 'ra', 'dec_'],7],
   'tcs_veron_cat': [['recno', 'viz_RAJ2000', 'viz_DEJ2000', 'z'],8],
   'tcs_cat_deep2dr3': [['OBJNAME', 'RA_deg', 'DEC_deg', 'Z'],9],
   'tcs_cat_md01_ned': [['Object_Name', 'RA_deg', 'DEC_deg', 'Redshift'],10],
   'tcs_cat_md02_ned': [['Object_Name', 'RA_deg', 'DEC_deg', 'Redshift'],11],
   'tcs_cat_md03_ned': [['Object_Name', 'RA_deg', 'DEC_deg', 'Redshift'],12],
   'tcs_cat_md04_ned': [['Object_Name', 'RA_deg', 'DEC_deg', 'Redshift'],13],
   'tcs_cat_md05_ned': [['Object_Name', 'RA_deg', 'DEC_deg', 'Redshift'],14],
   'tcs_cat_md06_ned': [['Object_Name', 'RA_deg', 'DEC_deg', 'Redshift'],15],
   'tcs_cat_md07_ned': [['Object_Name', 'RA_deg', 'DEC_deg', 'Redshift'],16],
   'tcs_cat_md08_ned': [['Object_Name', 'RA_deg', 'DEC_deg', 'Redshift'],17],
   'tcs_cat_md09_ned': [['Object_Name', 'RA_deg', 'DEC_deg', 'Redshift'],18],
   'tcs_cat_md10_ned': [['Object_Name', 'RA_deg', 'DEC_deg', 'Redshift'],19],
   'tcs_cat_md01_chiappetti2005': [['recno', 'viz_RAJ2000', 'viz_DEJ2000'],20],
   'tcs_cat_md01_pierre2007': [['recno', 'viz_RAJ2000', 'viz_DEJ2000'],21],
   'tcs_cat_md02_giacconi2002': [['recno', 'viz_RAJ2000', 'viz_DEJ2000'],22],
   'tcs_cat_md02_lefevre2004': [['recno', 'viz_RAJ2000', 'viz_DEJ2000', 'z'],23],
   'tcs_cat_md02_lehmer2005': [['recno', 'viz_RAJ2000', 'viz_DEJ2000'],24],
   'tcs_cat_md02_virani2006': [['recno', 'viz_RAJ2000', 'viz_DEJ2000'],25],
   'tcs_cat_md04_hasinger2007': [['recno', 'viz_RAJ2000', 'viz_DEJ2000'],26],
   'tcs_cat_md04_trump2007': [['recno', 'viz_RAJ2000', 'viz_DEJ2000', 'z'],27],
   'tcs_cat_md05_brunner2008': [['recno', 'viz_RAJ2000', 'viz_DEJ2000'],28],
   'tcs_cat_md07_laird2009': [['recno', 'viz_RAJ2000', 'viz_DEJ2000'],29],
   'tcs_cat_md07_nandra2005': [['recno', 'viz_RAJ2000', 'viz_DEJ2000'],30],
   'tcs_cat_md08_manners2003': [['recno', 'viz_RAJ2000', 'viz_DEJ2000'],31],
   'tcs_cat_sdss_stars_galaxies': [['Objid', 'ra', 'dec_'],32],
   'tcs_cat_v_sdss_starsgalaxies_stars': [['Objid', 'ra', 'dec_'],32],
   'tcs_cat_v_sdss_starsgalaxies_galaxies': [['Objid', 'ra', 'dec_'],32],
   'tcs_cat_sdss_lrg': [['Objid', 'ra', 'dec_'],33],
   'tcs_cat_slacs': [['Objid', 'ra', 'dec_'],34],
   'tcs_cat_milliquas': [['id', 'ra_deg', 'dec_deg', 'z'],35],
   'tcs_cat_sdss_dr9_photo_stars_galaxies': [['objID', 'ra', 'dec_', 'z_'],36], 
   'tcs_cat_v_sdss_dr9_galaxies_notspec': [['objID', 'ra', 'dec_', 'z_'],36], 
   'tcs_cat_v_sdss_dr9_stars': [['objID', 'ra', 'dec_'],36], 
   'tcs_cat_sdss_dr9_spect_galaxies_qsos': [['objID', 'ra', 'dec_', 'z_'],37], 
   'tcs_cat_v_sdss_dr9_spect_galaxies': [['objID', 'ra', 'dec_', 'z_'],37], 
   'tcs_cat_v_sdss_dr9_spect_qsos': [['objID', 'ra', 'dec_', 'z_'],37], 
   'tcs_cat_rosat_faint_1x29': [['id', 'ra_deg', 'dec_deg'],38],
   'tcs_cat_rosat_bright_1x10': [['id', 'ra_deg', 'dec_deg'],39],
   'tcs_cfa_detections': [['cfa_designation', 'raDeg', 'decDeg'],40],
   'tcs_cat_ps1_medium_deep_ref': [['id', 'ra', 'decl'],41],
   'tcs_cat_v_ps1_medium_deep_ref_stars': [['id', 'ra', 'decl'],41],
   'tcs_cat_v_ps1_medium_deep_ref_galaxies': [['id', 'ra', 'decl'],41],
   # 2015-02-07 KWS Added ps1 ubercal star catalog form Doug and Eddie
   'tcs_cat_ps1_ubercal_stars': [['id', 'RA', 'Dec'],43],

   # Added ATLAS Kepler 2 catalogue
   'tcs_cat_kepler_k2': [['name', 'ra_deg', 'dec_deg'],42],

   # 2017-12-05 KWS Added Kepler 2 pixel catalogue
   'tcs_cat_kepler_k2_pixels': [['id', 'ra_deg', 'dec_deg'],45],

   # 2016-09-16 KWS Added Gaia DR1 star catalog
   'tcs_cat_gaia_dr1': [['id', 'ra', 'dec'],44],

   # 2019-01-29 KWS Added Moon ephemerides 
   'tcs_cat_satellites': [['name', 'ra_deg', 'dec_deg'],46],

   # 2020-02-11 KWS Added Gaia DR2 catalogue
   'tcs_cat_gaia_dr2': [['source_id', 'ra', 'dec'],47],

   # PESSTO database catalogues
   # 2014-04-08 KWS Added cbat views for SN and PSN

   'transientBucket': [['primaryKeyId', 'raDeg', 'decDeg'],1000],
   'view_transientBucketMaster': [['primaryKeyId', 'raDeg', 'decDeg'],1001],
   'atel_coordinates': [['primaryId', 'raDeg', 'decDeg'],1002],
   'fs_chase': [['candidateID', 'ra_deg', 'dec_deg'],1003],
   'view_fs_crts_css_summary': [['name', 'raDeg', 'decDeg'],1004],
   'view_fs_crts_mls_summary': [['name', 'raDeg', 'decDeg'],1005],
   'view_fs_crts_sss_summary': [['name', 'raDeg', 'decDeg'],1006],
   'view_fs_lsq_summary': [['candidateID', 'ra_deg', 'dec_deg'],1007],
   'view_fs_ogle_summary': [['name', 'raDeg', 'decDeg'],1008],
   'cbats': [['name', 'raDeg', 'decDeg'],1009],
   'view_cbats_sn': [['name', 'raDeg', 'decDeg'],1010],
   'view_cbats_psn': [['name', 'raDeg', 'decDeg'],1011],
   # 2015-03-16 KWS Added fs_brightsnlist_discoveries (bright SN list)
   'fs_brightsnlist_discoveries': [['name', 'raDeg', 'decDeg'],1012],
   # 2015-04-21 KWS Added fs_asassn_sne and fs_asassn_transients
   'fs_asassn_sne': [['ID', 'RA', 'decl', 'Redshift'],1013],
   'fs_asassn_transients': [['name', 'raDeg', 'decDeg'],1014],
   'fs_tns_transients': [['objectName', 'raDeg', 'decDeg'],1015],

   # 2019-10-02 KWS Added tcs_cat_tns catalogue (on the panstarrs1 database)
   'tcs_cat_tns': [['tns_name', 'ra', 'decl'],1016],

   # 2015-01-26 KWS Added tcs_photpipe_detections for quick & dirty asteroid/fakes crossmatch
   'tcs_photpipe_detections': [['id', 'RA', 'Dec'],2000],
   # 2015-08-13 KWS Added tcs_tphot_detections for quick & dirty asteroid/fakes crossmatch
   'tcs_tphot_detections': [['id', 'ra', 'dec'],2001],
   # 2016-02-02 KWS Note that atlas_diff_objects ONLY works with HTM only queries.
   'atlas_diff_objects': [['id', 'ra', 'dec'],3000],
   # 2016-05-03 KWS Note that atlas_diff_detections ONLY works with HTM only queries.
   'atlas_diff_detections': [['id', 'ra', 'dec'],3001],
   # 2017-08-30 KWS Added atlas_metadata for ATLAS footprint searching
   'atlas_metadata': [['id', 'ra', 'dec'],3002],
   # 2017-09-26 KWS Added atlas_metadataddc for ATLAS footprint searching
   'atlas_metadataddc': [['id', 'ra', 'dec'],3003],
   # 2019-07-05 KWS Search just the views.
   'atlas_v_followup1': [['id', 'ra', 'dec'],3004],
   'atlas_v_followup2': [['id', 'ra', 'dec'],3005],
   'atlas_v_followup3': [['id', 'ra', 'dec'],3006],
   'atlas_v_followup4': [['id', 'ra', 'dec'],3007],
   'atlas_v_followup5': [['id', 'ra', 'dec'],3008],
   'atlas_v_followup6': [['id', 'ra', 'dec'],3009],
   'psdb_web_v_followup_bad_presentation': [['id', 'ra_psf', 'dec_psf'],4000],
   'psdb_web_v_followup_conf_presentation': [['id', 'ra_psf', 'dec_psf'],4001],
   'psdb_web_v_followup_good_presentation': [['id', 'ra_psf', 'dec_psf'],4002],
   'psdb_web_v_followup_poss_presentation': [['id', 'ra_psf', 'dec_psf'],4003],
   'psdb_web_v_followup_pend_presentation': [['id', 'ra_psf', 'dec_psf'],4004],
   'psdb_web_v_followup_attic_presentation': [['id', 'ra_psf', 'dec_psf'],4005],
   'psdb_web_v_followup_zoo_presentation': [['id', 'ra_psf', 'dec_psf'],4006],
   'psdb_web_v_followup_tbd_presentation': [['id', 'ra_psf', 'dec_psf'],4007],
   'psdb_web_v_followup_fast_presentation': [['id', 'ra_psf', 'dec_psf'],4008],
   'psdb_web_v_followup_all_presentation': [['id', 'ra_psf', 'dec_psf'],4100],

   # 2023-07-04 KWS Add a few extra catalogues from ePESSTO+ crossmatch_catalogues table. Start at 5000 for catalogue ID.
   'tcs_cat_2mass_psc_final': [['id', 'ra', 'decl'],5000],
   # 2023-07-04 KWS Note that RightAsc and Declination are in RADIANS for tcs_cat_guide_star_catalogue_v2_3.
   'tcs_cat_ned_stream': [['ned_name', 'raDeg', 'decDeg', 'redshift'],5004],
   'tcs_cat_ps1_dr1': [['objID', 'raAve', 'decAve'],5005],
   'tcs_cat_sdss_photo_stars_galaxies_dr12': [['objID', 'ra', 'dec_'],5007],
}

# 2012-02-02 KWS Cone Searcher based on the new SWIG C++ code.  Need speed.
# 2012-03-25 KWS Added django so that we can call the Django dict cursor if necessary.
def coneSearch(ra, dec, radius, tableName, htmLevel = 16, queryType = QUICK, conn = None, django = False):
   """coneSearch.

   Args:
        ra:
        dec:
        radius:
        tableName:
        htmLevel:
        queryType:
        conn:
        django:
   """

   # 2012-02-02 KWS Require database connections for cone searching
   import MySQLdb

   # 2012-02-02 KWS Introduced a new SWIG htmCircle library for cone searching
   from gkhtm import _gkhtm as htmCircle

   # Attempt a cone search of the given tableName.  Use internal models if conn
   # is None, otherwise use a given database connection (allows it to be called
   # externally as part of a script).

   # Code returns a list of lists.  First value in sublist is separation.  Second
   # is the row of data requested from the database.

   message = ""

   if htmLevel not in (16, 20):
      # We don't support anything other than Level 16 or Level 20 queries
      return "Must be HTM level 16 or 20", []

   # Check that RA and DEC are in decimal degrees.  If not, assume sexagesimal and attempt to convert

   if ':' in str(ra):
      ra = sexToDec(ra, ra=True)


   if ':' in str(dec):
      dec = sexToDec(dec, ra=False)

   # 2015-05-29 KWS Sometimes we send RA and Dec in string format, so
   #                need to make sure that they are doubles.

   ra = float(ra)
   dec = float(dec)

   try:
      quickColumns = CAT_ID_RA_DEC_COLS[tableName][0]
   except KeyError as e:
      return "Table %s not recognised." % tableName, []

   htmWhereClause = htmCircle.htmCircleRegion(htmLevel, ra, dec, radius)

   cartesians = calculate_cartesians(ra, dec)
   cartesianClause = 'and (cx * %.17f + cy * %.17f + cz * %.17f >= cos(%.17f))' % (cartesians[0], cartesians[1], cartesians[2], math.radians(radius/3600.0))

   columns = ['*']

   if queryType == QUICK:
      columns = quickColumns
   elif queryType == COUNT:
      columns = ['count(*) number']

   query = 'select ' + ','.join(columns) + ' from %s' % tableName + htmWhereClause + cartesianClause 
   #print query

   results = []

   if conn:
      # We have a database connection, so use it to make a call to the database

      # DO THE QUERY

      try:
         if django:
            cursor = conn.cursor ()
         else:
            cursor = conn.cursor (MySQLdb.cursors.DictCursor)

         cursor.execute(query)

         if django:
            resultSet = [ dict( (d[0],c) for d, c in zip(cursor.description, row) ) for row in cursor ]
         else:
            resultSet = cursor.fetchall ()


      except MySQLdb.Error as e:
         return "Error %d: %s" % (e.args[0], e.args[1]), []


      if resultSet:
         if queryType == COUNT:
            results = [[0.0, resultSet[0]['number']]]
            return "Count", results

         # Calculate the angular separation for each row
         for row in resultSet:
            if tableName == 'tcs_guide_star_cat' or tableName == 'tcs_cat_v_guide_star_ps':
               # Guide star cat RA and DEC are in RADIANS
               separation = getAngularSeparation(ra, dec, math.degrees(row[CAT_ID_RA_DEC_COLS[tableName][0][1]]), math.degrees(row[CAT_ID_RA_DEC_COLS[tableName][0][2]]))
            else:
               separation = getAngularSeparation(ra, dec, row[CAT_ID_RA_DEC_COLS[tableName][0][1]], row[CAT_ID_RA_DEC_COLS[tableName][0][2]])
            results.append([separation, row])

         # Sort by separation
         results.sort(key=itemgetter(0))
      else:
         message = "No matches from %s." % tableName
   else:
      message = query

   return message, results

# TODO We have the opportunity to inject another where clause component.
def coneSearchHTMWithExtraWhereClause(ra, dec, radius, tableName, htmLevel = 16, queryType = QUICK, conn = None, django = False, prefix = "htm", suffix = "ID", extraWhereClause = ''):
   """HTM only cone search.  Assumes a column in the catalogue which by default is called htm<n>ID where <n> is the HTM level.

   Args:
        ra:
        dec:
        radius:
        tableName:
        htmLevel:
        queryType:
        conn:
        django:
        prefix: HTM column prefix - default: "htm"
        suffix: HTM column suffix - default: "ID"
   """

   # 2012-02-02 KWS Require database connections for cone searching
   import MySQLdb

   # 2012-02-02 KWS Introduced a new SWIG htmCircle library for cone searching
   from gkhtm import _gkhtm as htmCircle

   # Attempt a cone search of the given tableName.  Use internal models if conn
   # is None, otherwise use a given database connection (allows it to be called
   # externally as part of a script).

   # Code returns a list of lists.  First value in sublist is separation.  Second
   # is the row of data requested from the database.

   message = ""

   if htmLevel not in (16, 20):
      # We don't support anything other than Level 16 or Level 20 queries
      return "Must be HTM level 16 or 20", []

   # Check that RA and DEC are in decimal degrees.  If not, assume sexagesimal and attempt to convert

   if ':' in str(ra):
      ra = sexToDec(ra, ra=True)


   if ':' in str(dec):
      dec = sexToDec(dec, ra=False)

   ra = float(ra)
   dec = float(dec)

   try:
      quickColumns = CAT_ID_RA_DEC_COLS[tableName][0]
   except KeyError as e:
      return "Table %s not recognised." % tableName, []

   # 2020-07-08 KWS htmCircleRegion has been modified to take two optional paramaters. Because
   #                of necessity to maintain older SWIG version, parameters cannot be named,
   #                but prefix and suffix are completely optional. Default values are htm and ID
   #                if omitted. If you need to pass the suffix only, you MUST specify the prefix
   #                as well. If you don't want the suffix, pass prefix and "".
   htmWhereClause = htmCircle.htmCircleRegion(htmLevel, ra, dec, radius, prefix, suffix)

   # We now have a query that returns a SUPERSET.  We need to trim the superset once
   # the query is done.

   columns = ['*']

   if queryType == QUICK:
      columns = quickColumns

   query = 'select ' + ','.join(columns) + ' from %s' % tableName + htmWhereClause + extraWhereClause
   #print query

   results = []

   if conn:
      # We have a database connection, so use it to make a call to the database

      # DO THE QUERY

      try:
         if django:
            cursor = conn.cursor ()
         else:
            cursor = conn.cursor (MySQLdb.cursors.DictCursor)

         cursor.execute(query)

         if django:
            resultSet = [ dict( (d[0],c) for d, c in zip(cursor.description, row) ) for row in cursor ]
         else:
            resultSet = cursor.fetchall ()


      except MySQLdb.Error as e:
         return "Error %d: %s" % (e.args[0], e.args[1]), []


      if resultSet:

         # Calculate the angular separation for each row
         for row in resultSet:
            if tableName == 'tcs_guide_star_cat' or tableName == 'tcs_cat_v_guide_star_ps':
               # Guide star cat RA and DEC are in RADIANS
               separation = getAngularSeparation(ra, dec, math.degrees(row[CAT_ID_RA_DEC_COLS[tableName][0][1]]), math.degrees(row[CAT_ID_RA_DEC_COLS[tableName][0][2]]))
            else:
               separation = getAngularSeparation(ra, dec, row[CAT_ID_RA_DEC_COLS[tableName][0][1]], row[CAT_ID_RA_DEC_COLS[tableName][0][2]])

            # For HTM only queries, only add the results if the separation is less than the radius.
            # This is because HTM queries will always be a superset.
            if separation is not None and separation < radius:
               results.append([separation, row])

         # Sort by separation
         results.sort(key=itemgetter(0))
      else:
         message = "No matches from %s." % tableName
   else:
      message = query

   return message, results



# TODO We have the opportunity to inject another where clause component.
# 2016-02-02 KWS Pure HTM conesearch. Does NOT use unit cartesian coords.
def coneSearchHTM(ra, dec, radius, tableName, htmLevel = 16, queryType = QUICK, conn = None, django = False, prefix = "htm", suffix = "ID"):
   """HTM only cone search.  Assumes a column in the catalogue which by default is called htm<n>ID where <n> is the HTM level.

   Args:
        ra:
        dec:
        radius:
        tableName:
        htmLevel:
        queryType:
        conn:
        django:
        prefix: HTM column prefix - default: "htm"
        suffix: HTM column suffix - default: "ID"
   """

   # 2012-02-02 KWS Require database connections for cone searching
   import MySQLdb

   # 2012-02-02 KWS Introduced a new SWIG htmCircle library for cone searching
   from gkhtm import _gkhtm as htmCircle

   # Attempt a cone search of the given tableName.  Use internal models if conn
   # is None, otherwise use a given database connection (allows it to be called
   # externally as part of a script).

   # Code returns a list of lists.  First value in sublist is separation.  Second
   # is the row of data requested from the database.

   message = ""

   if htmLevel not in (16, 20):
      # We don't support anything other than Level 16 or Level 20 queries
      return "Must be HTM level 16 or 20", []

   # Check that RA and DEC are in decimal degrees.  If not, assume sexagesimal and attempt to convert

   if ':' in str(ra):
      ra = sexToDec(ra, ra=True)


   if ':' in str(dec):
      dec = sexToDec(dec, ra=False)

   ra = float(ra)
   dec = float(dec)

   try:
      quickColumns = CAT_ID_RA_DEC_COLS[tableName][0]
   except KeyError as e:
      return "Table %s not recognised." % tableName, []

   # 2020-07-08 KWS htmCircleRegion has been modified to take two optional paramaters. Because
   #                of necessity to maintain older SWIG version, parameters cannot be named,
   #                but prefix and suffix are completely optional. Default values are htm and ID
   #                if omitted. If you need to pass the suffix only, you MUST specify the prefix
   #                as well. If you don't want the suffix, pass prefix and "".
   htmWhereClause = htmCircle.htmCircleRegion(htmLevel, ra, dec, radius, prefix, suffix)

   # We now have a query that returns a SUPERSET.  We need to trim the superset once
   # the query is done.

   columns = ['*']

   if queryType == QUICK:
      columns = quickColumns

   query = 'select ' + ','.join(columns) + ' from %s' % tableName + htmWhereClause
   #print query

   results = []

   if conn:
      # We have a database connection, so use it to make a call to the database

      # DO THE QUERY

      try:
         if django:
            cursor = conn.cursor ()
         else:
            cursor = conn.cursor (MySQLdb.cursors.DictCursor)

         cursor.execute(query)

         if django:
            resultSet = [ dict( (d[0],c) for d, c in zip(cursor.description, row) ) for row in cursor ]
         else:
            resultSet = cursor.fetchall ()


      except MySQLdb.Error as e:
         return "Error %d: %s" % (e.args[0], e.args[1]), []


      if resultSet:

         # Calculate the angular separation for each row
         for row in resultSet:
            if tableName == 'tcs_guide_star_cat' or tableName == 'tcs_cat_v_guide_star_ps':
               # Guide star cat RA and DEC are in RADIANS
               separation = getAngularSeparation(ra, dec, math.degrees(row[CAT_ID_RA_DEC_COLS[tableName][0][1]]), math.degrees(row[CAT_ID_RA_DEC_COLS[tableName][0][2]]))
            else:
               separation = getAngularSeparation(ra, dec, row[CAT_ID_RA_DEC_COLS[tableName][0][1]], row[CAT_ID_RA_DEC_COLS[tableName][0][2]])

            # For HTM only queries, only add the results if the separation is less than the radius.
            # This is because HTM queries will always be a superset.
            if separation < radius:
               results.append([separation, row])

         # Sort by separation
         results.sort(key=itemgetter(0))
      else:
         message = "No matches from %s." % tableName
   else:
      message = query

   return message, results


def coneSearchHTMCassandra (cassandraSession, ra, dec, radius, tableName, racol = 'ra', deccol = 'dec', refineResults = True, columns = None):
    """coneSearchHTMCassandra.

    Args:
        cassandraSession:  Connection to Cassandra cluster
        ra:
        dec:
        radius:
        tableName:
        racol:
        deccol:
        refineResults:
        columns:
    """

    from gkhtm._gkhtm import htmCircleRegionCassandra

    if ':' in str(ra):
        ra = sexToDec(ra, ra=True)
    if ':' in str(dec):
        dec = sexToDec(dec, ra=False)

    ra = float(ra)
    dec = float(dec)

    # There will often be more than one WHERE clause. This is because Cassandra can't do OR statements.
    # Hence we must query multiple times to get the complete dataset.
    whereClauses = htmCircleRegionCassandra(ra, dec, radius)

    # Columns is a list of strings. Join it so we can use it once here.
    if columns:
        columnString = ','.join(columns)

    resultSet = []
    if len(whereClauses) > 0:
        for w in whereClauses:
            if columns:
                fullQuery = "select %s from %s " % (columnString, tableName) + w
            else:
                fullQuery = "select * from %s " % (tableName) + w

            result = None
            try:
                result = cassandraSession.execute(fullQuery)
            except Exception as e:
                print(e)

            if result:
                resultSet += list(result)

        if resultSet and refineResults:
            # The following code only works if cassandra has specified session.row_factory = dict_factory
            refinedResultSet = []
            for row in resultSet:
                separation = getAngularSeparation(ra, dec, row[racol], row[deccol])
                if separation < radius:
                    refinedResultSet.append(row)
            resultSet = refinedResultSet

    return resultSet


# 2012-07-31 KWS Added new htmID code to the SWIG library.  This is a simple wrapper for returning
#                the HTM ID for a given (decimal) RA and DEC pair.

def htmID(ra, dec, htmLevel = 16):
   """htmID.

   Args:
        ra:
        dec:
        htmLevel:
   """
   id = None
   if htmLevel == 16 or htmLevel == 20:
      from gkhtm import _gkhtm as htmCircle

      try:
         id = htmCircle.htmID(htmLevel, ra, dec)

      except Exception as e:
         # Catch all exceptions. Result will be a None HTM ID.
         pass

   return id



# 2012-05-31 KWS Added new code.
# Brute force cone search.  Go through all objects in a CMF file and find out distance from given RA and DEC pairs.
# Code will produce a list of objects near to our stated RA and DEC pairs, but does not currently eliminate duplicates.

# 2012-06-01 KWS Picked out MJD-OBS, Filename and Filter

def bruteForceCMFConeSearch(filename, coordinatePairs, radius, delimiter = '\t', fitsInfo = None):
   """bruteForceCMFConeSearch.

   Args:
        filename:
        coordinatePairs:
        radius:
        delimiter:
        fitsInfo:
   """
   from astropy.io import fits as p

   h = t = cols = None
   if fitsInfo is None:
      h = p.open(filename)
      t = h[1].data
      cols = h[1].columns
   else:
      t = fitsInfo['table'].data
      cols = fitsInfo['table'].columns

   # Find filename, mjd and filter.  Looking for a single object in a single file will of course yield a single value
   # for all these.  But if this is scripted to look over multiple files, it's useful to know this data.
   header = ''
   tableRow = ''
   body = []
   zp = None
   exptime = None

   try:
      raIndex = cols.names.index('RA_PSF')
      decIndex = cols.names.index('DEC_PSF')
      if fitsInfo is None:
         mjd = h[0].header['MJD-OBS']
         filter = h[0].header['FPA.FILTERID'][0]
         zp = h[0].header['FPA.ZP']
         exptime = h[0].header['EXPTIME']
      else:
         # We're passing in an SMF extension
         mjd = fitsInfo['header'].header['MJD-OBS']
         filter = fitsInfo['header'].header['FILTERID'][0]
         exptime = fitsInfo['header'].header['EXPTIME']

   except KeyError as e:
      print("Cannot cone search this CMF. One of the prerequisite header values is missing")
      print(e)
      return header, body

   basename = os.path.basename(filename)

   # Pick out the columns that relate to RA and DEC.


   resultsTable = []

   # Check for matches, build a results table
   # 2012-06-01 KWS The coordinate pairs are presented in the order we entered them.
   #                We'll therefore add a column to the end of the list of columns
   #                so that we can identify our object again.
   # 2014-01-13 KWS Added the separation value to the results table (so we can refine
   #                the table results if necessary - e.g. all objects < 2 arcsec but
   #                > 1 arcsec)
   i = 0
   for coord in coordinatePairs:
      for row in t:
         raCat = row[raIndex]
         decCat = row[decIndex]

         separation = getAngularSeparation(coord[0], coord[1], raCat, decCat)
         if separation < radius:
            # Add the returned row (there may be more than one) and the object counter
            resultsTable.append([row, separation, i])
            #resultsTable.append([row, i])
      i += 1


   if resultsTable:
      # Column headers
      for name in cols.names:
         # Change names of the RA/DEC columns so the DS9 catalogue reader can read them
         if name == 'RA_PSF':
            name = 'RA_J2000'
         if name == 'DEC_PSF':
            name = 'DEC_J2000'

         header += "%s%s" % (name, delimiter)
      header += "%s%s%s%s%s%s%s%s%s%s%s%s%s" % ('filter', delimiter, 'exptime', delimiter, 'zp', delimiter, 'mjd', delimiter, 'filename', delimiter, 'separation', delimiter, 'object_id')

      # Data

      for row in resultsTable:
         tableRow = ''
         for col in row[0]:
            tableRow += "%s%s" % (col, delimiter)
            #print "%s\t" % col,

         tableRow += "%s%s%s%s%s%s%s%s%s%s%s%s%s" % (filter, delimiter, exptime, delimiter, zp, delimiter, mjd, delimiter, basename, delimiter, row[1], delimiter, row[2])
         body.append(tableRow)
         #print "%s\t%s\t%s\t%s" % (filter, mjd, basename, row[1])

   return header, body

# 2015-11-02 KWS Read new ATLAS ddet headers.
def readATLASddetHeader(filename, delimiter = '= ', useOrderedDict = False):
   '''Read an ATLAS ddet header'''

   import csv
   from collections import OrderedDict

   counter = 0

   header = {}
   if useOrderedDict:
       header = OrderedDict()

   with open(filename) as f:
      for line in f:
         if delimiter not in line:
            # Stop reading the header, if it exists
            break
         if line[0] == '#':
            headerRow = line.strip('#').strip().split(delimiter)
            if len(headerRow) == 2:
               # Check that there are no spaces in the header row
               if ' ' in headerRow[0]:
                  # We shouldn't have spaces
                  return counter, header
               if ' ' in headerRow[1]:
                  # There might be a space, because of the knownast value. Ditch it.
                  headerRow[1] = headerRow[1].split()[0]
               header[headerRow[0]] = headerRow[1]
               counter += 1
            else:
               # There's no delimiter - something went wrong.
               return counter, header
         else:
            # Something went wrong - this is not a header line.
            return counter, header

   return counter, header


# 2015-07-29 KWS Added new code to read generic space separated file with commented header line.
#                E.g. in John Tonry's tphot files, the firs commented line is the column header.
#                skipLines specifieds the number of header lines we want to skip.
# 2015-08-11 KWS Add ability to pass fieldnames in - e.g. where the file doesn't have a header.
# 2016-08-10 KWS Test the type of the variable 'filename'.  If it's a file, no need to open.
# 2017-05-05 KWS Allow use of OrderedDict instead of python dict. Useful when we want to order
#                the output by the original field order.
# 2022-10-10 KWS Added appendheaderlines, headerdelimiter, headerprefix and headerkeycollisionsuffix
#                parameters to allow readout of a header file with values such as '# RA= 10.0' and
#                append the values to a flattened dictionary row. Done for (e.g.) Cassandra
#                where we have flattened data with no foreign keys. Inefficient (uses too much
#                memory by inflating the size of each row), but effective.
# 2022-10-10 KWS Added a rownum column. If set, each row will have an extra column name with the
#                index offset. (Allows database inserts to be compared with source files.) Note
#                that the rownum column has been cast as a string for compatibility reasons.
# 2022-11-07 KWS New skipLines = -1 option == guess where the table header lives.
def readGenericDataFile(filename, delimiter = ' ', skipLines = 0, fieldnames = None, useOrderedDict = False, appendheaderlines=False, headerdelimiter='=', headerprefix='#', headerkeycollisionsuffix='HEAD', rownumcolumn=None):
   """readGenericDataFile.

   Args:
        filename:
        delimiter:
        skipLines:
        fieldnames:
        useOrderedDict:
        appendheaderlines:
        headerdelimiter:
        headerprefix:
        headerkeycollisionsuffix:
   """
   import csv
   from collections import OrderedDict

   # Sometimes the file has a very annoying initial # character on the first line.
   # We need to delete this character or replace it with a space.

   if type(filename).__name__ == 'file' or type(filename).__name__ == 'instance' or type(filename).__name__ == 'GzipFile' or type(filename).__name__ == 'StringIO':
      f = filename
   else:
      f = open(filename)

   data = []

   lineNumber = 0
   if skipLines == -1:
      # Iterate through the file and figure out where the table header is. It's the
      # commented line just before the data where there is no hash symbol.
      try:
         while f.readline()[0] == '#':
            lineNumber += 1
      except IndexError as e:
         # We got to the end of the file and there is no actual data.
         return data
      # Go back to the beginning of the file.
      f.seek(0,0)
      skipLines = lineNumber - 1

   headerdata = {}
   if skipLines > 0:
      if appendheaderlines:
         for i in range(skipLines):
            ln = f.readline().strip().replace(headerprefix,'')
            headerdata[ln.split(headerdelimiter)[0].strip()] = ln.split(headerdelimiter)[1].strip()
      else:
         [f.readline() for i in range(skipLines)]

   # We'll assume a comment line immediately preceding the data is the column headers.

   # If we already have a header line, skip trying to read the header
   if not fieldnames:
      index = 0
      header = f.readline().strip()
      if header[0] == '#':
         # Skip the hash
         index = 1

      if delimiter == ' ': # or delimiter == '\t':
         # Split on whitespace, regardless of however many spaces or tabs between fields
         fieldnames = header[index:].strip().split()
      else:
         fieldnames = header[index:].strip().split(delimiter)

   # 2018-02-12 KWS Strip out whitespace from around any fieldnames
   fieldnames = [x.strip() for x in fieldnames]
   lcfieldnames = [x.lower().strip() for x in fieldnames]
   # The file pointer is now at line 2

   t = csv.DictReader(f, fieldnames = fieldnames, delimiter=delimiter, skipinitialspace = True)

   counter = 0
   for row in t:
      if rownumcolumn:
          row[rownumcolumn] = str(counter)
          fieldnames.append(rownumcolumn)
      if useOrderedDict:
          od = OrderedDict((key, row[key]) for key in fieldnames)
          if appendheaderlines:
              for k,v in headerdata.items():
                  if k.lower() in lcfieldnames:
                      od[k+headerkeycollisionsuffix] = v
                  else:
                      od[k] = v
          data.append(od)
      else:
          if appendheaderlines:
              for k,v in headerdata.items():
                  if k.lower() in lcfieldnames:
                      row[k+headerkeycollisionsuffix] = v
                  else:
                      row[k] = v
          data.append(row)
      counter += 1

   # Only close the file if we opened it in the first place
   if not (type(filename).__name__ == 'file' or type(filename).__name__ == 'instance'):
      f.close()

   # We now have the data as a dictionary.
   return data



# 2015-01-07 KWS Added new generic brute force cone search.  Introduced because of
#                requirement to trim ATLAS fake catalogs.

# 2015-01-27 KWS Added new annulus parameter
# 2017-08-17 KWS Added pre-read catalogue parameter

def bruteForceGenericConeSearch(filename, coordinatePairs, radius, delimiter = '\t', inputDelimiter = '\t', raIndex = 'ra', decIndex = 'dec', minradius = 0.0, catalogue = []):
   """
   Pass a generic text (csv) catalog for searching. Assumes for now that the catalog is space separated.
   Default output is a tab separated header and tab separated data items.
   """
   import csv 

   # Sometimes the file has a very annoying initial # character on the first line.
   # We need to delete this character or replace it with a space.

   # Check annulus parameter
   if minradius > radius:
      # The min radius can't be greater than the radius
      minradius = 0.0

   if catalogue:
       cols = list(catalogue[0].keys())
       t = catalogue
   else:
       f = open(filename)

       index = 0
       header = f.readline().strip()
       if header[0] == '#':
          # Skip the hash
          index = 1

       fieldnames = header[index:].strip().split(inputDelimiter)

       # The file pointer is now at line 2

       t = csv.DictReader(f, fieldnames = fieldnames, delimiter=inputDelimiter, skipinitialspace = True)
       cols = t.fieldnames

   header = ''
   tableRow = ''
   body = []

   basename = os.path.basename(filename)

   resultsTable = []

   i = 0
   for coord in coordinatePairs:
      for row in t:
         raCat = row[raIndex]
         decCat = row[decIndex]

         separation = getAngularSeparation(coord[0], coord[1], raCat, decCat)
         if separation < radius and separation > minradius:
            # Add the returned row (there may be more than one) and the object counter
            resultsTable.append([row, separation, i])
      i += 1


   if resultsTable:
      # Column headers
      for name in cols:
         # Change names of the RA/DEC columns so the DS9 catalogue reader can read them
         header += "%s%s" % (name, delimiter)
      header += "%s%s%s%s%s" % ('filename', delimiter, 'separation', delimiter, 'object_id')

      # Data

      for row in resultsTable:
         tableRow = ''
         for name in cols:
            tableRow += "%s%s" % (row[0][name], delimiter)
            #print "%s\t" % col,

         tableRow += "%s%s%s%s%s" % (basename, delimiter, row[1], delimiter, row[2])
         body.append(tableRow)

   if not catalogue:
       f.close()

   return header, body



# 2014-08-05 KWS Generate a tab-separated-variable file from a CMF

def generateTSVfromCMF(filename, delimiter='\t'):
   """Generate a TSV file from a CMF file."""

   from astropy.io import fits as p

   h = t = cols = None
   h = p.open(filename)
   t = h[1].data
   cols = h[1].columns

   header = ''

   for name in cols.names:
      # Change names of the RA/DEC columns so the DS9 catalogue reader can read them
      header += "%s%s" % (name, delimiter)

   print(header)

   for row in t:
      tableRow = ''
      for name in cols.names:
         tableRow += "%s%s" % (row[name], delimiter)
      print(tableRow)

   return


# 2011-06-21 KWS New code added

# J2000 to Galactic coordinates calculation
# This code extracted from a JavaScript utility
# and converted into Python


J2000toGalactic = [
                   -0.054875529, -0.873437105, -0.483834992,
                    0.494109454, -0.444829594,  0.746982249,
                   -0.867666136, -0.198076390,  0.455983795
                  ]

# 2015-01-04 KWS More accurate values from Liu et al Reconsidering the galactic coordinate system, 2010
#                When implemented, don't forget to alter the C++ code equivalent
#J2000toGalactic = [-0.054875539390, -0.873437104725, -0.483834991775,
#                   +0.494109453633, -0.444829594298, +0.746982248696,
#                   -0.867666135681, -0.198076389622, +0.455983794523]

# 2015-01-04 KWS More accurate values from Liu et al Reconsidering the galactic coordinate system, 2010
#                When implemented, don't forget to alter the C++ code equivalent

# 2015-01-04 KWS Convert back from galactic to J2000. Is this not just a transposition of the original matrix??
GalactictoJ2000 = [-0.054875539390, +0.494109453633, -0.867666135681,
                   -0.873437104725, -0.444829594298, -0.198076389622,
                   -0.483834991775, +0.746982248696, +0.455983794523]

# 2015-06-13 KWS Ecliptic to Equatorial matrix
ETA = math.radians(23.4333333333333)

EcliptictoJ2000 = [1.0, 0.0, 0.0,
                   0.0, math.cos(ETA), -math.sin(ETA),
                   0.0, math.sin(ETA), math.cos(ETA)]

# returns a radec array of two elements
def transform ( coords, matrix ):
   """transform.

   Args:
        coords:
        matrix:
   """
   pi = math.pi

   r0 = calculate_cartesians(coords[0], coords[1]) 

   s0 = [
         r0[0]*matrix[0] + r0[1]*matrix[1] + r0[2]*matrix[2], 
         r0[0]*matrix[3] + r0[1]*matrix[4] + r0[2]*matrix[5], 
         r0[0]*matrix[6] + r0[1]*matrix[7] + r0[2]*matrix[8]
        ] 
 
   r = math.sqrt ( s0[0]*s0[0] + s0[1]*s0[1] + s0[2]*s0[2] )

   result = [ 0.0, 0.0 ]
   result[1] = math.asin ( s0[2]/r )

   cosaa = ( (s0[0]/r) / math.cos(result[1] ) )
   sinaa = ( (s0[1]/r) / math.cos(result[1] ) )
   result[0] = math.atan2 (sinaa,cosaa)
   if result[0] < 0.0:
      result[0] = result[0] + pi + pi

   # Convert to degrees

   result[0] = math.degrees(result[0])
   result[1] = math.degrees(result[1])

   return result


# 2015-01-06 KWS Hammer projection calculation - derived from a MATLAB routine extracted
#                from http://www.astro.caltech.edu/~eran/MATLAB/Map.html

def pr_hammer(Long,Lat,R):
   """pr_hammer.

   Args:
        Long:
        Lat:
        R:
   """
   Long = math.radians(Long)
   Lat = math.radians(Lat)

   X = 2.0*R*math.sqrt(2)*math.cos(Lat)*math.sin(Long/2)/math.sqrt(1+math.cos(Lat)*math.cos(Long/2))
   Y = R*math.sqrt(2)*math.sin(Lat)/math.sqrt(1+math.cos(Lat)*math.cos(Long/2))

   return X,Y


# 2012-03-07 KWS Created redshiftToDistance calculator based on our C++ code,
#                which is itself based on Ned Wright's Cosmology Calculator code.
# 2023-04-26 KWS Pass in H0 - e.g. lower value for Planck cosmology.

def redshiftToDistance(z, H0 = 70.0):
   """redshiftToDistance.

   Args:
        z:
        H0: Hubble constant (km s-1 Mpc-1, default = 70.0)
   """

   # Cosmological Parameters (to be changed if required)
   WM = 0.3           # Omega_matter
   WV = 0.7           # Omega_vacuum
   #H0 = 70.0           # Hubble constant (km s-1 Mpc-1)

   # Other variables
   h = H0/100.0
   WR = 4.165E-5/(h*h)     # Omega_radiation
   WK = 1.0-WM-WV-WR       # Omega_curvature = 1 - Omega(Total)
   c = 299792.458          # speed of light (km/s)

   # Arbitrarily set the values of these variables to zero just so we can define them.

   DCMR  = 0.0             # comoving radial distance in units of c/H0
   DCMR_Mpc = 0.0          # comoving radial distance in units of Mpc
   DA = 0.0                # angular size distance in units of c/H0
   DA_Mpc = 0.0            # angular size distance in units of Mpc
   DA_scale = 0.0          # scale at angular size distance in units of Kpc / arcsec
   DL = 0.0                # luminosity distance in units of c/H0
   DL_Mpc = 0.0            # luminosity distance in units of Mpc
   DMOD = 0.0              # Distance modulus determined from luminosity distance
   a = 0.0                 # 1/(1+z), the scale factor of the Universe

   az = 1.0/(1.0+z)        # 1/(1+z), for the given redshift

   # Compute the integral over a=1/(1+z) from az to 1 in n steps
   n = 1000
   for i in range(n):
      a = az+(1.0-az)*(i+0.5)/n
      adot = math.sqrt(WK+ (WM/a) + (WR/(math.pow(a,2))) +(WV*math.pow(a,2)))
      DCMR = DCMR + 1.0/(a*adot)

   DCMR = (1.0-az)*DCMR/n           # comoving radial distance in units of c/H0
   DCMR_Mpc = (c/H0)*DCMR           # comoving radial distance in units of Mpc

   # Tangental comoving radial distance
   x = math.sqrt(abs(WK))*DCMR
   if x > 0.1:
      if WK > 0.0:
         ratio = 0.5*(math.exp(x)-math.exp(-x))/x
      else:
         ratio = math.sin(x)/x
   else:
      y = math.pow(x,2)
      if WK < 0.0:
         y=-y
      ratio = 1 + y/6.0 + math.pow(y,2)/120.0

   DA = az*ratio*DCMR               #angular size distance in units of c/H0
   DA_Mpc = (c/H0)*DA               #angular size distance in units of Mpc
   DA_scale = DA_Mpc/206.264806     #scale at angular size distance in units of Kpc / arcsec
   DL = DA/math.pow(az,2)                #luminosity distance in units of c/H0
   DL_Mpc = (c/H0)*DL               #luminosity distance in units of Mpc
   DMOD = 5*math.log10(DL_Mpc*1e6)-5     #Distance modulus determined from luminosity distance


   results = \
   {
      "dcmr_mpc": DCMR_Mpc,
      "da_mpc": DA_Mpc,
      "da_scale": DA_scale,
      "dl_mpc": DL_Mpc,
      "dmod": DMOD,
      "z" : z
   }

   return results


# Some common error codes for bad HTTP access

OK                 = 0
PAGE_NOT_FOUND     = 1
BAD_SERVER_ADDRESS = 2
HTTP_ERROR         = 3

def getRemoteWebPage(url, username=None, password=None, realm=None):
   """getRemoteWebPage.

   Args:
        url:
        username:
        password:
        realm:
   """
   import urllib.request, urllib.error, urllib.parse

   responseErrorCode = OK
   responsePage = ''

   if username and password:
      # Use authentiction credentials

      # We want to do some basic authentication.
      # NOTE - if we don't know the Realm, just enter None for the first
      #        parameter of add_password
      #realm = 'Restricted Section'

      passman = urllib.request.HTTPPasswordMgrWithDefaultRealm()
      passman.add_password(realm, url, username, password)
      authhandler = urllib.request.HTTPBasicAuthHandler(passman)
      # create the AuthHandler

      opener = urllib.request.build_opener(authhandler)
      urllib.request.install_opener(opener)

   try:
      req = urllib.request.Request(url)
      responsePage = urllib.request.urlopen(req).read()

   except urllib.error.HTTPError as e:
      if e.code == 404:
         print("Page not found. Perhaps the server has not processed the request yet")
         responseErrorCode = PAGE_NOT_FOUND
      else:
         print(e)
         responseErrorCode = HTTP_ERROR

   except urllib.error.URLError as e:
      print("Bad URL")
      responseErrorCode = BAD_SERVER_ADDRESS

   return (responsePage, responseErrorCode)

# 2012-10-04 KWS Moved enum to utils.py
def enum(**enums):
   """enum.

   Args:
        enums:
   """
   return type('Enum', (), enums)

def ra_dec_id(ra, dec):
   """ra_dec_id.

   Args:
        ra:
        dec:
   """
   id = 1000000000000000000

   # Calculation from Decimal Degrees:

   ra_hh   = int(ra/15)
   ra_mm   = int((ra/15 - ra_hh)*60.0)
   ra_ss   = int(((ra/15 - ra_hh)*60.0 - ra_mm)*60.0)
   ra_fff  = int((((ra/15 - ra_hh)*60.0 - ra_mm)*60.0 - ra_ss)*1000.0)

   h = None

   if (dec >= 0):
      h = 1
   else:
      h = 0
      dec = dec * -1

   dec_deg = int(dec)
   dec_mm  = int((dec - dec_deg)*60.0)
   dec_ss  = int(((dec - dec_deg)*60.0 - dec_mm)*60.0)
   dec_ff  = int(((((dec - dec_deg)*60.0 - dec_mm)*60.0) - dec_ss)*100.0)

   id += (ra_hh *   10000000000000000)
   id += (ra_mm *     100000000000000)
   id += (ra_ss *       1000000000000)
   id += (ra_fff *         1000000000)

   id += (h *               100000000)
   id += (dec_deg *           1000000)
   id += (dec_mm *              10000)
   id += (dec_ss *                100)
   id += dec_ff

   return id

# 2013-02-04 KWS Create an object from a dictionary.
class Struct:
    """Create an object from a dictionary. Ensures compatibility between raw scripted queries and Django queries."""
    def __init__(self, **entries): 
        """__init__.

        Args:
            entries:
        """
        self.__dict__.update(entries)


# 2013-02-04 KWS Have decided to move some generic lightcurve processing code to utils.
#                Why not lightcurvequeries or commonqueries code? Because the common
#                queries and lightcurvequeries code is actually PS1 specific. This code
#                is (almost) completely generic.

# How we get the lcdata is left external to these methods.  We just want to reduce it
# down to colour vs MJD. This makes the code more portable for use inside or outside
# the web app. The whole set of lcdata is sent in (so the originating query only
# needs to be done once).  Each method will strip out its required filters.

def getReducedLC(filterdata, recurrencePeriod = 0.5):
    """Return a reduced array per filter. We need to do this because of PS1 skycell overlaps.
       The recurrence period by default is half a day, counting forwards."""

    # This method exists because of skycell overlaps.  We're dealing with the same
    # data, so produce a MEAN error rather than adding them in quadrature.

    import numpy as n

    # With overlapping skycells or multiple samples per filter
    # we only want the average mag vs average mjd

    filterAvgArray = []
    mjdMax = 0
    firstPass = True
    mags = []
    mjds = []
    magerrs = []
    for mjd, mag, magerr in filterdata:
        # Create a new g array with mean mjd, mean mag, mean error.

        if firstPass:
            mjdMax = mjd + recurrencePeriod
            firstPass = False

        if mjd > mjdMax: # which it can never be 1st time round
            mjdAvg = n.array(mjds).mean()
            magAvg = n.array(mags).mean()
            magErrAvg = n.array(magerrs).mean()
            filterAvgArray.append([mjdAvg, magAvg, magErrAvg])
            mjds = []
            mags = []
            magerrs = []
            mjdMax = mjd + recurrencePeriod

        mjds.append(mjd)
        mags.append(mag)
        magerrs.append(magerr)

    # Clean up the last set of mjds and mags
    if mjds:
        mjdAvg = n.array(mjds).mean()
        magAvg = n.array(mags).mean()
        magErrAvg = n.array(magerrs).mean()
        filterAvgArray.append([mjdAvg, magAvg, magErrAvg])

    return filterAvgArray


# 2013-02-04 KWS Added utility to get colour from two different sets of filter data
def getColour(cData1, cData2, dateDiffLimit, interpolate = False):
    '''Create an array of colour1 - colour2 points vs MJD'''
    #Algorithm:

    # Start with colour1
    # Some colour data is intra-day, but need to choose ONE recurrence of colour1 and ONE
    # recurrence of colour2 because of skycell overlaps. Probably choose mean of both.

    c1c2Colour = []

    # We can't do a colour plot if one of the filters is missing.
    if not cData1 or not cData2:
        return c1c2Colour

    # The filter arrays should be ordered by MJD. This means we should only need to walk forward
    # through the array.

    reducedC1 = getReducedLC(cData1)
    reducedC2 = getReducedLC(cData2)

    c1Dates = [row[0] for row in reducedC1]
    c2Dates = [row[0] for row in reducedC2]

    # OK We now have 2 reduced lightcurves.  Now subtract them.


    for c1idx, c1Date in enumerate(c1Dates):
        # Find the nearest r value to each g MJD
        c2idx = min(list(range(len(c2Dates))), key=lambda i: abs(c2Dates[i]-c1Date))

        if interpolate:
            # We want attempt to linearly interpolate, but I'm not sure
            # how I'll do that yet... I guess that if the nearest value is
            # within a specified period that's too far to average and the value
            # comes from a point in FRONT of the current date, we do a linear
            # interpolation from the date previous.

            pass
            
            #xx = n.array([parametri1['r'],parametri1['z']])
            #yy2 = n.array([cm['r'],cm['z']])
            #maginterp2=n.interp(parametri1['i'],xx,yy2)

        if abs(c1Date - c2Dates[c2idx]) < dateDiffLimit:
            colour = reducedC1[c1idx][1] - reducedC2[c2idx][1]
            avgDate = (reducedC1[c1idx][0] + reducedC2[c2idx][0])/2
            error = math.sqrt(reducedC1[c1idx][2] * reducedC1[c1idx][2] + reducedC2[c2idx][2] * reducedC2[c2idx][2])
            c1c2Colour.append([avgDate, colour, error])
            #print avgDate, colour

    return c1c2Colour


def getColourStats(colourData):
    """getColourStats.

    Args:
        colourData:
    """

    import numpy as n

    x = n.array(colourData)[:,0]
    y = n.array(colourData)[:,1]

    meanColour = y.mean()

    # We can rewrite the line equation as y = Ap, where A = [[x 1]]
    # and p = [[m], [c]]. Now use lstsq to solve for p

    A = n.vstack([x, n.ones(len(x))]).T

    # In this case the gradient is the colour evolution
    gradient, intercept = n.linalg.lstsq(A, y)[0]

    return meanColour, gradient


# 2013-02-15 KWS Added RMS scatter calculation code.  The objectInfo object
#                is a list of dictionaries with at least "RA" and "DEC" keys.

def calcRMS(objectInfo, avgRa, avgDec, rms = None):
   """calcRMS.

   Args:
        objectInfo:
        avgRa:
        avgDec:
        rms:
   """
   sep = sepsq = 0

   for objectRow in objectInfo:
      delra = (avgRa-objectRow["RA"]) * math.cos(math.radians(avgDec))
      deldec = avgDec - objectRow["DEC"]
      delra *= 3600
      deldec *= 3600
      sep = math.sqrt(delra**2 + deldec**2)

      if rms:
         if sep < (2 * rms):
            sepsq = sepsq + delra**2 + deldec**2
      else:
         sepsq = sepsq + delra**2 + deldec**2

   rms = math.sqrt(sepsq/len(objectInfo))
   rms = round(rms, 3)
   return rms



def calculateRMSScatter(objectInfo):
   """calculateRMSScatter.

   Args:
        objectInfo:
   """

   ### PRINT DETECTION INFORMATION & DETERMINE RMS SEPARATION FROM AVERAGE POSITION ###
   # 2017-10-30 KWS Set initial variables to zero, not equal to each other = 0.
   sep = 0
   totalRa = 0
   totalDec = 0
   sepsq = 0

   # Return negative RMS if no objects in the list (shouldn't happen)
   if len(objectInfo) == 0:
      return -1.0

   for objectRow in objectInfo:
      totalRa += objectRow["RA"]
      totalDec += objectRow["DEC"]

   avgRa = totalRa / len(objectInfo)
   avgDec = totalDec / len(objectInfo)

   #print "\taverage RA = %f, average DEC = %f" % (avgRa, avgDec)

   rms = calcRMS(objectInfo, avgRa, avgDec)

   ## APPLY 2-SIGMA CLIPPING TO THE RMS SCATTER -- TO REMOVE OUTLIERS (TWO ITERATIONS) ####

   rms = calcRMS(objectInfo, avgRa, avgDec, rms = rms)
   rms = calcRMS(objectInfo, avgRa, avgDec, rms = rms)

   return avgRa, avgDec, rms


class SetupMySQLSSHTunnel:
    """Setup SSH tunnel to remote MySQL server"""

    tunnelIsUp = False

    def checkServer(self, address, port):
        """Check that the TCP Port we've decided to use for tunnelling is available"""
        # Create a TCP socket
        import socket
        s = socket.socket()
        sys.stderr.write("Attempting to connect to %s on port %s\n" % (address, port))
        try:
            s.connect((address, port))
            sys.stderr.write("Connected to %s on port %s\n" % (address, port))
            return True
        except socket.error as e:
            sys.stderr.write("Connection to %s on port %s failed: %s\n" % (address, port, e))
            return False


    def __init__(self, sshUser, gateway, internalIP, sshPort):
        """__init__.

        Args:
            sshUser:
            gateway:
            internalIP:
            sshPort:
        """
        # Check that the tunnel is up.  If not, setup the tunnel.
        # NOTE: The public key of the user running this code on this machine must be installed on Starbase
        import time, subprocess
        localHostname = "127.0.0.1"
        mysqlPort = 3306

        self.tunnelIsUp = self.checkServer(localHostname, sshPort)

        if not self.tunnelIsUp:
            # Setup the tunnel
            process = subprocess.Popen("ssh -fnN %s@%s -L %d:%s:%d" % (sshUser, gateway, sshPort, internalIP, mysqlPort), shell=True, close_fds=True)
            time.sleep(2)
            self.tunnelIsUp = self.checkServer(localHostname, sshPort)


# 2013-08-06 KWS Added Minor Planet interrogation code
def slices(s, *args):
    """Code to split a string into fixed fields defined by list of numbers provided in args"""
    position = 0
    for length in args:
        yield s[position:position + length].strip()
        position += length


def extractMPInformation(htmlPage):
    """Parse the data returned by the MP Center into a dictionary"""

    from BeautifulSoup import BeautifulSoup
    movers = []
    soup = BeautifulSoup(BeautifulSoup(htmlPage).prettify())
    preData = soup.findAll('pre')

    if len(preData) == 1:
        if preData[0].text is not None:
            dataRows = preData[0].text.split('\n')
            # We have some results.  Skip the 1st 2 lines (header line, one blank line)
            if len(dataRows) > 2:
                for line in dataRows[2:]:
                    row = list(slices(line,25, 11, 10, 6, 7, 7, 7, 7, 6, 100))
                    details = {'designation': row[0],
                               'ra': row[1],
                               'dec': row[2],
                               'V': row[3],
                               'raOff': row[4],
                               'decOff': row[5],
                               'raMot': row[6],
                               'decMot': row[7],
                               'orbit': row[8],
                               'comments': row[9]}

                    movers.append(details)

    return movers



#MINORPLANETURL = 'http://mpcapp1.cfa.harvard.edu/cgi-bin/mpcheck.cgi'
#MINORPLANETURL = 'http://scully.cfa.harvard.edu/cgi-bin/mpcheck.cgi'
MINORPLANETURL = 'https://www.minorplanetcenter.net/cgi-bin/mpcheck.cgi'
# Note: This script was failing originally because the CGI script name
#       in the web URL is subtlely different from the one used to submit
#       requests.  (Web = checkmp.cgi.  Actual = mpcheck.cgi)


def sendMinorPlanetRequest(ra, dec, radius, mjd, limitingMag = 24.0):
   """Send a request to the Minor Planet Center. The ra and dec should be in decimal or colon delimited sexagesimal"""

   MP_SUCCESS = 1

   try:
      from collections import OrderedDict
   except ImportError:
      # python 2.6 or earlier, use backport
      from ordereddict import OrderedDict

   import urllib.request, urllib.parse, urllib.error, urllib.request, urllib.error, urllib.parse

   mpInfo = []

   try:
      ra = float(ra)
      dec = float(dec)
   except ValueError:
      # Attempt a sexagesimal conversion
      ra, dec = coords_sex_to_dec(ra, dec)
      if ra is None or dec is None:
         print("Can't parse the coordinates.")
         return []

   # The RA and dec must be in space delimited sexagesimal, but are given here in decimal
   raSex, decSex = coords_dec_to_sex(ra, dec, delimiter=' ')

   # Generally we have the date in MJD, so convert to date fraction

   year, month, day = getDateFractionMJD(mjd).split(' ')

   # Minimum radius of 5 arcmins and max of 300 arcmins allowed.
   if radius < 5:
      radius = 5
   if radius > 300:
      radius = 300

   # Setup an OrderedDict.  Used this because analysis of what the web page submits implies
   # that the values are sent in THIS order.  We'll do the same to simulate the web form
   # submission.
   values =  OrderedDict()

   values['year'] =  year
   values['month'] =  month
   values['day'] =  day
   values['which'] =  'pos'
   values['ra']  =  raSex
   values['decl']  =  decSex
   values['TextArea'] =  ''
   values['radius'] =  str(radius)
   values['limit'] =  str(limitingMag)
   values['oc'] =  '500'
   values['sort'] =  'd'
   values['mot'] =  'h'
   values['tmot'] =  's'
   values['pdes'] =  'u'
   values['needed'] =  'f'
   values['ps'] =  'n'
   values['type'] = 'p'

   data = urllib.parse.urlencode(values)

   txheaders =  {'User-agent' : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_5) AppleWebKit/536.30.1 (KHTML, like Gecko) Version/6.0.5 Safari/536.30.1'}

   # create a request object
   req = urllib.request.Request(MINORPLANETURL, data, txheaders)

   # Because the cookie handler is installed, this should result in two requests to the Server
   try:
       # Now send the file.
       psResponsePage = urllib.request.urlopen(req).read()
       mpInfo = extractMPInformation(psResponsePage)

   except IOError as e:
       print("Something went horribly wrong.")
       print(e)
       MP_SUCCESS = 0
   except Exception as e:
       print("Some other exception.")
       print(e)
       MP_SUCCESS = 0 

   return MP_SUCCESS, mpInfo

def checkMinorPlanetMatch(movers, matchRadius = 0.2, showMovers = True):
   """Check that the returned data from MPC is a match. Default offset threshold is 0.1 arcmin."""
   moverName = ''

   if showMovers:
      for mover in movers:
         print("Designation = %s, ra = %s (%s), dec = %s (%s), V = %s, RA Motion = %s, Dec Motion = %s" % (mover['designation'], mover['ra'], mover['raOff'], mover['dec'], mover['decOff'], mover['V'], mover['raMot'], mover['decMot']))

   # The movers are organised in order of increasing angular separation.
   # If the 1st row doesn't match, don't bother with the rest.
   if len(movers) > 0:
      if showMovers:
         print("%d results" % len(movers))
      # Get the offests.  We don't care which direction they are in. Value should be < 1.0 arcmins.
      if movers[0]['raOff'] and movers[0]['decOff']:
         # Get rid of the NESW designations
         raOff = decOff = None
         try:
            raOff = float(movers[0]['raOff'].replace('S','').replace('N','').replace('E','').replace('W',''))
            decOff = float(movers[0]['decOff'].replace('S','').replace('N','').replace('E','').replace('W',''))
         except ValueError as e:
            print("Can't convert the offsets %s, %s. Unable to check them." % (movers[0]['raOff'], movers[0]['decOff']))
            return moverName

         if raOff is not None and decOff is not None and raOff < matchRadius and decOff < matchRadius:
            if showMovers:
               print("Mover %s is a match. V = %s. RA Motion = %s, Dec Motion = %s" % (movers[0]['designation'], movers[0]['V'], movers[0]['raMot'], movers[0]['decMot']))
            moverName = movers[0]['designation']

   return moverName


# 2013-12-12 KWS Added option to return directories only
def find(pattern, path, directoriesOnly = False):
    """Find all files or directories that match a pattern"""
    import os, fnmatch
    result = []
    for root, dirs, files in os.walk(path):
        if directoriesOnly:
            for name in dirs:
                if fnmatch.fnmatch(name, pattern):
                    result.append(os.path.join(root, name))
        else:
            for name in files:
                if fnmatch.fnmatch(name, pattern):
                    result.append(os.path.join(root, name))
    return result


# 2013-11-15 KWS Added a new processing_flags column to PS1 database.  Here's what the
#                flags mean:
# 2015-03-19 KWS Added new flags to the flags table.
# 2016-01-19 KWS Added new mpc flag to the flags table.  Altered name of 'mover' to eph (ephemeris).
# 2016-06-07 KWS Added new tns (nameserver) and nondets (non detection stamp request) flags
PROCESSING_FLAGS = {'unprocessed':    0x0000,
                    'brightstar':     0x0001,
                    'convolution':    0x0002,
                    'ghost':          0x0004,
                    'eph':            0x0008,
                    'locationmap':    0x0010,
                    'eyeballed':      0x0020,
                    'stamps':         0x0040,
                    'reffinders':     0x0080,
                    'targetfinders':  0x0100,
                    'mpc':            0x0200,
                    'tns':            0x0400,
                    'nondets':        0x0800,
                    'moons':          0x1000}


def xy2sky(filename, x, y):
   '''This is a wrapper for WCSTools xy2sky'''

   ra = dec = None
   import subprocess, csv, io
   p = subprocess.Popen(['xy2sky','-d' , filename, x, y], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
   output, errors = p.communicate()
   line = list(csv.reader(io.StringIO(output.strip().decode('utf-8')), delimiter=' ', skipinitialspace = True))
   ra = float(line[0][0])
   dec = float(line[0][1])
   return ra, dec

# 2015-03-16 KWS New code to wrap sky2xy. Required for making finders and
#                otherwise annotating images with skycoords we already know.
def sky2xy(filename, ra, dec):
   '''This is a wrapper for WCSTools sky2xy'''

   x = y = None
   import subprocess, csv, io
   p = subprocess.Popen(['sky2xy', filename, str(ra), str(dec)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
   output, errors = p.communicate()
   line = list(csv.reader(io.StringIO(output.strip().decode('utf-8')), delimiter=' ', skipinitialspace = True))
   x = float(line[0][4])
   y = float(line[0][5])
   return x, y


# 2015-01-15 KWS Similar to splitList in multiprocessingUtils
def divideList(inputList, nChunks = 1, listChunkSize = None):
   '''Divide a list into chunks'''

   # Break the list of candidates up into the number of CPUs

   listChunks = []

   listLength = len(inputList)
   if listChunkSize is not None:
      if listLength > listChunkSize:
         nChunks = listLength / listChunkSize
         if listLength % listChunkSize:
            # Does the list divide evenly?
            # If not, add 1 to the number of chunks
            nChunks += 1
      else:
         nChunks = 1

   else:
      if nChunks > 1:
         if listLength < nChunks:
            nChunks = listLength
         listChunkSize = int(round((listLength * 1.0) / nChunks))



   if nChunks > 1:
      for i in range(nChunks-1):
         listChunks.append(inputList[i*listChunkSize:i*listChunkSize+listChunkSize])
      # Append the last (probably uneven) chunk.  Might have 1 extra or 1 fewer members.
      listChunks.append(inputList[(i+1)*listChunkSize:])

   else:
      listChunks = [inputList]

   return nChunks, listChunks


# 2015-01-15 KWS It turns out that you can pass xy2sky as many pairs of coords as you like,
#                with the limit that you can't pass more items than the length of ARG_MAX
#                will allow. On the mac, ARG_MAX is 262144.  On linux it's 10 times larger.
#                Let's work on the basis that you can't pass more than 5000 coordinate pairs
#                at a time.  Hence we need to split the input list into 5000 coordinate pair
#                chunks, remembering that we need to do the remainder.
def xy2skyList(filename, coordList):
   '''This is a wrapper for WCSTools xy2sky'''

   import subprocess, csv, io

   # There's a limit to the number of characters you can send to xy2sky, so let's
   # arbitrarily set the list length to 4000 sets of coordinates.

   n, coordListChunks = divideList(coordList, listChunkSize = 4000)

   raDecPairs = []
   for row in coordListChunks:

      args = ['xy2sky','-d', filename]
      for coord in row:
         args.append(str(coord[0]))
         args.append(str(coord[1]))

      p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
      output, errors = p.communicate()
      lines = list(csv.reader(io.StringIO(output.strip().decode('utf-8')), delimiter=' ', skipinitialspace = True))
      for line in lines:
         ra = float(line[0])
         dec = float(line[1])
         raDecPairs.append([ra, dec])

   return raDecPairs


def readPhotpipeDCMPFile(filename, xy2skyConvertByList = True):
   """readPhotpipeDCMPFile.

   Args:
        filename:
        xy2skyConvertByList:
   """
   #from astropy.wcs import wcs # We may need to modify which wcs library we use. This one is part of Ureka.
   # 2014-09-12 KWS Yet again had to try another wcs solution.  This time resort to external xy2sky.
   #import pywcs as wcs # pywcs from STScI, installed via PIP.
   import csv, io
   from astropy.io import fits as pf

   h = pf.open(filename)
   h.verify('fix') # Non-standard keywords.  Tell PyFITS to fix them.  Can't use WCS without this.

   # These photpipe dcmp files are ASCII files with a FITS header.  PyFITS *will* complain
   # but we should be able to get hold of the header OK.

   header = h[0].header
   mjd = header['MJD-OBS']
   exptime = header['EXPTIME']
   zeropt = None

   try:
      zeropt = header['ZPTMAGAV']
   except KeyError as e:
      print(e)
      try:
         # Maybe it's not a diff zeropt
         zeropt = header['ZPTMAG']
      except KeyError as e:
         # If all else fails - pick up the quick-look ZP if it's there.
         print(e)
         try:
            zeropt = header['QL_ZP']
         except KeyError as e:
            print("Cannot read the Zero Point info")
            print(e)
            return []


   del header['COMMENT']

   data = h[0].data.tostring()

   headerFields = []

   try:
      numberOfCols = header['NCOLTBL']
   except KeyError as e:
      print("Cannot read the DCMP table column headers.")
      print(e)
      return []

   try:
      for i in range(numberOfCols):
         headerFields.append(header['COLTBL%s'%(i+1)])
   except KeyError as e:
      print("Cannot read the DCMP table column headers.")
      print(e)
      return []

   headerLine = ' '.join(headerFields)
   headerLine += '\n'

   asciiData = headerLine + data

   dataDictFile = csv.DictReader(io.StringIO(asciiData.decode('utf-8')), delimiter=' ', skipinitialspace = True)

   # While we're here, let's add the RA and Dec. Don't forget we can only iterate once,
   # so let's create a list of dicts and return it.
   #wcs = wcs.WCS(header)

   dcmpData = []

   if xy2skyConvertByList:
      xyList = []
      # First scan through the list and add the exptime, mjd and zeropt
      # and grabbing the x and y values as we go.
      for row in dataDictFile:
         # 2015-06-07 KWS Remove None key - I've no idea how it gets there
         try:
            del row[None]
         except KeyError:
            print("no None Keys")

         row['exptime'] = exptime
         row['mjd'] = mjd
         row['zeropt'] = zeropt
         xyList.append([row['Xpos'], row['Ypos']])
         dcmpData.append(row)

      # Now pass the list of [x, y] values to the bulk converter
      raDecList = xy2skyList(filename, xyList)
      if len(raDecList) != len(xyList):
         # Something went horribly wrong
         dcmpData = []
      else:
         # OK to continue. Iterate through each row and
         # add the RA and Dec to each dict
         for i in range(len(xyList)):
            dcmpData[i]['RA'] = raDecList[i][0]
            dcmpData[i]['Dec'] = raDecList[i][1]

   else:
      for row in dataDictFile:
         #ra, dec = wcs.wcs_pix2sky(float(row['Xpos']),float(row['Ypos']), 1)
         ra, dec = xy2sky(filename, row['Xpos'], row['Ypos'])
         row['RA'] = ra
         row['Dec'] = dec
         # 2015-01-12 KWS Adding in exposure time, mjd and zeropoint so that we can do a one-off
         #                conversion to (e.g.) JSON and read the info from there when doing cross
         #                matching.
         row['exptime'] = exptime
         row['mjd'] = mjd
         row['zeropt'] = zeropt
         dcmpData.append(row)

   return header, dcmpData

def createDS9RegionFile(dirName, data, radec = True, size = 0.02, colour = 'cyan'):
   """
   Generic code for creating a DS9 region file

   **Key Arguments:**
       - ``filename`` -- The filename of the region file
       - ``data``   -- List of rowinates in RA and DEC (decimal degrees) or x and y, plus a label
       - ``radec``    -- Boolean value indicating ra and dec (True) or x and y (False) - not curently used
       - ``label``    -- the object label
       - ``size``     -- size of the markers
       - ``colour``   -- colour of the markers

    **Return:**
       - None

    **Todo**
       - Implement the x, y format

   """

   # Open file and print header

   previousExpName = ''

   rf = None

   for row in data:
      expName = row[0]
      if expName != previousExpName:
         if rf:
            rf.close()
         rf = open(dirName + expName + '.reg', 'w')
         rf.write('# Region file format: DS9 version 4.1\n' +
                  'global color=%s dashlist=8 3 width=1 font="helvetica 14 normal" select=1 highlite=1 dash=0 fixed=0 edit=1 move=1 delete=1 include=1 source=1\n' % (colour) +
                  'linear\n')
         rf.write('circle %f %f %.2f # color=%s text={%s}\n' % (row[1], row[2], size, colour, row[3]))
         previousExpName = expName
      else:
         rf.write('circle %f %f %.2f # color=%s text={%s}\n' % (row[1], row[2], size, colour, row[3]))
         
   if rf:
      rf.close()

# 2015-06-03 KWS Calculate Position Angle of body 1 wrt body 2
# 2017-08-30 KWS Finally fixed the PA calculation. It should return a value
#                between -90 and +270. (Must be a convention...)

def calculatePositionAngle(ra1, dec1, ra2, dec2):
   """
   Calculate the position angle (bearing) of body 1 w.r.t. body 2.  If either set of
   coordinates contains a colon, assume it's in sexagesimal and automatically
   convert into decimal before doing the calculation.
   """

   if ':' in str(ra1):
      ra1 = sexToDec(ra1, ra=True)
   if ':' in str(dec1):
      dec1 = sexToDec(dec1, ra=False)
   if ':' in str(ra2):
      ra2 = sexToDec(ra2, ra=True)
   if ':' in str(dec2):
      dec2 = sexToDec(dec2, ra=False)

   # 2013-10-20 KWS Always make sure that the ra and dec values are floats

   positionAngle = None

   if ra1 is not None and ra2 is not None and dec1 is not None and dec2 is not None:
      ra1 = math.radians(float(ra1))
      ra2 = math.radians(float(ra2))
      dec1 = math.radians(float(dec1))
      dec2 = math.radians(float(dec2))

      numerator = math.sin(ra1 - ra2)
      denominator = math.cos(dec2) * math.tan(dec1) - math.sin(dec2) * math.cos(ra1 - ra2)
      positionAngle = math.degrees(math.atan(numerator/denominator))
      if denominator < 0.0:
         positionAngle = 180.0 + positionAngle

   return positionAngle

# 2017-08-30 KWS Are the object coordinates inside an ATLAS footprint?
ATLAS_CONESEARCH_RADIUS = 13888.7 # (i.e. sqrt(5280 * 1.86^2 + 5280 * 1.86^2) )
ATLAS_HALF_WIDTH = 5280 * 1.86 # (also = 13888.7 * cos(45) )

def isObjectInsideATLASFootprint(objectRA, objectDec, fpRA, fpDec, separation = None):
    """isObjectInsideATLASFootprint.

    Args:
        objectRA:
        objectDec:
        fpRA:
        fpDec:
        separation:
    """

    if separation is None:
        # We need to calculate the angular separation. This is expensive, so if
        # we already have this value, use the one sent.
        separation = getAngularSeparation(objectRA, objectDec, fpRA, fpDec)

    pa = calculatePositionAngle(objectRA, objectDec, fpRA, fpDec) + 90.0
    if pa >= 90.0 and pa < 180.0:
        pa = pa - 90.0
    if pa >= 180.0 and pa < 270.0:
        pa = pa - 180.0
    if pa >= 270.0:
        pa = pa - 270.0

    # Bearing (pa) only needs to be between 45 and -45 degrees.
    pa -= 45.0
    pa = abs(pa)
    dist = float(separation) * math.cos(math.radians(45.0 - pa))
    inside = True
    if dist > ATLAS_HALF_WIDTH:
        inside = False

    return inside



# Add a grammatical join. Used by the Transient name server when adding lists of users
# to the comments section.
def grammarJoin(words):
    """grammarJoin.

    Args:
        words:
    """
    return reduce(lambda x, y: x and x + ' and ' + y or y,
                 (', '.join(words[:-1]), words[-1])) if words else ''

COORDS_DEC_REGEX = ""
#COORDS_SEX_REGEX = "^([0-2][0-9])[^0-9]+([0-5][0-9])[^0-9]+([0-5][0-9])(\.[0-9]+){0,1}[^0-9+\-]+([+-]){0,1}([0-9][0-9])[^0-9]+([0-5][0-9])[^0-9]+([0-5][0-9])(\.[0-9]+){0,1}[^0-9 ]{0,1}( ([0-9][0-9]{0,1})){0,1}"
#COORDS_SEX_REGEX = "^([0-2][0-9])[^0-9]{0,1}([0-5][0-9])[^0-9]{0,1}([0-5][0-9])(\.[0-9]+){0,1}[^0-9+\-]{0,5}([+-]){0,1}([0-9][0-9])[^0-9]{0,1}([0-5][0-9])[^0-9]{0,1}([0-5][0-9])(\.[0-9]+){0,1}[^0-9 ]{0,1}( +([0-9][0-9]{0,1})){0,1}"

# 2019-04-17 KWS Made the sexagesimal regex a bit more forgiving.
# 2024-04-10 KWS Allow up to 3 digits + fraction for the search radius.
#                                h    h               m    m                       s    s     .  f                       (+-)              d    d                    m    m               s    s     .  f                        (radius)
COORDS_SEX_REGEX = "^([0-2]{0,1}[0-9])[^0-9+\-\.]{0,}([0-5]{0,1}[0-9])[^0-9+\-\.]{0,}([0-5]{0,1}[0-9])(\.[0-9]+){0,1}[^0-9+\-\.]{0,}([+-]){0,1}([0-9]{0,1}[0-9])[^0-9+\-\.]{0,}([0-5]{0,1}[0-9])[^0-9+\-\.]{0,}([0-5]{0,1}[0-9])(\.[0-9]+){0,1}[^0-9+\-\.]{0,}(([0-9][0-9]{0,2}(\.[0-9]+){0,1})){0,1}$"
COORDS_SEX_REGEX_COMPILED = re.compile(COORDS_SEX_REGEX)

#COORDS_DEC_REGEX = "^([0-9]+(\.[0-9]+){0,1})[^0-9+\-]{0,5}([+-]{0,1}[0-9]+(\.[0-9]+){0,1})[^0-9 ]{0,1}( +([0-9][0-9]{0,1})){0,1}"
# 2019-04-17 KWS Made the decimal regex a bit more forgiving.
# 2024-04-10 KWS Allow up to 3 digits + fraction for the search radius.
#                            d.f                           (+-)            d.f                         (radius)
COORDS_DEC_REGEX = "^([0-9]+(\.[0-9]+){0,1})[^0-9+\-]{0,}([+-]{0,1}[0-9]+(\.[0-9]+){0,1})[^0-9]{0,}(([0-9][0-9]{0,2}(\.[0-9]+){0,1})){0,1}$"
COORDS_DEC_REGEX_COMPILED = re.compile(COORDS_DEC_REGEX)

# 2019-04-17 KWS Made the name search more forgiving and extended it to ZTF.
NAME_REGEX = "^(AT|SN|ATLAS|ASASSN-|ZTF|PS([1][\-]){0,1}){0,1} {0,1}([2][0]){0,1}([0-9][0-9][a-z]{1,7}|[0-9][0-9][A-Z])$"
NAME_REGEX_COMPILED = re.compile(NAME_REGEX)

def getObjectNamePortion(inputString):
    """getObjectNamePortion.

    Args:
        inputString:
    """
    # E.g. if the object name is '2016ffx' will return 16ffx
    #      If the object name is 'ATLAS16abc' will return 16abc
    namePortion = None
    name = NAME_REGEX_COMPILED.search(inputString)
    if name:
        prefix = name.group(1) if name.group(1) is not None else ''
        century = name.group(3) if name.group(3) is not None else ''
        namePortion = prefix + century + name.group(4)

    return namePortion

# 2019-04-30 KWS Changed the order of the match test. Try decimal then sexagesimal.
#                Also check the values of each sexagesimal field.
def getCoordsAndSearchRadius(inputString):
    """getCoordsAndSearchRadius.

    Args:
        inputString:
    """
    coords = {}
    ra = None
    dec = None
    radius = None

    sex = COORDS_SEX_REGEX_COMPILED.search(inputString)
    decimal = COORDS_DEC_REGEX_COMPILED.search(inputString)

    if decimal:
        ra = decimal.group(1)
        dec = decimal.group(3)
        radius = decimal.group(5)
        try:
            if float(ra) > 360.0 or float(ra) < 0.0 or float(dec) < -90.0 or float(dec) > 90.0:
                coords = {}
            else:
                coords['ra'] = ra
                coords['dec'] = dec
                coords['radius'] = radius

        except ValueError as e:
            coords = {}

    elif sex:
        hh = sex.group(1)
        mm = sex.group(2)
        ss = sex.group(3)
        ffra = sex.group(4) if sex.group(4) is not None else ''
        sign = sex.group(5) if sex.group(5) is not None else '+'
        deg = sex.group(6)
        mn = sex.group(7)
        sec = sex.group(8)
        ffdec = sex.group(9) if sex.group(9) is not None else ''
        try:
            if int(hh) > 24 or int(mm) > 59 or int(ss) > 59 or int(deg) > 90 or int(mn) > 59 or int(sec) > 59:
                coords = {}
            else:
                ra = "%s:%s:%s%s" % (hh, mm, ss, ffra)
                dec = "%s%s:%s:%s%s" % (sign, deg, mn, sec, ffdec)
                radius = sex.group(11)
                coords['ra'] = ra
                coords['dec'] = dec
                coords['radius'] = radius
        except ValueError as e:
            coords = {}

    return coords

# Return a string representing a float to digits decimal places, truncated.
# Used when we need to truncate an MJD to 3 decimal places for filename.
def truncate(f, digits):
    """truncate.

    Args:
        f:
        digits:
    """
    return ("{:.30f}".format(f))[:-30+digits]

# 2017-11-02 KWS Quick and dirty code to clean options dictionary as extracted by docopt.
def cleanOptions(options):
    """cleanOptions.

    Args:
        options:
    """
    cleanedOpts = {}
    for k,v in options.items():
        # Get rid of -- and <> from opts
        cleanedOpts[k.replace('--','').replace('<','').replace('>','')] = v

    return cleanedOpts

def nullValue(value):
   """nullValue.

   Args:
        value:
   """
   returnValue = None

   if value and value.strip():
      returnValue = value.strip()

   return returnValue


def floatValue(value):
   """floatValue.

   Args:
        value:
   """
   import numpy as n
   returnValue = None

   if value:
      try:
         f = float(value)
         if n.isfinite(f):
             returnValue = f
      except ValueError as e:
         pass

   return returnValue


def intValue(value):
   """intValue.

   Args:
        value:
   """
   returnValue = None

   if value:
      try:
         if '0x' in value:
             returnValue = int(value, 16)
         else:
             returnValue = int(value)
      except ValueError as e:
         pass

   return returnValue

# 2019-01-29 KWS Added "which" command.
def which(filename):
    """which.

    Args:
        filename:
    """
    for path in os.environ["PATH"].split(os.pathsep):
        fullpath = os.path.join(path, filename)
        if os.path.exists(fullpath) and os.access(fullpath, os.X_OK):
            return fullpath
    return None

def htmTriangleArea(level):
    """htmTriangleArea.

    Args:
        level:
    """
    skyInSqDegrees = 4.0 * math.pi * (180.0/math.pi)**2
    skyInSqArcsec = skyInSqDegrees * 3600.0 ** 2
    triangleArea = skyInSqArcsec/(8*4**level)
    return triangleArea


def fluxToMicroJansky(adu, exptime, zp):
    """fluxToMicroJansky.

    Args:
        adu: flux in adu - e.g. psf_inst_flux
        exptime: exposure time
        zp: zeropoint
    """

    factor = 10**(-0.4*(zp-23.9))
    uJy = adu/exptime*factor
    return uJy

# 2021-11-18 KWS Added code to grab the SFD extinction for PS1 and ATLAS filters.
def getSFDPanSTARRSATLASExtinction(ra, dec, dustmapDirectory, download = False):
    """getPanSTARRSATLASExtinction.

    Args:
        ra: right ascension in degrees
        dec: declination in degrees
        dustmapDirectory: directory where the SFD dustmaps are stored
        download: download the maps if they don't already exist
    """
    import os

    extinction = {}

    try:
        from astropy.coordinates import SkyCoord
    except ModuleNotFoundError as e:
        print (e)
        print ("Please install the astropy module.")
        return extinction

    try:
        from dustmaps.sfd import SFDQuery, fetch
    except ModuleNotFoundError as e:
        print (e)
        print ("Please install the dustmaps module.")
        return extinction

    from dustmaps.config import config
    config['data_dir'] = dustmapDirectory

    if not os.path.exists(dustmapDirectory + '/sfd/SFD_dust_4096_sgp.fits') or not os.path.exists(dustmapDirectory + '/sfd/SFD_dust_4096_ngp.fits'):
        if download == True:
            print("Downloading the SFD dustmap files...")
            if not os.path.exists(dustmapDirectory):
                os.makedirs(dustmapDirectory)
            try:
                fetch()
            except PermissionError as e:
                print (e)
                print ("No permission to write into the download directory.")
                return extinction
        else:
            print (e)
            print("SFD Maps not found! Please elect to download the maps!")
            return extinction

    coords = SkyCoord(ra, dec, unit='deg', frame='icrs')

    try:
        sfd = SFDQuery()
    except OSError as e:
        print (e)
        print ("Something went wrong - file is possibly corrupt. Try deleting the files and forcing a re-download.")
        return extinction
    except TypeError as e:
        print (e)
        print ("Something went wrong - file is possibly corrupt. Try deleting the files and forcing a re-download.")
        return extinction
    ebv = sfd(coords)

    # Schlegel, Finkbeiner, Davis PS1 Rv3.1 conversions from
    # https://ui.adsabs.harvard.edu/abs/1998ApJ...500..525S/abstract
    # https://ui.adsabs.harvard.edu/abs/2011ApJ...737..103S/abstract

    Rv31_PS1_g = 3.172
    Rv31_PS1_r = 2.271
    Rv31_PS1_i = 1.682
    Rv31_PS1_z = 1.322
    Rv31_PS1_y = 1.087

    extinction['A_gPS1'] = round(ebv * Rv31_PS1_g,3)
    extinction['A_rPS1'] = round(ebv * Rv31_PS1_r,3)
    extinction['A_iPS1'] = round(ebv * Rv31_PS1_i,3)
    extinction['A_zPS1'] = round(ebv * Rv31_PS1_z,3)
    extinction['A_yPS1'] = round(ebv * Rv31_PS1_y,3)

    # Calculating the ATLAS "c" and "o" from Tonry et al https://ui.adsabs.harvard.edu/abs/2018PASP..130f4505T/abstract
    extinction['A_c'] = round((0.49 * extinction['A_gPS1']) + (0.51 * extinction['A_rPS1']),3)
    extinction['A_o'] = round((0.55 * extinction['A_rPS1']) + (0.45 * extinction['A_iPS1']),3)

    return extinction


# This function expects a list of dicts with keys x, y, obs.
def calculateHeatMap(dataRows, resolution = 128, chipSize = 10560):
    """calculateHeatMap.

    Args:
        dataRows:
        resolution:
        chipSize:
    """

    import numpy as n

    matrix = None
    if resolution not in [8, 16, 32, 64, 128, 256, 512]:
        print("Heatmap resolution should be 8, 16, 32, 64, 128, 256 or 512")
        return matrix

    matrix = n.zeros((resolution,resolution), dtype=n.int)
    expmaps = {}

    oldExpname = ''
    numberOfRows = 0

    exps = set()
    for row in dataRows:
        x = int(float(row['x'])/(chipSize - 1) * resolution)
        #y = int(((chipSize - 1) - float(row['y']))/(chipSize - 1) * resolution)
        # For plotting we will need to flip the map, because the pixel coordinates have origin in top left, not bottom left.
        y = int(float(row['y'])/(chipSize - 1) * resolution)
        exps.add(row['obs'])

        if x >= 0 and y >= 0 and x < resolution and y < resolution:
            matrix[y][x] += 1

    mat = {'matrix': matrix, 'exps': exps}

    return mat

# 2023-01-03 KWS Get object name from remote nameserver.
# 2023-01-03 KWS Added a default 2 second timeout and a timeout error trap.
# 2024-01-07 KWS Added an alternative name, used in Pan-STARRS for the time being.
def getLocalObjectName(nameserverURL, nameserverToken, objectId, ra, dec, flagDate, dbName, timeout = 2, alias = None, insertDate = None):
    """getLocalObjectName.

    Args:
        nameserverURL: URL of nameserver API
        nameserverToken: API token
        objectId: Internal object ID
        ra: RA
        dec: Declination
        flagDate: Date the object was flagged
        dbName: Database name
        timeout: Connection timeout
        alias: An alias for the object (used in Pan-STARRS)
        insertDate: Date inserted

    Returns:
        Dictionary of HTTP status, name, counter, info
    """
    import requests
    from requests.exceptions import ConnectionError as RequestsConnectionError
    from requests.exceptions import Timeout as RequestsConnectionTimeoutError

    counter = None
    name = None
    message = None
    info = None

    reply = None

    response = {}
    response['status'] = None
    response['counter'] = None
    response['name'] = None
    response['info'] = None

    payload = {}
    payload['internalObjectId'] = objectId
    payload['ra'] = ra 
    payload['decl'] = dec
    payload['flagDate'] = flagDate
    payload['survey_database'] = dbName
    if alias:
        payload['internalName'] = alias
    if insertDate is None:
        insertDate = datetime.now()
    payload['insertDate'] = insertDate.strftime("%Y-%m-%d %H:%M:%S")

    try:
        r = requests.post(nameserverURL, json=payload, headers={'Authorization': 'Token ' + nameserverToken}, timeout = timeout)
    except RequestsConnectionError as e:
        response['info'] = "Error: Unable to connect. Exception is %s" % str(e)
        return response
    except RequestsConnectionTimeoutError as e:
        response['info'] = "Error: Request timed out. Exception is %s" % str(e)
        return response
    except Exception as e:
        response['info'] = "Error: Something went wrong. Exception is %s" % str(e)
        return response

    status = r.status_code

    try:
        reply = r.json()
    except ValueError as e:
        info = "Error: Something went wrong. %s" % str(e)
        response['info'] = info

    if reply:
        try:
            counter = reply['event_counter']
            name = reply['event_id']
            info = reply['info']
        except KeyError as e:
            info = str(reply)

    response = {}
    response['status'] = status
    response['counter'] = counter
    response['name'] = name
    response['info'] = info

    return response

# 2023-01-01 KWS Same as getLocalObjectName, but includes a multiplier
#                so we can derive the year and truncated year count.
#                I didn't include this in the above function because I
#                didn't want to build any dependency on the multiplier.
def getLocalName(nameserverURL, nameserverToken, objectId, ra, dec, flagDate, dbName, multiplier):
    """getLocalName.

    Args:
        nameserverURL: URL of nameserver API
        nameserverToken: API token
        objectId: Internal object ID
        ra: RA
        dec: Declination
        flagDate: Date the object was flagged
        dbName: Database name
        multiplier: The multiplier used to infer the year
    """
    nameData = {'objectName': None,
                'objectCounter': None,
                'year': None,
                'yearCounter': None,
                'responseInfo': None }

    response = getLocalObjectName(nameserverURL, nameserverToken, objectId, ra, dec, flagDate, dbName)
    try:
        nameData['objectName'] = response['name']
        nameData['objectCounter'] = response['counter']
        nameData['responseInfo'] = response['info']
    except KeyError as e:
        pass

    if nameData['objectName'] is not None and nameData['objectCounter'] is not None:
        nameData['year'] = nameData['objectCounter'] // multiplier
        nameData['yearCounter'] = nameData['objectCounter'] % multiplier

    return nameData

