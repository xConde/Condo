import re  # Standard Library

import csv  # 3rd Party Packages
import robin_stocks as r
import datetime as dt
from datetime import datetime
from heapq import nlargest

stocks_mentioned = {}  # Maintains stock ticker as key and times mentioned as value.


def writeStocksMentioned(timestamp):
    """Writes [stock ticker, iterations] from stocks_mentioned to "stocks_mentioned.csv"

    :return:
    """
    w = csv.writer(open("stocks_mentioned.csv", "w"))
    if w:
        print('Wrote stocks_mentioned to .csv ' + timestamp)
    for key, val in stocks_mentioned.items():
        w.writerow([key, val])


def readStocksMentioned():
    """Reads "stocks_mentioned.csv" to stocks_mentioned[stock ticker, iterations]

    :return:
    """
    reader = csv.reader(open("stocks_mentioned.csv"))
    if reader:
        print('Loaded stocks_mentioned dictionary from .csv')
    for row in reader:
        if row:
            key = row[0]
            stocks_mentioned[key] = int(row[1:][0])


def getCommands():
    res = ""
    res += "- Price checker: Receive the current price on a stock\n"
    res += "EX: .p (arg1), (arg2), ... (argN)\n"
    res += "- Option: Displays stock option information based on ticker, strike, type (call or put), " \
           "and expiration.\n"
    res += "Ex: .option [stock], [strike]\n" + "Ex: .option [stock], [strike], [type]\n" + "Ex: .option [stock], " \
                                                                                           "[strike], [type], " \
                                                                                           "[expiration]\n "
    res += "- Option chain: Displays stock option chain information based on ticker, type (call or put), " \
           "and expiration.\n"
    res += "Ex: .f [stock]\n" + "Ex: .f [stock], [type]\n" + "Ex: .f [stock], [type], [expiration]\n"
    res += "- Top/Bottom 5 S&P performing stocks\n"
    res += "Ex: .spyup\n" + "Ex: .spydown\n"
    res += "- Most mentioned stocks: Maintains a record of mentioned stocks.\n"
    res += "Ex: .used\n"
    return res


def pull_sp500(dir):
    movers = r.get_top_movers_sp500(dir)
    res = ""
    for i in range(0, 5):
        stock = movers[i]['symbol']
        stockRes, perc = pc(stock)
        res += stockRes
    return res


def formatThousand(val):
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
    perc = round(((curr - prev) / prev * 100), 2)
    perc = validateUporDown(float(perc))
    return perc + '%'


def evaluatePercent(curr, prev, perc):
    """Takes a string formatted percent [ex. '-5.62%'] and evaluates the numerical value to ensure it is not 0``
    returns perc in numerical form.

    :param curr:
    :param prev:
    :param perc:
    :return:
    """
    if curr != prev:
        return float(perc[:-1])
    else:
        return 0


def tickerPrice(stock):
    """Returns last trade price for provided stock

    :param stock: {1-5} character stock-ticker
    :return: [float] current price
    """
    price = float(r.get_latest_price(stock)[0])
    return price


def grabIntradayHL(stock):
    """Returns intra-day low/high of the day.

    :param stock: {1-5} character stock-ticker
    :return: [float] low, [float] high
    """
    quote = r.get_fundamentals(stock)
    quote = quote[0]
    low = '{:.2f}'.format(round(float(quote['low']), 2))
    high = '{:.2f}'.format(round(float(quote['high']), 2))
    return low, high


def pc(stock):
    """Generates and formats stock prices based on if market is open or in after-hours.

    :param stock: {1-5} character stock-ticker
    :return: [String] formatted output of price check.
    """
    dayIndex = dt.datetime.today().weekday()  # 0-6 index
    hour = datetime.now().hour + 1  # datetime.now().hour+1 for central to eastern (fix later)
    min = datetime.now().minute

    quote = r.get_quotes(stock)[0]
    curr = '{:.2f}'.format(round(float(quote['last_trade_price']), 2))
    prev = '{:.2f}'.format(round(float(quote['adjusted_previous_close']), 2))
    perc1 = grabPercent(float(curr), float(prev))

    if dayIndex < 5 and 9 <= hour < 16 and not (hour == 9 and min < 30):
        low, high = grabIntradayHL(stock)
        res = '{:<6}{:^8}{:>7}{:>2}{:>6}{:>11}'.format(stock.upper() + ':', '$' + str(curr), perc1,
                                                       '|', 'L: ' + str(low), 'H: ' + str(high)) + '\n'
        perc1 = evaluatePercent(float(curr), float(prev), perc1)
        return res, perc1
    elif quote['last_extended_hours_trade_price']:
        ah = '{:.2f}'.format(round(float(quote['last_extended_hours_trade_price']), 2))
        perc2 = grabPercent(float(ah), float(curr))
        res = '{:<6}{:^8}{:>7}{:>2}{:>6}{:>7}'.format(stock.upper() + ':', '$' + str(curr), perc1,
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


def autoPull(timestamp, hour, min):
    """Pulls stock quotes for scheduledStocks and formats them to be in order of highest gain to lowest gain.

    :return: [String] formatted result
    """
    scheduledStocks = ['SPY', 'AAPL', 'FB', 'AMZN', 'NFLX', 'GOOGL', 'MSFT']

    if hour <= 9 and not (hour == 9 and min >= 30):
        res = "[15M pull] Pre-market\n"
    elif hour < 16:
        res = "[15M pull] Intraday\n"
    else:
        res = "[15M pull] After-hours\n"

    stockQuote = {}
    stockPerc = {}
    for stock in scheduledStocks:
        stockRes, perc = pc(stock)
        stockQuote[stock] = stockRes
        stockPerc[stock] = perc

    highest = checkMostMentioned(stockPerc, len(scheduledStocks))
    for val in highest:
        res += stockQuote[val]
    print("Pulled [15M] " + timestamp)
    return res
