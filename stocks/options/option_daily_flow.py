from stocks.options import anomaly_option_controller as a
from stocks.options import option_controller as o
from stocks import stocks as s
from bot import cal as cal

import robin_stocks as r  # 3rd party packages


def loadStrikes(ticker, expir):
    """Loads strikes into call_strikes & put_strikes

    :return: 2 lists: call_strikes & put_strikes
    """
    strike_value = {}
    call_value = 0
    put_value = 0
    DTE = []
    callStrikeIterator = []
    price = s.tickerPrice(ticker)
    for exp in expir:
        DTE.append(cal.DTE(exp))
        callStrikeIterator.append(o.searchStrikeIterator(ticker, 'call', exp, price))
        print(o.searchStrikeIterator(ticker, 'call', exp, price))

    cvalue = o.pcOptionMin(ticker, 'call', expir,
                           strike_value, DTE, o.roundPrice(price, callStrikeIterator[0], 'call'), callStrikeIterator)
    call_value += cvalue

    pvalue = o.pcOptionMin(ticker, 'put', expir,
                           strike_value, DTE, o.roundPrice(price, callStrikeIterator[0], 'put'), callStrikeIterator)
    put_value += pvalue

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
    res += ")\n"
    return res


def mostExpensive(ticker):
    """Outputs dominating side and highest value strikes (+type)

    :param ticker:
    :return:
    """
    # friday = cal.find_friday()
    monthExp = cal.generate_3_months()

    import time

    start = time.time()
    strike_value, optionValue1 = loadStrikes(ticker, monthExp)
    end = time.time()
    print(end - start)

    call_value = optionValue1[0]
    put_value = optionValue1[1]

    res = dominatingSide(ticker, call_value, put_value, monthExp)

    highest = s.checkMostMentioned(strike_value, 5)
    for val in highest:
        cost = a.formatIntForHumans(strike_value.get(val))
        res += str(val) + ' = $' + cost + "\n"
    return res
