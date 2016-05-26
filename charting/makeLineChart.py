#!/usr/bin/env python3
import sys
import os
sys.path.insert(1,os.path.join(sys.path[0], '..'))
import json
from charting import getChartColors
from charting import getChartName
import plotly.plotly as py
import plotly.tools as tls
import plotly.graph_objs as go
from td_plotly import signIn

def make_chart(fig):
    signIn.auth()
    filename = getChartName.ts()
    plot_url = py.plot(fig, filename=filename, auto_open=False)
    embedInfo = tls.get_embed(plot_url)
    return(embedInfo)

def float_range(start,stop,step):
    rangeList = []
    while stop+0.01 >= start:
        rangeList.append(start)
        start += step
    return(rangeList)

def dollar_convert(x):
    x = "$"+str(round(float(x),2))
    if(x[-2]=="."):
        x = x+"0"
    if(x[-1]=="."):
        x = x+"00"
    return(x)

def make_pairs(numlist):
    x = list(range(1,len(numlist)+1))
    y = [float(x) for x in numlist]
    return(x,y)

def line_chart(lineList,nameList):
    xList = []
    yList = []
    for line in lineList:
        x,y = make_pairs(line)
        xList.append(x)
        yList.append(y)

    data = []
    for i in range(0,len(xList)):
        trace = go.Scatter(
                            y=yList[i],
                            x=xList[i],
                            name=nameList[i],
                            )
        data.append(trace)

    layout = go.Layout(
        title='',
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(x=0.9,y=1,bgcolor="rgba(0,0,0,0)"),
        xaxis=dict(
            title="T",
            showgrid=True,
            showline=True,
            zeroline=False,
            linecolor='rgba(200,200,200,1)',
            gridcolor='rgba(200,200,200,1)'
        ),
        yaxis=dict(
            title='$',
            showgrid=True,
            showline=True,
            zeroline=True,
            linecolor='rgba(200,200,200,1)',
            gridcolor='rgba(200,200,200,1)'
        )
    )

    fig = go.Figure(data=data, layout=layout)
    embedInfo = make_chart(fig)
    return(embedInfo)

def execute(line):
    embedInfo = line_chart(line)
    sys.stdout.write(embedInfo)
    sys.stdout.flush()

if __name__ == "__main__":
	pass
