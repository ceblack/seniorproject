#!/usr/bin/env python3
import sys
import os
sys.path.insert(1,os.path.join(sys.path[0], '..'))
from datetime import datetime
from datetime import timedelta
from datetime import date
from charting import makeLineChart
import objects
import getHistoricalPrices
import simulationConfig
import execution
import riskMethods
from multiprocessing import Pool

def rebalance(queue, portfolio):
    orderList = queue.get_orders()
    portfolio.modify_positions(orderList)
    portfolio.check_stops(queue)
    queue.orders = []

def pretty_print(portfolio, portfolioTracker):
    print("")
    firstLine = "\rPortfolio Stats for "+str(portfolioTracker.get_last_date())+":"
    secondLine = "ReturnToDate: "+str(round(portfolioTracker.get_total_return(),2))
    thirdLine = "TotalValue: $"+str(round(portfolioTracker.get_last(),2))
    secondLine = secondLine + " | " + thirdLine
    print(firstLine)
    print(secondLine)
    positions = portfolio.get_positions()
    positionList = []
    for p in positions:
        positionList.append(p.get_company().get_symbol() +" ("+  str(p.get_quantity())+")")
    positionString = " | ".join(positionList)
    print("Positions: "+positionString)
    sys.stdout.flush()

def json_boolean_conv(flagList):
    newList = []
    for flag in flagList:
        x = 0
        if(flag):
            x = 1
        newList.append(x)
    return(newList)

def consolidate_portfolio_stats(portfolioTracker, modelContainer):
    statDict = {}
    recordList = modelContainer.get_record_list()
    statDict["portfolioHistory"] = portfolioTracker.get_value_list()
    statDict["spread"] = recordList[0]
    statDict["spreadCoef"] = recordList[1]
    statDict["spreadIntercept"] = recordList[2]
    statDict["coef"] = recordList[3]
    statDict["intercept"] = recordList[4]
    statDict["enterFlag"] = json_boolean_conv(recordList[5])
    statDict["exitFlag"] = json_boolean_conv(recordList[6])
    statDict["shortFlag"] = json_boolean_conv(recordList[7])
    statDict["detrendedSpread"] = recordList[8]
    statDict["detrendedSpreadSigma"] = recordList[9]
    statDict["detrendedZScore"] = recordList[10]
    statDict["detrendedAvg"] = recordList[11]
    statDict["positionFlag"] = json_boolean_conv(recordList[12])
    sharpeRatio, sortinoRatio, maxDrawdown, stdDev, totalReturn = riskMethods.master(portfolioTracker.get_value_list())
    statDict["sharpeRatio"] = sharpeRatio
    statDict["sortinoRatio"] = sortinoRatio
    statDict["maxDrawdown"] = maxDrawdown
    statDict["stdDev"] = stdDev
    statDict["totalReturn"] = totalReturn
    return(statDict)

def iter_kalman(portfolio, portfolioTracker, pair, pairData, queue, dateStringList, dateTimeList, startDay, prettyPrint):
    priorDay = dateTimeList[0] - timedelta(days=1)
    a = pair[0]
    aData = pairData[0]
    b = pair[1]
    bData = pairData[1]
    startIndex = dateStringList.index(startDay)
    modelContainer = objects.ModelObjects()
    for i in range(startIndex,len(dateStringList)):
        d = dateStringList[i]
        dT = dateTimeList[i]
        a.update_date(d)
        b.update_date(d)
        portfolioTracker.add_date(portfolio, d)
        ################################
        ########EXECUTION LOGIC#########
        execution.pairs_kalman(a, b, portfolio, queue, modelContainer)
        ################################
        rebalance(queue,portfolio)
        queue.decrement_expirations(int((dT-priorDay).total_seconds()/86400.))
        priorDay = dT

    statDict = consolidate_portfolio_stats(portfolioTracker, modelContainer)
    return(statDict)

def iter_ols(portfolio, portfolioTracker, pair, pairData, queue, dateStringList, dateTimeList, startDay, prettyPrint):
    priorDay = dateTimeList[0] - timedelta(days=1)
    a = pair[0]
    aData = pairData[0]
    b = pair[1]
    bData = pairData[1]
    startIndex = dateStringList.index(startDay)
    modelContainer = objects.ModelObjects()
    for i in range(startIndex,len(dateStringList)):
        d = dateStringList[i]
        dT = dateTimeList[i]
        a.update_date(d)
        b.update_date(d)
        portfolioTracker.add_date(portfolio, d)
        ################################
        ########EXECUTION LOGIC#########
        execution.pairs_ols(a, b, portfolio, queue, modelContainer)
        ################################
        rebalance(queue,portfolio)
        queue.decrement_expirations(int((dT-priorDay).total_seconds()/86400.))
        priorDay = dT

    statDict = consolidate_portfolio_stats(portfolioTracker, modelContainer)
    return(statDict)

