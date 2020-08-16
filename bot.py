import discord
import os
import re
import time
from rh import rh
import pytz
from discord.ext import commands
from dotenv import load_dotenv
import datetime as dt
from datetime import datetime
from datetime import timedelta
from pytz import timezone
import schedule

day = dt.datetime.today().weekday()  # 0-6 index
hour = datetime.now().hour + 1  # datetime.now().hour+1 for central to eastern (fix later)
min = datetime.now().minute
client = commands.Bot(command_prefix='.')


@client.event
async def on_ready():
    print('Bot is ready')


def pc(arg1):
    temp = rh.get_quote_list(arg1.upper(), "symbol,last_trade_price")
    temp2 = rh.adjusted_previous_close(arg1.upper())
    prev_close = temp2[0]
    prev_close = round(float(prev_close[0]), 2)
    data = temp[0]
    data = round(float(data[1]), 2)
    percent = round(((data - prev_close) / prev_close * 100), 2)
    return arg1.upper() + ": $" + str(data) + "    " + str(percent) + "%"


@client.command(name='p')
async def priceCheck(ctx, arg1):
    if re.match(r'\b[a-zA-Z]{1,4}\b', arg1):
        res = pc(arg1)
        await ctx.send(res)


@client.command(name='pp')
async def priceCheckList(ctx, *args):
    res = ""
    for arg in args:
        if re.match(r'\b[a-zA-Z]{1,4}\b', arg):
            pcList = pc(arg)
            res += pcList + '\n'
    await ctx.send(res)


@client.event
async def checkMarket():
    res = pc('SPY')
    print("Checked SPY: " + res + " @ " + str(hour) + ":" + str(min))
    await client.get_all_channels.send(res)

#5
while day < 6:
    # in range(8,3). 15, 8, 15
    if min % 1 == 0 and 8 <= hour <= 24:
        checkMarket(message="SPY")
        time.sleep(60)

load_dotenv()
client.run(os.getenv('TOKEN'))
