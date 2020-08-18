import re
import robin_stocks as r
from bot_clock import min, hour, dayIndex
from heapq import nlargest
import csv

stocks_mentioned = {}


def writeStocksMentioned():
    w = csv.writer(open("stocks_mentioned.csv", "w"))
    if w:
        print('Wrote stocks_mentioned to .csv')
    for key, val in stocks_mentioned.items():
        w.writerow([key, val])


def readStocksMentioned():
    reader = csv.reader(open("stocks_mentioned.csv"))
    if reader:
        print('Loaded stocks_mentioned dictionary from .csv')
    for row in reader:
        if row:
            key = row[0]
            stocks_mentioned[key] = int(row[1:][0])
            # if key in stocks_mentioned:
            # implement your duplicate row handling here
            #    pass


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
    if dayIndex < 5 and 9 <= hour < 16:
        if hour != 9 or (hour == 9 and min >= 30):
            low, high = grabIntradayHL(stock)
            return '{:<6}{:^8}{:>7}{:>2}{:>6}{:>11}'.format(stock.upper() + ':', '$' + str(curr), perc1,
                                                            '|', 'L: ' + str(low), 'H: ' + str(high))
    elif quote['last_extended_hours_trade_price']:
        ah = '{:.2f}'.format(round(float(quote['last_extended_hours_trade_price']), 2))
        perc2 = grabPercent(float(ah), float(curr))
        return '{:<6}{:^8}{:>7}{:>2}{:>6}{:>7}'.format(stock.upper() + ':', '$' + str(curr), perc1,
                                                       '|', 'AH: $' + str(ah), perc2)
    else:
        return '{:<6}{:^8}{:>7}'.format(stock.upper() + ':', '$' + str(curr), perc1)


def validateTicker(stock):
    if not re.match(r'\b[a-zA-Z]{1,5}\b', stock):
        return False
    else:
        stocks_mentioned[stock.upper()] = stocks_mentioned.get(stock.upper(), 0) + 1
        return True
