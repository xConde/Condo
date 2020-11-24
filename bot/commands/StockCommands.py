from discord.ext import commands  # 3rd party package

from bot import cal
from stocks import stocks as s
import csv  # 3rd Party Packages


wl_dict = {}  # Maintains stock ticker as key and times mentioned as value.
wl_csv = "doc/watchlist.csv"


class StockCommands(commands.Cog):
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
        # res = "Discord user token: " + str(ctx.message.author.id) + "\n"
        author = ctx.message.author.id

        if author not in wl_dict:
            wl_dict[author] = author
            if args:
                wl_list = []
                for stock in args:
                    if s.validateTicker(stock):
                        wl_list.append(stock)
                wl_dict[author] = wl_list
        else:
            if args:
                old_wl_list = []
                for stock in wl_dict[author]:
                    old_wl_list.append(stock)
                for stock in args:
                    if s.validateTicker(stock):
                        if stock not in old_wl_list:
                            old_wl_list.append(stock)
                wl_dict[author] = old_wl_list

        res = ""
        for stock in wl_dict[author]:
            pcList, perc = s.pc(stock)
            res += pcList
        await ctx.send("```" + res + "```")

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


def loadWatchlist():
    """Reads "watchlist.csv" to wl[stock ticker, iterations]

    :return:
    """
    reader = csv.reader(open(wl_csv))
    if reader:
        print('Loaded watchlist dictionary from .csv')
    for row in reader:
        if row:
            key = row[0]
            wl_dict[key] = int(row[1:][0])


def writeWatchlist():
    """Writes [author.id, (list of stock tickers) ['SPY', 'ESTC']] from wl_csv to "watchlist.csv"

    :return:
    """
    w = csv.writer(open(wl_csv, "w"))
    if w:
        print('Wrote stocks_mentioned to .csv @' + cal.getEstTimestamp())
    for key, val in wl_dict.items():
        w.writerow([key, val])


def setup(bot):
    bot.add_cog(StockCommands(bot))
