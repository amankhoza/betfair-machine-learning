import urllib
import urllib.error
from bs4 import BeautifulSoup


def convertNameToBetfairName(name):
    extensions = ['City', 'United', 'Hotspur', 'Albion', 'rystal', 'wich']
    if 'Man' in name:
        name = name.replace('chester', '')
        name = name.replace('United', 'Utd')
    else:
        for ext in extensions:
            name = name.replace(ext, '')
    return name


try:
    web_page = urllib.request.urlopen("http://www.bbc.co.uk/sport/football/premier-league/table")
    soup = BeautifulSoup(web_page, 'lxml')
    teams = [td.find('a').getText() for td in soup.findAll('td', class_='team-name')[0:20]]
    out = open('rankings.csv', 'w')
    headers = 'Ranking,Team'
    out.write(headers+'\n')
    for i in range(0, len(teams)):
        out.write(str(i+1)+','+convertNameToBetfairName(teams[i]).strip()+'\n')
    out.close()
except urllib.error.HTTPError:
    print("HTTPERROR!")
except urllib.error.URLError:
    print("URLERROR!")
