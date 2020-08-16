import discord
import os
import re
import time
from rh import rh
from discord.ext import commands
from dotenv import load_dotenv
import datetime as dt
from datetime import datetime


day = dt.datetime.today().weekday()  # 0-6 index
hour = datetime.now().hour + 1  # datetime.now().hour+1 for central to eastern (fix later)
min = datetime.now().minute
if hour < 12:
    AM = True
else:
    AM = False

client = commands.Bot(command_prefix='.')
load_dotenv()


@client.event
async def on_ready():
    print('Bot successfully launched!')


def pc(arg1):
    temp = rh.get_quote_list(arg1.upper(), "symbol,last_trade_price")
    temp2 = rh.adjusted_previous_close(arg1.upper())
    prev_close = temp2[0]
    prev_close = round(float(prev_close[0]), 2)
    data = temp[0]
    data = round(float(data[1]), 2)
    percent = round(((data - prev_close) / prev_close * 100), 2)
    if percent > 0:
        percent = '+' + str(percent) + '%'
    else:
        percent = str(percent) + '%'
    return arg1.upper() + ": $" + str(data) + "    " + percent


def validateTicker(stock):
    if not re.match(r'\b[a-zA-Z]{1,4}\b', stock):
        return False
    else:
        return True


@client.command(name='p')
async def priceCheckList(ctx, *args):
    res = ""
    for arg in args:
        if validateTicker(arg):
            pcList = pc(arg)
            res += pcList + '\n'
        else:
            res += arg.upper() + " is not a valid ticker."
    await ctx.send(res)


# < 5
async def background_loop():
    await client.wait_until_ready()
    print(os.getenv('DISCORD_CHANNEL'))
    channel = client.get_channel(os.getenv('DISCORD_CHANNEL'))
    print(channel)
    while day <= 6 and not client.is_closed():
        # in range(8,3). 15, 8, 15
        if min % 1 == 0 and 8 <= hour <= 24:
            res = pc('SPY')
            print(("Checked " + res + " @ " + str(hour) + ":" + str(min) + "AM" if AM else "PM"))
            await channel.send(res)
            time.sleep(60)


client.loop.create_task(background_loop())
client.run(os.getenv('DISCORD_TOKEN'))

