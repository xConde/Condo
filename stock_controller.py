import re
import robin_stocks as r
from bot_clock import hour, dayIndex


def checkPopularity(stock):
    stock_instrument = r.get_url(r.quote_data(stock)["instrument"])["id"]
    return r.get_url(urls.build_instruments(stock_instrument, "popularity"))["num_open_positions"]


def grabPercent(curr, prev):
    perc = round(((curr - prev) / prev * 100), 2)
    if perc >= 0:
        perc = '+' + str(perc) + '%'
        return perc
    else:
        perc = str(perc) + '%'
        return perc


def tickerPrice(arg1):
    quote = r.get_quotes(arg1)
    curr = round(float(quote['last_trade_price']), 2)
    return curr


def pc(arg1):
    quote = r.get_quotes(arg1)
    quote = quote[0]
    curr = round(float(quote['last_trade_price']), 2)
    prev = round(float(quote['adjusted_previous_close']), 2)
    perc1 = grabPercent(curr, prev)
    res = '{:<6}{:^12}{:<10}'.format(arg1.upper() + ':', '$' + str(curr), perc1)
    if dayIndex < 5 and 8 <= hour <= 15:
        return res
    else:
        ah = round(float(quote['last_extended_hours_trade_price']), 2)
        perc2 = grabPercent(ah, curr)
        res = res + '{:<4}{:<25}'.format('|    AH: $' + str(ah), "    " + perc2)
        return res


def validateTicker(stock):
    if not re.match(r'\b[a-zA-Z]{1,5}\b', stock):
        return False
    else:
        return True
