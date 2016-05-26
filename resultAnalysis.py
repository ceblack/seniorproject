#!/usr/bin/env python3
import sys
import os
sys.path.insert(1,os.path.join(sys.path[0], '..'))
from datetime import datetime
from datetime import timedelta
import json
from charting import getChartColors
from charting import getChartName
import plotly.plotly as py
import plotly.tools as tls
import plotly.graph_objs as go
from td_plotly import signIn

def plotly_height_changer(plotlyURL, desiredHeight):
    newURL = plotlyURL.replace('height="525"','height="'+str(int(desiredHeight))+'"')
    return(newURL)

def right_pad(padNum, val):
    try:
        val = str(round(float(val),padNum))
        while(len(val[val.index("."):])<4):
            val = val + "0"
        return(val)
    except:
        return(val)

def html_table_generator(valueMatrix):
    prefix = "<table cellpadding=\"3\">"
    suffix = "</table>"
    headers = valueMatrix[0]
    headerString = "<tr>"
    for h in headers:
        tempString = "<th>"+h+"</th>"
        headerString = headerString + tempString
    headerString = headerString + "</tr>"
    tableString = ""
    for i in range(1,len(valueMatrix)):
        tempStringList = []
        for val in valueMatrix[i]:
            if(type(val)!=str):
                val = str(round(float(val),3))
            val = right_pad(3, val)
            tempStringList.append("<td>"+val+"</td>")
        rowString = " ".join(tempStringList)
        rowString = "<tr>"+rowString+"</tr>"
        tableString = tableString + rowString
    table = prefix + headerString + tableString + suffix
    return(table)

def read_file(filepath):
    jData = json.loads(open(filepath).read())
    return(jData)

def annualize_by_traded_days(totalReturn, positionList):
    tradedDays = sum(positionList)
    exponentList = []
    try:
        if(tradedDays!=0):
            if(tradedDays>=252):
                annualizedReturn = 1+((totalReturn-1)*(252/tradedDays))
            else:
                annualizedReturn = totalReturn ** (252/tradedDays)
                if(type(annualizedReturn)==complex):
                    annualizedReturn = 1
        else:
            annualizedReturn = 1
    except Exception as e:
        annualizedReturn = 1
    annualizedReturn = round(float(annualizedReturn),5)
    return(annualizedReturn)

def annualize_returns(totalReturn, positionList):
    totalDays = len(positionList)
    try:
        if(totalDays>252):
            annualizedReturn = totalReturn * (252/totalDays)
        else:
            annualizedReturn = totalReturn ** (252/totalDays)
    except:
        annualizedReturn = 1
    annualizedReturn = round(float(annualizedReturn),5)
    return(annualizedReturn)

def get_basic_stats(valueList):
    try:
        listAvg = sum(valueList) / len(valueList)
    except:
        listAvg = 0
    listRange = max(valueList) - min(valueList)
    listMax = max(valueList)
    listMin = min(valueList)
    listMedian = 0
    if(len(valueList)%2==0):
        topInd = int(len(valueList) / 2)
        bottomInd = topInd - 1
        try:
            listMedian = (valueList[topInd] + valueList[bottomInd]) / 2
        except:
            listMedian = 0
    else:
        medInd = int((len(valueList)-1) / 2)
        listMedian = valueList[medInd]
    return([listAvg, listMedian, listRange, listMax, listMin])

def add_leader_flag(jData):
    resultContainer = jData["results"]
    for r in resultContainer:
        results = resultContainer[r]
        for i in range(0,len(results)):
            key = list(results[i].keys())[0]
            pair = results[i][key]
            stratKeys = pair["AB"].keys()
            for s in stratKeys:
                ABleader = 0
                BAleader = 0
                ABreturn = pair["AB"][s]["totalReturn"]
                BAreturn = pair["BA"][s]["totalReturn"]
                if(ABreturn>BAreturn):
                    ABleader = 1
                elif(BAreturn>ABreturn):
                    BAleader = 1
                pair["AB"][s]["leader"] = ABleader
                pair["BA"][s]["leader"] = BAleader
    return(jData)

