from stocks.options import anomaly_option_controller as a
from stocks.options import option_controller as o
from stocks import stock_controller as s
from bot import cal as cal
from functools import lru_cache


def loadStrikes(ticker, expir):
    """Loads strikes into call_strikes & put_strikes

    :return: 2 lists: call_strikes & put_strikes
    """
    strike_value = {}
    days_till_expiration = []
    callStrikeIterator = []
    price = s.tickerPrice(ticker)
    for exp in expir:
        days_till_expiration.append(cal.DTE(exp))
        callStrikeIterator.append(o.searchStrikeIterator(ticker, 'call', exp, price))

    call_value = o.pcOptionMin(ticker, 'call', expir,
                               strike_value, days_till_expiration, o.roundPrice(price, callStrikeIterator[0], 'call'),
                               callStrikeIterator)

    put_value = o.pcOptionMin(ticker, 'put', expir,
                              strike_value, days_till_expiration, o.roundPrice(price, callStrikeIterator[0], 'put'),
                              callStrikeIterator)

    return strike_value, [call_value, put_value]


def dominatingSide(ticker, call, put, expDates=None):
    """Determines dominating side (calls vs puts) and returns result

    :param exp:
    :param call:
    :param put:
    :return:
    """
    if not expDates:
        exp = cal.find_friday()

    expRes = "("
    for exp in expDates:
        expRes += exp + ", "
    expRes = expRes[:-2] + ")"

    res = "Valued " + ticker.upper() + " " + expRes + " options\n"
    largeSide = "Calls" if call > put else "Puts"
    call_abv = a.formatIntForHumans(call)
    put_abv = a.formatIntForHumans(put)
    res += largeSide + " are dominating ("
    res += call_abv if call > put else put_abv
    res += " > "
    res += call_abv if call < put else put_abv
    res += ") Value = Vol * Price\n"
    return res


def mostExpensive(ticker):
    """Outputs dominating side and highest value strikes (+type)

    :param ticker:
    :return:
    """
    monthExp = cal.generate_multiple_months(ticker, 3)
    strike_value, optionValue1 = loadStrikes(ticker, monthExp)

    call_value = optionValue1[0]
    put_value = optionValue1[1]

    res = dominatingSide(ticker, call_value, put_value, monthExp)

    highest = s.checkMostMentioned(strike_value, 5)
    for val in highest:
        cost = a.formatIntForHumans(strike_value.get(val))
        res += str(val) + ' = $' + cost + "\n"
    return res
