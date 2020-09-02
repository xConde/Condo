
import csv
import datetime as dt

from Discord_Stonks import option_controller as o, stock_controller as s, bot_calendar as cal


strike_value_SPY = {}   # Maintains SPY strike value (Strike : Cost [volume * premium])
SPY_strike_value_csv = "Discord_Stonks/doc/SPY_strike_value.csv"
call_strikes_SPY = []
put_strikes_SPY = []

now = dt.datetime.now()
friday_expir = cal.find_friday()
monthly_expir = cal.third_friday(now.year, now.month, now.day).strftime("%Y-%m-%d")


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


def loadStrikes_SPY():
    """Loads strikes into call_strikes & put_strikes for SPY

    :return:
    """
    price = s.tickerPrice('SPY')
    callprice = o.roundPrice(price, 1, 'call')
    putprice = o.roundPrice(price, 1, 'put')

    for i in range(0, 15):  # Now that we have the iterator and rounded price, collect actual strikes
        call_strikes_SPY.append(o.grabStrike(callprice, 1, 'call', i))
        put_strikes_SPY.append(o.grabStrike(putprice, 1, 'put', i))


def writeStocksMentioned(timestamp):
    """Writes [strike, value] from strike_value_SPY to "SPY_strike_value.csv"

    :return:
    """
    w = csv.writer(open(SPY_strike_value_csv, "w"))
    if w:
        print('Wrote SPY_strike_value to .csv ' + timestamp)
    for key, val in strike_value_SPY.items():
        w.writerow([key, val])


def readStocksMentioned():
    """Reads "SPY_strike_value.csv" to strike_value_SPY[strike, value]

    :return:
    """
    loadStrikes_SPY()
    reader = csv.reader(open(SPY_strike_value_csv))
    if reader:
        print('Loaded SPY_strike_value dictionary from .csv')
    for row in reader:
        if row:
            key = row[0]
            strike_value_SPY[key] = int(row[1:][0])


def formatIntForHumans(num):
    """Formats integer into a readable string format

    :param num:
    :return:
    """
    num = float('{:.3g}'.format(num))
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    return '{}{}'.format('{:f}'.format(num).rstrip('0').rstrip('.'), ['', 'K', 'M', 'B', 'T'][magnitude])


def generateValue(ticker, call_strikes, put_strikes, exp):
    """Generates value from strike (premium) * volume. Stores everything in strike_value, returns call_value & put_value

    :return: 2 ints call_value, put_value
    """
    strike_value = {}
    call_value = 0
    put_value = 0

    for strike in call_strikes:
        value = o.pcOptionMin(ticker, strike, 'call', exp)
        strike_value[str(strike)+'C'] = value
        call_value += value
    for strike in put_strikes:
        value = o.pcOptionMin(ticker, strike, 'put', exp)
        strike_value[str(strike)+'P'] = value
        put_value += value
    res = dominatingSide(ticker, call_value, put_value, exp)
    return strike_value, res


def checkDiff(anomaly, value, strike, type, expir, DTE):
    """Checks difference in the last recorded price and reports if the difference is greater than highestDiff for
    DTE

    :param anomaly:
    :param value:
    :param strike:
    :param type:
    :param DTE:
    :return: anomaly (empty or populated)
    """
    if DTE < 7:
        highestDiff = 450000
    else:
        highestDiff = 525000
    prev_value = strike_value_SPY.get(expir + ' ' + str(strike) + type)
    diff = int(value - prev_value)
    if diff > highestDiff:
        anomaly[str(DTE) + ' ' + str(strike) + type] = diff
    return anomaly


def generateValue_SPY(strike, type, expir, anomaly):
    """Generates value from strike (premium) * volume. Stores everything in strike_value_SPY, returns anomaly.

    :param strike:
    :param type:
    :param expir:
    :param anomaly:
    :return: anomaly (empty or populated)
    """
    DTE = cal.DTE(expir)
    typeAbv = type[0].upper()
    value = o.pcOptionMin('SPY', strike, type, expir)
    if strike_value_SPY.get(expir + ' ' + str(strike) + typeAbv):
        anomaly = checkDiff(anomaly, value, strike, typeAbv, expir, DTE)
    strike_value_SPY[expir + ' ' + str(strike) + typeAbv] = int(value)
    return anomaly


def generate_SPY():
    """calls generateValue_SPY for every strike and expiration and seeks anomalies. Returns anomaly

    :return: extraneous cash flows
    """
    anomaly = {}

    for strike in call_strikes_SPY:
        anomaly = generateValue_SPY(strike, 'call', friday_expir, anomaly)
        anomaly = generateValue_SPY(strike, 'call', monthly_expir, anomaly)
    for strike in put_strikes_SPY:
        anomaly = generateValue_SPY(strike, 'put', friday_expir, anomaly)
        anomaly = generateValue_SPY(strike, 'put', monthly_expir, anomaly)
    return anomaly


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
    call_abv = formatIntForHumans(call)
    put_abv = formatIntForHumans(put)
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
        cost = formatIntForHumans(strike_value.get(val))
        res += str(val) + ' = $' + cost + "\n"
    return res


def checkAnomalies(timestamp):
    """Called every 3m to check records against current option values. Reports any anomalies found.

    :param timestamp:
    :return:
    """
    anomaly = generate_SPY()
    writeStocksMentioned(timestamp)

    if anomaly:
        print("Found anomalies " + timestamp)
        res = "Found large cash movement in past 3 min:\n"
        for val in anomaly:
            cost = formatIntForHumans(anomaly.get(val))
            res += str(val) + ' = +$' + cost + "\n"
        return res

