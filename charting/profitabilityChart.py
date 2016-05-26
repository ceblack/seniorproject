#!/usr/bin/env python3
import sys
import os
sys.path.insert(1,os.path.join(sys.path[0], '..'))
import json
from charting import getChartColors
from charting import getChartName
from xignite import profitability
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

def profit_chart(profitData):
    profits = profitData[0]
    intervalList = profitData[1]
    skews = profitData[2]
    callSkew = skews[0]
    callStrikes = skews[1]
    putSkew = skews[2]
    putStrikes = skews[3]
    zeroCrossings = profitData[3]
    stockPrice = profitData[4]
    maxY = max(profits)
    minY = min(profits)
    minX = min(zeroCrossings)
    maxX = max(zeroCrossings)
    strikeCombo = list(set(putStrikes + callStrikes))
    if(min(strikeCombo)<minX):
        minX = min(strikeCombo)
    if(max(strikeCombo)>maxX):
        maxX = max(strikeCombo)

    maxX = maxX + abs(maxX*0.06)
    minX = minX - abs(maxX*0.06)

    colors = getChartColors.line_number(3,0.8)

    profitTrace = go.Scatter(
                        y=profits,
                        x=intervalList,
                        name='Profit/Loss',
                        line = dict(
                                color = colors[1],
                                width = 3,
                                )
                        )

    callSkewTrace = go.Scatter(
                        y=callSkew,
                        x=callStrikes,
                        name='Call IV',
                        yaxis='y2',
                        line=dict(
                                color=colors[2],
                                width=2
                                )
                        )
    putSkewTrace = go.Scatter(
                        y=putSkew,
                        x=putStrikes,
                        name='Put IV',
                        yaxis='y2',
                        line=dict(
                                color=colors[0],
                                width=2
                                )
                        )
    data = [profitTrace,callSkewTrace,putSkewTrace]
    layout = go.Layout(
        title='',
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(x=0.9,y=1,bgcolor="rgba(0,0,0,0)"),
        xaxis=dict(
            title="Strike",
            range=[minX,maxX],
            showgrid=True,
            showline=True,
            zeroline=False,
            linecolor='rgba(200,200,200,1)',
            gridcolor='rgba(200,200,200,1)'
        ),
        yaxis=dict(
            title='Profit/Loss',
            showgrid=True,
            showline=True,
            zeroline=True,
            linecolor='rgba(200,200,200,1)',
            gridcolor='rgba(200,200,200,1)'
        ),
        yaxis2=dict(
            title='IV',
            showgrid=False,
            showline=True,
            zeroline=False,
            titlefont=dict(
                color='rgba(0,0,0,0.7)'
            ),
            tickfont=dict(
                color='rgba(0,0,0,0.7)'
            ),
            overlaying='y',
            side='right'
        )
    )

    fig = go.Figure(data=data, layout=layout)
    embedInfo = make_chart(fig)
    return(embedInfo)

def execute(inputData):
    profitData = json.loads(profitability.execute(inputData))
    profitPayload = profitData["payload"]
    chartData = profit_chart(profitPayload)
    return(chartData)

if __name__ == "__main__":
	try:
		inputData = sys.argv[1]
		chartData = execute(inputData)
	except Exception as e:
		chartData = str(e)
	sys.stdout.write(chartData)
	sys.stdout.flush()
