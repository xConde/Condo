import re

import robin_stocks as r
import datetime as dt
from datetime import datetime

import stock_controller as s  # local source

optionFormat = 'Ex: [stock], [strike]\n' \
               'Ex: [stock], [strike], [type]\n' \
               'Ex: [stock], [strike], [type], [expiration]\n'


def third_friday(year, month, day):
    """Return datetime.date for monthly option expiration given year and
    month
    """
    # The 15th is the lowest third day in the month
    third = dt.date(year, month, 15)
    # What day of the week is the 15th?
    w = third.weekday()
    # Friday is weekday 4
    if w != 4:
        # Replace just the day (of month)
        third = third.replace(day=(15 + (4 - w) % 7))

    if day > third.day:
        month += 1
        third = dt.date(year, month, 15)
        w = third.weekday()
        if w != 4:
            third = third.replace(day=(15 + (4 - w) % 7))

    if month < 10:
        month = '0' + str(month)
    else:
        month = str(month)

    currentDate = str(year) + '-' + month + '-' + str(day)

    if str(third) != currentDate:
        return third
    else:
        return third_friday(int(year), int(month), int(day)+1)


def searchStrikeIterator(stock, type, expir, price):
    strikeOptionList = [5, 2.5, 1, .5]
    for i in range(0, len(strikeOptionList)):
        strikeIterator = strikeOptionList[i]
        price = price - (price % strikeIterator)
        checkStrike = strikeIterator * round(price / strikeIterator) + strikeIterator * 1
        if r.find_options_by_expiration_and_strike(stock, expir, checkStrike, type):
            return strikeIterator
    print("Did not find any strikes")


def grabStrikeIterator(stock, type, expir, price):
    list1 = ['SPY', 'QQQ', 'IWM', 'SPCE', 'VXX']
    list5 = ['AAPL', 'FB', 'MSFT', 'NFLX', 'JPM', 'DIS', 'SQ', 'TSLA', 'ESTC', 'GOOGL', 'NVDA', 'TGT', 'WMT']
    if stock.upper() in list1:
        return 1
    elif stock.upper() in list5:
        return 5
    else:
        return searchStrikeIterator(stock, type, expir, price)


def pcOptionChain(stock, type, expir):
    strikes = []
    price = s.tickerPrice(stock)
    type = validateType(type)
    expir = validateExp(expir)
    strikeIterator = grabStrikeIterator(stock, type, expir, price)

    if type == 'call':
        price = price - (price % strikeIterator)
    else:
        if (strikeIterator * round(price / strikeIterator) + strikeIterator * 0) == (price - (price % strikeIterator)):
            price = strikeIterator * round(price / strikeIterator) + strikeIterator * 1  # round up
        else:
            price = strikeIterator * round(price / strikeIterator) + strikeIterator * 0  # round up

    for i in range(0, 4):
        if type == 'call':
            strikes.append((strikeIterator * round(price / strikeIterator)) + strikeIterator * i)
        else:
            strikes.append(price)
            price = price - price % strikeIterator - strikeIterator

    res = "Option chain for " + stock.upper() + ": (1 ITM / 3 OTM)\n"
    i = 1
    for strike in strikes:
        opt, msg = pcOption(stock, strike, type, expir)
        res += str(i) + ". " + opt + '\n'
        i += 1
    return res


def validateStrike(stock, type, expir, strike):
    price = s.tickerPrice(stock)
    if not r.find_options_by_expiration_and_strike(stock, expir, strike, type):
        return searchStrikeIterator(stock, type, expir, price)
    else:
        return strike


def validateType(type):
    if type and (type.lower() == 'puts' or type.lower() == 'put' or type.lower() == 'p'):
        return 'put'
    else:
        return 'call'


def validateExp(expir):
    now = dt.datetime.now()
    generatedExp = third_friday(now.year, now.month, now.day).strftime("%Y-%m-%d")
    if expir and re.match(r'^\d{4}-\d{2}-\d{2}$', expir):
        return expir
    else:
        return generatedExp


def pcOption(stock, strike, type, expir):
    type = validateType(type)
    exp = validateExp(expir)
    vstrike = validateStrike(stock, type, expir, strike)

    res = str(stock.upper()) + " " + exp[5:] + " " + str(vstrike) + type[0].upper() + " "
    msg = ""
    if s.validateTicker(stock):  # Option request invalidated
        if expir and expir != exp:
            msg += 'Defaulted expiration date to ' + exp + '. YYYY-MM-DD\n' + optionFormat + '\n'
        if vstrike != strike:
            msg += 'Defaulted strike to ' + str(vstrike) + '.'

        option = r.find_options_by_expiration_and_strike(stock, exp, vstrike, type)[0]
        curr = '{:.2f}'.format(round(float(option['adjusted_mark_price']), 2))
        prev = '{:.2f}'.format(round(float(option['previous_close_price']), 2))
        breakeven = '{:.2f}'.format(round(float(option['break_even_price']), 2))
        iv = int(float(option['implied_volatility']) * 100)
        perc = s.grabPercent(float(curr), float(prev))
        volume = int(option['volume'])
        volume = s.formatThousand(volume)
        oi = int(option['open_interest'])
        oi = s.formatThousand(oi)

        res = '{:<4}{:<6}{:>10}{:>2}{:>7}{:>7}{:>11}'.format(res, '$' + str(curr), perc + '\n',
                                                             'Vol:' + str(volume), 'OI:' + str(oi),
                                                             'IV:' + str(iv) + '%',
                                                             'BE:' + str(breakeven) + '\n')
    else:
        res = stock.upper() + " is not a valid ticker.\n"

    return res, msg
