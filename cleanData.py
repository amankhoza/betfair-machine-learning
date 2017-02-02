import pandas as pd
import sys
import os

cleanedFilesFolderName = 'CLEANED_FILES'

def cleanFile(directory,fileName):
    df = pd.read_csv(directory+fileName)

    inp = open(directory+fileName)
    out = open(directory+cleanedFilesFolderName+'/'+fileName,'a')

    marketVersionColumn = df['Version']
    totalMatchedColumn = df['Total Matched']

    n = len(marketVersionColumn)

    marketVersion = marketVersionColumn[0]
    totalMatched = totalMatchedColumn[0]

    headers = inp.readline()

    out.write(headers)

    errors = 0

    for i in range(0,n-1):
        currentLine = inp.readline()

        currentVersion = marketVersionColumn[i]
        currentMatched = totalMatchedColumn[i]

        if currentVersion > marketVersion:
            marketVersion = currentVersion

        if currentMatched > totalMatched:
            totalMatched = currentMatched

        # this ensures marketVersion and totalMatched are strictly non-decreasing
        if marketVersion==currentVersion and currentMatched==totalMatched:
            out.write(currentLine)
        else:
            errors += 1

    return errors

def removeOddsFromEndOfMatch(directory,fileName):
    df = pd.read_csv(directory+fileName)

    statusColumn = df['Status']

    n = len(statusColumn)
    i = n-1

    while (statusColumn[i] == 'SUSPENDED'):
        i -= 1

    finalSuspendIndex = i+1 # add one for headers

    errors = n - finalSuspendIndex

    f = open(directory+fileName,'r+')

    for i in range(0,n-1):
        currentLine = f.readline()

        if (i == finalSuspendIndex):
            f.truncate()
            break

    f.close()

    return errors

directory = sys.argv[1] if sys.argv[1].endswith('/') else sys.argv[1]+'/'
cleanDirectory = directory+cleanedFilesFolderName+'/'

if os.path.exists(cleanDirectory):
    print('ERROR CLEANING HAS ALREADY BEEN RAN ON THIS DIRECTORY')
else:
    os.makedirs(cleanDirectory)
    print('\nREMOVING NOISE:\n')
    for fileName in os.listdir(directory):
        if not fileName.endswith('.csv'):
            continue # skip directories and other files
        errorsFixed = cleanFile(directory,fileName)
        print(fileName+': '+str(errorsFixed)+' errors fixed')
    print('\nREMOVING ODDS FROM END OF MATCH:\n')
    for fileName in os.listdir(cleanDirectory):
        errorsFixed = removeOddsFromEndOfMatch(cleanDirectory,fileName)
        print(fileName+': '+str(errorsFixed)+' errors fixed')