def get_paired_returns(data, strategy):
    dataDict = {}
    resultContainer = data["results"]
    for r in resultContainer:
        results = resultContainer[r]
        for i in range(0,len(results)):
            key = list(results[i].keys())[0]
            pair = results[i][key]
            AB = pair["AB"][strategy]["totalReturn"]
            BA = pair["BA"][strategy]["totalReturn"]
            dataDict[key] = {"AB":AB, "BA":BA}
    return(dataDict)

def get_annualized_by_activity(data, strategy, leaderFlag, laggerFlag):
    dataList = []
    resultContainer = data["results"]
    for r in resultContainer:
        results = resultContainer[r]
        for i in range(0,len(results)):
            key = list(results[i].keys())[0]
            pair = results[i][key]
            ABreturn = pair["AB"][strategy]["totalReturn"]
            ABpositionFlag = pair["AB"][strategy]["positionFlag"]
            BAreturn = pair["BA"][strategy]["totalReturn"]
            BApositionFlag = pair["BA"][strategy]["positionFlag"]
            AB = annualize_by_traded_days(ABreturn, ABpositionFlag)
            BA = annualize_by_traded_days(BAreturn, BApositionFlag)
            ABleader = pair["AB"][strategy]["leader"]
            BAleader = pair["BA"][strategy]["leader"]
            if(leaderFlag):
                if(ABleader==1):
                    dataList.append(AB)
                if(BAleader==1):
                    dataList.append(BA)
            elif(laggerFlag):
                if(ABleader==0):
                    dataList.append(AB)
                if(BAleader==0):
                    dataList.append(BA)
            else:
                dataList.append(AB)
                dataList.append(BA)
    return(dataList)

def extractValue(data, value, strategy, leaderFlag, laggerFlag):
    dataList = []
    resultContainer = data["results"]
    for r in resultContainer:
        results = resultContainer[r]
        for i in range(0,len(results)):
            key = list(results[i].keys())[0]
            pair = results[i][key]
            AB = pair["AB"][strategy][value]
            BA = pair["BA"][strategy][value]
            ABleader = pair["AB"][strategy]["leader"]
            BAleader = pair["BA"][strategy]["leader"]
            if(leaderFlag):
                if(ABleader==1):
                    dataList.append(AB)
                if(BAleader==1):
                    dataList.append(BA)
            elif(laggerFlag):
                if(ABleader==0):
                    dataList.append(AB)
                if(BAleader==0):
                    dataList.append(BA)
            else:
                dataList.append(AB)
                dataList.append(BA)
    return(dataList)

def get_total_pairs(data):
    n = 0
    resultContainer = data["results"]
    for r in resultContainer:
        results = resultContainer[r]
        for i in range(0,len(results)):
            n += 1
    return(n)

def get_traded_days(data, strategy, leaderFlag, laggerFlag):
    dataList = []
    resultContainer = data["results"]
    for r in resultContainer:
        results = resultContainer[r]
        for i in range(0,len(results)):
            key = list(results[i].keys())[0]
            pair = results[i][key]
            AB = sum(pair["AB"][strategy]["positionFlag"])
            BA = sum(pair["BA"][strategy]["positionFlag"])
            ABleader = pair["AB"][strategy]["leader"]
            BAleader = pair["BA"][strategy]["leader"]
            if(leaderFlag):
                if(ABleader==1):
                    dataList.append(AB)
                if(BAleader==1):
                    dataList.append(BA)
            elif(laggerFlag):
                if(ABleader==0):
                    dataList.append(AB)
                if(BAleader==0):
                    dataList.append(BA)
            else:
                dataList.append(AB)
                dataList.append(BA)
    return(dataList)

