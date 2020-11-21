import os  # Standard library

from discord.ext import commands, tasks  # 3rd party packages
from dotenv import load_dotenv
import robin_stocks as r

from Discord_Stonks import option_controller as o, stock_controller as s, BotCalendar as cal, option_daily_flow as flow

client = commands.Bot(command_prefix='.')
load_dotenv()
rhlogin = r.login(username=os.getenv('USER'), password=os.getenv('PASS'))


@client.command(name='read')
async def readFridayOptionChain(ctx, stock):
    if s.validateTicker(stock):
        price = s.tickerPrice(stock)
        if price >= 5:
            res = flow.mostExpensive(stock)
            await ctx.send("```" + res + "```")
        else:
            await ctx.send("```" + stock.upper() + " is not a valid ticker for options.\n" + "```")
    else:
        await ctx.send("```" + stock.upper() + " is not a valid ticker.\n" + "```")


@client.command(name='commands')
async def commands(ctx):
    res = ""
    with open('Discord_Stonks/doc/commands.txt', 'r') as file:
        for line in file:
            res += line
    await ctx.send("```" + res + "```")


@client.command(name='spyup')
async def top_sp500(ctx):
    """Prints out top 5 S&P performers for the day

    :param ctx:
    :return:
    """
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
    res = "Most mentioned stocks:\n"
    for val in highest:
        res += str(val) + ' = ' + str(s.stocks_mentioned.get(val)) + " \n"
    await ctx.send("```" + res + "```")


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
        price = s.tickerPrice(stock)
        if price >= 5:
            res = o.pcOptionChain(stock, type, expir, price)
            await ctx.send("```" + res + "```")
        else:
            await ctx.send("```" + stock.upper() + " is not a valid ticker for options.\n" + "```")
    else:
        await ctx.send("```" + stock.upper() + " is not a valid ticker.\n" + "```")


@client.command(name='wl')
async def pullWL(ctx, *args):
    res = "Discord user token: " + str(ctx.message.author.id) + "\n"
    # if str(ctx.message.author.id)
    for stock in args:
        if s.validateTicker(stock):
            res += stock  # currently not using perc return - maybe in future?
    await ctx.send("```" + res + "```")


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
    if s.validateTicker(stock):
        price = s.tickerPrice(stock)
        if price >= 5:
            res, msg = o.pcOption(stock, strike, type, expir)
            if msg:
                await ctx.send("```" + msg + '\n' + res + "```")
            else:
                await ctx.send("```" + res + "```")
        else:
            await ctx.send("```" + stock.upper() + " is not a valid ticker for options.\n" + "```")
    else:
        await ctx.send("```" + stock.upper() + " is not a valid ticker.\n" + "```")


@client.command(name='port')
async def checkPort(ctx):
    """Prints out the Robinhood owner's account information: balance, buying power, and open positions (shares & options)``
    . Will only allow the provided discord user id (Robinhood account owner) to use command.

    **WORK IN PROGRESS - [currently not available] need to print user's open positions.
    :param ctx:
    :return:
    """
    if int(ctx.message.author.id) == int(os.getenv('ROBINHOOD_USER_ACCOUNT')):
        profileData = r.load_portfolio_profile()
        option_positions = {}
        option_info = {}
        prev = round(float(profileData['adjusted_portfolio_equity_previous_close']), 2)
        bp = round(float(profileData['excess_margin']), 2)

        if cal.getDay() < 5 and 13 <= cal.getHour() <= 24:
            if cal.getHour() != 13 or (cal.getHour() == 13 and cal.getMinute() >= 30):
                curr = round(float(profileData['last_core_portfolio_equity']), 2)
            else:
                curr = round(float(profileData['extended_hours_equity']), 2)
        perc = s.grabPercent(curr, prev)
        diff = round(curr - prev, 2)
        diff = s.validateUporDown(diff)
        balance = '{:<10}{:^12}{:>7}{:>12}'.format("Current Balance:", '$' + str(curr), diff, perc + '\n')
        buyingPower = "Buying power: $" + str(bp)
        await ctx.send(balance + buyingPower)
    else:
        await ctx.send("You are not authorized to use this command.")


@client.command(name='conde')
async def printWL(ctx):
    res = ""
    wl = ['ESTC', 'NET', 'SPCE', 'TWTR', 'UBER', 'JPM', 'ABBV', 'TXN', 'XOM']
    for i in range(len(wl)):
        pcList, perc = s.pc(wl[i])
        res += pcList
    await ctx.send("```" + res + "```")


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
6

# async def grabMessage(message):
#     channel = client.get_channel(int(os.getenv(str(message.channel).upper())))
#     index = 1
#     async for message in channel.history():
#         if index == 2:
#             await channel.send(message.content)
#             break
#         index += 1
#
#
# @client.event
# async def on_message(message):
#     if (str(message.author) == "StockBot#3314" and message.content[:19] == "The requested chart" or message.content[:5] == "```Hi") or \
#             str(message.author) == "OptionsFamBot#9520" and message.content[:28] == "This command is on cooldown.":
#         await grabMessage(message)


@tasks.loop(minutes=1)
async def background_loop():
    """Runs on startup and every minute that the bot is running. [Specified in EST, but made in UTC]
    Task 1: If the US market is open (9AM[pre-market] - 8PM[after-hours] and not holiday), print a SPY chart``
     every 15 minutes.
    Task 2: Every 10 minutes (global time) write the stocks mentioned to 'stocks_mentioned.csv'.
    Task 3: If the US market is pre-market (9AM and weekday), but it's a holiday - make an announcement.

    :return:
    """
    await client.wait_until_ready()
    channel = client.get_channel(int(os.getenv('DISCORD_CHANNEL')))
    holidayDate = cal.getHolidays()

    if cal.getDay() < 5 and not client.is_closed() and cal.getCurrentDay() not in holidayDate and \
            (13 <= cal.getHour() <= 24):
        """if min % 15 == 0 and (13 <= hour <= 24):
            res = a.checkAnomalies(timestamp, daystamp)
            if res:
                await channel.send("```" + res + "```")"""
        if cal.getMinute() % 15 == 0:
            res = s.autoPull()
            await channel.send("```" + res + "```")
        if cal.getMinute() % 5 == 0:
            if not s.validateTicker('SPY'):
                if r.login(username=os.getenv('USER'), password=os.getenv('PASS')):
                    await channel.send("```" + 'Restarted Robinhood instance successfully.' + "```")
                    print("Restarted Robinhood instance successfully.")
                else:
                    await channel.send(
                        "```" + 'Failed to create Robinhood instance. Bot owner has been sent an SMS.' + "```")
                    print("Failed to create Robinhood instance.")
            s.stocks_mentioned['SPY'] = s.stocks_mentioned.get('SPY', 0) - 1
    if cal.getMinute() % 10 == 0:
        s.writeStocksMentioned()
    if cal.getCurrentDay() in holidayDate and cal.getHour() == 9 and cal.getMinute() == 0:
        await channel.send("Today is " + holidayDate[cal.getCurrentDay()] + " the market is closed. Enjoy your holiday!")


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
# a.prepare_Anomalies()  # Populate option value for SPY friday option chain
background_loop.start()  # Start up background_loop
client.run(os.getenv('DISCORD_TOKEN'))  # Start up discord bot
