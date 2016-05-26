#!/usr/bin/env python3
import sys
import os
sys.path.insert(1,os.path.join(sys.path[0], '..'))
import getYahoo

def get_prices(symbol,begin,end):
    try:
        prices = getYahoo.get_historical_prices(symbol,begin,end)
        return(prices)
    except Exception as e:
        raise Exception("Historical Price Request Failure")
