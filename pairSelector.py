#!/usr/bin/env python3
import sys
import os
sys.path.insert(1,os.path.join(sys.path[0], '..'))
import simulationConfig
from prediction_methods import ols
from itertools import combinations
import stockCollector
import json
import getHistoricalPrices
from datetime import datetime
from datetime import timedelta

def get_stocks(exchangeList):
    stocks = stockCollector.execute(exchangeList)
    return(stocks)

def get_rsquared(symbolA,symbolB):
    coef, intercept = ols.OLS(symbolA, symbolB)
    rSquared = ols.r_squared(coef, intercept, symbolA, symbolB)
    return(rSquared)

def sort_stocks(stocks):
    sectorList = []
    for s in stocks:
        sectorList.append(s["sectorName"])
    sectorList = list(set(sectorList))

    comboDict = {}
    sectorDict = {}
    for s in sectorList:
        sectorDict[s] = {}
        comboDict[s] = {}

    for s in stocks:
        tempList = sectorDict[s["sectorName"]]
        if(type(tempList) == type({})):
            tempList = []
        tempList.append(s["symbol"])
        sectorDict[s["sectorName"]] = tempList

    for s in sectorDict:
        comboDict[s] = ["/".join(map(str,comb)) for comb in combinations(sectorDict[s], 2)]

    return(comboDict, sectorDict)

def clean_historical_data(historicalData):
    newDict = {}
    dateList = []
    valueList = []
    for d in historicalData:
        dateList.append(datetime.strptime(d,"%Y-%m-%d"))
        newDict[d] = float(historicalData[d]["Adj Close"])
    sortedDateList = list(sorted(dateList))
    sortedDateStrings = [datetime.strftime(x,"%Y-%m-%d") for x in sortedDateList]
    for s in sortedDateStrings:
        valueList.append(newDict[s])
    return(valueList)

def get_historical_data(a, beginDate, endDate):
    try:
        aData = clean_historical_data(getHistoricalPrices.get_prices(a, beginDate, endDate))
        return(aData)
    except:
        return(None)

def add_rsquared(comboDict, sectorDict):
    sectors = simulationConfig._sectors
    historyDict = {}
    threshold = simulationConfig._rSquaredThreshold
    endDate = simulationConfig._startDate
    beginDateTime = datetime.strptime(endDate,"%Y-%m-%d") - timedelta(days=simulationConfig._lookBackDays)
    beginDate = datetime.strftime(beginDateTime,"%Y-%m-%d")
    for sector in sectors:
        for symbol in sectorDict[sector]:
            data = get_historical_data(symbol,beginDate,endDate)
            if(data!=None):
                historyDict[symbol] = get_historical_data(symbol,beginDate,endDate)
    rDict = {}
    for sector in sectors:
        rDict[sector] = {}
        for combo in comboDict[sector]:
            partA = combo[:combo.index("/")]
            partB = combo[combo.index("/")+1:]
            try:
                priceA = historyDict[partA]
                priceB = historyDict[partB]
                rSq = get_rsquared(historyDict[partA],historyDict[partB])
                if(type(rDict[sector])==type({})):
                    rDict[sector] = [{combo:rSq}]
                else:
                    rDict[sector].append({combo:rSq})
            except:
                pass

    for sector in sectors:
        rList = rDict[sector]
        newList = []
        for r in rList:
            combo = list(r.keys())[0]
            partA = combo[:combo.index("/")]
            partB = combo[combo.index("/")+1:]
            value = float(list(r.values())[0])
            if(value>=threshold):
                newList.append({combo:value})
        rDict[sector] = newList
    return(rDict)


def execute(exchangeList):
    stocks = get_stocks(exchangeList)
    comboDict, sectorDict = sort_stocks(stocks)
    rDict = add_rsquared(comboDict, sectorDict)
    return(rDict)

if __name__ == "__main__":
    execute(["NYS"])
