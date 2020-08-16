import datetime as dt
import os
import re
import time
import holidays
from datetime import datetime

from discord.ext import commands
from dotenv import load_dotenv

from robinhood import rh

dayIndex = dt.datetime.today().weekday()  # 0-6 index
hour = datetime.now().hour + 1  # datetime.now().hour+1 for central to eastern (fix later)
min = datetime.now().minute
currentDay = str(dt.datetime.today().date())[5:7] + '-' + str(dt.datetime.today().date())[8:]

if hour < 12:
    AM = True
else:
    AM = False

holidayDate = {}
for date in holidays.UnitedStates(years=2020).items():
    holidayDate[str(date[0])[5:]] = str(date[1])

client = commands.Bot(command_prefix='.')
load_dotenv()


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
    percent = grabPercent(curr, prev)
    res = '{:<6}{:^16}{:>12}'.format(arg1.upper() + ':', '$'+str(curr), percent)
    return res


def validateTicker(stock):
    if not re.match(r'\b[a-zA-Z]{1,5}\b', stock):
        return False
    else:
        return True


@client.event
async def on_ready():
    print('Bot successfully launched!')


@client.command(name='port')
async def checkPort(ctx):
    if int(ctx.message.author.id) == int(os.getenv('ROBINHOOD_USER_ACCOUNT')):
        data = rh.portfolios()
        curr = round(float(data['extended_hours_portfolio_equity']), 2)
        prev = round(float(data['adjusted_portfolio_equity_previous_close']), 2)
        percentChange = grabPercent(curr, prev)
        await ctx.send("Current Balance: $" + str(curr) + " " + percentChange)
    else:
        await ctx.send("You are not authorized to use this command.")


@client.command(name='p')
async def priceCheckList(ctx, *args):
    res = ""
    for arg in args:
        if validateTicker(arg):
            pcList = pc(arg)
            res += pcList + '\n'
        else:
            res += arg.upper() + " is not a valid ticker.\n"
    await ctx.send(res)


# < 5
async def background_loop():
    await client.wait_until_ready()
    print(os.getenv('DISCORD_CHANNEL'))
    channel = client.get_channel(os.getenv('DISCORD_CHANNEL'))
    print(channel)
    while dayIndex <= 6 and not client.is_closed() and currentDay not in holidayDate:
        # in range(8,3). 15, 8, 15
        if min % 1 == 0 and 8 <= hour <= 24:
            res = pc('SPY')
            print(("Checked " + res + " @ " + str(hour) + ":" + str(min) + "AM" if AM else "PM"))
            await channel.send(res)
            time.sleep(60)
    if currentDay in holidayDate:
        await channel.send("Today is " + holidayDate[currentDay] + " the market is closed. Enjoy your holiday!")
        time.sleep(60 * 60 * 12)  # sleep for 12hrs


# client.loop.create_task(background_loop())
client.run(os.getenv('DISCORD_TOKEN'))