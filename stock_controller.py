import re
import robin_stocks as r
from bot_clock import min, hour, dayIndex
from heapq import nlargest

stocks_mentioned = {}


def checkPopularity(stock):
    stock_instrument = r.get_url(r.quote_data(stock)["instrument"])["id"]
    return r.get_url(urls.build_instruments(stock_instrument, "popularity"))["num_open_positions"]


def checkMostMentioned():
    fiveHighest = nlargest(5, stocks_mentioned, key=stocks_mentioned.get)
    return fiveHighest


def validateUporDown(var):
    if var >= 0:
        return '+' + str(var)
    else:
        return str(var)


def grabPercent(curr, prev):
    perc = round(((curr - prev) / prev * 100), 2)
    perc = validateUporDown(perc)
    return perc + '%'


def tickerPrice(stock):
    quote = r.get_quotes(stock)
    curr = round(float(quote['last_trade_price']), 2)
    return curr


def grabIntradayHL(stock):
    quote = r.get_fundamentals(stock)
    quote = quote[0]
    low = round(float(quote['low']), 2)
    high = round(float(quote['high']), 2)
    return 'L: ' + str(low) + '    H: ' + str(high)


def pc(stock):
    quote = r.get_quotes(stock)
    quote = quote[0]
    curr = round(float(quote['last_trade_price']), 2)
    prev = round(float(quote['adjusted_previous_close']), 2)
    perc1 = grabPercent(curr, prev)
    res = '{:<6}{:^12}{:<10}'.format(stock.upper() + ':', '$' + str(curr), perc1)
    if dayIndex < 5 and 9 <= hour <= 16:
        if hour != 9 or (hour == 9 and min >= 30):
            intraday = grabIntradayHL(stock)
            return res + '|    ' + intraday
    else:
        ah = round(float(quote['last_extended_hours_trade_price']), 2)
        perc2 = grabPercent(ah, curr)
        res = res + '{:<4}{:<25}'.format('|    AH: $' + str(ah), "    " + perc2)
        return res


def validateTicker(stock):
    if not re.match(r'\b[a-zA-Z]{1,5}\b', stock):
        return False
    else:
        stocks_mentioned[stock.upper()] = stocks_mentioned.get(stock.upper(), 0) + 1
        return True
