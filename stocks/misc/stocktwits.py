import requests
from stocks import stock_controller as s
from stocks.options import option_controller as o
from bot import cal as cal

lastTimeStamp = ''


def trending():
    try:
        result = requests.get("https://api.stocktwits.com/api/2/trending/symbols.json")
        if result.status_code == 200:
            res = ''
            found = 0
            for symbol in result.json()["symbols"]:
                stock = symbol["symbol"]
                if stock.find('.') == -1 and found <= 10 and s.validateTicker(stock):
                    pc, _ = s.WLpc(stock)
                    res += pc
                    found += 1
            return res
        else:
            print("Failure to pull Stocktwits trending.")
    except Exception as e:
        print(e)


def sweepcast(base=600000):
    try:
        result = requests.get("https://api.stocktwits.com/api/2/streams/user/SweepCast.json")
        if result.status_code == 200:
            res = "Unusual Options Activity @ " + cal.getEstTimestamp() + '\n---------------------------------\n'
            global lastTimeStamp
            found = 0
            localRecentTimeStamp = ''
            for idx, msg in enumerate(result.json()['messages']):
                timestamp = msg["created_at"].replace("T", " ").replace("Z", "")

                if idx == 0:
                    localRecentTimeStamp = timestamp

                if idx > 30 or timestamp == lastTimeStamp:
                    break

                body = (msg['body'].split('observed: ')[1]).split('|')[0]
                ticker = (body.split('$')[1]).split(' ')[0]
                strike = (body.split('$')[2]).split(' ')[0]
                side = (body.split('$')[2]).split(' ')[1]
                expDate = (body.split('Expiring: ')[1]).split(' ')[0]
                sValue = cal.formatStrForComputers((((body.split('worth ')[1]).split(' ')[0])[:-1]))
                monthsOut = cal.getMonthsOut(expDate)

                adjustedBase = base + base * (.1 * monthsOut)

                if sValue > adjustedBase or ticker == 'BIGC':
                    convertExp = cal.convertDate(expDate)
                    found += 1
                    pc, _ = s.pc(ticker)
                    oPc = o.stPcOption(ticker, strike, side.lower(), convertExp)
                    res += ('--------------------\n' if found > 1 else '') + ticker + ' ' + str(cal.DTE(convertExp)) + 'DTE ' + \
                           cal.formatIntForHumans(sValue) + (' <<<< BULL' if side.lower() == 'call' else ' >>>> BEAR') + '\n' + oPc + pc

            lastTimeStamp = localRecentTimeStamp
            return res, found > 0
    except Exception as e:
        print('Failure to pull SweepCast from Stocktwits.', e)
