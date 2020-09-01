
import csv

from Discord_Stonks import option_controller as o, stock_controller as s, bot_calendar as cal


strike_value = {}   # Maintains SPY strike value (Strike : Cost [volume * premium])
SPY_strike_value_csv = "Discord_Stonks/doc/SPY_strike_value.csv"
call_strikes_SPY = []
put_strikes_SPY = []
expir = cal.find_friday()


def loadStrikes(ticker):
    """Loads strikes into call_strikes & put_strikes

    :return: 2 lists: call_strikes & put_strikes
    """
    call_strikes = []
    put_strikes = []

    price = s.tickerPrice(ticker)
    strikeIterator = o.grabStrikeIterator(ticker, type, expir, price)
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
    """Writes [stock ticker, iterations] from stocks_mentioned to "stocks_mentioned.csv"

    :return:
    """
    w = csv.writer(open(SPY_strike_value_csv, "w"))
    if w:
        print('Wrote SPY_strike_value to .csv ' + timestamp)
    for key, val in strike_value.items():
        w.writerow([key, val])


def readStocksMentioned():
    """Reads "stocks_mentioned.csv" to stocks_mentioned[stock ticker, iterations]

    :return:
    """
    loadStrikes_SPY()
    reader = csv.reader(open(SPY_strike_value_csv))
    if reader:
        print('Loaded SPY_strike_value dictionary from .csv')
    for row in reader:
        if row:
            key = row[0]
            strike_value[key] = int(row[1:][0])


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
    return call_value, put_value


def generateValue_SPY():
    """Generates value from strike (premium) * volume. Stores everything in strike_value, returns call_value & put_value

    :return: 2 ints call_value, put_value
    """
    loadStrikes_SPY()
    call_value = 0
    put_value = 0
    for strike in call_strikes_SPY:
        value = o.pcOptionMin('SPY', strike, 'call', expir)
        strike_value[str(strike)+'C'] = value
        call_value += value
    for strike in put_strikes_SPY:
        value = o.pcOptionMin('SPY', strike, 'put', expir)
        strike_value[str(strike)+'P'] = value
        put_value += value
    return call_value, put_value


def dominatingSide(ticker, call, put, exp=None):
    """Determines dominating side (calls vs puts) and returns result

    :param exp:
    :param call:
    :param put:
    :return:
    """
    if not exp:
        exp = expir

    res = "Valued " + ticker + " " + exp + " options\n"
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
    call_strikes, put_strikes = loadStrikes(ticker)
    exp = o.validateExp(ticker, expir, call_strikes[0], 'call')
    call, put = generateValue(ticker, call_strikes, put_strikes, exp)
    res = dominatingSide(ticker, call, put, exp)
    highest = s.checkMostMentioned(strike_value, 5)
    for val in highest:
        cost = formatIntForHumans(strike_value.get(val))
        res += str(val) + ' = $' + cost + "\n"
    return res


def mostExpensive_SPY():
    """Outputs dominatingSide and highest value strikes (+type)

    :return:
    """
    call, put = generateValue_SPY()
    res = dominatingSide('SPY', call, put)
    highest = s.checkMostMentioned(strike_value, 5)
    for val in highest:
        cost = formatIntForHumans(strike_value.get(val))
        res += str(val) + ' = $' + cost + "\n"
    return res

