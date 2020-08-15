import os
from dotenv import load_dotenv
from pyrh import Robinhood

load_dotenv()
rh = Robinhood()
rh.login(username=os.getenv('USER'), password=os.getenv('PASS'))
rh.print_quote("AAPL")
rh.get_news("ESTC")