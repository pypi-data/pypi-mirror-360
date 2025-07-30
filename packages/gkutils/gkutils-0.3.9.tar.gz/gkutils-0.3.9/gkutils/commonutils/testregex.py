#                                h    h               m    m                       s    s     .  f                       (+-)              d    d                    m    m               s    s     .  f                                                            (radius)
import re
COORDS_SEX_REGEX = "^([0-2]{0,1}[0-9])[^0-9+\\-\\.]{0,}([0-5]{0,1}[0-9])[^0-9+\\-\\.]{0,}([0-5]{0,1}[0-9])(\\.[0-9]+){0,1}[^0-9+\\-\\.]{0,}([+-]){0,1}([0-9]{0,1}[0-9])[^0-9+\\-\\.]{0,}([0-5]{0,1}[0-9])[^0-9+\\-\\.]{0,}([0-5]{0,1}[0-9])(\\.[0-9]+){0,1}[^0-9+\\-\\.a-z=]{0,}(([0-9][0-9]{0,2}(\\.[0-9]+){0,1})){0,1}[^0-9+\\-\\.a-z=]{0,}(list=(all|[0-9]+)){0,1}$"
COORDS_SEX_REGEX_COMPILED = re.compile(COORDS_SEX_REGEX)

#COORDS_DEC_REGEX = "^([0-9]+(\.[0-9]+){0,1})[^0-9+\-]{0,5}([+-]{0,1}[0-9]+(\.[0-9]+){0,1})[^0-9 ]{0,1}( +([0-9][0-9]{0,1})){0,1}"
# 2019-04-17 KWS Made the decimal regex a bit more forgiving.
# 2024-04-10 KWS Allow up to 3 digits + fraction for the search radius.
#                            d.f                           (+-)            d.f                         (radius)
COORDS_DEC_REGEX = "^([0-9]+(\\.[0-9]+){0,1})[^0-9+\\-]{0,}([+-]{0,1}[0-9]+(\\.[0-9]+){0,1})[^0-9+\\-\\.a-z=]{0,}(([0-9][0-9]{0,2}(\\.[0-9]+){0,1})){0,1}[^0-9+\\-\\.a-z=]{0,}(list=(all|[0-9]+)){0,1}$"
COORDS_DEC_REGEX_COMPILED = re.compile(COORDS_DEC_REGEX)

#COORDS_SEX_REGEX = "^([0-2]{0,1}[0-9])[^0-9+\-\.]{0,}([0-5]{0,1}[0-9])[^0-9+\-\.]{0,}([0-5]{0,1}[0-9])(\.[0-9]+){0,1}[^0-9+\-\.]{0,}([+-]){0,1}([0-9]{0,1}[0-9])[^0-9+\-\.]{0,}([0-5]{0,1}[0-9])[^0-9+\-\.]{0,}([0-5]{0,1}[0-9])(\.[0-9]+){0,1}[^0-9+\-\.]{0,}(([0-9][0-9]{0,2}(\.[0-9]+){0,1})){0,1}$"
COORDS_SEX_REGEX_COMPILED = re.compile(COORDS_SEX_REGEX)

#COORDS_DEC_REGEX = "^([0-9]+(\.[0-9]+){0,1})[^0-9+\-]{0,5}([+-]{0,1}[0-9]+(\.[0-9]+){0,1})[^0-9 ]{0,1}( +([0-9][0-9]{0,1})){0,1}"
# 2019-04-17 KWS Made the decimal regex a bit more forgiving.
# 2024-04-10 KWS Allow up to 3 digits + fraction for the search radius.
# 2025-03-28 KWS Specify sublist to search instead of whole database. Can be list ID or all.
#                            d.f                           (+-)            d.f                         (radius = 0-999.f...)                              list=all or 0-99

# 2025-03-28 KWS Added ability to extract the detection list from the regular expression.
def getCoordsAndSearchRadius(inputString):
    """getCoordsAndSearchRadius.
   
    Args:
        inputString:
    """
    coords = {}
    ra = None
    dec = None
    radius = None
    detectionlist = None

    sex = COORDS_SEX_REGEX_COMPILED.search(inputString)
    decimal = COORDS_DEC_REGEX_COMPILED.search(inputString)
   
    if decimal:
        ra = decimal.group(1)
        dec = decimal.group(3)
        radius = decimal.group(5)
        detectionlist = decimal.group(9)
        try:
            if float(ra) > 360.0 or float(ra) < 0.0 or float(dec) < -90.0 or float(dec) > 90.0:
                coords = {}
            else:
                coords['ra'] = ra
                coords['dec'] = dec
                coords['radius'] = radius
                coords['detectionlist'] = detectionlist

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
        detectionlist = sex.group(14)
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
                coords['detectionlist'] = detectionlist
        except ValueError as e:
            coords = {}

    return coords

inputString = "233.85747 +12.05775 111 list=all"
print (getCoordsAndSearchRadius(inputString))
inputString = "15:35:25.79 +12:03:27.8 111 list=all"
print (getCoordsAndSearchRadius(inputString))
