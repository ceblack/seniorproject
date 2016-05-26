#!/usr/bin/env python3
import sys
import os
sys.path.insert(1,os.path.join(sys.path[0], '..'))
import plotly.plotly as py
import plotly.tools as tls
from td_plotly import signIn
from td_plotly import chartConfigs

def create(chartTitle, xTitle, yTitle, data, filename, shapes, minX, maxX, minY, maxY):
    signIn.auth()
    if(shapes==None):
        layout = dict(title = chartTitle,
                    plot_bgcolor=chartConfigs._chartBgColor,
                    paper_bgcolor=chartConfigs._chartBgColor,
                    xaxis = dict(title = xTitle, gridcolor=chartConfigs._gridColor),
                    yaxis = dict(title = yTitle, gridcolor=chartConfigs._gridColor),
                    legend=dict(x=0.9,y=1,bgcolor=chartConfigs._chartBgColor),
                    margin=dict(t=chartConfigs_topMargin,
                            b=chartConfigs_bottomMargin,
                            l=chartConfigs_leftMargin,
                            r=chartConfigs_rightMargin,
                            pad=chartConfigs_padding,
                            color=chartConfigs._marginColor)
                            )
    else:
        layout = dict(title = chartTitle,
                    plot_bgcolor=chartConfigs._chartBgColor,
                    paper_bgcolor=chartConfigs._chartBgColor,
                    font=dict(color=chartConfigs._titleColor),
                    xaxis = dict(title = xTitle,
                            ticks="inside",
                            tickfont=dict(color=chartConfigs._tickColor),
                            titlefont=dict(color=chartConfigs._tickColor),
                            tickcolor=chartConfigs._tickColor,
                            range=[minX,maxX],
                            gridcolor=chartConfigs._gridColor,
                            linecolor=chartConfigs._lineColor,
                            linewidth=chartConfigs._lineWidth,
                            zerolinecolor=chartConfigs._zeroLineColor,
                            zerolinewidth=chartConfigs._lineWidth),
                    yaxis = dict(title = yTitle,
                            ticks="inside",
                            tickfont=dict(color=chartConfigs._tickColor),
                            titlefont=dict(color=chartConfigs._tickColor),
                            tickcolor=chartConfigs._tickColor,
                            range=[minY,maxY],
                            gridcolor=chartConfigs._gridColor,
                            linecolor=chartConfigs._lineColor,
                            linewidth=chartConfigs._lineWidth,
                            zerolinecolor=chartConfigs._zeroLineColor,
                            zerolinewidth=chartConfigs._lineWidth),
                    shapes=shapes,
                    legend=dict(x=0.88,y=1,bgcolor=chartConfigs._chartBgColor,font=dict(color=chartConfigs._legendColor))
                    )
    fig = dict(data=data, layout=layout)
    plot_url = py.plot(fig, filename=filename, auto_open=False)
    embedInfo = tls.get_embed(plot_url)
    return(embedInfo)
