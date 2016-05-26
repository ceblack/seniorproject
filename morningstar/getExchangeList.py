#!/usr/bin/env python3
import sys
import os
sys.path.insert(1,os.path.join(sys.path[0], '..'))
import requests
import json
from morningstar import getToken as gt
import urllib
import http.client
from morningstar.json_toolkit import formatOutput

def auth():
    from morningstar.morningstarConfig import _username, _password
    success,token = gt.getLoginToken(_username,_password)
    return(success,token)

def getAllData(token):
    host = "equityapi.morningstar.com"
    url = "/WebService/GlobalMasterListsService.asmx/GetExchangeList"
    port = 80
    fileName=None
    conn = http.client.HTTPConnection(host, port)
    headers = {"Content-type":"application/x-www-form-urlencoded"}
    params = urllib.parse.urlencode({"category":"GetExchangeList", "identifier":"ALL", "identifierType":"ALL","responseType":"Json", "token":token}, doseq=0)
    conn.request("POST", url, params, headers)
    response = conn.getresponse()
    data = response.read().decode()
    return(data)

def getUSAData(token):
    host = "equityapi.morningstar.com"
    url = "/WebService/GlobalMasterListsService.asmx/GetExchangeList"
    port = 80
    fileName=None
    conn = http.client.HTTPConnection(host, port)
    headers = {"Content-type":"application/x-www-form-urlencoded"}
    params = urllib.parse.urlencode({"category":"GetExchangeList", "identifier":"USA", "identifierType":"CountryId","responseType":"Json", "token":token}, doseq=0)
    conn.request("POST", url, params, headers)
    response = conn.getresponse()
    data = response.read().decode()
    return(data)

def consolidate(usa,intl):
    usa = json.loads(usa)
    intl = json.loads(intl)
    exchangeList = []
    for e in usa["ExchangeEntityList"]:
        ex = e["ExchangeId"]
        ex = ex.replace(" ","").replace("\r","").replace("\n","")
        exchangeList.append(ex)
    for e in intl["ExchangeEntityList"]:
        ex = e["ExchangeId"]
        ex = ex.replace(" ","").replace("\r","").replace("\n","")
        exchangeList.append(ex)
    return(exchangeList)

def execute():
    try:
        success,token = auth()
        usa = getUSAData(token)
        intl = getAllData(token)
        alldata = consolidate(usa,intl)
        jdata = formatOutput.format_json("success","",alldata)
    except Exception as e:
        jdata = formatOutput.format_json("failure",str(e),"")
    return(jdata)

if __name__ == "__main__":
    try:
        jdata = execute()
    except Exception as e:
        jdata = formatOutput.format_json("failure",str(e),"")
    sys.stdout.write(jdata)
    sys.stdout.flush()
