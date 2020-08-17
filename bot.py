import os
import time
import stock_controller as s
from bot_clock import min, hour, dayIndex, currentDay, holidayDate, AM
from discord.ext import commands
from dotenv import load_dotenv
import robin_stocks as r

client = commands.Bot(command_prefix='.')
load_dotenv()

login = r.login(username=os.getenv('USER'), password=os.getenv('PASS'))

if login:
    print("Created Robinhood instance.")
else:
    print("Failed to create Robinhood instance.")

channel = client.get_channel(int(os.getenv('DISCORD_CHANNEL')))


@client.command(name='f')
async def findOptions(ctx, stock, expir=None, type='call'):
    info = r.find_options_by_expiration(stock, '2020-08-21', type)
    first = info[0]
    price = s.tickerPrice(stock)
    print(str(price))
    print(info)
    print(first)


@client.command(name='port')
async def checkPort(ctx):
    if int(ctx.message.author.id) == int(os.getenv('ROBINHOOD_USER_ACCOUNT')):
        profileData = r.load_portfolio_profile()
        curr = round(float(profileData['extended_hours_equity']), 2)
        prev = round(float(profileData['adjusted_portfolio_equity_previous_close']), 2)
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
