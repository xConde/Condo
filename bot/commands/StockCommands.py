from discord.ext import commands  # 3rd party package

from bot import cal
from stocks import stock_controller as s
import csv  # 3rd Party Packages

wl_csv = "doc/watchlist.csv"


class StockCommands(commands.Cog):
    wl_dict = {}  # Maintains stock ticker as key and times mentioned as value.

    def __init__(self, bot):
        self.bot = bot

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
                            stockWPrice[stock] = s.grabSimplePrice(stock)
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
                        old_wl.append(stock)
                    if args[0].lower() == 'rm' or args[0].lower() == 'remove':
                        for stock in args:
                            if s.validateTicker(stock) and stock in old_wl:
                                updatedList = True
                                stockWPrice.pop(stock)
                    else:
                        for stock in args:
                            if s.validateTicker(stock) and stock not in old_wl:
                                updatedList = True
                                stockWPrice[stock] = s.grabSimplePrice(stock)
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
            stockWPrice = self.wl_dict.get(author)
            for stock in stockWPrice:
                pcList, perc = s.pc(stock)
                stockList[stock] = pcList
                stockPercent[stock] = perc
            highestStock = s.checkMostMentioned(stockPercent, len(self.wl_dict[author]))
            for val in highestStock:
                res += stockList[val]

            authorName = str(await self.bot.fetch_user(author)).split('#')
            await ctx.send("```" + responseRet + '------\n' + authorName[0] + "'s Watchlist\n" +
                           '---------------------------------\n' + res + "```")

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
                                                "Added @ $" + currPrice) + '\n'
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
