import os
import time
import stock_controller as s
from bot_clock import min, hour, dayIndex, currentDay, holidayDate
from discord.ext import commands
from dotenv import load_dotenv
from robinhood import rh

client = commands.Bot(command_prefix='.')
load_dotenv()
channel = client.get_channel(int(os.getenv('DISCORD_CHANNEL')))


@client.command(name='hq')
async def commandBot(ctx, *args):
    res = ""
    for stock in args:
        if s.validateTicker(stock):
            await ctx.send('do something')


@client.command(name='port')
async def checkPort(ctx):
    if int(ctx.message.author.id) == int(os.getenv('ROBINHOOD_USER_ACCOUNT')):
        data = rh.portfolios()
        curr = round(float(data['extended_hours_portfolio_equity']), 2)
        prev = round(float(data['adjusted_portfolio_equity_previous_close']), 2)
        perc = s.grabPercent(curr, prev)
        await ctx.send("Current Balance: $" + str(curr) + " " + perc)
    else:
        await ctx.send("You are not authorized to use this command.")


@client.command(name='p')
async def priceCheckList(ctx, *args):
    res = ""
    for stock in args:
        if s.validateTicker(stock):
            pcList = s.pc(stock)
            res += pcList + '\n'
        else:
            res += stock.upper() + " is not a valid ticker.\n"
    await ctx.send(res)


async def background_loop():
    await client.wait_until_ready()
    while dayIndex < 5 and not client.is_closed() and currentDay not in holidayDate:
        # in range(8,3).
        if min % 15 == 0 and 8 <= hour <= 15:
            res = s.pc('SPY')
            print(("Checked " + res + " @ " + str(hour) + ":" + str(min) + "AM" if AM else "PM"))
            await channel.send("15 Minute SPY pull " + res)
            time.sleep(60)
    if currentDay in holidayDate:
        await channel.send("Today is " + holidayDate[currentDay] + " the market is closed. Enjoy your holiday!")
        time.sleep(60 * 60 * 12)  # sleep for 12hrs


@client.event
async def on_ready():
    print('Bot successfully launched!')


client.loop.create_task(background_loop())
client.run(os.getenv('DISCORD_TOKEN'))
