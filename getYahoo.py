#!/usr/bin/env python3
import sys
import os
sys.path.insert(1,os.path.join(sys.path[0], '..'))
from urllib.request import Request, urlopen
from urllib.parse import urlencode

def _request(symbol, stat):
    url = 'http://finance.yahoo.com/d/quotes.csv?s=%s&f=%s' % (symbol, stat)
    req = Request(url)
    resp = urlopen(req)
    content = resp.read().decode().strip()
    return content

def get_all(symbol):
    """
    Get all available quote data for the given ticker symbol.
    Returns a dictionary.
    0 a2 avg daily volume
    1 c6 change (rt)
    2 c8 aftr hours change
    3 d dividend/share
    4 e eps
    5 e7 eps est this year
    6 e8 eps est next year
    7 e9 eps est next qtr
    8 f6 float shares
    9 g day low
    10 h day high
    11 j 52 week low
    12 k 52 week high
    13 g3 annualized gain
    14 j3 mkt cap
    15 j4 ebitda
    16 m2 day range
    17 p5 price sales
    18 p6 price book
    19 q ex-div date
    20 r1 div pay date
    21 r2 pe ratio
    22 r5 PEG
    23 r6 price/eps estimate current year
    24 r7 price/eps estimate next year
    25 s1 shares owned
    26 s7 short ratio
    27 t8 1 yr target price
    28 v volume
    29 w 52 week range
    30 w4 days value change
    31 x stock exchange
    32 y div yield
    """
    ids = \
        'a2c6c8dee7e8e9f6ghjkg3j3j4m2p5p6qr1r2r5r6r7s1s7t8vww4xy'
    values = _request(symbol, ids).split(',')
    return dict(
        AvgDailyVolume = values[0],
        Change = values[1],
        AfterHoursChange = values[2],
        Dividend = values[3],
        EPS = values[4],
        EstCurrentYrEPS = values[5],
        EstNextYrEPS = values[6],
        EstNextQtrEPS = values[7],
        FloatShares = values[8],
        DayLow = values[9],
        DayHigh = values[10],
        YrLow = values[11],
        YrHigh = values[12],
        AnnualizedGain = values[13],
        MarketCap = values[14],
        EBITDA = values[15],
        DayRange = values[16],
        PriceToSales = values[17],
        PriceToBook = values[18],
        ExDivDate = values[19],
        DivDate = values[20],
        PE = values[21],
        PEG = values[22],
        EstCurrentYrPE = values[23],
        EstNextYrPE = values[24],
        SharesOwned = values[25],
        ShortRatio = values[26],
        OneYearTarget = values[27],
        Volume = values[28],
        YrRange = str(round(float(values[12])-float(values[11]),2)),
        DayValChange = values[30],
        Exchange = values[31],
        DivYield = values[32]
    )

def get_dividend_yield(symbol):
    return _request(symbol, 'y')

def get_dividend_per_share(symbol):
    return _request(symbol, 'd')

def get_ask_realtime(symbol):
    return _request(symbol, 'b2')

def get_dividend_pay_date(symbol):
    return _request(symbol, 'r1')

def get_bid_realtime(symbol):
    return _request(symbol, 'b3')

def get_ex_dividend_date(symbol):
    return _request(symbol, 'q')

def get_previous_close(symbol):
    return _request(symbol, 'p')

def get_today_open(symbol):
    return _request(symbol, 'o')

def get_change(symbol):
    return _request(symbol, 'c1')

def get_last_trade_date(symbol):
    return _request(symbol, 'd1')

def get_change_percent_change(symbol):
    return _request(symbol, 'c')

def get_trade_date(symbol):
    return _request(symbol, 'd2')

def get_change_realtime(symbol):
    return _request(symbol, 'c6')

def get_last_trade_time(symbol):
    return _request(symbol, 't1')

def get_change_percent_realtime(symbol):
    return _request(symbol, 'k2')

def get_change_percent(symbol):
    return _request(symbol, 'p2')

def get_after_hours_change(symbol):
    return _request(symbol, 'c8')

def get_change_200_sma(symbol):
    return _request(symbol, 'm5')

def get_commission(symbol):
    return _request(symbol, 'c3')

def get_percent_change_200_sma(symbol):
    return _request(symbol, 'm6')

def get_todays_low(symbol):
    return _request(symbol, 'g')

def get_change_50_sma(symbol):
    return _request(symbol, 'm7')

def get_todays_high(symbol):
    return _request(symbol, 'h')

def get_percent_change_50_sma(symbol):
    return _request(symbol, 'm8')

def get_last_trade_realtime_time(symbol):
    return _request(symbol, 'k1')

def get_50_sma(symbol):
    return _request(symbol, 'm3')

def get_last_trade_time_plus(symbol):
    return _request(symbol, 'l')

def get_200_sma(symbol):
    return _request(symbol, 'm4')

def get_last_trade_price(symbol):
    return _request(symbol, 'l1')

def get_1_year_target(symbol):
    return _request(symbol, 't8')

def get_todays_value_change(symbol):
    return _request(symbol, 'w1')

def get_holdings_gain_percent(symbol):
    return _request(symbol, 'g1')

