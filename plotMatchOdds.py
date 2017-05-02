import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.lines as lines
import pandas as pd
import sys
from datetime import datetime
import time
import math


def nanToOne(n):
    if math.isnan(n):
        return 1
    else:
        return 1+0.95*(n-1)  # account for betfair commission


def getProbabilities(hbOdds, abOdds, dbOdds):
    n = max(len(hbOdds), len(abOdds), len(dbOdds))
    hbPs = []
    abPs = []
    dbPs = []
    for i in range(0, n):
        hbInvOdds = 1/nanToOne(hbOdds[i])
        abInvOdds = 1/nanToOne(abOdds[i])
        dbInvOdds = 1/nanToOne(dbOdds[i])
        booksum = hbInvOdds + abInvOdds + dbInvOdds
        hbPs.append(100 * hbInvOdds/booksum)
        abPs.append(100 * abInvOdds/booksum)
        dbPs.append(100 * dbInvOdds/booksum)
    return {'hb': hbPs, 'ab': abPs, 'db': dbPs}


def setPlotLabels(xLabel, yLabel, title):
    if (args > 2):
        dashed_line = lines.Line2D([0, 0], [0, 0], color='black', label='Goal', linestyle='dashed')
        inplay = mpatches.Patch(color='lightgreen', label='In-play')
        legend2 = plt.legend(handles=[inplay, dashed_line], loc='upper right')
        plt.gca().add_artist(legend2)
    plt.xlabel(xLabel)
    plt.ylabel(yLabel)
    plt.legend(loc='upper left')
    plt.title(title)


def setKeyEvents(maxYValue):
    y1 = 0
    y2 = maxYValue
    if (args > 2):
        HT = 15  # half time length
        fhET = int(sys.argv[2])  # first half extra time
        shET = int(sys.argv[3])  # second half extra time
        fhKO = 0  # first half kickoff
        shKO = 45+fhET+HT  # second half kickoff
        fig, ax = plt.subplots()
        plt.plot((-60, -60), (y1, y2), 'k--')  # plot odds when lineups announced
        ax.fill_betweenx([y1, y2], fhKO, 45+fhET, color='lightgreen')
        ax.fill_betweenx([y1, y2], shKO, shKO+45+shET, color='lightgreen')
    if (args > 3):
        for i in range(4, args):
            keyEventString = sys.argv[i]
            if '+' in keyEventString:
                s = keyEventString.split('+')
                minute = int(s[0])
                extra = int(s[1])
                if minute == 45:
                    minute += extra
                elif minute == 90:
                    minute += fhET + HT + extra
                else:
                    print ('Error parsing extra time minute: '+keyEventString)
                    exit()
            else:
                minute = int(keyEventString)
                if minute>45:
                    minute += fhET + HT
            plt.plot((minute, minute), (y1, y2), 'k--')


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


plt.style.use('ggplot')

args = len(sys.argv)

filePath = sys.argv[1]
fileName = (filePath.split('/')[-1]).split('.')[0]
matchTitle = fileName.split('_')[2]
matchDate = fileName.split('_')[0]
matchTime = fileName.split('_')[1]
homeTeam = matchTitle.split(' v ')[0]
awayTeam = matchTitle.split(' v ')[1]

df = pd.read_csv(filePath)

timestamps = df['Time']
matchDateTime = matchDate+' '+matchTime+':00'
timeInMinutes = getTimeInMinutes(matchDateTime, timestamps)

hbOdds = df['HB1 odds'].tolist()
hlOdds = df['HL1 odds'].tolist()
abOdds = df['AB1 odds'].tolist()
alOdds = df['AL1 odds'].tolist()
dbOdds = df['DB1 odds'].tolist()
dlOdds = df['DL1 odds'].tolist()
probabilities = getProbabilities(hbOdds, abOdds, dbOdds)

# print back odds
setKeyEvents(1000)
plt.figure(1)
plt.plot(timeInMinutes, hbOdds, label=homeTeam+' back')
plt.plot(timeInMinutes, abOdds, label=awayTeam+' back')
plt.plot(timeInMinutes, dbOdds, label='Draw back')
setPlotLabels('time in minutes after kickoff', 'odds', matchTitle+' on '+matchDate)

# print lay odds
setKeyEvents(1000)
plt.figure(2)
plt.plot(timeInMinutes, hlOdds, label=homeTeam+' lay')
plt.plot(timeInMinutes, alOdds, label=awayTeam+' lay')
plt.plot(timeInMinutes, dlOdds, label='Draw lay')
setPlotLabels('time in minutes after kickoff', 'odds', matchTitle+' on '+matchDate)

# print probabilities
setKeyEvents(100)
plt.figure(3)
plt.plot(timeInMinutes, probabilities['hb'], label=homeTeam)
plt.plot(timeInMinutes, probabilities['ab'], label=awayTeam)
plt.plot(timeInMinutes, probabilities['db'], label='Draw')
setPlotLabels('time in minutes after kickoff', 'probability of outcome', matchTitle+' on '+matchDate)

plt.show()
