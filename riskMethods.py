#!/usr/bin/env python3
import sys
import os
sys.path.insert(1,os.path.join(sys.path[0], '..'))

def get_sequenced_returns(sequence):
    pctList = []
    for i in range(1,len(sequence)):
        pctList.append(((sequence[i]/sequence[i-1])-1.))
    return(pctList)

def standard_deviation(numList):
    try:
        numMean = sum(numList) / len(numList)
    except:
        numMean = 0
    errorList = []
    for n in numList:
        errorList.append((n-numMean))
    sqErrorList = [x*x for x in errorList]
    sumSqError = sum(sqErrorList)
    try:
        variance = sumSqError / len(sqErrorList)
        sigma = variance**(1/2)
    except:
        variance = 0
        sigma = 0
    return(sigma)

def sortino_ratio(valueList):
    pctList =  get_sequenced_returns(valueList)
    downPctList = [x for x in pctList if x<0]
    downPctSigma = standard_deviation(downPctList)
    totalReturn = total_return(valueList)
    try:
        sortino = totalReturn / downPctSigma
    except:
        sortino = 0
    return(sortino)

def sharpe_ratio(valueList):
    pctList = get_sequenced_returns(valueList)
    pctSigma = standard_deviation(pctList)
    totalReturn = total_return(valueList)
    try:
        sharpe = totalReturn / pctSigma
    except:
        sharpe = 0
    return(sharpe)

def total_return(valueList):
    totalReturn = (valueList[-1]/valueList[0])-1
    return(totalReturn)

def maximum_drawdown(valueList):
    high = 0
    maxDrawdown = 0
    for v in valueList:
        if(v>high):
            high = v
        if(v<high):
            drawdown = 1-(v/high)
            if(drawdown>maxDrawdown):
                maxDrawdown = drawdown
    return(abs(maxDrawdown))

def master(valueList):
    valueList = [x["totalValue"] for x in valueList]
    sharpeRatio = sharpe_ratio(valueList)
    sortinoRatio = sortino_ratio(valueList)
    maxDrawdown = maximum_drawdown(valueList)
    pctList = get_sequenced_returns(valueList)
    stdDev = standard_deviation(pctList)
    totalReturn = total_return(valueList)
    return(sharpeRatio, sortinoRatio, maxDrawdown, stdDev, totalReturn)
