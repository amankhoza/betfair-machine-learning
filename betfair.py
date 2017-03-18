#!/usr/bin/env python3

import urllib
import urllib.request
import urllib.error
import json
import datetime
import sys
import time
import os
import threading


def log(logName, accessMode, logMsg):
    log_out = open(logName, accessMode)
    log_out.write(time.ctime()+' - '+logMsg+'\n\n')
    log_out.close()


def tryCallApiAgain(errorMsg, endpoint, jsonrpc_req, retry):
    log('./log/error.log', 'a', errorMsg)
    if retry:
        time.sleep(60)
        retryMsg = 'Trying to call api again\n'+'Endpoint: '+endpoint
        log('./log/error.log', 'a', retryMsg)
        return callApi(endpoint, jsonrpc_req, retry)
    else:
        return None


# make call to api and return response as a python object
def callApi(endpoint, jsonrpc_req, retry):
    try:
        req = urllib.request.Request(endpoint, jsonrpc_req.encode('utf-8'), headers)
        response = urllib.request.urlopen(req)
        jsonResponse = response.read()
        jsonString = jsonResponse.decode('utf-8')
        pythonObject = json.loads(jsonString)
        if pythonObject.get('error'):  # log api call errors to text file
            errorMsg = 'Exception from API-NG: '+str(pythonObject.get('error'))+'\n'+str(pythonObject)+'\n'+'Endpoint: '+str(endpoint)
            return tryCallApiAgain(errorMsg, endpoint, jsonrpc_req, retry)
        else:
            return pythonObject
    except urllib.error.URLError as e:
        errorMsg = str(e.reason)+'\n'+'Endpoint: '+str(endpoint)
        return tryCallApiAgain(errorMsg, endpoint, jsonrpc_req, retry)
    except urllib.error.HTTPError as e:
        errorMsg = str(e.reason)+'\n'+'Not a valid operation from the service: '+str(endpoint)
        return tryCallApiAgain(errorMsg, endpoint, jsonrpc_req, retry)
    except Exception as e:
        errorMsg = str(e.reason)+'\n'+'Unexpected exception at: '+str(endpoint)
        return tryCallApiAgain(errorMsg, endpoint, jsonrpc_req, retry)


def keepSessionAlive():
    keep_alive_req = ''
    keep_alive = callApi(keep_alive_endpoint, keep_alive_req, False)
    if keep_alive:
        keep_alive_msg = 'Last keep alive called'+'\n'+'Status: '+keep_alive['status']
        log('./log/last_keep_alive.log', 'w', keep_alive_msg)
    else:
        keep_alive_msg = 'Keep alive failed'
        log('./log/last_keep_alive.log', 'a', keep_alive_msg)
    t = threading.Timer(600, keepSessionAlive)  # run every 10 minutes
    t.daemon = True
    t.start()


def getMarketCatalogue(eventTypeID, competitionIds, marketCountries, marketTypes):
    if (eventTypeID is not None):
        start_time = (datetime.datetime.now() - datetime.timedelta(hours=2)).strftime('%Y-%m-%dT%H:%M:%SZ')
        end_time = (datetime.datetime.now() + datetime.timedelta(hours=2)).strftime('%Y-%m-%dT%H:%M:%SZ')
        # these start & end time filters ensure data is collected from 2 hours before ko, up to 2 hours after ko
        market_catalogue_req = ('{"jsonrpc": "2.0", "method": "SportsAPING/v1.0/listMarketCatalogue", "params": {"filter":{"eventTypeIds":["' + eventTypeID + '"], "competitionIds":["' + competitionIds + '"], "marketCountries":["' + marketCountries + '"], "marketTypeCodes":["' + marketTypes + '"], "marketStartTime":{"from":"' + start_time + '", "to":"' + end_time + '"}}, "sort":"FIRST_TO_START", "maxResults":"100", "marketProjection":["EVENT", "RUNNER_METADATA"]}, "id": 1}')
        market_catalogue = callApi(betting_endpoint, market_catalogue_req, True)
        market_catalouge_results = market_catalogue['result']
        return market_catalouge_results


def getEplMarketCatalogue():
    return getMarketCatalogue('1', '10932509', '', 'MATCH_ODDS')


