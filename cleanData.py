import pandas as pd
import sys
import os
import math
import time

cleanedFilesFolderName = 'CLEAN_'

changeLimit = 0.2

def fixOrder(inDirectory, outDirectory, fileName):
    df = pd.read_csv(inDirectory+fileName)

    inp = open(inDirectory+fileName)
    out = open(outDirectory+fileName, 'a')

    marketVersionColumn = df['Version']
    totalMatchedColumn = df['Total Matched']

    n = len(marketVersionColumn)

    marketVersion = marketVersionColumn[0]
    totalMatched = totalMatchedColumn[0]

    headers = inp.readline()

    out.write(headers)

    errors = 0

    for i in range(0, n-1):
        currentLine = inp.readline()

        currentVersion = marketVersionColumn[i]
        currentMatched = totalMatchedColumn[i]

        if currentVersion > marketVersion:
            marketVersion = currentVersion

        # this ensures marketVersion is strictly non-decreasing
        # and totalMatched is strictly increasing
        if marketVersion==currentVersion and currentMatched>totalMatched:
            totalMatched = currentMatched
            out.write(currentLine)
        else:
            errors += 1

    inp.close()
    out.close()

    return errors

def removeSuspendedOddsFromEndOfMatch(inDirectory, outDirectory, fileName):
    df = pd.read_csv(inDirectory+fileName)

    inp = open(inDirectory+fileName)
    out = open(outDirectory+fileName, 'a')

    statusColumn = df['Status']

    n = len(statusColumn)
    i = n-1

    while (statusColumn[i] == 'SUSPENDED'):
        i -= 1

    finalSuspendIndex = i+1 # add one for headers

    errors = n - finalSuspendIndex

    for i in range(0, n-1):
        currentLine = inp.readline()

        if (i == finalSuspendIndex):
            break
        else:
            out.write(currentLine)

    inp.close()
    out.close()

    return errors

def nanToOne(n):
    if math.isnan(n):
        return 1
    else:
        return n

def checkIfAnomalousResult(prev, curr, next):
    sign = lambda x: math.copysign(1, x) # ensures only spikes on graph are detected
    diff1 = nanToOne(prev) - nanToOne(curr)
    diff2 = nanToOne(next) - nanToOne(curr)
    change1 = diff1 / nanToOne(prev)
    change2 = diff2 / nanToOne(next)
    return (abs(change1)>changeLimit and abs(change2)>changeLimit and sign(change1)==sign(change2))

def removeAnomalousResults(inDirectory, outDirectory, fileName):
    df = pd.read_csv(inDirectory+fileName)

    inp = open(inDirectory+fileName)
    out = open(outDirectory+fileName, 'a')

    hbOdds = df['HB1 odds']
    abOdds = df['AB1 odds']
    dbOdds = df['DB1 odds']
    timestamps = df['Time']

    n = len(hbOdds)

    headers = inp.readline()
    firstLine = inp.readline()
    out.write(headers)
    out.write(firstLine)

    errors = 0

    i = 1

    while (i < n-1):
        currentLine = inp.readline()

        hbBool = checkIfAnomalousResult(hbOdds[i-1], hbOdds[i], hbOdds[i+1])
        abBool = checkIfAnomalousResult(abOdds[i-1], abOdds[i], abOdds[i+1])
        dbBool = checkIfAnomalousResult(dbOdds[i-1], dbOdds[i], dbOdds[i+1])

        if (hbBool or abBool or dbBool):
            #print ('SBP: ', timestamps[i], hbOdds[i], hbBool, abOdds[i], abBool, dbOdds[i], dbBool)
            errors += 1
        elif (i<(n-2) and (hbOdds[i]==hbOdds[i+1] or abOdds[i]==abOdds[i+1] or dbOdds[i]==dbOdds[i+1])):
            # double bad point check
            hbBool = hbOdds[i]==hbOdds[i+1] and checkIfAnomalousResult(hbOdds[i-1], hbOdds[i], hbOdds[i+2])
            abBool = abOdds[i]==abOdds[i+1] and checkIfAnomalousResult(abOdds[i-1], abOdds[i], abOdds[i+2])
            dbBool = dbOdds[i]==dbOdds[i+1] and checkIfAnomalousResult(dbOdds[i-1], dbOdds[i], dbOdds[i+2])
            if (hbBool or abBool or dbBool):
                #print ('DBP: ', timestamps[i], hbOdds[i], hbBool, abOdds[i], abBool, dbOdds[i], dbBool)
                badLine = inp.readline()
                errors += 2
                i += 1
            else:
                #print ('NO ERROR: ', timestamps[i], hbOdds[i], hbBool, abOdds[i], abBool, dbOdds[i], dbBool)
                out.write(currentLine)
        else:
            #print ('NO ERROR: ', timestamps[i], hbOdds[i], hbBool, abOdds[i], abBool, dbOdds[i], dbBool)
            out.write(currentLine)

        i += 1

    lastLine = inp.readline()
    out.write(lastLine)

    inp.close()
    out.close()

    return errors

