class EmptyClass:
    pass

def getFARTimes(far):
    fardata = EmptyClass()
    
    secondsInYear = 24*3600*365.2425

    farInYears = 1/(far * secondsInYear)
    farInMonths = 12 * 1/(far * secondsInYear)
    farInWeeks = 52 * 1/(far * secondsInYear)
    farInDays = 365.2425 * 1/(far * secondsInYear)

    fardata.years = farInYears
    fardata.months = farInMonths
    fardata.weeks = farInWeeks
    fardata.days = farInDays
    return fardata


#far = 2/(24*3600*365.2425)
#far = 0.00000006337747701362287
far = 1.533216963076217e-12
print('{:.23f}'.format(far))

fardata =  getFARTimes(far)
print(fardata.years)
print(fardata.months)
print(fardata.weeks)
print(fardata.days)
