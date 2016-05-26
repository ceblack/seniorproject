#!/usr/bin/env python3
import sys
import os
sys.path.insert(1,os.path.join(sys.path[0], '..'))
import portfolioConfig
from datetime import date
from datetime import timedelta
from datetime import datetime

def cost_basis(newQuantity, newFill, oldQuantity, oldFill):
    costBasis = ((newQuantity*newFill) + (oldQuantity*oldFill)) / (oldQuantity + newQuantity)
    return(costBasis)

class PortfolioTracker(object):
    def __init__(self):
        self.valueList = []

    def add_date(self,portfolio,date):
        totalValue = portfolio.get_total_portfolio_value()
        cashValue = portfolio.get_cash_value()
        assetValue = portfolio.get_net_exposure()
        dateDict = {"date":date, "totalValue":totalValue, "cashValue":cashValue, "assetValue":assetValue}
        self.valueList.append(dateDict)

    def get_last_date(self):
        return(self.valueList[-1]["date"])

    def get_last(self):
        return(self.valueList[-1]["totalValue"])

    def get_value_list(self):
        return(self.valueList)

    def get_total_return(self):
        if(len(self.valueList)>2):
            totalReturn = ((self.valueList[-1]["totalValue"] / self.valueList[0]["totalValue"]) - 1)*100.
            return(totalReturn)
        else:
            return(0)

class Portfolio(object):
    def __init__(self):
        self.netExposure = 0
        self.totalExposure = 0
        self.netDecimalExposure = 0
        self.totalDecimalExposure = 0
        self.cash = portfolioConfig._startingCapital
        self.positions = []
        self.companies = []

    def get_cash_value(self):
        return(self.cash)

    def update_companies(self):
        tempList = []
        for p in self.positions:
            tempList.append(p.get_company())
        self.companies = list(set(tempList))

    def get_net_decimal_exposure(self):
        return(self.netDecimalExposure)

    def get_net_exposure(self):
        valList = []
        if(len(self.positions)!=0):
            for p in self.positions:
                valList.append(p.get_quantity() * p.get_company().get_price())
            value = sum(valList)
            self.netExposure = value
            self.netDecimalExposure = self.netExposure / (self.netExposure + self.cash)
        else:
            self.netExposure = 0
            self.netDecimalExposure = 0
        return(self.netExposure)

    def get_total_exposure(self):
        valList = []
        if(len(self.positions)!=0):
            for p in self.positions:
                valList.append(p.get_quantity() * p.get_company().get_price())
            absList = [abs(x) for x in valList]
            self.totalExposure = sum(absList)
            self.totalDecimalExposure = self.totalExposure / self.get_total_portfolio_value()
        else:
            self.totalExposure = 0
            self.totalDecimalExposure = 0
        return(self.totalExposure)

    def get_available_cash(self):
        availableCash = (self.cash + self.get_net_exposure()) - self.get_total_exposure()
        return(availableCash)

    def get_total_portfolio_value(self):
        assetVal = self.get_net_exposure()
        return(self.cash + assetVal)

    def get_open_pnl(self):
        valList = []
        if(len(self.positions)!=0):
            for h in self.positions:
                valList.append(h.get_pnl())
            value = sum(valList)
            return(value)
        else:
            return(0)

    def get_positions_by_company(self,company):
        coQuantity = 0
        for p in self.positions:
            if(p.get_company() == company):
                coQuantity += p.get_quantity()
        return(coQuantity)

    def get_positions(self):
        return(self.positions)

    def check_stops(self, queue):
        stopList = queue.get_stops()
        if(len(stopList)!=0):
            for s in stopList:
                if(s.expiration>=1 or s.expiration<=-999):
                    if(s.trigger(self.get_total_portfolio_value())):
                        orderList = []
                        for p in self.positions:
                            co = p.get_company()
                            quantity = p.get_quantity()
                            orderList.append(MarketOrder(co,-1*quantity,10))
                        self.modify_positions(orderList)
                        queue.stops = []

    def is_closing_trade(self, orderList):
        closing = False
        exposureDeltaList = []
        for newOrder in orderList:
            exposureDeltaList.append(newOrder.get_company().get_price() * newOrder.get_quantity())
        exposureDelta = sum(exposureDeltaList)
        netExposure = self.get_net_exposure()
        if(abs(netExposure + exposureDelta) <= abs(netExposure)):
            closing = True
        return(closing)

    def modify_positions(self, orderList):
        self.get_net_exposure()
        self.get_total_exposure()
        if(orderList!=0):
            closingTrade = self.is_closing_trade(orderList)
            for newOrder in orderList:
                if(newOrder.get_expiration()>=1 or newOrder.get_expiration()<=-999):
                    newCo = newOrder.get_company()
                    newFill = newCo.get_price()
                    newQuantity = newOrder.get_quantity()
                    newCost = newFill * newQuantity

                    if(abs(newCost) > abs(self.get_available_cash()) and not closingTrade):
                        pass

                    else:
                        if(newCo in self.companies):
                            for p in self.positions:
                                if(p.get_company() == newCo):
                                    existingPos = p
                            oldQuantity = existingPos.get_quantity()
                            finalQuantity = newQuantity + oldQuantity
                            noSignChange = ((finalQuantity*oldQuantity)>0)
                            costBasis = newFill
                            if(noSignChange):
                                oldQuantity = existingPos.get_quantity()
                                oldFill = existingPos.get_fill_price()
                                costBasis = cost_basis(newQuantity, newFill, oldQuantity, oldFill)

                            self.cash -= newCost
                            self.positions.remove(existingPos)
                            if(finalQuantity!=0):
                                newStock = Stock(newCo, costBasis, finalQuantity)
                                self.positions.append(newStock)

                        else:
                            newStock = Stock(newCo, newFill, newQuantity)
                            self.cash -= newCost
                            self.positions.append(newStock)

                    self.update_companies()
                    self.get_net_exposure()
                    self.get_total_exposure()

