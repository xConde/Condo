from Discord_Stonks import option_controller as o, stock_controller as s, bot_calendar as cal, \
    anomaly_option_controller as a

friday_expir = cal.find_friday()


def loadStrikes(ticker):
    """Loads strikes into call_strikes & put_strikes

    :return: 2 lists: call_strikes & put_strikes
    """

    call_strikes = []
    put_strikes = []

    price = s.tickerPrice(ticker)
    strikeIterator = o.grabStrikeIterator(ticker, 'call', friday_expir, price)
    callprice = o.roundPrice(price, strikeIterator, 'call')
    putprice = o.roundPrice(price, strikeIterator, 'put')

    for i in range(0, 10):  # Now that we have the iterator and rounded price, collect actual strikes
        call_strikes.append(o.grabStrike(callprice, strikeIterator, 'call', i))
        put_strikes.append(o.grabStrike(putprice, strikeIterator, 'put', i))
    return call_strikes, put_strikes


def generateValue(ticker, call_strikes, put_strikes, exp):
    """Generates value from strike (premium) * volume. Stores everything in strike_value, returns call_value & put_value

    :return: 2 ints call_value, put_value
    """
    strike_value = {}
    call_value = 0
    put_value = 0

    for strike in call_strikes:
        value = o.pcOptionMin(ticker, strike, 'call', exp)
        strike_value[str(strike) + 'C'] = value
        call_value += value
    for strike in put_strikes:
        value = o.pcOptionMin(ticker, strike, 'put', exp)
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
        exp = friday_expir

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
    exp = o.validateExp(ticker, friday_expir, call_strikes[0], 'call')
    strike_value, res = generateValue(ticker, call_strikes, put_strikes, exp)

    highest = s.checkMostMentioned(strike_value, 5)
    for val in highest:
        cost = a.formatIntForHumans(strike_value.get(val))
        res += str(val) + ' = $' + cost + "\n"
    return res