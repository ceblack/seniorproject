#!/usr/bin/env python3
import urllib
import http.client
import datetime
import time
from xml.dom import minidom

class TokenEntity():
    def __init__(self, isSuccess=False, token=None, expireDate=None):
        self.isSuccess = isSuccess
        self.token = token
        self.expireDate = expireDate

    #Creates the token given the response XML
    def createToken(self, xmlStr):
        document = minidom.parseString(xmlStr)

        isSuccess = document.getElementsByTagName("IsSuccess")
        token = document.getElementsByTagName("Token")
        expireDate = document.getElementsByTagName("expireDate")

        if((isSuccess.length == 1) and (token.length == 1) and (expireDate.length == 1)):
            for node in isSuccess[0].childNodes:
                if (node.nodeValue == "true"):
                    self.isSuccess = True
            for node in token[0].childNodes:
                self.token = node.nodeValue
            for node in expireDate[0].childNodes:
                strTime = node.nodeValue.split(".")
                self.expireDate = datetime.datetime(*time.strptime(strTime[0], "%Y-%m-%dT%H:%M:%S")[0:6])

def getLoginToken(email, password):
    #Host details
    host = "equityapi.morningstar.com"
    url = "/WSLogin/Login.asmx/Login"
    port = 80

    #Create HTTP connection
    conn = http.client.HTTPConnection(host, port)
    headers = {"Content-type":"application/x-www-form-urlencoded"}
    params = urllib.parse.urlencode({"email":email, "password":password}, doseq=0)
    conn.request("POST", url, params, headers)

    #Retrieve HTTP response
    response = conn.getresponse()
    data = response.read()

    #Generate Token
    token = TokenEntity()
    token.createToken(data)

    #Close HTTP connection
    conn.close()

    return(token.isSuccess,token.token)


if __name__ == "__main__":
    from morningstarConfig import _username, _password
    print(getLoginToken(_username,_password))
