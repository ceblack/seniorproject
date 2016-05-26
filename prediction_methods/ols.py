#!/usr/bin/env python3
import sys
import os
sys.path.insert(1,os.path.join(sys.path[0], '..'))

def OLS(x,y):
    xhat = sum(x)/len(x)
    yhat = sum(y)/len(y)
    n = len(y)
    multipairs = []
    for i in range(0,n):
        multipairs.append(x[i]*y[i])
    topmA = n*sum(multipairs)
    topmB = sum(x)*sum(y)
    topm = topmA - topmB
    xsquared = [i*i for i in x]
    bottomm = (n*sum(xsquared)) - (sum(x)*sum(x))
    m = topm/bottomm
    b = (sum(y) - (m*sum(x)))/n
    coef = m
    intercept = b
    return(coef,intercept)

def get_equation_sigma(coef, intercept, x, y):
    line = make_line(coef,intercept,x)
    square_errors = []
    for i in range(0,len(y)):
        err = y[i] - line[i]
        square_errors.append(err**2)
    square_errorsum = sum(square_errors)
    if(len(y)==2 or len(y)==1):
        var = (1/(len(y)))*square_errorsum
        sigma = math.sqrt(var)
    elif(len(y)>=3):
        var = (1/(len(y)-2))*square_errorsum
        sigma = math.sqrt(var)
    elif(len(y)==0):
        var = 0.
        sigma = 0.
    return(sigma)

def get_standard_sigma(line):
    lineAvg = sum(line) / len(line)
    sqErr = []
    for l in line:
        sqErr.append((l - lineAvg)*(l - lineAvg))
    sumSqErr = sum(sqErr)
    var = (1/len(line))*sumSqErr
    sigma = var**(1/2)
    return(sigma)

def make_line(coef,intercept,x):
    line = [coef*i+intercept for i in x]
    return(line)

def r_squared(coef, intercept, x ,y):
    #SSE = Sum of Squared Errors
    #SSTO = Sum of (ActualY - AverageY)**2
    line = make_line(coef,intercept,x)
    yhat = sum(y) / len(y)
    SE = []
    STO = []
    for i in range(0,len(y)):
        err = y[i] - line[i]
        SE.append(err**2)

        avgDiff = y[i] - yhat
        STO.append(avgDiff**2)

    SSE = sum(SE)
    SSTO = sum(STO)
    try:
        RSqP = 1-(SSE/SSTO)
    except:
        RSqP = 0
    return(RSqP)

def make_pairs(numlist):
    x = list(range(1,len(numlist)+1))
    y = [float(x) for x in numlist]
    return(x,y)

def regress_against_time(Y):
    X, Y = make_pairs(Y)
    data = OLS(X, Y)
    return(data)