def total_strategy_sharpe(data,leader,lagger):
    ols = extractValue(data,"sharpeRatio","kalmanData",leader,lagger)
    odr = extractValue(data,"sharpeRatio","odrData",leader,lagger)
    kalman = extractValue(data,"sharpeRatio","olsData",leader,lagger)
    return([ols,odr,kalman])

def total_strategy_sortino(data,leader,lagger):
    ols = extractValue(data,"sortinoRatio","kalmanData",leader,lagger)
    odr = extractValue(data,"sortinoRatio","odrData",leader,lagger)
    kalman = extractValue(data,"sortinoRatio","olsData",leader,lagger)
    return([ols,odr,kalman])

def total_strategy_maxdrawdown(data,leader,lagger):
    ols = extractValue(data,"maxDrawdown","kalmanData",leader,lagger)
    odr = extractValue(data,"maxDrawdown","odrData",leader,lagger)
    kalman = extractValue(data,"maxDrawdown","olsData",leader,lagger)
    return([ols,odr,kalman])

def total_strategy_stddev(data,leader,lagger):
    ols = extractValue(data,"stdDev","kalmanData",leader,lagger)
    odr = extractValue(data,"stdDev","odrData",leader,lagger)
    kalman = extractValue(data,"stdDev","olsData",leader,lagger)
    return([ols,odr,kalman])

def total_strategy_return(data,leader,lagger):
    ols = extractValue(data,"totalReturn","kalmanData",leader,lagger)
    odr = extractValue(data,"totalReturn","odrData",leader,lagger)
    kalman = extractValue(data,"totalReturn","olsData",leader,lagger)
    return([ols,odr,kalman])

def total_strategy_positionflag(data,leader,lagger):
    ols = extractValue(data,"positionFlag","kalmanData",leader,lagger)
    odr = extractValue(data,"positionFlag","odrData",leader,lagger)
    kalman = extractValue(data,"positionFlag","olsData",leader,lagger)
    return([ols,odr,kalman])

def total_strategy_zscore(data,leader,lagger):
    ols = extractValue(data,"detrendedZScore","kalmanData",leader,lagger)
    odr = extractValue(data,"detrendedZScore","odrData",leader,lagger)
    kalman = extractValue(data,"detrendedZScore","olsData",leader,lagger)
    return([ols,odr,kalman])

def total_strategy_activity(data,leader,lagger):
    ols = get_traded_days(data,"kalmanData",leader,lagger)
    odr = get_traded_days(data,"odrData",leader,lagger)
    kalman = get_traded_days(data,"olsData",leader,lagger)
    return([ols,odr,kalman])

def total_strategy_activity_annualized(data,leader,lagger):
    ols = get_annualized_by_activity(data,"kalmanData",leader,lagger)
    odr = get_annualized_by_activity(data,"odrData",leader,lagger)
    kalman = get_annualized_by_activity(data,"olsData",leader,lagger)
    return([ols,odr,kalman])

def make_histogram(layers,labels,name,xAxis,yAxis):
    data = []
    for i in range(0,len(layers)):
        trace = go.Histogram(
        x=layers[i],
        name=labels[i],
        opacity=0.75
        )
        data.append(trace)

    layout = go.Layout(
        barmode='overlay',
        title=name,
        height=350,
        margin=dict(
            t=50,
            b=100,
            l=10,
            r=10,
            pad=30,
        ),
        xaxis=dict(
            title=xAxis
        ),
        yaxis=dict(
            title=yAxis
        )
    )
    name = getChartName.ts()
    fig = go.Figure(data=data, layout=layout)
    plot_url = py.plot(fig, filename=name,auto_open=False)
    embedInfo = tls.get_embed(plot_url)
    embedInfo = plotly_height_changer(embedInfo,300)
    return(embedInfo)

