#!/usr/bin/env python3
import sys
import os
sys.path.insert(1,os.path.join(sys.path[0], '..'))
import json
import requests
from morningstar import getToken as gt
from morningstar import getExchangeList
import urllib
import http.client
from morningstar.json_toolkit import formatOutput

def auth():
    from morningstar.morningstarConfig import _username, _password
    success,token = gt.getLoginToken(_username,_password)
    return(success,token)

def get_stock_data(exchange,token):
#http://equityapi.morningstar.com/WebService/GlobalMasterListsService.asmx/GetStockExchangeSecurityList?category=GetStockExchangeSecurityList&exchangeId=NYS&identifier=NYS&identifierType=ExchangeId&stockStatus=Active&responseType=Json&Token=R53EVCgAuVrASXaFc2IsaXF_hQZVzq2Xy1AHRiWyOelN3XfDVtmcYydw89P1AwiN71UhXqbTT_laVZnw-iMIREAW9rWMnB5c55jjImlBn2o1
    host = "equityapi.morningstar.com"
    url = "/WebService/GlobalMasterListsService.asmx/GetStockExchangeSecurityList"
    port = 80
    fileName=None
    conn = http.client.HTTPConnection(host, port)
    headers = {"Content-type":"application/x-www-form-urlencoded"}
    params = urllib.parse.urlencode({"category":"GetStockExchangeSecurityList","identifier":exchange,"exchangeId":exchange,"identifierType":"ExchangeId","stockStatus":"Active","responseType":"Json", "token":token}, doseq=0)
    conn.request("POST", url, params, headers)
    response = conn.getresponse()
    data = response.read().decode()
    return(data)

def strip_exchange(data):
    exchangeList = []
    for e in data["ExchangeEntityList"]:
        ex = e["ExchangeId"]
        ex = ex.replace(" ","").replace("\r","").replace("\n","")
        exchangeList.append(ex)
    return(exchangeList)

def stock_strip(data):
    data = json.loads(data)
    stocks = data["StockExchangeSecurityEntityList"]
    symbols = []
    if(stocks!=None):
        for s in stocks:
            if(s["InvestmentTypeId"].lower()=="eq"):
                symbols.append({"symbol":s["Symbol"],"exchange":s["ExchangeId"]})
    return(symbols)

def iter_exchanges(exchanges, token):
    badExchangeList = ["PINX"]
    exchangeData = []
    for ex in exchanges:
        if(ex not in badExchangeList):
            data = get_stock_data(ex, token)
            exchangeData.append(data)

    stockMaster = []
    for ex in exchangeData:
        stocks = stock_strip(ex)
        stockMaster.append(stocks)

    flatList = []
    for stock in stockMaster:
        for s in stock:
            flatList.append(s)

    return(flatList)

def execute():
    success,token = auth()
    exchangeData = json.loads(getExchangeList.getUSAData(token))
    #exchangeData = json.loads(getExchangeList.getAllData(token))
    exchanges = strip_exchange(exchangeData)
    stockList = iter_exchanges(exchanges, token)
    return(stockList)
    '''try:
        success,token = auth()
        exchangeData = json.loads(getExchangeList.execute())
        exchanges = exchangeData["payload"]
        jdata = formatOutput.format_json("success","",alldata)
    except Exception as e:
        jdata = formatOutput.format_json("failure",str(e),"")
    return(jdata)'''

if __name__ == "__main__":
    '''try:
        jdata = execute()
    except Exception as e:
        jdata = formatOutput.format_json("failure",str(e),"")
    sys.stdout.write(jdata)
    sys.stdout.flush()'''
    execute()
