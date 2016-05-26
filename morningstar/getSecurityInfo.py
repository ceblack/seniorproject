#!/usr/bin/env python3
import sys
import os
sys.path.insert(1,os.path.join(sys.path[0], '..'))
import urllib
import http.client

def get_stock_info(symbol,exchange,token):
    host = "equityapi.morningstar.com"
    url = "/WebService/GlobalMasterListsService.asmx/GetCompanyFinancialAvailabilityList"
    port = 80
    fileName=None
    conn = http.client.HTTPConnection(host, port)
    headers = {"Content-type":"application/x-www-form-urlencoded"}
    params = urllib.parse.urlencode({"category":"GetStockExchangeSecurityList","identifier":symbol,"exchangeId":exchange,"identifierType":"Symbol","responseType":"Json", "token":token}, doseq=0)
    conn.request("POST", url, params, headers)
    response = conn.getresponse()
    data = response.read().decode()
    return(data)
