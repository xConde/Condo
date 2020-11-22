from discord.ext import commands  # 3rd party package
from stocks import stocks as s


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
        res = "Discord user token: " + str(ctx.message.author.id) + "\n"
        # if str(ctx.message.author.id)
        for stock in args:
            if s.validateTicker(stock):
                res += stock  # currently not using perc return - maybe in future?
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


def setup(bot):
    bot.add_cog(StockCommands(bot))
