#!/usr/bin/env python3
import sys
import os
sys.path.insert(1,os.path.join(sys.path[0], '..'))
from prediction_methods import ols
from prediction_methods import odr
from prediction_methods import kalman
from charting import makeLineChart
import simulationConfig
import numpy as np
import objects

def record_model_data(modelContainer, spread, spreadCoef, spreadIntercept, coef, intercept, enterFlag, exitFlag, shortFlag, detrendedSpread, detrendedSpreadSigma, detrendedZScore, detrendedAvg, portfolio):
    positions = portfolio.get_positions()
    positionFlag = (len(positions)!=0)
    if(len(modelContainer.get_record_list())<=0):
        modelContainer.add_record([spread])
        modelContainer.add_record([spreadCoef])
        modelContainer.add_record([spreadIntercept])
        modelContainer.add_record([coef])
        modelContainer.add_record([intercept])
        modelContainer.add_record([enterFlag])
        modelContainer.add_record([exitFlag])
        modelContainer.add_record([shortFlag])
        modelContainer.add_record([detrendedSpread])
        modelContainer.add_record([detrendedSpreadSigma])
        modelContainer.add_record([detrendedZScore])
        modelContainer.add_record([detrendedAvg])
        modelContainer.add_record([positionFlag])
    else:
        recordList = modelContainer.get_record_list()
        recordList[0].append(spread)
        recordList[1].append(spreadCoef)
        recordList[2].append(spreadIntercept)
        recordList[3].append(coef)
        recordList[4].append(intercept)
        recordList[5].append(enterFlag)
        recordList[6].append(exitFlag)
        recordList[7].append(shortFlag)
        recordList[8].append(detrendedSpread)
        recordList[9].append(detrendedSpreadSigma)
        recordList[10].append(detrendedZScore)
        recordList[11].append(detrendedAvg)
        recordList[12].append(positionFlag)
        modelContainer.recordList = recordList

def pairs_kalman(aCompany, bCompany, portfolio, queue, modelContainer):
    existingOrders = queue.get_orders()
    existingStops = queue.get_stops()
    orderList = []
    stopList = existingStops
    availableCash = portfolio.get_available_cash()
    value = portfolio.get_total_portfolio_value()
    aTrailingPrices = aCompany.get_trailing_days(simulationConfig._lookBackDays)
    bTrailingPrices = bCompany.get_trailing_days(simulationConfig._lookBackDays)
    d = aCompany.get_current_date()
    if(len(modelContainer.get_model_list())<=0):
        kf = kalman.Regression(aTrailingPrices,bTrailingPrices,d)
        modelContainer.add_model(kf)
        coef = kf.state_mean.beta
        intercept = kf.state_mean.alpha
    else:
        kf = modelContainer.get_model(0)
        kf.update([aTrailingPrices[-1],bTrailingPrices[-1]],d)
        coef = kf.state_mean.beta
        intercept = kf.state_mean.alpha
    spread = [0]
    detrendedSpread = [0]
    spreadCoef = 0
    spreadIntercept = 0
    enterFlag = True
    exitFlag = True
    shortFlag = True
    detrendedSpreadSigma = 0
    detrendedZScore = 0
    detrendedAvg = 0
    if(coef>0):
        spread = []
        detrendedSpread = []
        for i in range(0,len(aTrailingPrices)):
            spread.append(aTrailingPrices[i] - (coef * bTrailingPrices[i]))
        spreadSigma = ols.get_standard_sigma(spread)
        spreadX = list(range(1,len(spread)+1))

        if(len(modelContainer.get_model_list())<=1):
            spread_kf = kalman.Regression(spread, spreadX, d)
            modelContainer.add_model(spread_kf)
            spreadCoef = spread_kf.state_mean.beta
            spreadIntercept = spread_kf.state_mean.alpha
        else:
            spread_kf = modelContainer.get_model(1)
            spread_kf.update([spread[-1], spreadX[-1]], d)
            spreadCoef = spread_kf.state_mean.beta
            spreadIntercept = spread_kf.state_mean.alpha
        spreadLine = ols.make_line(spreadCoef,spreadIntercept,spreadX)
        for i in range(0,len(spread)):
            detrendedSpread.append(spreadLine[i] - spread[i])
        detrendedSpreadSigma = ols.get_standard_sigma(detrendedSpread)
        detrendedAvg = sum(detrendedSpread)/len(detrendedSpread)
        detrendedZScore = (detrendedSpread[-1] - detrendedAvg) / detrendedSpreadSigma
        existingAShares = portfolio.get_positions_by_company(aCompany)
        existingBShares = portfolio.get_positions_by_company(bCompany)
        enterFlag = abs(detrendedZScore)>=simulationConfig._lowEnterSigma and abs(detrendedZScore)<=simulationConfig._highEnterSigma
        exitFlag = abs(detrendedZScore)<simulationConfig._lowExitSigma or abs(detrendedZScore)>simulationConfig._highEnterSigma
        shortFlag = (detrendedZScore < 0)
        if(enterFlag):
            totalSpreadCost = aTrailingPrices[-1] - coef*bTrailingPrices[-1]
            absoluteSpreadCost = aTrailingPrices[-1] + coef*bTrailingPrices[-1]
            units = availableCash / absoluteSpreadCost
            aShares = int(units)
            bShares = int(units*coef)*-1
            if(shortFlag):
                aShares = aShares * -1
                bShares = bShares * -1
            aOrder = objects.MarketOrder(aCompany,aShares,10)
            bOrder = objects.MarketOrder(bCompany,bShares,10)
            orderList.append(bOrder)
            orderList.append(aOrder)
            if(len(existingStops)==0):
                stopList.append(objects.StopOrder(portfolio.get_total_portfolio_value()*simulationConfig._stopLossPercentage,-999))
        if(exitFlag):
            stopList = []
            orderList = []
            orderList = get_flat(portfolio)


    if(len(existingOrders)!=0):
        orderList = []

    queue.orders = orderList
    queue.stops = stopList

    record_model_data(modelContainer, spread[-1], spreadCoef, spreadIntercept, coef, intercept, enterFlag, exitFlag,
                        shortFlag, detrendedSpread[-1], detrendedSpreadSigma, detrendedZScore, detrendedAvg, portfolio)

