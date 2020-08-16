import re
from robinhood import rh
from bot_clock import hour, dayIndex


def grabPercent(curr, prev):
    perc = round(((curr - prev) / prev * 100), 2)
    if perc >= 0:
        perc = '+' + str(perc) + '%'
        return perc
    else:
        perc = str(perc) + '%'
        return perc


def pc(arg1):
    temp = rh.get_quote_list(arg1.upper(), "symbol,last_trade_price")
    temp2 = rh.adjusted_previous_close(arg1.upper())
    prev = round(float((temp2[0])[0]), 2)
    curr = round(float((temp[0])[1]), 2)
    perc1 = grabPercent(curr, prev)
    res = '{:<6}{:^16}{:>12}'.format(arg1.upper() + ':', '$' + str(curr), perc1)
    if dayIndex < 5 and 8 <= hour <= 15:
        return res
    else:
        temp = rh.get_quote_list(arg1.upper(), "symbol,last_extended_hours_trade_price")
        ah = round(float((temp[0])[1]), 2)
        perc2 = grabPercent(ah, curr)
        res = res + '{:>14}{:<25}'.format('    |    AH: $' + str(ah), "    " + perc2)
        return res


def validateTicker(stock):
    if not re.match(r'\b[a-zA-Z]{1,5}\b', stock):
        return False
    else:
        return True
