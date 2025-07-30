from generalutils import readGenericDataFile

filename = 'test1.ddc'

data = readGenericDataFile(filename, delimiter=' ', useOrderedDict=True, skipLines=-1, appendheaderlines=True)

for row in data:
    print(row)
