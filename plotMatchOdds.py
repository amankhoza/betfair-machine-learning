import matplotlib.pyplot as plt
import pandas as pd
import sys

plt.style.use('ggplot')

filePath = sys.argv[1]
fileName = (filePath.split('/')[-1]).split('.')[0]
matchTitle = fileName.split('_')[2]
matchDate = fileName.split('_')[0]
homeTeam = matchTitle.split(' v ')[0]
awayTeam = matchTitle.split(' v ')[1]

df = pd.read_csv(filePath)

hbOdds = df['HB1 odds']
abOdds = df['AB1 odds']
dbOdds = df['DB1 odds']

plt.plot(hbOdds,label=homeTeam)
plt.plot(abOdds,label=awayTeam)
plt.plot(dbOdds,label='Draw')

plt.xlabel('time')
plt.ylabel('odds')
plt.legend(loc='upper left')
plt.title(matchTitle+' on '+matchDate)

plt.show()
