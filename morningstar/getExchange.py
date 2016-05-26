#!/usr/bin/env python3
import sys
import json
from json_toolkit import formatOutput
import getIncomeStatementTTM
from datetime import datetime
import getExchangeList
import getToken

class exchangeRef():
    def exchangeList(self, e):
        self.exList = e

def testExchange(symbol,exchange,token,Byear,Bmonth,Ayear,Amonth):
    data = json.loads(getIncomeStatementTTM.getData(symbol,exchange,str(Amonth),str(Byear),str(Amonth),str(Ayear),token))
    if(int(data["MessageInfo"]["MessageCode"])==200 or int(data["MessageInfo"]["MessageCode"])==50002):
        return(data)
    else:
        raise Exception("Bad Exchange")

def guessExchange(symbol,exchange,index,exObj,token):
    possibleExchanges = exObj.exList
    try:
        now = datetime.now()
        Ayear = now.year
        Byear = Ayear
        Amonth = now.month
        monthdiff = Amonth-4
        Bmonth = abs(monthdiff)%12
        if(monthdiff==0):
            Bmonth = 12
        if(monthdiff<=0):
            Byear = Ayear-1
        data = testExchange(symbol,exchange,token,Byear,Bmonth,Ayear,Amonth)
        try:
            companyName = data["GeneralInfo"]["CompanyName"]
        except:
            companyName = "unavailable"
        return(exchange, companyName)
    except:
        if(index<=int(len(possibleExchanges)-1)):
            return(guessExchange(symbol,possibleExchanges[index],int(index+1),exObj,token))
        else:
            raise Exception("No Good Exchange")

def execute(symbol,token):
    try:
        exchangeData = json.loads(getExchangeList.execute())
        exchanges = exchangeData["payload"]
        exObj = exchangeRef()
        exObj.exchangeList(exchanges)
        e, c = guessExchange(symbol,"NYS",0,exObj,token)
        eDict = {"exchange":e, "company":c}
        jdata = formatOutput.format_json("success","",eDict)
    except Exception as e:
        jdata = formatOutput.format_json("failure",str(e),"")
    return(jdata)

def auth():
    from morningstarConfig import _username, _password
    success,token = getToken.getLoginToken(_username,_password)
    return(success,token)

if __name__ == "__main__":
    success,token = auth()
    symbol = sys.argv[1]
    try:
        jdata = execute(symbol,token)
    except Exception as e:
        jdata = formatOutput.format_json("failure",str(e),"")
    sys.stdout.write(jdata)
    sys.stdout.flush()
