import re  # Standard library

import robin_stocks as r  # 3rd party packages
import datetime as dt

import stock_controller as s  # local source

optionFormat = 'Ex: [stock], [strike]\n' \
               'Ex: [stock], [strike], [type]\n' \
               'Ex: [stock], [strike], [type], [expiration]\n'


def third_friday(year, month, day):
    """Return datetime.date for monthly option expiration given year and month.

    :param year:
    :param month:
    :param day:
    :return:
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

    if str(third) != currentDate:  # See if current day is the monthly expiration, if it is move to next month.
        return third
    else:
        return third_friday(int(year), int(month), int(day) + 1)


def roundPrice(price, strikeIterator, type):
    """Round up/down based on 'type' of option desired to allow first option shown to be ITM for
    that type. It is possible when initially rounding up [puts] for a strike price to be closer to a rounded down 5, so
    it compares that with the [calls] ITM to ensure they're not the same.

    :param price:
    :param strikeIterator:
    :return:
    """
    if type == 'call':  # Round down to make the first call shown ITM
        return price - (price % strikeIterator)
    else:  # Round up to make the first put shown ITM
        if (strikeIterator * round(price / strikeIterator) + strikeIterator * 0) == (price - (price % strikeIterator)):
            return strikeIterator * round(
                price / strikeIterator) + strikeIterator * 1  # round up further to make strike ITM
        else:
            return strikeIterator * round(price / strikeIterator) + strikeIterator * 0  # round up


def searchStrikeIterator(stock, type, expir, price):
    """Iterate through a list of possible strike option iterators from greatest to least (to prevent a possible match for
    rounding, but not actually exist for 1-3 more option strike prices). Return strike iterator.

    :param stock:
    :param type:
    :param expir:
    :param price:
    :return:
    """
    if price > 1000:
        strikeOptionList = [5, 10, 50]
    elif price > 100:
        strikeOptionList = [1, 5, 10, 50]
    elif price < 100:
        strikeOptionList = [.5, 1, 5, 10, 50]

    for i in range(0, len(strikeOptionList)):
        strikeIterator = strikeOptionList[i]
        price = price - (price % strikeIterator)
        checkStrike = strikeIterator * round(price / strikeIterator) + strikeIterator * 0
        checkStrike2 = strikeIterator * round(price / strikeIterator) + strikeIterator * 1
        if r.find_options_by_expiration_and_strike(stock, expir, checkStrike, type) \
                and r.find_options_by_expiration_and_strike(stock, expir, checkStrike2, type)[0]['volume']:
            return strikeIterator
    print("Did not find any strikes")


def grabStrikeIterator(stock, type, expir, price):
    """Check to see if stock option chain iterator being requested is one of the highly used tickers inside of one of two lists.
    If it is not, send information to search strike iterator and find the strike iterator.

    :param stock:
    :param type:
    :param expir:
    :param price:
    :return:
    """
    list1 = ['SPY', 'QQQ', 'IWM', 'SPCE', 'VXX']
    list5 = ['AAPL', 'FB', 'MSFT', 'NFLX', 'JPM', 'DIS', 'SQ', 'ESTC', 'GOOGL', 'NVDA', 'TGT', 'WMT']
    if stock.upper() in list1:
        return 1
    elif stock.upper() in list5:
        return 5
    else:
        return searchStrikeIterator(stock, type, expir, price)


def grabStrike(price, strikeIterator, type, i):
    """Grabs strike price for a rounded price, strike iterator, and iteration based on type.

    :param price:
    :param strikeIterator:
    :param i:
    :return:
    """
    if type == 'call':
        return strikeIterator * round(price / strikeIterator) + strikeIterator * i
    else:
        if i != 0:
            return price - price % strikeIterator - strikeIterator * i
        else:
            return price


def validateType(type):
    """Given a type return a type that is corrected or defaulted.

    :param type:
    :return:
    """
    if type and (type.lower() == 'puts' or type.lower() == 'put' or type.lower() == 'p'):
        return 'put'
    else:
        return 'call'


def validateExp(expir):
    """Given an expiration date return an expiration that is provided if correct or a default date.

    :param expir:
    :return:
    """
    now = dt.datetime.now()
    generatedExp = third_friday(now.year, now.month, now.day).strftime("%Y-%m-%d")
    if expir and re.match(r'^\d{4}-\d{2}-\d{2}$', expir):
        return expir
    else:
        return generatedExp


def validateStrike(stock, type, expir, strike):
    """Given parameters that should all be correct validate strike price. If strike price is not correct, return a
    correct one.

    :param stock:
    :param type:
    :param expir:
    :param strike:
    :return:
    """
    price = s.tickerPrice(stock)
    if not r.find_options_by_expiration_and_strike(stock, expir, strike, type):
        strikeIterator = grabStrikeIterator(stock, type, expir, price)
        price = roundPrice(price, strikeIterator, type)
        return grabStrike(price, strikeIterator, type, 0)
    else:
        return strike


def pcOption(stock, strike, type, expir):
    """Given parameters needed to collect option data, validate/correct type, exp, and strike, and return option data
    relating to all of these fields. Also returns a msg if something major was defaulted when the user attempted to
    provide that certain parameter.

    :param stock:
    :param strike:
    :param type:
    :param expir:
    :return:
    """
    type = validateType(type)
    exp = validateExp(expir)
    vstrike = validateStrike(stock, type, expir, strike)

    res = str(stock.upper()) + " " + exp[5:] + " " + str(vstrike) + type[0].upper() + " "
    msg = ""

    if expir and expir != exp:
        msg += 'Defaulted expiration date to ' + exp + '. YYYY-MM-DD\n' + optionFormat + '\n'
    if vstrike != strike:
        msg += 'Strike price ' + strike + ' did not exist for ' + stock.upper() + \
               '.\nDefaulted strike to ' + str(vstrike) + ' (1 ITM).\n'
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
    return res, msg


def pcOptionChain(stock, type, expir, price):
    """Provided a stock ticker, type, expiration - validate type and expiration given. Generate strike iterator to move
    up/down option chain. Round up/down based on 'type' of option desired. Formats options gathered and returns a string.

    :param stock:
    :param type:
    :param expir:
    :return:
    """
    strikes = []
    type = validateType(type)
    expir = validateExp(expir)
    strikeIterator = grabStrikeIterator(stock, type, expir, price)

    price = roundPrice(price, strikeIterator, type)

    for i in range(0, 4):  # Now that we have the iterator and rounded price, collect actual strikes
        strikes.append(grabStrike(price, strikeIterator, type, i))

    res = "Option chain for " + stock.upper() + ":\n"
    i = 0
    for strike in strikes:  # We have strikes, call pcOption and format output
        opt, msg = pcOption(stock, strike, type, expir)
        if i == 0:
            res += "[ITM] " + opt + '------------------------------------\n'
        else:
            res += str(i) + " OTM. " + opt + '------------------------------------\n'
        i += 1
    return res