def pairs_odr(aCompany, bCompany, portfolio, queue, modelContainer):
    existingOrders = queue.get_orders()
    existingStops = queue.get_stops()
    orderList = []
    stopList = existingStops
    availableCash = portfolio.get_available_cash()
    value = portfolio.get_total_portfolio_value()
    aTrailingPrices = aCompany.get_trailing_days(simulationConfig._lookBackDays)
    bTrailingPrices = bCompany.get_trailing_days(simulationConfig._lookBackDays)
    coef, intercept = odr.ortho_regress(aTrailingPrices, bTrailingPrices)
    spread = [0]
    detrendedSpread = [0]
    spreadCoef = 0
    spreadIntercept = 0
    enterFlag = True
    exitFlag = True
    shortFlag = True
    detrendedSpreadSigma = 0
    detrendedZScore = 0
    detrendedAvg = 0
    if(coef>0):
        spread = []
        detrendedSpread = []
        for i in range(0,len(aTrailingPrices)):
            spread.append(aTrailingPrices[i] - (coef * bTrailingPrices[i]))
        spreadSigma = ols.get_standard_sigma(spread)
        spreadX = list(range(1,len(spread)+1))
        spreadCoef,spreadIntercept = odr.ortho_regress(spreadX,spread)
        spreadLine = ols.make_line(spreadCoef,spreadIntercept,spreadX)
        for i in range(0,len(spread)):
            detrendedSpread.append(spreadLine[i] - spread[i])
        detrendedSpreadSigma = ols.get_standard_sigma(detrendedSpread)
        detrendedAvg = sum(detrendedSpread)/len(detrendedSpread)
        detrendedZScore = (detrendedSpread[-1] - detrendedAvg) / detrendedSpreadSigma
        existingAShares = portfolio.get_positions_by_company(aCompany)
        existingBShares = portfolio.get_positions_by_company(bCompany)
        enterFlag = abs(detrendedZScore)>=simulationConfig._lowEnterSigma and abs(detrendedZScore)<=simulationConfig._highEnterSigma
        exitFlag = abs(detrendedZScore)<simulationConfig._lowExitSigma or abs(detrendedZScore)>simulationConfig._highEnterSigma
        shortFlag = (detrendedZScore < 0)
        if(enterFlag):
            totalSpreadCost = aTrailingPrices[-1] - coef*bTrailingPrices[-1]
            absoluteSpreadCost = aTrailingPrices[-1] + coef*bTrailingPrices[-1]
            units = availableCash / absoluteSpreadCost
            aShares = int(units)
            bShares = int(units*coef)*-1
            if(shortFlag):
                aShares = aShares * -1
                bShares = bShares * -1
            aOrder = objects.MarketOrder(aCompany,aShares,10)
            bOrder = objects.MarketOrder(bCompany,bShares,10)
            orderList.append(bOrder)
            orderList.append(aOrder)
            if(len(existingStops)==0):
                stopList.append(objects.StopOrder(portfolio.get_total_portfolio_value()*simulationConfig._stopLossPercentage,-999))
        if(exitFlag):
            stopList = []
            orderList = []
            orderList = get_flat(portfolio)


    if(len(existingOrders)!=0):
        orderList = []

    queue.orders = orderList
    queue.stops = stopList

    record_model_data(modelContainer, spread[-1], spreadCoef, spreadIntercept, coef, intercept, enterFlag, exitFlag,
                        shortFlag, detrendedSpread[-1], detrendedSpreadSigma, detrendedZScore, detrendedAvg, portfolio)

