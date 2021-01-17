import re  # Standard library
import math
from multiprocessing import Pool
from functools import lru_cache

import robin_stocks as r  # 3rd party packages

from stocks import stock_controller as s
from bot import cal as cal

optionFormat = 'Ex: [stock], [strike]\n' \
               'Ex: [stock], [strike], [type]\n' \
               'Ex: [stock], [strike], [type], [expiration]\n'


@lru_cache(maxsize=200)
def round10(price):
    return int(math.ceil(price/10.0)) * 10


@lru_cache(maxsize=200)
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


@lru_cache(maxsize=200)
def searchStrikeIterator(stock, type, expir, price):
    """Iterate through a list of possible strike option iterators from greatest to least (to prevent a possible match for
    rounding, but not actually exist for 1-3 more option strike prices). Return strike iterator.

    :param stock:
    :param type:
    :param expir:
    :param price:
    :return:
    """
    actualPrice = price
    if actualPrice > 1000:
        strikeOptionList = [2.5, 5, 10, 50]
    elif actualPrice > 100:
        strikeOptionList = [1, 2.5, 5, 10, 50]
    else:
        strikeOptionList = [.5, 1, 2.5, 5, 10, 50]

    for i in range(len(strikeOptionList)):
        strikeIterator = strikeOptionList[i]
        price = price - (price % strikeIterator)
        checkStrike = strikeIterator * round(price / strikeIterator) + strikeIterator * 0
        checkStrike2 = strikeIterator * round(price / strikeIterator) + strikeIterator * 1
        checkStrike3 = strikeIterator * round(price / strikeIterator) + strikeIterator * 2
        if r.find_options_by_expiration_and_strike(stock, expir, str(checkStrike), type) \
                and r.find_options_by_expiration_and_strike(stock, expir, str(checkStrike2), type) \
                and r.find_options_by_expiration_and_strike(stock, expir, str(checkStrike3), type):
            return strikeIterator
    return 5


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


@lru_cache(maxsize=100)
def validateExp(stock, expir, type, strike=None):
    """Given an expiration date return an expiration that is provided if correct or a default date.

    :param stock:
    :param expir:
    :param type:
    :param strike:
    :return:
    """
    if expir and re.match(r'^\d{4}-\d{2}-\d{2}$', expir):

        while True and strike:
            print("Trying", stock, expir, strike, type)
            options = r.find_options_by_expiration_and_strike(stock, expir, strike, type)
            if options and options[0]:
                print("EZ")
                return expir
            else:
                expir = cal.generate_next_month_exp(expir)
    else:
        return cal.third_friday(cal.getYear(), cal.getMonth(), cal.getMonthlyDay()).strftime("%Y-%m-%d")


@lru_cache(maxsize=100)
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
        strikeIterator = searchStrikeIterator(stock, type, expir, price)
        price = roundPrice(price, strikeIterator, type)
        return grabStrike(price, strikeIterator, type, 0)
    else:
        return strike


def pcOptionMin(stock, type, expir, strike_value=None, DTE=None, price=None, strikeIterator=None):
    """Given parameters needed to collect option data, provide the current volume and price for option. ***Used
    for anomaly_option_controller (parameters are verified).

    :param stock:
    :param strike:
    :param type:
    :param expir:
    :return:
    """
    totalValue = 0

    for i in range(len(expir)):
        j = 0
        while True:
            strike = grabStrike(price, strikeIterator[i], type, j)
            j += 1
            option = r.find_options_by_expiration_and_strike(stock, expir[i], strike, type)
            if not option or not option[0]['volume']:
                break
            volume = int(option[0]['volume'])
            if volume > 25:
                curr = round(float(option[0]['adjusted_mark_price']) * 100, 2)
                value = curr * volume
                totalValue += value
                strike_value['[' + str(DTE[i]) + ' DTE] ' + str(strike) + type.upper()[:1]] = value
                print('[' + str(DTE[i]) + ' DTE] ' + str(strike) + type.upper()[:1])
            else:
                break
    return totalValue


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
    exp = validateExp(stock, expir, type, strike)
    vstrike = validateStrike(stock, type, exp, strike)

    res = str(stock.upper()) + " " + exp[5:] + " " + str(vstrike) + type[0].upper() + " "
    msg = ""

    if expir and expir != exp:
        msg += 'Defaulted expiration date to ' + exp + '. YYYY-MM-DD\n' + optionFormat + '\n'
    if vstrike != strike:
        msg += 'Strike price ' + strike + ' did not exist for ' + stock.upper() + \
               '.\nDefaulted strike to ' + str(vstrike) + ' (1 ITM).\n'
    option = r.find_options_by_expiration_and_strike(stock, exp, vstrike, type)[0]
    # print(option)
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
    exp = validateExp(stock, expir, type, None)
    strikeIterator = searchStrikeIterator(stock, type, exp, price)

    price = roundPrice(price, strikeIterator, type)

    for i in range(0, 4):  # Now that we have the iterator and rounded price, collect actual strikes
        strikes.append(grabStrike(price, strikeIterator, type, i))

    expir = validateExp(stock, expir, type, strikes[0])
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
