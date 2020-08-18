import robin_stocks as rh
from datetime import datetime
import numpy as np
import tulipy as ti
import sched
import time


s = sched.scheduler(time.time, time.sleep)

# Setup our variables, we haven't entered a trade yet and our RSI period
enteredTrade = False
rsiPeriod = 10


# Initiate our scheduler so we can keep checking every minute for new price changes

def run(sc):
    global enteredTrade
    global rsiPeriod
    print("Getting historical quotes")
    # Get 5 minute bar data for Ford stock
    historical_quotes = rh.get_historical_quotes("BTC", "day", "week")
    closePrices = []
    # format close prices for RSI
    currentIndex = 0
    currentSupport = 0
    currentResistance = 0
    for key in historical_quotes["results"][0]["historicals"]:
        if currentIndex >= len(historical_quotes["results"][0]["historicals"]) - (rsiPeriod + 1):
            if currentIndex >= (rsiPeriod - 1) and datetime.strptime(key['begins_at'],
                                                                     '%Y-%m-%dT%H:%M:%SZ').minute == 0:
                currentSupport = 0
                currentResistance = 0
                print("Resetting support and resistance")
            if float(key['close_price']) < currentSupport or currentSupport == 0:
                currentSupport = float(key['close_price'])
                print("Current Support is: ")
                print(currentSupport)
            if float(key['close_price']) > currentResistance:
                currentResistance = float(key['close_price'])
                print("Current Resistance is: ")
                print(currentResistance)
            closePrices.append(float(key['close_price']))
        currentIndex += 1
    DATA = np.array(closePrices)
    if len(closePrices) > rsiPeriod:
        # Calculate RSI
        rsi = ti.rsi(DATA, period=rsiPeriod)
        instrument = rh.instruments("BTC")[0]
        # If rsi is less than or equal to 30 buy
        if rsi[len(rsi) - 1] <= 30 and float(key['close_price']) <= currentSupport and not enteredTrade:
            print("RSI for " + 'SPY' + " is below 30 for rsi period " + rsiPeriod)
            # await channel.send("RSI is below 30 for rsi period " + rsiPeriod)
            enteredTrade = True
        # Sell when RSI reaches 70
        if rsi[len(rsi) - 1] >= 70 and float(key['close_price']) >= currentResistance > 0 and enteredTrade:
            print("RSI is above 70 for rsi period " + rsiPeriod)
            # await channel.send("RSI is above 70 for rsi period " + rsiPeriod)
            enteredTrade = False
        print(rsi)
    # call this method again every 5 minutes for new price changes
    s.enter(300, 1, run, (sc,))


s.enter(1, 1, run, (s,))
s.run()
