#!/usr/bin/env python3
import sys
import os
sys.path.insert(1,os.path.join(sys.path[0], '..'))
import json
from morningstar import getSecurities
from morningstar import getExchangeList
from morningstar import getSecurityInfo
import stockLists

def get_exchange_data(exchanges,token):
    stockList = getSecurities.iter_exchanges(exchanges,token)
    return(stockList)

def get_security_info(stock,exchange,token):
    securityInfo = getSecurityInfo.get_stock_info(symbol,exchange,token)
    return(securityInfo)

def add_stock_info(stockList, token):
    infoList = []
    n = 0
    for stock in stockList:
        n += 1
        symbol = stock["symbol"]
        exchange = stock["exchange"]
        if(symbol.upper() in stockLists._SP500):
            info = json.loads(getSecurityInfo.get_stock_info(symbol,exchange,token))
            if(int(info["MessageInfo"]["MessageCode"])==200):
                sectorId = int(info["CompanyFinancialAvailabilityEntityList"][0]["SectorId"])
                sectorName = info["CompanyFinancialAvailabilityEntityList"][0]["SectorName"]
                infoList.append({"symbol":symbol,"sectorId":sectorId,"sectorName":sectorName})
    return(infoList)

def execute(exchanges):
    success,token = getExchangeList.auth()
    stockList = get_exchange_data(exchanges,token)
    infoList = add_stock_info(stockList,token)
    return(infoList)

if __name__ == "__main__":
    execute(["NYS"])
