import os  # Standard library
from discord.ext import commands  # 3rd party package
from stocks.misc.stocktwits import trending
from stocks.misc.ark import get_ark_daily, get_ark_holdings


class MiscCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='trend')
    async def stocktwitsTrending(self, ctx):
        await ctx.send("```" + "Stocktwits Trending Stock Tickers" + '\n---------------------------------\n'
                       + trending() + '---------------------------------\n' + "```")

    @commands.command(name='ark')
    async def arkOrders(self, ctx):
        # get_ark_daily()
        await ctx.send("```" + "ARK Orders" + '\n---------------------------------\n'
                       + get_ark_daily() + '\n---------------------------------\n' + "```")

    @commands.command(name='ark_holdings')
    async def arkHoldings(self, ctx):
        # get_ark_daily()
        await ctx.send("```" + "ARK Orders" + '\n---------------------------------\n'
                       + get_ark_holdings() + '\n---------------------------------\n' + "```")





def setup(bot):
    bot.add_cog(MiscCommands(bot))