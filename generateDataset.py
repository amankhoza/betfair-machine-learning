import pandas as pd
import sys
import os
import math
from datetime import datetime
import time

changeLimit = 2
timeDiffLimit = 3


def isSigChange(pStr1, pStr2):
    hbP1, abP1, dbP1 = pStr1.split(',')
    hbP2, abP2, dbP2 = pStr2.split(',')
    hDiff = abs(eval(hbP1)-eval(hbP2))
    aDiff = abs(eval(abP1)-eval(abP2))
    dDiff = abs(eval(dbP1)-eval(dbP2))
    return (hDiff > changeLimit or aDiff > changeLimit or dDiff > changeLimit)


def diffPsCalc(pStr1, pStr2):
    hbP1, abP1, dbP1 = pStr1.split(',')
    hbP2, abP2, dbP2 = pStr2.split(',')
    hDiff = eval(hbP2) - eval(hbP1)
    aDiff = eval(abP2) - eval(abP1)
    dDiff = eval(dbP2) - eval(dbP1)
    return (str(hDiff)+','+str(aDiff)+','+str(dDiff))


def getTimeInMinutes(matchDateTime, timestamps):
    timeInMinutes = []
    timeFormat = '%Y-%m-%d %H:%M:%S'
    for i in range(0, len(timestamps)):
        timestamp = timestamps[i].split('.')[0]
        d1 = datetime.strptime(matchDateTime, timeFormat)
        d2 = datetime.strptime(timestamp, timeFormat)
        # convert to unix timestamp
        d1_ts = time.mktime(d1.timetuple())
        d2_ts = time.mktime(d2.timetuple())
        # they are now in seconds, subtract and then divide by 60 to get minutes.
        diff = float(d2_ts-d1_ts) / 60
        timeInMinutes.append(diff)
    return timeInMinutes


def nanToOne(n):
    if math.isnan(n):
        return 1
    else:
        return 1 + 0.95 * (n-1)  # account for betfair commission


def nanToOneNoCommision(n):
    if math.isnan(n):
        return 1
    else:
        return n


def getProbabilities(hbOdds, abOdds, dbOdds):
    hbInvOdds = 1/nanToOne(hbOdds)
    abInvOdds = 1/nanToOne(abOdds)
    dbInvOdds = 1/nanToOne(dbOdds)
    booksum = hbInvOdds + abInvOdds + dbInvOdds
    hbP = 100 * (hbInvOdds/booksum)
    abP = 100 * (abInvOdds/booksum)
    dbP = 100 * (dbInvOdds/booksum)
    return str(hbP)+','+str(abP)+','+str(dbP)


def convertName(betfairName):
    if betfairName == 'C Palace':
        return 'Crystal Palace'
    else:
        return betfairName


def fetchMatchStats(matchDate, matchTime, homeTeam, awayTeam):
    homeTeam = convertName(homeTeam)
    awayTeam = convertName(awayTeam)
    print (matchDate+','+matchTime+','+homeTeam+','+awayTeam)
    stats = eventsDf[(eventsDf['Date']==matchDate) & (eventsDf['Time']==matchTime) & (eventsDf['Home']==homeTeam) & (eventsDf['Away']==awayTeam)]
    et = stats['ET'].values[0].split(' ')
    fhET = eval(et[0])  # first half extra time
    shET = eval(et[1])  # second half extra time
    redCards = []
    goals = []
    if str(stats['Red Cards'].values[0]) != 'nan':
        redCards = stats['Red Cards'].values[0].split(' ')
    if str(stats['Goals'].values[0]) != 'nan':
        goals = stats['Goals'].values[0].split(' ')
    return fhET, shET, redCards, goals


def fetchRanking(team):
    teamDF = rankingsDF[rankingsDF['Team']==team]
    return (float(teamDF['Ranking'].values[0]) / 20)  # normalise ranking


def convertGoalsToMinutesAfterKO(goals, fhEt):
    convertedGoals = []
    ht = 15  # half time length

    for i in range(0, len(goals)):
        keyEventString = goals[i].replace('-', '')
        if '+' in keyEventString:
            s = keyEventString.split('+')
            minute = int(s[0])
            extra = int(s[1])
            if minute == 45:
                minute += extra
            elif minute == 90:
                minute += fhET + ht + extra
            else:
                print ('Error parsing extra time minute: '+keyEventString)
                exit()
        else:
            minute = int(keyEventString)
            if minute > 45:
                minute += fhET + ht
        convertedGoals.append(minute)

    return convertedGoals


def sign(num):
    return math.copysign(1, num)


def getGoalDeficit(goals, goalIndex):
    deficit = 0
    for i in range(0, goalIndex):
        if '-' in goals[i]:
            deficit -= 1
        else:
            deficit += 1
    return deficit


def matchGoalWithChange(goalIndex, goals, convertedGoals, unassignedChangeIndexes, changes):
    for i in unassignedChangeIndexes:
        diff = abs(convertedGoals[goalIndex]-changes[i]['t'])
        diffOdds = map(eval, changes[i]['diffOdds'].split(','))
        hbDiff = diffOdds[0]
        abDiff = diffOdds[1]

        isAwayGoal = '-' in goals[goalIndex]
        isHomeGoal = not isAwayGoal

        homeGoalDetected = isHomeGoal and hbDiff<0 and abDiff>0
        awayGoalDetected = isAwayGoal and hbDiff>0 and abDiff<0

        if diff<timeDiffLimit and (homeGoalDetected or awayGoalDetected):
            return i

    return -1


os.system('reset')

directory = sys.argv[1] if sys.argv[1].endswith('/') else sys.argv[1]+'/'

