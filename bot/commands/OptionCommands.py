from discord.ext import commands  # 3rd party package
from stocks import stock_controller as s
from stocks.options import option_flow_controller as flow, option_controller as o


class OptionCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='option')
    async def findOptions(self, ctx, stock=None, strike=None, type=None, expir=None):
        """Takes in a stock ticker, strike, an optional type (defaulted to call), and an optional expiration date
         (defaulted to friday expiration [if applicable]),``and prints the information (Strike, price, volume, OI)
         to discord.

        :param strike:
        :param ctx:
        :param stock: {1-5} character stock-ticker.
        :param type: Defaulted to 'call'. Can be either 'call' or 'put'.
        :param expir: Defaulted to 'None'. Represents the expiration date in the format YYYY-MM-DD

        :return:
        """
        if stock and s.validateTicker(stock):
            price = s.tickerPrice(stock)
            if price >= 5:
                res, msg = o.pcOption(stock, strike, type, expir)
                if msg:
                    await ctx.send("```" + msg + '\n' + res + "```")
                else:
                    await ctx.send("```" + res + "```")
            else:
                await ctx.send("```" + stock.upper() + " is not a valid ticker for options.\n" + "```")
        elif stock:
            await ctx.send("```" + stock.upper() + " is not a valid ticker.\n" + "```")
        else:
            res = "Option: Displays stock option information based on ticker, strike, type(call or put), " \
                  "and expiration.\n" + \
                  "Ex:.option[stock], [strike]\n" + \
                  "Ex:.option[stock], [strike], [type]\n" + \
                  "Ex:.option[stock], [strike], [type], [expiration]\n"
            await ctx.send("```" + res + "```")

    @commands.command(name='f')
    async def findOptionChain(self, ctx, stock=None, type=None, expir=None):
        """Takes in a stock ticker, an optional expiration date (defaulted to friday expiration [if applicable]),
        a type (defaulted to call) and prints the information (Strike, price, volume, OI) on 1 ITM strike and 3
        OTM strikes to discord.

        :param ctx:
        :param stock: {1-5} character stock-ticker.
        :param type: Defaulted to 'call'. Can be either 'call' or 'put'.
        :param expir: Defaulted to 'None'. Represents the expiration date in the format YYYY-MM-DD
        :return:
        """
        if stock and s.validateTicker(stock):
            price = s.tickerPrice(stock)
            if price >= 5:
                res = o.pcOptionChain(stock, type, expir, price)
                await ctx.send("```" + res + "```")
            else:
                await ctx.send("```" + stock.upper() + " is not a valid ticker for options.\n" + "```")
        elif stock:
            await ctx.send("```" + stock.upper() + " is not a valid ticker.\n" + "```")
        else:
            res = "Option chain: Displays stock option chain information based on ticker, type (call or put), " \
                  "and expiration.\n" + \
                  "Ex: .f [stock]\n" + \
                  "Ex: .f [stock], [type]\n" + \
                  "Ex: .f [stock], [type], [expiration]\n"
            await ctx.send("```" + res + "```")

    @commands.command(name='read')
    async def readOptionChain(self, ctx, stock=None):
        """Takes a stock ticker as the parameter to parse multiple option chains on multiple generated expirations

        :param ctx:
        :param stock:
        :return:
        """
        if stock and s.validateTicker(stock):
            price = s.tickerPrice(stock)
            if price >= 10:
                junk = await ctx.send("```" + "Loading the option chain for " + str(stock).upper() + "..." + "```")
                try:
                    res = flow.mostExpensive(stock)
                    if res:
                        await ctx.send("```" + res + "```")
                except:
                    await ctx.send("```" + "Failed to load the option chain for " + str(stock).upper() + "\n"
                                            "This may be due to low activity in the option chain, Robinhood API, "
                                            "or other abnormal activity." + "```")
                finally:
                    await junk.delete()
            else:
                await ctx.send("```" + stock.upper() + " is not a valid ticker for options.\n" + "```")
        elif stock:
            await ctx.send("```" + stock.upper() + " is not a valid ticker.\n" + "```")
        else:
            res = "Read Option Info: Displays closest valued options for a ticker with which side is dominating and " \
                  "top 5 most valued strikes.\n" + \
                  "Ex. .read [stock]\n"
            await ctx.send("```" + res + "```")


def setup(bot):
    bot.add_cog(OptionCommands(bot))
