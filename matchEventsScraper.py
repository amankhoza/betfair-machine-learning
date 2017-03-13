import urllib
import urllib.error
from bs4 import BeautifulSoup
import json
import time


def extractData(dataString):
    secondOpenBraceIndex = 1
    secondToLastClosedBraceIndex = 1
    for i in range(0, len(dataString)):
        if dataString[i] == '{':
            if secondOpenBraceIndex == 1:
                secondOpenBraceIndex -= 1
            else:
                secondOpenBraceIndex = i
                break
    for i in range(len(dataString)-1, 0, -1):
        if dataString[i] == '}':
            if secondToLastClosedBraceIndex == 1:
                secondToLastClosedBraceIndex -= 1
            else:
                secondToLastClosedBraceIndex = i+1
                break
    jsonString = dataString[secondOpenBraceIndex:secondToLastClosedBraceIndex]
    data = json.loads(jsonString)
    if 'event' in data['body']:
        return data['body']['event']
    return data['body']


def extractGoalsAndRedCards(playerActions):
    redCards = []
    goals = []
    for player in playerActions:
        for action in player['actions']:
            time = str(action['displayTime']).replace('\"', '').replace('\'', '')
            if action['type'] == 'goal':
                goals.append(time)
            elif action['type'] == 'red-card' or action['type'] == 'yellow-red-card':
                redCards.append(time)
            else:
                print('NEW ACTION FOUND: '+action['type'])
    return goals, redCards


def sortEvents(homeEvents, awayEvents):
    homeEvents = sorted(homeEvents, key=eval)
    awayEvents = sorted(awayEvents, key=eval)
    if not homeEvents and not awayEvents:
        return []
    elif not awayEvents:
        return homeEvents
    elif not homeEvents:
        return ['-'+time for time in awayEvents]
    else:
        sortedEvents = []
        i = 0
        j = 0
        while (i<len(homeEvents) and j<len(awayEvents)):
            if eval(homeEvents[i]) < eval(awayEvents[j]):
                sortedEvents.append(homeEvents[i])
                i += 1
            else:
                sortedEvents.append('-'+awayEvents[j])
                j += 1
        while (i<len(homeEvents) or j<len(awayEvents)):
            if i<len(homeEvents):
                sortedEvents.append(homeEvents[i])
                i += 1
            else:
                sortedEvents.append('-'+awayEvents[j])
                j += 1
        return sortedEvents


def fetchMatchStats(match_url):
    web_page = urllib.request.urlopen("http://www.bbc.co.uk/"+match_url)
    soup = BeautifulSoup(web_page, 'lxml')
    et = 'NULL'

    for script in soup.findAll('script'):
        if '/data/bbc-morph-sport-football-header-data' in str(script):
            data = extractData(str(script))
            homeGoals, homeRedCards = extractGoalsAndRedCards(data['homeTeam']['playerActions'])
            awayGoals, awayRedCards = extractGoalsAndRedCards(data['awayTeam']['playerActions'])
            homeTeam = data['homeTeam']['name']['abbreviation']
            awayTeam = data['awayTeam']['name']['abbreviation']
            startTime = data['startTimeInUKHHMM']
            startDate = data['formattedDateInUKTimeZone']['YYYYMMDD']
            redCards = sortEvents(homeRedCards, awayRedCards)
            goals = sortEvents(homeGoals, awayGoals)

        if 'data/bbc-morph-lx-commentary-data' in str(script):
            data = extractData(str(script))
            for dataPacket in data:
                if 'title' in dataPacket['payload']:
                    if dataPacket['payload']['title'] == 'Full Time':
                        time = str(dataPacket['payload']['time'])
                        additionalMins = (time.split('+')[1]).split('\'')[0]
                        shET = additionalMins
                    if dataPacket['payload']['title'] == 'Half Time':
                        time = str(dataPacket['payload']['time'])
                        additionalMins = (time.split('+')[1]).split('\'')[0]
                        fhET = additionalMins
            et = fhET+' '+shET

    return (startDate+','+startTime+','+homeTeam+','+awayTeam+','+et+','+' '.join(redCards)+','+' '.join(goals))


# Source: http://stackoverflow.com/questions/3173320/text-progress-bar-in-the-console
def printProgressBar(iteration, total, prefix='', suffix='', decimals=1, length=100, fill='█'):
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end='\r')
    if iteration == total:
        print()


try:
    start = time.time()

    web_page = urllib.request.urlopen("http://www.bbc.co.uk/sport/football/premier-league/results")
    soup = BeautifulSoup(web_page, 'lxml')
    matches = soup.findAll('a', class_='report')
    n = len(matches)
    counter = 0
    out = open('events.csv', 'w')
    headers = 'Date,Time,Home,Away,ET,Red Cards,Goals'
    out.write(headers+'\n')

    for match in matches:
        out.write(fetchMatchStats(match['href'])+'\n')
        counter += 1
        printProgressBar(counter, n, prefix='Progress:', suffix='Complete', length=50)

    out.close()
    end = time.time()
    print('Time elapsed: {} minutes {} seconds'.format(int((end-start)/60), int((end-start) % 60)))

except urllib.error.HTTPError:
    print("HTTPERROR!")

except urllib.error.URLError:
    print("URLERROR!")