def make_line_chart(layers,labels,name,xAxis,yAxis):
    data = []
    for i in range(0,len(layers)):
        trace = go.Scatter(
            x = list(range(1,len(layers[i]))),
            name = labels[i],
            y = layers[i]
        )
        data.append(trace)
    layout = go.Layout(
        barmode='overlay',
        title=name,
        xaxis=dict(
            title=xAxis
        ),
        yaxis=dict(
            title=yAxis
        )
    )
    fig = go.Figure(data=data, layout=layout)
    plot_url = py.plot(fig, filename=name,auto_open=False)
    embedInfo = tls.get_embed(plot_url)
    return(embedInfo)

def split_combos(combo):
    partA = combo[:combo.index("/")]
    partB = combo[combo.index("/")+1:]
    return(partA, partB)

def extract_return_stats(returnDict):
    pass

def total_strategy_return_stats(data):
    ols = get_paired_returns(data,"olsData")
    odr = get_paired_returns(data,"odrData")
    kalman = get_paired_returns(data,"kalmanData")

def compile_ratio_stats(leaders, laggers, total):
    leaderOLSStats = get_basic_stats(leaders[0])
    leaderODRStats = get_basic_stats(leaders[1])
    leaderKalmanStats = get_basic_stats(leaders[2])
    laggerOLSStats = get_basic_stats(laggers[0])
    laggerODRStats = get_basic_stats(laggers[1])
    laggerKalmanStats = get_basic_stats(laggers[2])
    totalOLSStats = get_basic_stats(total[0])
    totalODRStats = get_basic_stats(total[1])
    totalKalmanStats = get_basic_stats(total[2])
    leaderStats = [leaderOLSStats, leaderODRStats, leaderKalmanStats]
    laggerStats = [laggerOLSStats, laggerODRStats, laggerKalmanStats]
    totalStats = [totalOLSStats, totalODRStats, totalKalmanStats]
    overallStats = [leaderStats,laggerStats,totalStats]
    return(overallStats)

def get_histogram_table_matrix(leaderStats, laggerStats, totalStats):
    headers = ["", "Avg", "Median","Range","Max","Min"]
    leaderOLS = ["OLS"]+leaderStats[0]
    leaderODR = ["ODR"] + leaderStats[1]
    leaderKalman = ["Kalman"] + leaderStats[2]
    laggerOLS = ["OLS"]+laggerStats[0]
    laggerODR = ["ODR"] + laggerStats[1]
    laggerKalman = ["Kalman"] + laggerStats[2]
    totalOLS = ["OLS"]+totalStats[0]
    totalODR = ["ODR"] + totalStats[1]
    totalKalman = ["Kalman"] + totalStats[2]
    leaderMatrix = [headers, leaderOLS, leaderODR, leaderKalman]
    laggerMatrix = [headers, laggerOLS, laggerODR, laggerKalman]
    totalMatrix = [headers, totalOLS, totalODR, totalKalman]
    leaderTable = html_table_generator(leaderMatrix)
    laggerTable = html_table_generator(laggerMatrix)
    totalTable = html_table_generator(totalMatrix)
    return([leaderTable, laggerTable, totalTable])


def sharpe_ratio_histograms(data):
    stratList = ["OLS","ODR","Kalman"]
    title = "Sharpe Dist."
    xAxis = "Sharpe"
    yAxis = ""
    leaders = total_strategy_sharpe(data, True, False)
    laggers = total_strategy_sharpe(data, False, True)
    total = total_strategy_sharpe(data, False, False)
    overallStats = compile_ratio_stats(leaders, laggers, total)
    leaderStats = overallStats[0]
    laggerStats = overallStats[1]
    totalStats = overallStats[2]
    leaderChart = make_histogram(leaders,stratList,title+" (Leaders)",xAxis,yAxis)
    laggerChart = make_histogram(laggers,stratList,title+" (Laggers)",xAxis,yAxis)
    totalChart = make_histogram(total,stratList,title+" (Total)",xAxis,yAxis)
    htmlTables = get_histogram_table_matrix(leaderStats, laggerStats, totalStats)
    return(leaderChart, laggerChart, totalChart, htmlTables)

