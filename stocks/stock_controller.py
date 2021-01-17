import re  # Standard Library

import csv  # 3rd Party Packages
import robin_stocks as r
from heapq import nlargest

from bot import cal as cal

stocks_mentioned = {}  # Maintains stock ticker as key and times mentioned as value.
stocks_mentioned_csv = "doc/stocks_mentioned.csv"


def writeStocksMentioned():
    """Writes [stock ticker, iterations] from stocks_mentioned to "stocks_mentioned.csv"

    :return:
    """
    w = csv.writer(open(stocks_mentioned_csv, "w"))
    if w:
        print('Wrote stocks_mentioned to .csv @' + cal.getEstTimestamp())
        w.writerow(['Stock Ticker', 'Quantity'])
    for key, val in stocks_mentioned.items():
        w.writerow([key, val])


def readStocksMentioned():
    """Reads "stocks_mentioned.csv" to stocks_mentioned[stock ticker, iterations]

    :return:
    """
    reader = csv.reader(open(stocks_mentioned_csv))
    if reader:
        print('Loaded stocks_mentioned dictionary from .csv')
    rows = 0
    for row in reader:
        if row and rows != 0:
            key = row[0]
            stocks_mentioned[key] = int(row[1:][0])
        rows += 1


def pull_sp500(dir):
    """ Pull top movers from SPY.

    :param dir:
    :return:
    """
    movers = r.get_top_movers_sp500(dir)
    res = ""
    for i in range(0, 5):
        stock = movers[i]['symbol']
        stockRes, perc = pc(stock)
        res += stockRes
    return res


def formatThousand(val):
    """ Transform large numbers to an easily read number.

    :param val:
    :return:
    """
    if val > 1000:
        val = '{:.2f}'.format(round(val / 1000), 1) + 'K'
        if val[-3:] == '00K':
            return val[:-4] + 'K'
    return val


def checkMostMentioned(dict, max):
    """Finds the top 5 most mentioned stocks.

    :return: Returns a dictionary of the top 5 most mentioned stocks
    """
    fiveHighest = nlargest(max, dict, key=dict.get)
    return fiveHighest


def validateUporDown(var):
    """Evaluates if value is positive, if it is add a '+' and return it as a string. If it is not, just return it as``
     a string.

    :param var:
    :return: Returns a string.
    """
    if var >= 0:
        return '+' + str(var)
    else:
        return str(var)


def grabPercent(curr, prev):
    """Converts current and previous value to produce a percent difference.

    :param curr: [float] current value
    :param prev: [float] previous value
    :return: [string] percent difference
    """
    perc = validateUporDown(float(round(((curr - prev) / prev * 100), 2)))
    return perc + '%'


def evaluatePercent(curr, prev, perc):
    """Takes a string formatted percent [ex. '-5.62%'] and evaluates the numerical value to ensure it is not 0``
    returns perc in numerical form.

    :param curr:
    :param prev:
    :param perc:
    :return:
    """
    if curr != prev and perc[-2:] != "0%":
        return float(perc[:-1])
    else:
        return 0


def tickerPrice(stock):
    """Returns last trade price for provided stock

    :param stock: {1-5} character stock-ticker
    :return: [float] current price
    """
    return float(r.get_latest_price(stock)[0])


def grabIntradayHL(stock):
    """Returns intra-day low/high of the day.

    :param stock: {1-5} character stock-ticker
    :return: [float] low, [float] high
    """
    quote = r.get_fundamentals(stock)[0]
    low = '{:.2f}'.format(round(float(quote['low']), 2))
    high = '{:.2f}'.format(round(float(quote['high']), 2))
    return low, high


def grabSimplePrice(stock):
    """Grabs a simple float price. If AH, use the extended hours price instead.

    :param stock:
    :return:
    """
    quote = r.get_quotes(stock)[0]

    if quote['last_extended_hours_trade_price']:
        return '{:.2f}'.format(round(float(quote['last_extended_hours_trade_price']), 2))
    else:
        return '{:.2f}'.format(round(float(quote['last_trade_price']), 2))


