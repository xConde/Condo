import os
import time
import stock_controller as s
from bot_clock import min, hour, dayIndex, currentDay, holidayDate, AM
from discord.ext import commands, tasks
from dotenv import load_dotenv
import robin_stocks as r
from itertools import cycle

client = commands.Bot(command_prefix='.')
load_dotenv()
rhlogin = r.login(username=os.getenv('USER'), password=os.getenv('PASS'))


@client.command(name='used')
async def mostUsed(ctx):
    highest = s.checkMostMentioned()
    res = ""
    await ctx.send("Most mentioned stock tickers since startup: ")
    for val in highest:
        res += str(val) + ' = ' + str(s.stocks_mentioned.get(val)) + " \n"
    await ctx.send(res)


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
        positionData = r.get_all_open_option_orders()
        option_positions = {}
        option_info = {}
        print(positionData)
        for option in positionData:
            option_positions[option['chain_symbol']] = option['quantity']
            option_info[option['chain_symbol']] = option['price']

        res = ''
        for val in option_positions:
            res += '[' + str(int(float(option_positions.get(val)))) + '] ' + str(val) + ' ' + str(
                round(float(option_info.get(val)), 2)) + '\n'

        prev = round(float(profileData['adjusted_portfolio_equity_previous_close']), 2)
        bp = round(float(profileData['excess_margin']), 2)

        if dayIndex < 5 and 9 <= hour <= 16:
            if hour != 9 or (hour == 9 and min >= 30):
                curr = round(float(profileData['last_core_portfolio_equity']), 2)
            else:
                curr = round(float(profileData['extended_hours_equity']), 2)
        perc = s.grabPercent(curr, prev)
        diff = round(curr - prev, 2)
        diff = s.validateUporDown(diff)
        balance = '{:<10}{:^12}{:>7}{:>12}'.format("Current Balance:", '$' + str(curr), diff, perc + '\n')
        buyingPower = "Buying power: $" + str(bp)
        await ctx.send(balance + buyingPower)
        await ctx.send("Option positions: \n" + res)
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

    await ctx.send("```" + res + "```")


@tasks.loop(minutes=1)
async def background_loop():
    await client.wait_until_ready()
    channel = client.get_channel(int(os.getenv('DISCORD_CHANNEL')))
    if dayIndex < 5 and not client.is_closed() and currentDay not in holidayDate and 9 <= hour < 20 \
            and min % 15 == 0:
        res = s.pc('SPY')
        print(("Checked " + res + " @ " + str(hour) + ":" + str(min)) + ("AM" if AM else "PM"))
        await channel.send("[15m] " + res)
    if currentDay in holidayDate and hour == 9 and min:
        await channel.send("Today is " + holidayDate[currentDay] + " the market is closed. Enjoy your holiday!")


@client.event
async def on_ready():
    if rhlogin:
        print("Created Robinhood instance.")
    else:
        print("Failed to create Robinhood instance.")
    print('Bot successfully launched!')

background_loop.start()
client.run(os.getenv('DISCORD_TOKEN'))
