import matplotlib.pyplot as plt
import pandas as pd
import sys

def setPlotLabels(matchTitle,matchDate):
    plt.xlabel('time')
    plt.ylabel('odds')
    plt.legend(loc='upper left')
    plt.title(matchTitle+' on '+matchDate)

plt.style.use('ggplot')

filePath = sys.argv[1]
fileName = (filePath.split('/')[-1]).split('.')[0]
matchTitle = fileName.split('_')[2]
matchDate = fileName.split('_')[0]
homeTeam = matchTitle.split(' v ')[0]
awayTeam = matchTitle.split(' v ')[1]

df = pd.read_csv(filePath)

time = df['Time']
hbOdds = df['HB1 odds']
hlOdds = df['HL1 odds']
abOdds = df['AB1 odds']
alOdds = df['AL1 odds']
dbOdds = df['DB1 odds']
dlOdds = df['DL1 odds']

plt.figure(1)
plt.plot(hbOdds,label=homeTeam+' back')
plt.plot(abOdds,label=awayTeam+' back')
plt.plot(dbOdds,label='Draw back')
setPlotLabels(matchTitle,matchDate)

plt.figure(2)
plt.plot(hlOdds,label=homeTeam+' lay')
plt.plot(alOdds,label=awayTeam+' lay')
plt.plot(dlOdds,label='Draw lay')
setPlotLabels(matchTitle,matchDate)

plt.show()
