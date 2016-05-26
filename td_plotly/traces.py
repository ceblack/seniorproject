#!/usr/bin/env python3
import sys
import os
sys.path.insert(1,os.path.join(sys.path[0], '..'))
import plotly.plotly as py
import plotly.graph_objs as go
import plotly.tools as tls
from td_plotly import chartConfigs

def make_dot_trace(x, y, name, color, width):
    trace = go.Scatter(x = x, y = y, name = name, line = dict(color = (color), width = width, dash="dot"))
    return(trace)

def make_dash_trace(x, y, name, color, width):
    trace = go.Scatter(x = x, y = y, name = name, line = dict(color = (color), width = width, dash="dash"))
    return(trace)

def make_line_trace(x, y, name, color, width):
    trace = go.Scatter(x = x, y = y, name = name, line = dict(color = (color), width = width))
    return(trace)

def make_title_text_trace(textString, x, y):
    trace = go.Scatter(x=[x], y=[y], text=[textString], mode='text', textposition='top middle',
    showlegend=False,
    hoverinfo='none',
    textfont=dict(
        size=chartConfigs._titleSize,
        color=chartConfigs._legendColor
    ))
    return(trace)

def make_text_trace(textString, x, y, size):
    trace = go.Scatter(x=[x], y=[y], text=[textString], mode='text', textposition='top middle',
    showlegend=False,
    hoverinfo='none',
    textfont=dict(
        size=size,
        color=chartConfigs._legendColor
    ))
    return(trace)

def make_watermark_trace(textString, x, y, size, color):
    trace = go.Scatter(x=[x], y=[y], text=[textString], mode='text', textposition='top middle',
    showlegend=False,
    hoverinfo='none',
    textfont=dict(
        size=size,
        color=color
    ))
    return(trace)
