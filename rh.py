import os
from dotenv import load_dotenv
from pyrh import Robinhood

load_dotenv()
rh = Robinhood()
if rh.login(username=os.getenv('USER'), password=os.getenv('PASS')):
    print("Created Robinhood instance.")
else:
    print("Failed to create Robinhood instance.")

"""
def print_quote(self, stock=""):  # pragma: no cover
    data = self.get_quote_list(stock, "symbol,last_trade_price")
    for item in data:
        quote_str = item[0] + ": $" + item[1]
        return quote_str
"""