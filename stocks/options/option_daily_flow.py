from stocks.options import anomaly_option_controller as a
from stocks.options import option_controller as o
from stocks import stocks as s
from bot import cal as cal

import robin_stocks as r  # 3rd party packages


def loadStrikes(ticker, expir):
    """Loads strikes into call_strikes & put_strikes

    :return: 2 lists: call_strikes & put_strikes
    """

    call_strikes = []
    put_strikes = []
    i = 0
    fillCalls = True
    fillPuts = True
    price = s.tickerPrice(ticker)
    strikeIterator = o.searchStrikeIterator(ticker, 'call', expir, price)

    callprice = o.roundPrice(price, strikeIterator, 'call')
    putprice = o.roundPrice(price, strikeIterator, 'put')
    while fillCalls or fillPuts:  # Now that we have the iterator and rounded price, collect actual strikes
        if i == 0 and not r.find_options_by_expiration_and_strike(
                ticker, cal.find_friday(), o.grabStrike(callprice, strikeIterator, 'call', i), 'call'):
            expir = str(cal.third_friday(cal.getYear(), cal.getMonth(), cal.getMonthlyDay()))

        if fillCalls and r.find_options_by_expiration_and_strike(
                    ticker, expir, o.grabStrike(callprice, strikeIterator, 'call', i), 'call')[0]['volume']:
            call_strikes.append(o.grabStrike(callprice, strikeIterator, 'call', i))
        elif fillCalls:
            print('calls filled', call_strikes)
            fillCalls = False

        if fillPuts and r.find_options_by_expiration_and_strike(
                    ticker, expir, o.grabStrike(putprice, strikeIterator, 'put', i), 'put')[0]['volume']:
            put_strikes.append(o.grabStrike(putprice, strikeIterator, 'put', i))
        elif fillPuts:
            print('puts filled', put_strikes)
            fillPuts = False
        i += 1
    return call_strikes, put_strikes


def generateValue(ticker, call_strikes, put_strikes, exp):
    """Generates value from strike (premium) * volume. Stores everything in strike_value, returns call_value & put_value

    :return: 2 ints call_value, put_value
    """
    strike_value = {}
    call_value = 0
    put_value = 0
    DTE = cal.DTE(exp)
    for strike in call_strikes:
        if o.pcOptionMin(ticker, strike, 'call', exp):
            value, _ = o.pcOptionMin(ticker, strike, 'call', exp)
            strike_value['[' + str(DTE) + ' DTE] ' + str(strike) + 'C'] = value
            call_value += value
        else:
            print('Something went wrong with: o.pcOptionMin(' + str(ticker), str(strike), 'call', str(exp))
    for strike in put_strikes:
        if o.pcOptionMin(ticker, strike, 'put', exp):
            value, _ = o.pcOptionMin(ticker, strike, 'put', exp)
            strike_value['[' + str(DTE) + ' DTE] ' + str(strike) + 'P'] = value
            put_value += value
        else:
            print('Something went wrong with: o.pcOptionMin(' + str(ticker), str(strike), 'put', str(exp))

    return strike_value, [call_value, put_value, exp]


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
    expRes = expRes[:-2]+")"

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
    monthly1 = str(cal.third_friday(cal.getYear(), cal.getMonth(), cal.getMonthlyDay()))
    monthly2 = str(cal.third_friday(cal.getYear(), cal.getMonth()+1, cal.getMonthlyDay()))
    monthly3 = str(cal.third_friday(cal.getYear(), cal.getMonth()+2, cal.getMonthlyDay()))

    call_strikes1, put_strikes1 = loadStrikes(ticker, monthly1)
    call_strikes2, put_strikes2 = loadStrikes(ticker, monthly2)
    call_strikes3, put_strikes3 = loadStrikes(ticker, monthly3)

    strike_value1, optionValue1 = generateValue(ticker, call_strikes1, put_strikes1, monthly1)
    strike_value2, optionValue2 = generateValue(ticker, call_strikes2, put_strikes2, monthly2)
    strike_value3, optionValue3 = generateValue(ticker, call_strikes3, put_strikes3, monthly3)
    strike_value = {**strike_value1, **strike_value2, **strike_value3}

    call_value = optionValue1[0] + optionValue2[0] + optionValue3[0]
    put_value = optionValue1[1] + optionValue2[1] + optionValue3[1]

    res = dominatingSide(ticker, call_value, put_value, [monthly1, monthly2, monthly3])

    highest = s.checkMostMentioned(strike_value, 5)
    for val in highest:
        cost = a.formatIntForHumans(strike_value.get(val))
        res += str(val) + ' = $' + cost + "\n"
    return res
