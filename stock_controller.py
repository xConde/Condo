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
    perc = '{:.2f}'.format(round(((curr - prev) / prev * 100), 2))
    perc = validateUporDown(float(perc))
    return perc + '%'


def tickerPrice(stock):
    quote = r.get_quotes(stock)
    curr = '{:.2f}'.format((float(quote['last_trade_price']), 2))
    return curr


def grabIntradayHL(stock):
    quote = r.get_fundamentals(stock)
    quote = quote[0]
    low = '{:.2f}'.format(round(float(quote['low']), 2))
    high = '{:.2f}'.format(round(float(quote['high']), 2))
    return low, high


def pc(stock):
    quote = r.get_quotes(stock)
    quote = quote[0]
    curr = '{:.2f}'.format(round(float(quote['last_trade_price']), 2))
    prev = '{:.2f}'.format(round(float(quote['adjusted_previous_close']), 2))
    perc1 = grabPercent(float(curr), float(prev))
    if dayIndex < 5 and 9 <= hour <= 16:
        if hour != 9 or (hour == 9 and min >= 30):
            low, high = grabIntradayHL(stock)
            return '{:<6}{:^10}{:^6}{:>2}{:>6}{:>11}'.format(stock.upper() + ':', '$' + str(curr), perc1,
                                                             '|', 'L: ' + str(low), 'H: ' + str(high))
    else:
        ah = '{:.2f}'.format(round(float(quote['last_extended_hours_trade_price']), 2))
        perc2 = grabPercent(ah, curr)
        return '{:<6}{:^10}{:^6}{:>2}{:>6}{:>11}'.format(stock.upper() + ':', '$' + str(curr), perc1,
                                                         '|', 'AH: $' + str(ah), 'H: ' + perc2)


def validateTicker(stock):
    if not re.match(r'\b[a-zA-Z]{1,5}\b', stock):
        return False
    else:
        stocks_mentioned[stock.upper()] = stocks_mentioned.get(stock.upper(), 0) + 1
        return True
