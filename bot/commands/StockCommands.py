import os  # Standard library
import websocket
import json
from discord.ext import commands  # 3rd party package

from bot import cal
from stocks import stock_controller as s
import csv  # 3rd Party Packages
from dotenv import load_dotenv
import alpaca_trade_api as tradeapi

wl_csv = "doc/watchlist.csv"


class StockCommands(commands.Cog):
    wl_dict = {}  # Maintains stock ticker as key and times mentioned as value.

    def __init__(self, bot, on_close=None):
        self.bot = bot
        load_dotenv()
        ws = websocket.WebSocketApp(os.getenv('APCA_SOCKET'), on_open=self.on_open, on_message=self.on_message)
        ws.run_forever()
        self.alpaca_api = tradeapi.REST(
            os.getenv('APCA_API_KEY_ID'),
            os.getenv('APCA_API_SECRET_KEY'),
            os.getenv('APCA_API_BASE_URL'),
            'v2')

    def on_open(self, ws):
        auth_data = {
            "action": "authenticate",
            "data": {"key_id": os.getenv('APCA_API_KEY_ID'), "secret_key": os.getenv('APCA_API_SECRET_KEY')}
        }
        ws.send(json.dumps(auth_data))

        listen = {"action": "listen", "data": {"streams": ["Q.BIGC"]}}
        ws.send(json.dumps(listen))

    def on_message(self, ws, msg):
        print(msg)

    @commands.command(name='alpaca')
    async def testalpaca(self, ctx, *args):
        # Get daily price data for AAPL over the last 5 trading days.
        barset = self.alpaca_api.get_barset('AAPL', 'day', limit=5)
        aapl_bars = barset['AAPL']

        # See how much AAPL moved in that timeframe.
        week_open = aapl_bars[0].o
        week_close = aapl_bars[-1].c
        percent_change = (week_close - week_open) / week_open * 100
        print('AAPL moved {}% over the last 5 days'.format(percent_change))

    @commands.command(name='p')
    async def priceCheck(self, ctx, *args):
        """Takes in any amount of arguments for a price check on each ticker.

        :param ctx:
        :param args: (arg1), (arg2), ... (argN) Takes one to multiple stock tickers.
        :return:
        """
        res = ""
        stocksRequested = []
        for stock in args:
            if s.validateTicker(stock) and stock not in stocksRequested:
                stocksRequested.append(stock)
                pcList, perc = s.pc(stock)  # currently not using perc return - maybe in future?
                res += pcList
            elif stock in stocksRequested:
                continue
            else:
                res += stock.upper() + " is not a valid ticker.\n"
        await ctx.send("```" + res + "```")

    @commands.command(name='wl_create')
    async def createWL(self, ctx, *args):
        author = args[0]
        wlKeywords = ['refresh', 'reset', 'rm', 'remove']
        if args and ctx.message.author.id == 247095523197190154:
            if not args[0].lower() in wlKeywords:
                stockWPrice = {}
                stockInArgs = False
                for stock in args:
                    stock = stock[1:-2]
                    print(stock)
                    if s.validateTicker(stock) and stock not in stockWPrice:
                        print(stock)
                        stockInArgs = True
                        stockWPrice[stock] = s.grabSimplePrice(stock)
                if stockInArgs:
                    print(stockWPrice)
                    self.wl_dict[author] = stockWPrice
                    writeWatchlist(self.wl_dict)
                    await ctx.send("```" + "Watchlist instance successfully created\n" + "```")

    @commands.command(name='wl')
    async def pullWL(self, ctx, *args):
        author = str(ctx.message.author.id)
        initiatedUser = True
        sudoUser = False
        wlKeywords = ['refresh', 'reset', 'rm', 'remove']

        if not self.wl_dict:
            self.loadWatchlist()
        responseRet = ""

        if args and args[0][:3] == '<@!':
            sudoUser = True
            author = args[0][3:-1]
        elif args and args[0][:2] == '<@':
            sudoUser = True
            author = args[0][2:-1]

        if self.wl_dict.get(author) is None and not sudoUser:
            if args:
                if not args[0].lower() in wlKeywords:
                    stockWPrice = {}
                    stockInArgs = False
                    for stock in args:
                        if s.validateTicker(stock) and stock not in stockWPrice:
                            stockInArgs = True
                            stockWPrice[stock.upper()] = s.grabSimplePrice(stock)
                    if stockInArgs:
                        self.wl_dict[author] = stockWPrice
                        writeWatchlist(self.wl_dict)
                        responseRet += "Watchlist instance successfully created\n"
            else:
                initiatedUser = False
                await ctx.send("```" + "To create a personal watchlist use the command \".wl\" followed by stock "
                                       "tickers.\n"
                                       "Example: .wl estc net\n"
                                       "To view other user's watchlists use the command \".wl @user\"\n"
                                       "To remove a stock use the command \".wl rm\"\n"
                                       "To remove watchlist use the command \".wl refresh\"\n" + "```")
        elif not sudoUser:
            if args:
                if args[0].lower() == 'refresh' or args[0].lower() == 'reset':
                    self.wl_dict.pop(author, None)
                    await ctx.send(
                        "```" + "Watchlist instance successfully removed for " + str(ctx.message.author) + "```")
                else:
                    stockWPrice = self.wl_dict.get(author)
                    old_wl = []
                    updatedList = False
                    for stock in self.wl_dict[author]:
                        old_wl.append(stock.upper())
                    if args[0].lower() == 'rm' or args[0].lower() == 'remove':
                        for stock in args:
                            if s.validateTicker(stock) and stock.upper() in old_wl:
                                updatedList = True
                                stockWPrice.pop(stock.upper())
                    else:
                        for stock in args:
                            if s.validateTicker(stock) and stock not in old_wl:
                                updatedList = True
                                stockWPrice[stock.upper()] = s.grabSimplePrice(stock)
                    if updatedList:
                        self.wl_dict[author] = stockWPrice
                        writeWatchlist(self.wl_dict)
                        responseRet += "Watchlist instance successfully updated\n"
                    else:
                        responseRet += "Watchlist had no unique stock tickers to add\n"
        if initiatedUser and self.wl_dict.get(author) is not None:
            res = ""
            stockList = {}
            stockPercent = {}
            netPercentDAY = 0
            countDay = 0
            netPercentAH = 0
            countAH = 0
            stockWPrice = self.wl_dict.get(author)
            for stock in stockWPrice:
                pcList, perc = s.WLpc(stock)
                stockList[stock] = pcList
                netPercentDAY += perc[0]
                countDay += 1
                if len(perc) == 1:
                    stockPercent[stock] = perc[0]
                else:
                    stockPercent[stock] = perc[1]
                    netPercentAH += perc[1]
                    countAH += 1

            highestStock = s.checkMostMentioned(stockPercent, len(self.wl_dict[author]))
            for val in highestStock:
                res += stockList[val]

            if countAH > 1:
                totalPercent = '{:<6}{:>15}{:>2}{:>4}{:>15}'.format('NET: ', s.validateUporDown(round(netPercentDAY/countDay, 2)) + '%',
                                                      '|', 'AH: ', s.validateUporDown(round(netPercentAH/countAH, 2)) + '%' )
            else:
                totalPercent = '{:<6}{:>15}'.format('NET: ', s.validateUporDown(round(netPercentDAY/countDay, 2)) + '%')

            authorName = str(await self.bot.fetch_user(author)).split('#')
            await ctx.send("```" + responseRet + '------\n' + authorName[0] + "'s Watchlist\n" +
                           '---------------------------------\n' + res + '---------------------------------\n' +
                           totalPercent + "```")

    @commands.command(name='wl_history')
    async def wl_history(self, ctx, *args):
        """Price change since adding a stock into your watchlist.

        :param: ctx:
        :return:
        """
        if args and args[0][:3] == '<@!':
            author = args[0][3:-1]
        elif args and args[0][:2] == '<@':
            author = args[0][2:-1]
        else:
            author = str(ctx.message.author.id)

        if not self.wl_dict:
            self.loadWatchlist()

        if self.wl_dict.get(author) is not None:
            stockWPrice = self.wl_dict.get(author)
            res = ""
            resPercDict = {}
            for stock in stockWPrice:
                currPrice = s.grabSimplePrice(stock)
                tickerPrice = ""
                for price in stockWPrice[stock]:
                    tickerPrice += price
                percDiff = s.grabPercent(float(currPrice), float(tickerPrice))
                resPercDict[stock.upper()] = float(percDiff[:-1]), '{:<6}{:^8}{:>7}'.format(stock.upper() + ':', percDiff,
                                                "Added @ $" + tickerPrice) + '\n'
            highestStock = s.checkMostMentioned(resPercDict, len(self.wl_dict[author]))
            for val in highestStock:
                res += resPercDict[val][1]

            authorName = str(await self.bot.fetch_user(author)).split('#')
            await ctx.send("```" + authorName[0] + "'s Watchlist History\n" +
                           '---------------------------------\n' + res + "```")

    @commands.command(name='spyup')
    async def top_sp500(self, ctx):
        """Prints out top 5 S&P performers for the day

        :param ctx:
        :return:
        """
        res = s.pull_sp500('up')
        await ctx.send("```" + res + "```")

    @commands.command(name='spydown')
    async def bottom_sp500(self, ctx):
        """Prints out bottom 5 S&P performers for the day

        :param ctx:
        :return:
        """
        res = s.pull_sp500('down')
        await ctx.send("```" + res + "```")

    @commands.command(name='used')
    async def mostUsed(self, ctx):
        """Prints out the top five most used stock tickers from stocks_mentioned to the discord channel.

        :param ctx:
        :return:
        """
        highest = s.checkMostMentioned(s.stocks_mentioned, 5)
        res = "Most mentioned stocks:\n"
        for val in highest:
            res += str(val) + ' = ' + str(s.stocks_mentioned.get(val)) + " \n"
        await ctx.send("```" + res + "```")

    def loadWatchlist(self):
        """Reads "watchlist.csv" to wl[stock ticker, iterations]

        :return:
        """
        reader = csv.reader(open(wl_csv))
        if reader:
            print('Loaded watchlist dictionary from .csv')
        rows = 0
        for row in reader:
            if row and rows != 0:
                key = row[0]
                stockList = {}
                ticker = ""
                stockString = row[1:][0]
                word = ""
                price = ""
                for char in stockString:
                    if char == ':':
                        ticker = word
                        word = ""
                    elif char == ',' or char == '}':
                        stockList[ticker] = price
                        price = ""
                    elif char.isalpha() or (char == '.' and len(word) > 0):
                        word += char
                    elif char.isdigit() or char == '.':
                        price += char
                self.wl_dict[key] = stockList
            rows += 1


def writeWatchlist(d):
    """Writes [author.id, (list of stock tickers) ['SPY', 'ESTC'] from wl_csv to "watchlist.csv"

    :return:
    """
    w = csv.writer(open(wl_csv, "w"))
    if w:
        print('Wrote wl_csv @' + cal.getEstTimestamp())
        w.writerow(['Author_ID', 'Watchlist', 'Price Added'])
        print(d.items())
        w.writerows(d.items())


def setup(bot):
    bot.add_cog(StockCommands(bot))