def total_return_histograms(data):
    stratList = ["OLS","ODR","Kalman"]
    title = "Total Return"
    xAxis = "Return"
    yAxis = ""
    leaders = total_strategy_return(data, True, False)
    laggers = total_strategy_return(data, False, True)
    total = total_strategy_return(data, False, False)
    overallStats = compile_ratio_stats(leaders, laggers, total)
    leaderStats = overallStats[0]
    laggerStats = overallStats[1]
    totalStats = overallStats[2]
    leaderChart = make_histogram(leaders,stratList,title+" (Leaders)",xAxis,yAxis)
    laggerChart = make_histogram(laggers,stratList,title+" (Laggers)",xAxis,yAxis)
    totalChart = make_histogram(total,stratList,title+" (Total)",xAxis,yAxis)
    htmlTables = get_histogram_table_matrix(leaderStats, laggerStats, totalStats)
    return(leaderChart, laggerChart, totalChart, htmlTables)

def sortino_ratio_histograms(data):
    stratList = ["OLS","ODR","Kalman"]
    title = "Sortino Dist."
    xAxis = "Sortino"
    yAxis = ""
    leaders = total_strategy_sortino(data, True, False)
    laggers = total_strategy_sortino(data, False, True)
    total = total_strategy_sortino(data, False, False)
    overallStats = compile_ratio_stats(leaders, laggers, total)
    leaderStats = overallStats[0]
    laggerStats = overallStats[1]
    totalStats = overallStats[2]
    leaderChart = make_histogram(leaders,stratList,title+" (Leaders)",xAxis,yAxis)
    laggerChart = make_histogram(laggers,stratList,title+" (Laggers)",xAxis,yAxis)
    totalChart = make_histogram(total,stratList,title+" (Total)",xAxis,yAxis)
    htmlTables = get_histogram_table_matrix(leaderStats, laggerStats, totalStats)
    return(leaderChart, laggerChart, totalChart, htmlTables)

def drawdown_histograms(data):
    stratList = ["OLS","ODR","Kalman"]
    title = "Drawdown Dist."
    xAxis = "Drawdown"
    yAxis = ""
    leaders = total_strategy_maxdrawdown(data, True, False)
    laggers = total_strategy_maxdrawdown(data, False, True)
    total = total_strategy_maxdrawdown(data, False, False)
    overallStats = compile_ratio_stats(leaders, laggers, total)
    leaderStats = overallStats[0]
    laggerStats = overallStats[1]
    totalStats = overallStats[2]
    leaderChart = make_histogram(leaders,stratList,title+" (Leaders)",xAxis,yAxis)
    laggerChart = make_histogram(laggers,stratList,title+" (Laggers)",xAxis,yAxis)
    totalChart = make_histogram(total,stratList,title+" (Total)",xAxis,yAxis)
    htmlTables = get_histogram_table_matrix(leaderStats, laggerStats, totalStats)
    return(leaderChart, laggerChart, totalChart, htmlTables)

def stddev_histograms(data):
    stratList = ["OLS","ODR","Kalman"]
    title = "Std. Dev. Dist."
    xAxis = "Std. Dev."
    yAxis = ""
    leaders = total_strategy_stddev(data, True, False)
    laggers = total_strategy_stddev(data, False, True)
    total = total_strategy_stddev(data, False, False)
    overallStats = compile_ratio_stats(leaders, laggers, total)
    leaderStats = overallStats[0]
    laggerStats = overallStats[1]
    totalStats = overallStats[2]
    leaderChart = make_histogram(leaders,stratList,title+" (Leaders)",xAxis,yAxis)
    laggerChart = make_histogram(laggers,stratList,title+" (Laggers)",xAxis,yAxis)
    totalChart = make_histogram(total,stratList,title+" (Total)",xAxis,yAxis)
    htmlTables = get_histogram_table_matrix(leaderStats, laggerStats, totalStats)
    return(leaderChart, laggerChart, totalChart, htmlTables)

