import os  # Standard library

from discord.ext import commands, tasks  # 3rd party packages
from dotenv import load_dotenv
import robin_stocks as r
import datetime as dt
import holidays
from datetime import datetime

import stock_controller as s  # local source
import option_controller as o

client = commands.Bot(command_prefix='.')
load_dotenv()
rhlogin = r.login(username=os.getenv('USER'), password=os.getenv('PASS'))

holidayDate = {}
for date in holidays.UnitedStates(years=2020).items():
    holidayDate[str(date[0])[5:]] = str(date[1])


@client.command(name='commands')
async def commands(ctx):
    res = s.getCommands()
    await ctx.send("```" + res + "```")


@client.command(name='spyup')
async def top_sp500(ctx):
    """Prints out top 5 S&P performers for the day

    :param ctx:
    :return:
    """
    curr = 358.79
    prev = 358.79

    res = s.pull_sp500('up')
    await ctx.send("```" + res + "```")


@client.command(name='spydown')
async def bottom_sp500(ctx):
    """Prints out bottom 5 S&P performers for the day

    :param ctx:
    :return:
    """
    res = s.pull_sp500('down')
    await ctx.send("```" + res + "```")


@client.command(name='used')
async def mostUsed(ctx):
    """Prints out the top five most used stock tickers from stocks_mentioned to the discord channel.

    :param ctx:
    :return:
    """
    highest = s.checkMostMentioned(s.stocks_mentioned, 5)
    res = ""
    await ctx.send("Most mentioned stocks: ")
    for val in highest:
        res += str(val) + ' = ' + str(s.stocks_mentioned.get(val)) + " \n"
    await ctx.send(res)


@client.command(name='f')
async def findOptionChain(ctx, stock, type=None, expir=None):
    """Takes in a stock ticker, an optional expiration date (defaulted to friday expiration [if applicable]),``
     a type (defaulted to call) and prints the information (Strike, price, volume, OI) on 1 ITM strike and 3 OTM strikes``
     to discord.

    :param ctx:
    :param stock: {1-5} character stock-ticker.
    :param type: Defaulted to 'call'. Can be either 'call' or 'put'.
    :param expir: Defaulted to 'None'. Represents the expiration date in the format YYYY-MM-DD
    :return:
    """
    if s.validateTicker(stock):
        res = o.pcOptionChain(stock, type, expir)
        await ctx.send("```" + res + "```")
    else:
        await ctx.send("```" + stock.upper() + " is not a valid ticker.\n" + "```")


@client.command(name='option')
async def findOptions(ctx, stock, strike, type=None, expir=None):
    """Takes in a stock ticker, strike, an optional expiration date (defaulted to friday expiration [if applicable]),``
     a type (defaulted to call) and prints the information (Strike, price, volume, OI) to discord.

    :param ctx:
    :param stock: {1-5} character stock-ticker.
    :param type: Defaulted to 'call'. Can be either 'call' or 'put'.
    :param expir: Defaulted to 'None'. Represents the expiration date in the format YYYY-MM-DD

    :return:
    """
    res, msg = o.pcOption(stock, strike, type, expir)
    if msg:
        await ctx.send("```" + msg + "```")
    await ctx.send("```" + res + "```")


@client.command(name='port')
async def checkPort(ctx):
    """Prints out the Robinhood owner's account information: balance, buying power, and open positions (shares & options)``
    . Will only allow the provided discord user id (Robinhood account owner) to use command.

    **WORK IN PROGRESS - [currently not available] need to print user's open positions.
    :param ctx:
    :return:
    """
    if int(ctx.message.author.id) == int(os.getenv('ROBINHOOD_USER_ACCOUNT')):
        dayIndex = dt.datetime.today().weekday()  # 0-6 index
        hour = datetime.now().hour + 1  # datetime.now().hour+1 for central to eastern (fix later)
        min = datetime.now().minute
        profileData = r.load_portfolio_profile()
        # positionData = r.get_all_open_option_orders()
        option_positions = {}
        option_info = {}
        # print(positionData)
        """for option in positionData:
            option_positions[option['chain_symbol']] = option['quantity']
            option_info[option['chain_symbol']] = option['price']

        res = ''
        for val in option_positions:
            res += '[' + str(int(float(option_positions.get(val)))) + '] ' + str(val) + ' ' + str(
                round(float(option_info.get(val)), 2)) + '\n'"""

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
        # await ctx.send("Option positions: \n" + res)
    else:
        await ctx.send("You are not authorized to use this command.")


@client.command(name='p')
async def priceCheck(ctx, *args):
    """Prints the price for stock tickers provided to discord.

    :param ctx:
    :param args: (arg1), (arg2), ... (argN) Takes one to multiple stock tickers.
    :return:
    """
    res = ""
    for stock in args:
        if s.validateTicker(stock):
            pcList, perc = s.pc(stock)  # currently not using perc return - maybe in future?
            res += pcList
        else:
            res += stock.upper() + " is not a valid ticker.\n"
    await ctx.send("```" + res + "```")


@tasks.loop(minutes=1)
async def background_loop():
    """Runs on startup and every minute that the bot is running.
    Task 1: If the US market is open (9AM[pre-market] - 8PM[after-hours] and not holiday), print a SPY chart``
     every 15 minutes.
    Task 2: Every 10 minutes (global time) write the stocks mentioned to 'stocks_mentioned.csv'.
    Task 3: If the US market is pre-market (9AM and weekday), but it's a holiday - make an announcement.

    :return:
    """
    await client.wait_until_ready()
    channel = client.get_channel(int(os.getenv('DISCORD_CHANNEL')))

    dayIndex = dt.datetime.today().weekday()  # 0-6 index
    currentDay = str(dt.datetime.today().date())[5:7] + '-' + str(dt.datetime.today().date())[8:]
    hour = datetime.now().hour + 1  # datetime.now().hour+1 for central to eastern (fix later)
    min = datetime.now().minute
    timestamp = " @ " + str(hour) + ":" + str(min) + ("AM" if (hour < 12) else "PM")

    if dayIndex < 5 and not client.is_closed() and currentDay not in holidayDate and (8 <= hour < 20) \
            and min % 15 == 0:
        res = s.autoPull(timestamp, hour, min)
        await channel.send("```" + res + "```")

    if min % 10 == 0:
        s.writeStocksMentioned(timestamp)
    if currentDay in holidayDate and hour == 8 and min == 0:
        await channel.send("Today is " + holidayDate[currentDay] + " the market is closed. Enjoy your holiday!")


@client.event
async def on_ready():
    """Prints out start-up statuses to console for operator.

    :return:
    """
    if rhlogin:
        print("Created Robinhood instance.")
    else:
        print("Failed to create Robinhood instance.")
    print('Bot successfully launched!')


s.readStocksMentioned()  # Populate stocks_mentioned dictionary with .csv items
background_loop.start()  # Start up background_loop
client.run(os.getenv('DISCORD_TOKEN'))  # Start up discord bot