class Stock(object):
    def __init__(self, company, fillPrice, quantity):
        self.company = company
        self.fillPrice = fillPrice
        self.quantity = quantity

    def get_company(self):
        return(self.company)

    def get_symbol(self):
        return(self.company.get_symbol())

    def get_quantity(self):
        return(self.quantity)

    def get_fill_price(self):
        return(self.fillPrice)

    def update_quantity(self, quantity):
        self.quantity = quantity

    def update_fill_price(self, fillPrice):
        self.fillPrice = fillPrice

    def get_pnl(self):
        currentPrice = self.company.get_price()
        unitProfit = currentPrice - self.fillPrice
        return(unitProfit * self.quantity)

class MarketOrder(object):
    def __init__(self, company, quantity, expiration):
        self.company = company
        self.quantity = quantity
        self.expiration = expiration

    def get_company(self):
        return(self.company)

    def get_symbol(self):
        return(self.company.get_symbol())

    def get_quantity(self):
        return(self.quantity)

    def get_expiration(self):
        return(self.expiration)

    def update_expiration(self,days):
        self.expiration -= days
        return(self.expiration)

class StopOrder(object):
    def __init__(self, stopValue, expiration):
        self.stopValue= stopValue
        self.expiration = expiration

    def trigger(self,value):
        return((self.stopValue>=value))

    def get_expiration(self):
        return(self.expiration)

class Queue(object):
    def __init__(self):
        self.orders = []
        self.stops = []

    def get_orders(self):
        return(self.orders)

    def get_stops(self):
        return(self.stops)

    def decrement_expirations(self, days):
        if(len(self.orders)!=0):
            for o in self.orders:
                o.update_expiration(days)

    def remove_order(self,o):
        for obj in self.orders:
            if(obj == o):
                self.orders.remove(obj)

    def remove_stop(self,s):
        for obj in self.stops:
            if(obj == s):
                self.stops.remove(s)

    def add_order(self,o):
        self.orders.append(o)

    def add_stop(self,s):
        self.stops.append(s)

    def clear_orders(self):
        self.orders = []

class Company(object):
    def __init__(self, symbol, priceDict, dateList, currentDate):
        self.symbol = symbol
        self.prices = priceDict
        self.currentDate = currentDate
        self.dateList = dateList
        self.currentPrice = priceDict[currentDate]

    def get_symbol(self):
        return(self.symbol)

    def get_price(self):
        return(self.currentPrice)

    def update_date(self, newDate):
        self.currentDate = newDate
        try:
            self.currentPrice = float(self.prices[newDate])
        except KeyError:
            pass

    def get_current_date(self):
        return(self.currentDate)

    def get_trailing_days(self, days):
        currentDayIndex = self.dateList.index(self.currentDate)
        trailingList = []
        if(currentDayIndex-days<=0):
            dates = self.dateList[0:currentDayIndex]
        else:
            dates = self.dateList[currentDayIndex-days:currentDayIndex]
        for d in dates:
            trailingList.append(float(self.prices[d]))
        return(trailingList)

class ModelObjects(object):
    def __init__(self):
        self.modelList = []
        self.recordList = []

    def get_model(self, modelIndex):
        return(self.modelList[modelIndex])

    def get_model_list(self):
        return(self.modelList)

    def add_model(self, model):
        self.modelList.append(model)

    def remove_model(self, model):
        self.modelList.remove(model)

    def get_record(self, recordIndex):
        return(self.modelList[recordIndex])

    def get_record_list(self):
        return(self.recordList)

    def add_record(self, record):
        self.recordList.append(record)

    def remove_record(self, record):
        self.recordList.remove(record)
