import matplotlib.pyplot as plt
import pandas as pd
import sys
from datetime import datetime
import time

def setPlotLabels(matchTitle,matchDate):
    plt.xlabel('time in minutes before/after kickoff')
    plt.ylabel('odds')
    plt.legend(loc='upper left')
    plt.title(matchTitle+' on '+matchDate)

def getTimeInMinutes(matchDateTime,timestamps):
    timeInMinutes = []
    timeFormat = '%Y-%m-%d %H:%M:%S'
    for i in range(0,len(timestamps)):
        timestamp = timestamps[i].split('.')[0]
        d1 = datetime.strptime(matchDateTime,timeFormat)
        d2 = datetime.strptime(timestamp,timeFormat)
        # convert to unix timestamp
        d1_ts = time.mktime(d1.timetuple())
        d2_ts = time.mktime(d2.timetuple())
        # they are now in seconds, subtract and then divide by 60 to get minutes.
        diff = float(d2_ts-d1_ts) / 60
        timeInMinutes.append(diff)
    return timeInMinutes

plt.style.use('ggplot')

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
timeInMinutes = getTimeInMinutes(matchDateTime,timestamps)

hbOdds = df['HB1 odds'].tolist()
hlOdds = df['HL1 odds'].tolist()
abOdds = df['AB1 odds'].tolist()
alOdds = df['AL1 odds'].tolist()
dbOdds = df['DB1 odds'].tolist()
dlOdds = df['DL1 odds'].tolist()

plt.figure(1)
plt.plot(timeInMinutes,hbOdds,label=homeTeam+' back')
plt.plot(timeInMinutes,abOdds,label=awayTeam+' back')
plt.plot(timeInMinutes,dbOdds,label='Draw back')
setPlotLabels(matchTitle,matchDate)

plt.figure(2)
plt.plot(timeInMinutes,hlOdds,label=homeTeam+' lay')
plt.plot(timeInMinutes,alOdds,label=awayTeam+' lay')
plt.plot(timeInMinutes,dlOdds,label='Draw lay')
setPlotLabels(matchTitle,matchDate)

plt.show()
