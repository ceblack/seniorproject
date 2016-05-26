#!/usr/bin/env python3
import sys
import os
sys.path.insert(1,os.path.join(sys.path[0], '..'))

def auth():
    import plotly.plotly as py
    from td_plotly.plotlyConfig import _user, _key
    py.sign_in(_user,_key)