def getCustomMarketCatalogue():
    return getMarketCatalogue('1', '2005', '', 'MATCH_ODDS')


def extractOddsAsString(runnerString):
    n = len(runnerString)
    if (n == 0):
        return ',,,,,'

    ans = ''

    for odds in runnerString:
        if ans:
            ans += ','
        ans += str(odds['price'])+','+str(odds['size'])

    # if there are less than 3 sets of odds, then add blanks so that odds columns align correctly
    if (n == 1):
        ans += ',,,,'
    elif (n == 2):
        ans += ',,'

    return ans


def getRunnerDataString(runners):
    runnerDataString = ''
    for runner in runners:
        if runnerDataString:
            runnerDataString += ','
        runnerDataString += extractOddsAsString(runner['ex']['availableToBack'])+','+extractOddsAsString(runner['ex']['availableToLay'])
    return runnerDataString


def getMarketBookBestOffers(marketId):
    market_book_req = '{"jsonrpc": "2.0", "method": "SportsAPING/v1.0/listMarketBook", "params": {"marketIds":["' + marketId + '"], "priceProjection":{"priceData":["EX_BEST_OFFERS"], "virtualise":"true"}}, "id": 1}' #with virtualise
    market_book = callApi(betting_endpoint, market_book_req, True)
    market_book_result = market_book['result'][0]
    return market_book_result


def createDirectories(directories):
    for directory in directories:
        if not os.path.exists('./'+directory):
            os.makedirs('./'+directory)


args = len(sys.argv)

if (args < 3):
    print ('Please provide application key and session token as command-line arguments')
    exit()
else:
    appKey = sys.argv[1]
    sessionToken = sys.argv[2]

betting_endpoint = "https://api.betfair.com/exchange/betting/json-rpc/v1"
keep_alive_endpoint = "https://identitysso.betfair.com/api/keepAlive"
headers = {'x-application': appKey, 'x-authentication': sessionToken, 'content-type': 'application/json', 'accept': 'application/json'}

createDirectories(['data', 'log'])

keepSessionAlive()

while True:

    marketCatalogueResult = getEplMarketCatalogue()
    # marketCatalogueResult = getCustomMarketCatalogue()

    for market in marketCatalogueResult:

        marketid = market['marketId']

        eventName = market['event']['name'].strip()
        eventDate = market['event']['openDate'].split('T')[0]
        eventTime = market['event']['openDate'].split('T')[1][:5]
        filename = eventDate+'_'+eventTime+'_'+eventName+'.csv'
        filepath = './data/'+filename

        if (os.path.isfile(filepath)):
            fo = open(filepath, 'a')
        else:
            fo = open(filepath, 'a')
            fo.write('Time,Inplay,Status,Version,Total Matched,Total Available,HB1 odds,HB1 liquidity,HB2 odds,HB2 liquidity,HB3 odds,HB3 liquidity,HL1 odds,HL1 liquidity,HL2 odds,HL2 liquidity,HL3 odds,HL3 liquidity,AB1 odds,AB1 liquidity,AB2 odds,AB2 liquidity,AB3 odds,AB3 liquidity,AL1 odds,AL1 liquidity,AL2 odds,AL2 liquidity,AL3 odds,AL3 liquidity,DB1 odds,DB1 liquidity,DB2 odds,DB2 liquidity,DB3 odds,DB3 liquidity,DL1 odds,DL1 liquidity,DL2 odds,DL2 liquidity,DL3 odds,DL3 liquidity\n')
            # H = Home Team, A = Away Team, D = Draw
            # B = Back, L = Lay
            # 1 = best odds, 2 = second best odds, 3 = third best odds
            # For back odds higher price is better
            # For lay odds lower price is better

        market_book_result = getMarketBookBestOffers(marketid)

        current_time = datetime.datetime.now()
        isInplay = market_book_result['inplay']
        status = market_book_result['status']
        version = market_book_result['version']
        totalMatched = market_book_result['totalMatched']
        totalAvailable = market_book_result['totalAvailable']

        runnerDataString = getRunnerDataString(market_book_result['runners'])

        fo.write(str(current_time)+','+str(isInplay)+','+status+','+str(version)+','+str(totalMatched)+','+str(totalAvailable)+','+runnerDataString+'\n')

    time.sleep(1)
