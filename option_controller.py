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
    exp = ""
    type = validateType(type)
    exp = validateExp(expir)

    res = str(stock.upper()) + " " + exp[5:] + " " + strike + type[0].upper() + " "
    msg = ""
    if s.validateTicker(stock):  # Option request invalidated
        if expir and expir != exp:
            msg = 'Defaulted expiration date to ' + exp + '. YYYY-MM-DD\n' + optionFormat

        option = r.find_options_by_expiration_and_strike(stock, exp, strike, type)[0]
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
