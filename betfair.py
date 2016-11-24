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

#appkey for ref = GCLKwLC319cpyBZE
#login to betfair.com
#then go to https://developer.betfair.com/exchange-api/accounts-api-demo/
#and get session id
#to play around with visual API tool visit https://developer.betfair.com/exchange-api/betting-api-demo/

"""
make a call API-NG
"""

def callApi(endpoint,jsonrpc_req):
    try:
        req = urllib.request.Request(endpoint, jsonrpc_req.encode('utf-8'), headers)
        response = urllib.request.urlopen(req)
        jsonResponse = response.read()
        return jsonResponse.decode('utf-8')
    except urllib.error.URLError as e:
        print (e.reason)
        print ('Oops no service available at ' + str(endpoint))
        exit()
    except urllib.error.HTTPError:
        print ('Oops not a valid operation from the service ' + str(endpoint))
        exit()

def keepSessionAlive():
    keep_alive_req = ''
    keep_alive_response = callApi(keep_alive_endpoint,keep_alive_req)
    keep_alive_loads = json.loads(keep_alive_response)
    #print(time.ctime())
    #print ('called keep alive: ',keep_alive_loads['status'])
    #maybe log these into a log file
    threading.Timer(600, keepSessionAlive).start()

"""
Calling marketCatalouge to get marketDetails
"""

def getMarketCatalogue(eventTypeID,competitionIds,marketCountries,marketTypes):
    if (eventTypeID is not None):
        start_time = (datetime.datetime.now() - datetime.timedelta(hours=2)).strftime('%Y-%m-%dT%H:%M:%SZ')
        end_time = (datetime.datetime.now() + datetime.timedelta(hours=2)).strftime('%Y-%m-%dT%H:%M:%SZ')
        #these start & end time filters ensure data is collected from 2 hours before ko, up to 2 hours after ko
        market_catalogue_req = ('{"jsonrpc": "2.0", "method": "SportsAPING/v1.0/listMarketCatalogue", "params": {"filter":{"eventTypeIds":["' + eventTypeID + '"],"competitionIds":["' + competitionIds + '"],"marketCountries":["' + marketCountries + '"],"marketTypeCodes":["' + marketTypes + '"], "marketStartTime":{"from":"' + start_time + '","to":"' + end_time + '"}},"sort":"FIRST_TO_START","maxResults":"100","marketProjection":["EVENT","RUNNER_METADATA"]}, "id": 1}')
        market_catalogue_response = callApi(betting_endpoint,market_catalogue_req)
        market_catalouge_loads = json.loads(market_catalogue_response)
        try:
            market_catalouge_results = market_catalouge_loads['result']
            return market_catalouge_results
        except:
            print ('Exception from API-NG' + str(market_catalouge_results['error']))
            exit()

def getEplMarketCatalogue():
    return getMarketCatalogue('1','31','','MATCH_ODDS')

def getCustomMarketCatalogue():
    return getMarketCatalogue('1','2005','','MATCH_ODDS')

def getRunnerMappings(market):
    mappings = {}
    for runner in market['runners']:
        mappings[runner['selectionId']] = str(runner['runnerName'])
    return mappings

# def getRunnerData(runners):
#     runnerData = {}
#     for runner in runners:
#         runnerData[runner['selectionId']] = {}
#         runnerData[runner['selectionId']]['back'] = runner['ex']['availableToBack']
#         runnerData[runner['selectionId']]['lay'] = runner['ex']['availableToLay']
#     return runnerData

def extractOddsAsString(runnerString):
    ans = ''
    #print ('len of runnerString is: ',len(runnerString),'\n')
    for odds in runnerString:
        if ans:
            ans += ','
        ans += str(odds['price'])+','+str(odds['size'])
    return ans

def getRunnerDataString(runners):
    runnerDataString = ''
    for runner in runners:
        if runnerDataString:
            runnerDataString += ','
        runnerDataString += extractOddsAsString(runner['ex']['availableToBack'])+','+extractOddsAsString(runner['ex']['availableToLay'])
    return runnerDataString

def getMarketBookBestOffers(marketId):
    market_book_req = '{"jsonrpc": "2.0", "method": "SportsAPING/v1.0/listMarketBook", "params": {"marketIds":["' + marketId + '"],"priceProjection":{"priceData":["EX_BEST_OFFERS"]}}, "id": 1}'
    market_book_response = callApi(betting_endpoint,market_book_req)
    market_book_loads = json.loads(market_book_response)
    try:
        market_book_result = market_book_loads['result'][0]
        return market_book_result
    except:
        print  ('Exception from API-NG' + str(market_book_result['error']))
        exit()

args = len(sys.argv)

if ( args < 3):
    print ('Please provide Application key and session token')
    appKey = input('Enter your application key :')
    sessionToken = input('Enter your session Token/SSOID :')
    print ('Thanks for the input provided')
else:
    appKey = sys.argv[1]
    sessionToken = sys.argv[2]

betting_endpoint = "https://api.betfair.com/exchange/betting/json-rpc/v1"
keep_alive_endpoint = "https://identitysso.betfair.com/api/keepAlive"
headers = {'x-application': appKey, 'x-authentication': sessionToken, 'content-type': 'application/json', 'accept': 'application/json'}

if not os.path.exists('./data'):
    os.makedirs('./data')

keepSessionAlive()

while True:

    marketCatalogueResult = getEplMarketCatalogue()
    #marketCatalogueResult = getCustomMarketCatalogue()

    #print (marketCatalogueResult)

    for market in marketCatalogueResult:

        marketid = market['marketId']

        eventName = market['event']['name'].strip()
        eventDate = market['event']['openDate'].split('T')[0]
        eventTime = market['event']['openDate'].split('T')[1][:5]
        runnerMappings = getRunnerMappings(market) #ignoring since we don't use runner mapping id's etc
        filename = eventDate+'_'+eventTime+'_'+eventName+'.csv'
        #print (eventName,'\n',eventDate,'\n',runnerMappings,'\n')

        fo = open('./data/'+filename, 'a')

        market_book_result = getMarketBookBestOffers(marketid)

        current_time = datetime.datetime.now()
        isInplay = market_book_result['inplay']
        status = market_book_result['status']
        version = market_book_result['version']
        totalMatched = market_book_result['totalMatched']
        totalAvailable = market_book_result['totalAvailable']

        runnerDataString = getRunnerDataString(market_book_result['runners'])

        fo.write(str(current_time)+','+str(isInplay)+','+status+','+str(version)+','+str(totalMatched)+','+str(totalAvailable)+','+runnerDataString+'\n')

        #store all stuff above in db

    time.sleep(1)