def removePrematchAndSuspendedOdds(inDirectory, outDirectory, fileName):
    df = pd.read_csv(inDirectory+fileName)

    inp = open(inDirectory+fileName)
    out = open(outDirectory+fileName, 'a')

    statusColumn = df['Status']
    inplayColumn = df['Inplay']

    n = len(statusColumn)

    headers = inp.readline()
    out.write(headers)

    errors = 0

    for i in range(0, n-1):
        currentLine = inp.readline()
        inplay = inplayColumn[i]
        status = statusColumn[i]

        if inplay and status != 'SUSPENDED':
            out.write(currentLine)
        else:
            errors += 1

    inp.close()
    out.close()

    return errors

def executeCleaningStage(stageNo, runNo, cleaningFunc, cleaningDesc):
    global inDirectory
    outDirectory = directory+cleanedFilesFolderName+str(stageNo)+str(runNo)+'/'
    os.makedirs(outDirectory)
    if runNo == 0:
        print('\n*** CLEANING STAGE '+str(stageNo)+' ***')
        print('\n'+cleaningDesc+':\n')
    else:
        print('\nRUN '+str(runNo+1)+'\n')
    totalErrorsFixed = 0
    for fileName in filesList:
        errorsFixed = cleaningFunc(inDirectory, outDirectory, fileName)
        print(fileName+': '+str(errorsFixed)+' errors fixed')
        totalErrorsFixed += errorsFixed
    print('\n'+'Total errors fixed in stage '+str(stageNo)+' run '+str(runNo+1)+': '+str(totalErrorsFixed))
    inDirectory = outDirectory
    return totalErrorsFixed

directory = sys.argv[1] if sys.argv[1].endswith('/') else sys.argv[1]+'/'
inDirectory = directory

filesList = [fileName for fileName in sorted(os.listdir(directory)) if fileName.endswith('.csv')]

cleanStageOneDirectory = directory+cleanedFilesFolderName+'10'

if os.path.exists(cleanStageOneDirectory):
    print('ERROR CLEANING HAS ALREADY BEEN RAN ON THIS DIRECTORY')
else:
    start = time.clock()

    stageNo = 1
    runNo = 0
    cleaningFunc = fixOrder
    cleaningDesc = 'Fixing order (using market version & total matched)'
    executeCleaningStage(stageNo, runNo, cleaningFunc, cleaningDesc)

    stageNo = 2
    runNo = 0
    cleaningFunc = removeSuspendedOddsFromEndOfMatch
    cleaningDesc = 'Removing suspended odds from end of match'
    executeCleaningStage(stageNo, runNo, cleaningFunc, cleaningDesc)

    stageNo = 3
    runNo = 0
    cleaningFunc = removeAnomalousResults
    cleaningDesc = 'Removing anomalous results'
    flag = True
    while flag:
        totalErrorsFixed = executeCleaningStage(stageNo, runNo, cleaningFunc, cleaningDesc)
        if totalErrorsFixed > 0:
            flag =  True
            runNo += 1
        else:
            flag = False

    stageNo = 4
    runNo = 0
    cleaningFunc = removePrematchAndSuspendedOdds
    cleaningDesc = 'Removing pre match and suspended odds'
    executeCleaningStage(stageNo, runNo, cleaningFunc, cleaningDesc)

    end = time.clock()

    print('\n*** CLEANING COMPLETE ***\n')
    print('Time elapsed: '+str(int(end-start))+' seconds\n')