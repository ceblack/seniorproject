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
import resultAnalysis

def get_page_header():
    top = "<!DOCTYPE html><html lang=\"en\"><head><title>Senior Research Project</title>"
    styleSheets = "<link rel=\"stylesheet\" href=\"css/styles.css\"><link rel=\"stylesheet\" href=\"https://maxcdn.bootstrapcdn.com/bootstrap/3.3.6/css/bootstrap.min.css\"><link rel=\"stylesheet\" href=\"https://maxcdn.bootstrapcdn.com/bootstrap/3.3.6/css/bootstrap-theme.min.css\">"
    js = "<script src=\"https://ajax.googleapis.com/ajax/libs/jquery/1.11.3/jquery.min.js\"></script><script src=\"https://maxcdn.bootstrapcdn.com/bootstrap/3.3.6/js/bootstrap.min.js\"></script>"
    bottom = "</head><body>"
    return(top+styleSheets+js+bottom)

def get_page_footer():
    bottom = "</body></html>"
    return(bottom)

def generate_row_obj(chart, table):
    prefix = "\n<div class=\"col-md-4\">\n"
    suffix = "</div>\n"
    tablePrefixA = "\n<div id=\"overallDiv\">\n"
    tablePrefixB = "<div id=\"mainBody\">\n"
    tableSuffixAB = "\n</div>\n</div>\n"
    rowObjString = prefix+chart+tablePrefixA+tablePrefixB+table+tableSuffixAB+suffix
    return(rowObjString)

def generate_chart_row(data):
    leader = data[0]
    lagger = data[1]
    total = data[2]
    leaderTable = data[3][0]
    laggerTable = data[3][1]
    totalTable = data[3][2]
    prefix = "<div class=\"row\">\n"
    suffix = "\n</div>\n"
    leaderObj = generate_row_obj(leader,leaderTable)
    laggerObj = generate_row_obj(lagger,laggerTable)
    totalObj = generate_row_obj(total,totalTable)
    chartRow = prefix + leaderObj + laggerObj + totalObj + suffix + generate_empty_paragraph()
    return(chartRow)

def generate_empty_paragraph():
    return("<div class=\"row\"><br/><br/><p>TEXT GOES HERE</p><br/><br/></div>")

def generate_sim_header(simTable):
    prefix = "<br/><br/><br/><div class=\"row\"><div id=\"overallDiv\"><div id=\"mainBody\">"
    suffix = "<br/><br/></div></div></div>"
    return(prefix+simTable+suffix)


def iter_analysis(analysisList):
    prefix = "<div class=\"container\">"
    suffix = "</div>"
    simList = []
    for analysis in analysisList:
        #[sharpeData, sortinoData, totalReturnData, maxDrawdownData, stdDevData, activityData, annualizedActivityData, simTable]
        sharpeData = analysis[0]
        sortinoData = analysis[1]
        totalReturnData = analysis[2]
        maxDrawdownData = analysis[3]
        stdDevData = analysis[4]
        activityData = analysis[5]
        annualizedActivityData = analysis[6]
        simTable = analysis[7]

        header = generate_sim_header(simTable)
        totalReturnRow = generate_chart_row(totalReturnData)
        maxDrawdownRow = generate_chart_row(maxDrawdownData)
        stdDevRow = generate_chart_row(stdDevData)
        activityRow = generate_chart_row(activityData)
        sharpeRow = generate_chart_row(sharpeData)
        sortinoRow = generate_chart_row(sortinoData)
        annualizedActivityRow = generate_chart_row(annualizedActivityData)
        simItem = header + totalReturnRow + maxDrawdownRow + stdDevRow + activityRow + sharpeRow + sortinoRow + annualizedActivityRow + "<hr>"
        simList.append(simItem)
    pageString = "\n".join(simList)
    pageString = prefix + pageString + suffix
    header = get_page_header()
    footer = get_page_footer()
    pageString = header + pageString + footer
    return(pageString)

def execute(filepathList):
    analysisList = []
    for f in filepathList:
        a = resultAnalysis.execute(f)
        analysisList.append(a)
    page = iter_analysis(analysisList)
    html_file= open("site/analysis.html","w")
    html_file.write(page)
    html_file.close()

if __name__ == "__main__":
    execute(sys.argv[1:])
