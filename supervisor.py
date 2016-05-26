#!/usr/bin/env python3
import sys
import os
sys.path.insert(1,os.path.join(sys.path[0], '..'))
import pairSelector
import simulationConfig
import master
import time
import json
from multiprocessing import Pool

def get_pairs(exchanges):
    pairDict = pairSelector.execute(exchanges)
    return(pairDict)

def run_pairs(pair):
    combo = list(pair.keys())[0]
    partA = combo[:combo.index("/")]
    partB = combo[combo.index("/")+1:]
    value = float(list(pair.values())[0])
    AB = master.execute(partA, partB)
    BA = master.execute(partB, partA)
    return({combo:{"AB":AB,"BA":BA,"RSQ":value}})

def iter_sectors(pairDict):
    sectors = simulationConfig._sectors

    n = 0
    for sector in sectors:
        n += len(pairDict[sector])

    k = 0
    resultsDict = {}
    for sector in sectors:
        pool = Pool(processes=16)
        pairList = pairDict[sector]
        #pairList = pairList[0:1]
        backtestResults = pool.map(run_pairs,pairList)
        resultsDict[sector] = backtestResults
    return(resultsDict)

def execute():
    start = time.time()
    exchanges = simulationConfig._exchanges
    pairs = get_pairs(exchanges)
    resultsDict = iter_sectors(pairs)
    end = time.time()
    runTime = round(float((end-start) / 60),2)
    startDate = simulationConfig._startDate
    endDate = simulationConfig._endDate
    highEnterSigma = simulationConfig._highEnterSigma
    highExitSigma = simulationConfig._highEnterSigma
    lowEnterSigma = simulationConfig._lowEnterSigma
    lowExitSigma = simulationConfig._lowExitSigma
    stopLossPercentage = simulationConfig._stopLossPercentage
    lookBackDays = simulationConfig._lookBackDays
    rSqThreshold = simulationConfig._rSquaredThreshold
    exchanges = simulationConfig._exchanges
    stats = {"start":startDate,
            "end":endDate,
            "highExitSigma":highExitSigma,
            "highEnterSigma":highEnterSigma,
            "lowEnterSigma":lowEnterSigma,
            "lowExitSigma":lowExitSigma,
            "stopLossPercentage":stopLossPercentage,
            "lookBackDays":lookBackDays,
            "rSqThreshold":rSqThreshold,
            "exchanges":exchanges}
    jData = json.dumps({"runTime":runTime, "results":resultsDict, "stats":stats})
    outString = str(int(end))
    with open('results/'+outString+'.json', 'w') as outfile:
        outfile.write(jData)

if __name__ == "__main__":
    execute()