def pairs_ols(aCompany, bCompany, portfolio, queue, modelContainer):
    existingOrders = queue.get_orders()
    existingStops = queue.get_stops()
    orderList = []
    stopList = existingStops
    availableCash = portfolio.get_available_cash()
    value = portfolio.get_total_portfolio_value()
    aTrailingPrices = aCompany.get_trailing_days(simulationConfig._lookBackDays)
    bTrailingPrices = bCompany.get_trailing_days(simulationConfig._lookBackDays)
    coef, intercept = ols.OLS(aTrailingPrices, bTrailingPrices)
    spread = [0]
    detrendedSpread = [0]
    spreadCoef = 0
    spreadIntercept = 0
    enterFlag = True
    exitFlag = True
    shortFlag = True
    detrendedSpreadSigma = 0
    detrendedZScore = 0
    detrendedAvg = 0
    if(coef>0):
        spread = []
        detrendedSpread = []
        for i in range(0,len(aTrailingPrices)):
            spread.append(aTrailingPrices[i] - (coef * bTrailingPrices[i]))
        spreadSigma = ols.get_standard_sigma(spread)
        spreadX = list(range(1,len(spread)+1))
        spreadCoef,spreadIntercept = ols.OLS(spreadX,spread)
        spreadLine = ols.make_line(spreadCoef,spreadIntercept,spreadX)
        for i in range(0,len(spread)):
            detrendedSpread.append(spreadLine[i] - spread[i])
        detrendedSpreadSigma = ols.get_standard_sigma(detrendedSpread)
        detrendedAvg = sum(detrendedSpread)/len(detrendedSpread)
        detrendedZScore = (detrendedSpread[-1] - detrendedAvg) / detrendedSpreadSigma
        existingAShares = portfolio.get_positions_by_company(aCompany)
        existingBShares = portfolio.get_positions_by_company(bCompany)
        enterFlag = abs(detrendedZScore)>=simulationConfig._lowEnterSigma and abs(detrendedZScore)<=simulationConfig._highEnterSigma
        exitFlag = abs(detrendedZScore)<simulationConfig._lowExitSigma or abs(detrendedZScore)>simulationConfig._highEnterSigma
        shortFlag = (detrendedZScore < 0)
        if(enterFlag):
            totalSpreadCost = aTrailingPrices[-1] - coef*bTrailingPrices[-1]
            absoluteSpreadCost = aTrailingPrices[-1] + coef*bTrailingPrices[-1]
            units = availableCash / absoluteSpreadCost
            aShares = int(units)
            bShares = int(units*coef)*-1
            if(shortFlag):
                aShares = aShares * -1
                bShares = bShares * -1
            aOrder = objects.MarketOrder(aCompany,aShares,10)
            bOrder = objects.MarketOrder(bCompany,bShares,10)
            orderList.append(bOrder)
            orderList.append(aOrder)
            if(len(existingStops)==0):
                stopList.append(objects.StopOrder(portfolio.get_total_portfolio_value()*simulationConfig._stopLossPercentage,-999))
        if(exitFlag):
            stopList = []
            orderList = []
            orderList = get_flat(portfolio)


    if(len(existingOrders)!=0):
        orderList = []

    queue.orders = orderList
    queue.stops = stopList

    record_model_data(modelContainer, spread[-1], spreadCoef, spreadIntercept, coef, intercept, enterFlag, exitFlag,
                    shortFlag, detrendedSpread[-1], detrendedSpreadSigma, detrendedZScore, detrendedAvg, portfolio)

def get_flat(portfolio):
    tempOrderList = []
    for p in portfolio.get_positions():
        newOrder = objects.MarketOrder(p.get_company(),-1*p.get_quantity(),10)
        tempOrderList.append(newOrder)
    return(tempOrderList)

def calculate_share_difference(target, actual):
    newOrder = 0
    if(target*actual<0):
        newOrder = target + -1*actual
    elif(target>0):
        newOrder = target-actual
    elif(target<0):
        newOrder = (abs(target) - abs(actual))*-1
    return(newOrder)

def chart_spread(spread,spreadSigma):
    spreadAvg = sum(spread) / len(spread)
    spreadAvgList = [spreadAvg] * len(spread)
    negativeOneSigma = [spreadAvg-spreadSigma] * len(spread)
    negativeTwoSigma = [spreadAvg-(2*spreadSigma)] * len(spread)
    negativeThreeSigma = [spreadAvg-(3*spreadSigma)] * len(spread)
    positiveOneSigma = [spreadAvg+spreadSigma] * len(spread)
    positiveTwoSigma = [spreadAvg+(2*spreadSigma)] * len(spread)
    positiveThreeSigma = [spreadAvg+(3*spreadSigma)] * len(spread)
    nameList = ["Spread","Avg","-1 Sigma","+1 Sigma","-2 Sigma","+2 Sigma","-3 Sigma","+3 Sigma"]
    lineList = [spread,spreadAvgList,negativeOneSigma,positiveOneSigma,negativeTwoSigma,positiveTwoSigma,negativeThreeSigma,positiveThreeSigma]
    print(makeLineChart.line_chart(lineList,nameList))

if __name__ == "__main__":
    pass
