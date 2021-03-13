import requests
from stocks import stock_controller as s


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