# load key events into pandas df
eventsDf = pd.read_csv('eventsComplete.csv')

# load rankings into pandas df
rankingsDF = pd.read_csv('rankings.csv')

out = open('train.csv', 'w')

headers = 'Home,Away,Home_Rank,Away_Rank,Home_pmP,Away_pmP,Draw_pmP,Score_deficit,Home_or_Away_goal,Time_of_goal,Prev_home_p,Prev_away_p,Prev_draw_p,\
           Curr_home_p,Curr_away_p,Curr_draw_p,Change_home_p,Change_away_p,Change_draw_p,Home_pmOdds,Away_pmOdds,Draw_pmOdds,Prev_home_odds,Prev_away_odds,\
           Prev_draw_odds,Curr_home_odds,Curr_away_odds,Curr_draw_odds'
out.write(headers+'\n')

correct = 0
total = 0

goalCorrect = 0
goalTotal = 0

fails = 0

for fileName in sorted(os.listdir(directory)):
    if not fileName.endswith('.csv'):
        continue  # skip directories and other files

    df = pd.read_csv(directory+fileName)

    hbOdds  = df['HB1 odds']
    abOdds  = df['AB1 odds']
    dbOdds  = df['DB1 odds']
    markets = df['Version']
    inplays = df['Inplay']

    fileN      = (fileName.split('/')[-1]).split('.')[0]
    matchTitle = fileN.split('_')[2]
    matchDate  = fileN.split('_')[0]
    matchTime  = fileN.split('_')[1]
    homeTeam   = matchTitle.split(' v ')[0]
    awayTeam   = matchTitle.split(' v ')[1]
    timestamps = df['Time']
    matchDateTime = matchDate+' '+matchTime+':00'
    timeInMinutes = getTimeInMinutes(matchDateTime, timestamps)

    fhET, shET, redCards, goals = fetchMatchStats(matchDate, matchTime, homeTeam, awayTeam)
    convertedGoals = convertGoalsToMinutesAfterKO(goals, fhET)

    prematchPs = getProbabilities(hbOdds[0], abOdds[0], dbOdds[0])
    prematchOdds = str(nanToOneNoCommision(hbOdds[0]))+','+str(nanToOneNoCommision(abOdds[0]))+','+str(nanToOneNoCommision(dbOdds[0]))
    currentMarket = markets[0]
    changes = []
    otherChanges = []

    for i in range(0, len(inplays)):
        if markets[i] == currentMarket:
            continue
        else:
            t = timeInMinutes[i]
            prevPs = getProbabilities(hbOdds[i-1], abOdds[i-1], dbOdds[i-1])
            currPs = getProbabilities(hbOdds[i], abOdds[i], dbOdds[i])
            diffPs = diffPsCalc(prevPs, currPs)
            prevOdds = str(nanToOneNoCommision(hbOdds[i-1]))+','+str(nanToOneNoCommision(abOdds[i-1]))+','+str(nanToOneNoCommision(dbOdds[i-1]))
            currOdds = str(nanToOneNoCommision(hbOdds[i]))+','+str(nanToOneNoCommision(abOdds[i]))+','+str(nanToOneNoCommision(dbOdds[i]))
            diffOdds = diffPsCalc(prevOdds, currOdds)
            changes.append({'t': t, 'pmPs': prematchPs, 'prevPs': prevPs, 'currPs': currPs, 'diffPs': diffPs, 'pmOdds': prematchOdds, 'prevOdds': prevOdds, 'currOdds': currOdds, 'diffOdds': diffOdds})
            currentMarket = markets[i]

    total += 1
    goalTotal += len(convertedGoals)

    assignedPairs = {}

    print('Index\t\tGoal\t\tConverted\t\tMatched With\t\tOdds Change')
    for i in range(0, len(convertedGoals)):
        deficit = getGoalDeficit(goals, i)
        unassignedChangeIndexes = [x for x in range(0, len(changes)) if x not in assignedPairs.values()]
        changeIndex = matchGoalWithChange(i, goals, convertedGoals, unassignedChangeIndexes, changes)
        if changeIndex != -1:
            print(str(i)+'\t\t'+goals[i]+'\t\t'+str(convertedGoals[i])+'\t\t\t'+str(int(changes[changeIndex]['t']))+'\t\t\t'+changes[changeIndex]['diffOdds']+'\t\t\t'+str(eval(changes[changeIndex]['diffOdds'].replace('-', '').replace(',', '+'))))
            if '-' in goals[i]:
                signGoal = -1
            else:
                signGoal = 1
            minuteFraction = float(goals[i].replace('-', '').split('+')[0]) / 90
            if not redCards:
                out.write('{},{},{},{},{},{},{},{},{},{},{},{},{},{}\n'.format(homeTeam, awayTeam, fetchRanking(homeTeam), fetchRanking(awayTeam), changes[changeIndex]['pmPs'], float(deficit)/3, signGoal, minuteFraction, changes[changeIndex]['prevPs'], changes[changeIndex]['currPs'], changes[changeIndex]['diffPs'], changes[changeIndex]['pmOdds'], changes[changeIndex]['prevOdds'], changes[changeIndex]['currOdds']))
            assignedPairs[i] = changeIndex
            goalCorrect += 1
        else:
            print(str(i)+'\t\t'+goals[i]+'\t\t'+str(convertedGoals[i])+'\t\t\t'+'None')
    print('')

    if len(goals) == len(assignedPairs):
        correct += 1
    else:
        correct += 0

print (correct, total, float(correct)/float(total))
print (goalCorrect, goalTotal, float(goalCorrect)/float(goalTotal))
print('fails', fails)