def iter_odr(portfolio, portfolioTracker, pair, pairData, queue, dateStringList, dateTimeList, startDay, prettyPrint):
    priorDay = dateTimeList[0] - timedelta(days=1)
    a = pair[0]
    aData = pairData[0]
    b = pair[1]
    bData = pairData[1]
    startIndex = dateStringList.index(startDay)
    modelContainer = objects.ModelObjects()
    for i in range(startIndex,len(dateStringList)):
        d = dateStringList[i]
        dT = dateTimeList[i]
        a.update_date(d)
        b.update_date(d)
        portfolioTracker.add_date(portfolio, d)
        ################################
        ########EXECUTION LOGIC#########
        execution.pairs_odr(a, b, portfolio, queue, modelContainer)
        ################################
        rebalance(queue,portfolio)
        queue.decrement_expirations(int((dT-priorDay).total_seconds()/86400.))
        priorDay = dT

    statDict = consolidate_portfolio_stats(portfolioTracker, modelContainer)
    return(statDict)

def result_chart(portfolioTracker):
    valueList = portfolioTracker.get_value_list()
    dollarList = []
    for v in valueList:
        dollarList.append(v["totalValue"])
    print(makeLineChart.line_chart([dollarList],["TotalValue"]))

def companies_chart(companyList, startIndex, dateStringList):
    tradingLength = len(dateStringList)-startIndex
    priceList = []
    nameList = []
    for c in companyList:
        priceList.append(c.get_trailing_days(tradingLength))
        nameList.append(c.get_symbol())
    print(makeLineChart.line_chart(priceList,nameList))

def get_date_range(yahooData, lookBack):
    dateList = []
    for y in yahooData:
        dateList.append(y)

    dateObjList = [datetime.strptime(x, "%Y-%m-%d") for x in dateList]
    dateObjList = [date(x.year,x.month,x.day) for x in dateObjList]
    dateObjList = list(sorted(dateObjList))
    dateStringList = [datetime.strftime(x,"%Y-%m-%d") for x in dateObjList]
    maxDateObj = max(dateObjList)
    maxDateString = dateStringList[-1]
    minDateString = dateStringList[0]
    minDateObj = min(dateObjList)
    tradingDays = len(dateObjList)
    allDays = int((maxDateObj - minDateObj).total_seconds()/86400.)
    startDateObj = dateObjList[lookBack-1]
    startDateString = dateStringList[lookBack-1]
    dateInfo = [minDateString, maxDateString, dateStringList, dateObjList, startDateObj, startDateString, tradingDays, allDays]
    return(dateInfo)

def combine_date_lists(a,b):
    c = a+b
    d = list(set(c))
    dateObjList = [datetime.strptime(x, "%Y-%m-%d") for x in d]
    dateObjList = [date(x.year,x.month,x.day) for x in dateObjList]
    dateObjList = list(sorted(dateObjList))
    dateStringList = [datetime.strftime(x,"%Y-%m-%d") for x in dateObjList]
    return(dateStringList, dateObjList)

def clean_historical_data(historicalData):
    newDict = {}
    for d in historicalData:
        newDict[d] = float(historicalData[d]["Adj Close"])
    return(newDict)

def get_historical_data(a, b, beginDate, endDate, lookBack):
    historyStartDate = datetime.strptime(beginDate, "%Y-%m-%d") - timedelta(days=lookBack)
    historyStartDate = datetime.strftime(historyStartDate, "%Y-%m-%d")
    aData = clean_historical_data(getHistoricalPrices.get_prices(a, historyStartDate, endDate))
    bData = clean_historical_data(getHistoricalPrices.get_prices(b, historyStartDate, endDate))
    aDateInfo = get_date_range(aData, lookBack)
    bDateInfo = get_date_range(bData, lookBack)
    return(aDateInfo, aData, bDateInfo, bData)

def iter_strats(portfolio, portfolioTracker, pair, pairData, queue, dateStringList, dateObjList, startDay, prettyPrint):
    kalmanData = iter_kalman(portfolio, portfolioTracker, pair, pairData, queue, dateStringList, dateObjList, startDay, prettyPrint)
    olsData = iter_ols(portfolio, portfolioTracker, pair, pairData, queue, dateStringList, dateObjList, startDay, prettyPrint)
    odrData = iter_odr(portfolio, portfolioTracker, pair, pairData, queue, dateStringList, dateObjList, startDay, prettyPrint)
    return(kalmanData, olsData, odrData)

def execute(a, b):
    portfolio = objects.Portfolio()
    portfolioTracker = objects.PortfolioTracker()
    queue = objects.Queue()
    beginDate = simulationConfig._startDate
    endDate = simulationConfig._endDate
    lookBack = int(simulationConfig._lookBackDays * 2)
    aDateInfo, aData, bDateInfo, bData = get_historical_data(a, b, beginDate, endDate, lookBack)
    dateStringList, dateObjList = combine_date_lists(aDateInfo[2], bDateInfo[2])
    pairData = [aData, bData]
    pair = [objects.Company(a,aData,aDateInfo[2],aDateInfo[5]), objects.Company(b,bData,bDateInfo[2],bDateInfo[5])]
    prettyPrint = True
    kalmanData, olsData, odrData = iter_strats(portfolio, portfolioTracker, pair, pairData, queue, dateStringList, dateObjList, aDateInfo[5], prettyPrint)
    dataDict = {"kalmanData":kalmanData, "olsData":olsData, "odrData":odrData}
    return(dataDict)


if __name__ == "__main__":
    print(execute(sys.argv[1],sys.argv[2]))
