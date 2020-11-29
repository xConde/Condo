from stocks.options import anomaly_option_controller as a
from stocks.options import option_controller as o
from stocks import stocks as s
from bot import cal as cal

import robin_stocks as r  # 3rd party packages


def loadStrikes(ticker):
    """Loads strikes into call_strikes & put_strikes

    :return: 2 lists: call_strikes & put_strikes
    """

    call_strikes = []
    put_strikes = []
    i = 0
    expir = cal.find_friday()
    price = s.tickerPrice(ticker)
    strikeIterator = o.searchStrikeIterator(ticker, 'call', cal.find_friday(), price)

    callprice = o.roundPrice(price, strikeIterator, 'call')
    putprice = o.roundPrice(price, strikeIterator, 'put')
    while True:  # Now that we have the iterator and rounded price, collect actual strikes
        if i == 0 and not r.find_options_by_expiration_and_strike(
                    ticker, cal.find_friday(), o.grabStrike(callprice, strikeIterator, 'call', i), 'call'):
            expir = str(cal.third_friday(cal.getYear(), cal.getMonth(), cal.getMonthlyDay()))

        if i > 5:  # Find the highest strike applicable
            if not r.find_options_by_expiration_and_strike(
                    ticker, expir, o.grabStrike(callprice, strikeIterator, 'call', i), 'call')[0]['volume']\
                    or not r.find_options_by_expiration_and_strike(
                    ticker, expir, o.grabStrike(callprice, strikeIterator, 'call', i+1), 'call'):
                break
        # print(o.grabStrike(callprice, strikeIterator, 'call', i))
        call_strikes.append(o.grabStrike(callprice, strikeIterator, 'call', i))
        put_strikes.append(o.grabStrike(putprice, strikeIterator, 'put', i))
        i += 1
    return call_strikes, put_strikes


def generateValue(ticker, call_strikes, put_strikes, exp):
    """Generates value from strike (premium) * volume. Stores everything in strike_value, returns call_value & put_value

    :return: 2 ints call_value, put_value
    """
    strike_value = {}
    call_value = 0
    put_value = 0

    for strike in call_strikes:
        # print('generateValue', ticker, strike, 'call', exp)
        value, _ = o.pcOptionMin(ticker, strike, 'call', exp)
        strike_value[str(strike) + 'C'] = value
        call_value += value
    for strike in put_strikes:
        value, _ = o.pcOptionMin(ticker, strike, 'put', exp)
        strike_value[str(strike) + 'P'] = value
        put_value += value
    res = dominatingSide(ticker, call_value, put_value, exp)
    return strike_value, res


def dominatingSide(ticker, call, put, exp=None):
    """Determines dominating side (calls vs puts) and returns result

    :param exp:
    :param call:
    :param put:
    :return:
    """
    if not exp:
        exp = cal.find_friday()

    res = "Valued " + ticker.upper() + " " + exp + " options\n"
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
    call_strikes, put_strikes = loadStrikes(ticker)
    exp = o.validateExp(ticker, cal.find_friday(), call_strikes[0], 'call')
    strike_value, res = generateValue(ticker, call_strikes, put_strikes, exp)

    highest = s.checkMostMentioned(strike_value, 5)
    for val in highest:
        cost = a.formatIntForHumans(strike_value.get(val))
        res += str(val) + ' = $' + cost + "\n"
    return res
