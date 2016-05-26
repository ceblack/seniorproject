#!/usr/bin/env python3
import sys
import os
sys.path.insert(1,os.path.join(sys.path[0], '..'))

##DD-MM-YYYY
_startDate = "2011-04-30"
_endDate = "2016-04-30"
_highEnterSigma = 4.5
_lowEnterSigma = 3.5
_lowExitSigma = 2.0
_stopLossPercentage = 0.97
_lookBackDays = 100
_sectors = ["Financial Services"]
_exchanges = ["NYS"]
_rSquaredThreshold = 0.7
