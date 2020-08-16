import os
from dotenv import load_dotenv
from pyrh import Robinhood

load_dotenv()
rh = Robinhood()
if rh.login(username=os.getenv('USER'), password=os.getenv('PASS')):
    print("Created Robinhood instance.")
else:
    print("Failed to create Robinhood instance.")