def get_todays_value_change_realtime(symbol):
    return _request(symbol, 'w4')

def get_annualized_gain(symbol):
    return _request(symbol, 'g3')

def get_price_paid(symbol):
    return _request(symbol, 'p1')

def get_holdings_gain(symbol):
    return _request(symbol, 'g4')

def get_todays_range(symbol):
    return _request(symbol, 'm')

def get_holdings_gain_percent_realtime(symbol):
    return _request(symbol, 'g5')

def get_todays_range_realtime(symbol):
    return _request(symbol, 'm2')

def get_holdings_gain_realtime(symbol):
    return _request(symbol, 'g6')

def get_52_week_high(symbol):
    return _request(symbol, 'k')

def get_more_info(symbol):
    return _request(symbol, 'v')

def get_52_week_low(symbol):
    return _request(symbol, 'j')

def get_market_cap(symbol):
    return _request(symbol, 'j1')

def get_change_from_52_week_low(symbol):
    return _request(symbol, 'j5')

def get_market_cap_realtime(symbol):
    return _request(symbol, 'j3')

def get_change_from_52_week_high(symbol):
    return _request(symbol, 'k4')

def get_float_shares(symbol):
    return _request(symbol, 'f6')

def get_percent_change_from_52_week_low(symbol):
    return _request(symbol, 'j6')

def get_company_name(symbol):
    return _request(symbol, 'n')

def get_percent_change_from_52_week_high(symbol):
    return _request(symbol, 'k5')

def get_notes(symbol):
    return _request(symbol, 'n4')

def get_52_week_range(symbol):
    return _request(symbol, 'w')

def get_shares_owned(symbol):
    return _request(symbol, 's1')

def get_stock_exchange(symbol):
    return _request(symbol, 'x')

def get_shares_outstanding(symbol):
    return _request(symbol, 'j2')

def get_volume(symbol):
    return _request(symbol, 'v')

def get_ask_size(symbol):
    return _request(symbol, 'a5')

def get_bid_size(symbol):
    return _request(symbol, 'b6')

def get_last_trade_size(symbol):
    return _request(symbol, 'k3')

def get_ticker_trend(symbol):
    return _request(symbol, 't7')

def get_average_daily_volume(symbol):
    return _request(symbol, 'a2')

def get_trade_links(symbol):
    return _request(symbol, 't6')

def get_order_book_realtime(symbol):
    return _request(symbol, 'i5')

def get_high_limit(symbol):
    return _request(symbol, 'l2')

def get_eps(symbol):
    return _request(symbol, 'e')

def get_low_limit(symbol):
    return _request(symbol, 'l3')

def get_eps_estimate_current_year(symbol):
    return _request(symbol, 'e7')

def get_holdings_value(symbol):
    return _request(symbol, 'v1')

def get_eps_estimate_next_year(symbol):
    return _request(symbol, 'e8')

def get_holdings_value_realtime(symbol):
    return _request(symbol, 'v7')

def get_eps_estimate_next_quarter(symbol):
    return _request(symbol, 'e9')

def get_revenue(symbol):
    return _request(symbol, 's6')

def get_book_value(symbol):
    return _request(symbol, 'b4')

def get_ebitda(symbol):
    return _request(symbol, 'j4')

def get_price_sales(symbol):
    return _request(symbol, 'p5')

def get_price_book(symbol):
    return _request(symbol, 'p6')

def get_pe(symbol):
    return _request(symbol, 'r')

def get_pe_realtime(symbol):
    return _request(symbol, 'r2')

def get_peg(symbol):
    return _request(symbol, 'r5')

def get_price_eps_estimate_current_year(symbol):
    return _request(symbol, 'r6')

def get_price_eps_estimate_next_year(symbol):
    return _request(symbol, 'r7')

def get_short_ratio(symbol):
    return _request(symbol, 's7')

def get_historical_prices(symbol, start_date, end_date):
    """
    Get historical prices for the given ticker symbol.
    Date format is 'YYYY-MM-DD'
    Returns a nested dictionary (dict of dicts).
    outer dict keys are dates ('YYYY-MM-DD')
    """
    params = urlencode({
        's': symbol,
        'a': int(start_date[5:7]) - 1,
        'b': int(start_date[8:10]),
        'c': int(start_date[0:4]),
        'd': int(end_date[5:7]) - 1,
        'e': int(end_date[8:10]),
        'f': int(end_date[0:4]),
        'g': 'd',
        'ignore': '.csv',
    })
    url = 'http://real-chart.finance.yahoo.com/table.csv?%s' % params
    req = Request(url)
    resp = urlopen(req)
    content = str(resp.read().decode('utf-8').strip())
    daily_data = content.splitlines()
    hist_dict = dict()
    keys = daily_data[0].split(',')
    for day in daily_data[1:]:
        day_data = day.split(',')
        date = day_data[0]
        hist_dict[date] = \
            {keys[1]: day_data[1],
             keys[2]: day_data[2],
             keys[3]: day_data[3],
             keys[4]: day_data[4],
             keys[5]: day_data[5],
             keys[6]: day_data[6]}
    return hist_dict