def pc(stock):
    """Generates and formats stock prices based on if market is open or in after-hours.

    :param stock: {1-5} character stock-ticker
    :return: [String] formatted output of price check.
    """
    quote = r.get_quotes(stock)[0]
    curr = '{:.2f}'.format(round(float(quote['last_trade_price']), 2))
    prev = '{:.2f}'.format(round(float(quote['adjusted_previous_close']), 2))
    perc1 = grabPercent(float(curr), float(prev))

    if cal.getDay() < 5 and 14 <= cal.getHour() < 21 and not (cal.getHour() == 14 and cal.getMinute() < 30):
        low, high = grabIntradayHL(stock)
        res = '{:<6}{:^8}{:>7}{:>2}{:>6}{:>11}'.format(stock.upper() + ':', '$' + str(curr), perc1,
                                                       '|', 'L: ' + str(low), 'H: ' + str(high)) + '\n'
        perc1 = evaluatePercent(float(curr), float(prev), perc1)
        return res, perc1
    elif quote['last_extended_hours_trade_price']:
        ah = '{:.2f}'.format(round(float(quote['last_extended_hours_trade_price']), 2))
        perc2 = grabPercent(float(ah), float(curr))
        res = '{:<6}{:^8}{:>7}{:>2}{:>6}{:>9}'.format(stock.upper() + ':', '$' + str(curr), perc1,
                                                      '|', 'AH: $' + str(ah), perc2) + '\n'
        perc2 = evaluatePercent(float(ah), float(prev), perc2)
        return res, perc2
    else:
        res = '{:<6}{:^8}{:>7}'.format(stock.upper() + ':', '$' + str(curr), perc1) + '\n'
        perc1 = evaluatePercent(float(curr), float(prev), perc1)
        return res, perc1


def validateTicker(stock):
    """Validates user input. If it is allowed, return True and add it to the stocks_mentioned dict.

    :param stock:
    :return:
    """
    if not re.match(r'\b[a-zA-Z]{1,5}\b', stock) or not r.get_quotes(stock)[0]:
        return False
    else:
        stocks_mentioned[stock.upper()] = stocks_mentioned.get(stock.upper(), 0) + 1
        return True


def autoPull():
    """Pulls stock quotes for scheduledStocks and formats them to be in order of highest gain to lowest gain.

    :return: [String] formatted result
    """
    scheduledIndex = ['SPY', 'QQQ', 'IWM', 'VXX']
    scheduledStocks = ['AAPL', 'FB', 'AMZN', 'NFLX', 'GOOGL', 'MSFT', 'NVDA', 'JPM', 'TSLA']

    if cal.getHour() <= 13 and not (cal.getHour() == 14 and cal.getMinute() >= 30):
        res = "[15M pull] Pre-market @ " + cal.getEstTimestamp() + "\n"
    elif cal.getHour() < 21:
        res = "[15M pull] Intraday @ " + cal.getEstTimestamp() + "\n"
    else:
        res = "[15M pull] After-hours @ " + cal.getEstTimestamp() + "\n"

    indexQuote = {}
    stockQuote = {}

    indexPerc = {}
    stockPerc = {}

    for index in scheduledIndex:
        indexRes, perc = pc(index)
        indexQuote[index] = indexRes
        indexPerc[index] = perc

    for stock in scheduledStocks:
        stockRes, perc = pc(stock)
        stockQuote[stock] = stockRes
        stockPerc[stock] = perc

    highestIndex = checkMostMentioned(indexPerc, len(scheduledIndex))
    highestStock = checkMostMentioned(stockPerc, len(scheduledStocks))

    for val in highestIndex:
        res += indexQuote[val]
    res += "----------\n"
    for val in highestStock:
        res += stockQuote[val]
    print("Pulled [15M] " + cal.getEstTimestamp())
    return res