def activity_histograms(data):
    stratList = ["OLS","ODR","Kalman"]
    title = "Activity Dist."
    xAxis = "Activity (Traded Days)"
    yAxis = ""
    leaders = total_strategy_activity(data, True, False)
    laggers = total_strategy_activity(data, False, True)
    total = total_strategy_activity(data, False, False)
    overallStats = compile_ratio_stats(leaders, laggers, total)
    leaderStats = overallStats[0]
    laggerStats = overallStats[1]
    totalStats = overallStats[2]
    leaderChart = make_histogram(leaders,stratList,title+" (Leaders)",xAxis,yAxis)
    laggerChart = make_histogram(laggers,stratList,title+" (Laggers)",xAxis,yAxis)
    totalChart = make_histogram(total,stratList,title+" (Total)",xAxis,yAxis)
    htmlTables = get_histogram_table_matrix(leaderStats, laggerStats, totalStats)
    return(leaderChart, laggerChart, totalChart, htmlTables)

def activity_annualized_histograms(data):
    stratList = ["OLS","ODR","Kalman"]
    title = "Annualized Return Dist."
    xAxis = "Returns"
    yAxis = ""
    leaders = total_strategy_activity_annualized(data, True, False)
    laggers = total_strategy_activity_annualized(data, False, True)
    total = total_strategy_activity_annualized(data, False, False)
    overallStats = compile_ratio_stats(leaders, laggers, total)
    leaderStats = overallStats[0]
    laggerStats = overallStats[1]
    totalStats = overallStats[2]
    leaderChart = make_histogram(leaders,stratList,title+" (Leaders)",xAxis,yAxis)
    laggerChart = make_histogram(laggers,stratList,title+" (Laggers)",xAxis,yAxis)
    totalChart = make_histogram(total,stratList,title+" (Total)",xAxis,yAxis)
    htmlTables = get_histogram_table_matrix(leaderStats, laggerStats, totalStats)
    return(leaderChart, laggerChart, totalChart, htmlTables)

def simulation_stats(data):
    stats = data["stats"]
    highExitSigma = stats["highExitSigma"]
    highEnterSigma = stats["highEnterSigma"]
    lowExitSigma = stats["lowExitSigma"]
    lowEnterSigma = stats["lowEnterSigma"]
    stopLossPercentage = stats["stopLossPercentage"]
    lookBackDays = stats["lookBackDays"]
    rSqThreshold = stats["rSqThreshold"]
    statList = [highEnterSigma,highExitSigma,lowEnterSigma,lowExitSigma,stopLossPercentage,lookBackDays,rSqThreshold]
    return(statList)

def get_sim_table(simStats):
    header = ["High Enter Sigma","High Exit Sigma","Low Enter Sigma", "Low Exit Sigma", "Stop Loss %", "Look Back (Days)", "R-Squared Threshold"]
    table = html_table_generator([header,simStats])
    return(table)

def execute(filepath):
    signIn.auth()
    jData = read_file(filepath)
    data = add_leader_flag(jData)
    simStats = simulation_stats(data)
    simTable = get_sim_table(simStats)
    sharpeData = list(sharpe_ratio_histograms(data)[0:4])
    sortinoData = list(sortino_ratio_histograms(data)[0:4])
    totalReturnData = list(total_return_histograms(data)[0:4])
    maxDrawdownData = list(drawdown_histograms(data)[0:4])
    stdDevData = list(stddev_histograms(data)[0:4])
    activityData = list(activity_histograms(data)[0:4])
    annualizedActivityData = list(activity_annualized_histograms(data)[0:4])
    return([sharpeData, sortinoData, totalReturnData, maxDrawdownData, stdDevData, activityData, annualizedActivityData, simTable])

if __name__ == "__main__":
    execute(sys.argv[1])
