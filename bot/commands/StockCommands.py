from discord.ext import commands  # 3rd party package

from bot import cal
from stocks import stocks as s
import csv  # 3rd Party Packages

wl_csv = "doc/watchlist.csv"


class StockCommands(commands.Cog):
    wl_dict = {}  # Maintains stock ticker as key and times mentioned as value.

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='p')
    async def priceCheck(self, ctx, *args):
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

    @commands.command(name='conde')
    async def printWL(self, ctx):
        res = ""
        wl = ['ESTC', 'NET', 'SPCE', 'TWTR', 'UBER', 'JPM', 'ABBV', 'TXN', 'XOM']
        for i in range(len(wl)):
            pcList, perc = s.pc(wl[i])
            res += pcList
        await ctx.send("```" + res + "```")

    @commands.command(name='wl')
    async def pullWL(self, ctx, *args):
        author = str(ctx.message.author.id)
        initiatedUser = True
        sudoUser = False
        if not self.wl_dict:
            self.loadWatchlist()

        if args and args[0][:2] == '<@':
            if args[0][:3] == '<@!':
                author = args[0][3:-1]
            elif args[0][:2] == '<@':
                author = args[0][2:-1]
            sudoUser = True
            if len(args) > 1:
                await ctx.send(
                    "```" + "Cannot modify other watchlists" + "```")

        if self.wl_dict.get(author) is None and not sudoUser:
            if args:
                if not (args[0]).lower() == 'refresh' or not (args[0]).lower() == 'reset':
                    wl_list = []
                    stockInArgs = False
                    for stock in args:
                        if s.validateTicker(stock) and stock not in wl_list:
                            stockInArgs = True
                            wl_list.append(stock)
                    if stockInArgs:
                        self.wl_dict[author] = wl_list
                        writeWatchlist(self.wl_dict)
                        await ctx.send(
                            "```" + "Watchlist instance successfully created for " + str(ctx.message.author) + "```")
            else:
                initiatedUser = False
                await ctx.send("```" + "To create a personal watchlist use the command \".wl\" followed by stock "
                                       "tickers.\n"
                                       "Example: .wl estc net\n"
                                       "To view other user's watchlists use the command \".wl @user\"\n"
                                       "To remove watchlist use the command \".wl refresh\"" + "```")
        elif not sudoUser:
            if args:
                if (args[0]).lower() == 'refresh' or (args[0]).lower() == 'reset':
                    self.wl_dict.pop(author, None)
                    await ctx.send(
                        "```" + "Watchlist instance successfully removed for " + str(ctx.message.author) + "```")
                else:
                    old_wl_list = []
                    updatedList = False
                    for stock in self.wl_dict[author]:
                        old_wl_list.append(stock)
                    for stock in args:
                        if s.validateTicker(stock):
                            if stock not in old_wl_list:
                                updatedList = True
                                old_wl_list.append(stock)
                    self.wl_dict[author] = old_wl_list
                    if updatedList:
                        writeWatchlist(self.wl_dict)
                        await ctx.send(
                            "```" + "Watchlist instance successfully updated for " + str(ctx.message.author) + "```")
                    else:
                        await ctx.send("```" + "Watchlist had no unique stock tickers to add" + "```")
        if initiatedUser and self.wl_dict.get(author) is not None:
            res = ""
            for stock in self.wl_dict[author]:
                pcList, perc = s.pc(stock)
                res += pcList
            authorName = str(await self.bot.fetch_user(author)).split('#')
            await ctx.send("```" + authorName[0] + "'s Watchlist\n" +
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
                stockList = []
                stockString = row[1:][0]
                word = ""
                for char in stockString:
                    if char == ',' or char == ']':
                        stockList.append(word)
                        word = ""
                    elif char.isalpha():
                        word += char
                self.wl_dict[key] = stockList
            rows += 1


def writeWatchlist(d):
    """Writes [author.id, (list of stock tickers) ['SPY', 'ESTC'] from wl_csv to "watchlist.csv"

    :return:
    """
    w = csv.writer(open(wl_csv, "w"))
    if w:
        print('Wrote wl_csv @' + cal.getEstTimestamp())
        w.writerow(['Author_ID', 'Watchlist'])
        w.writerows(d.items())


def setup(bot):
    bot.add_cog(StockCommands(bot))
