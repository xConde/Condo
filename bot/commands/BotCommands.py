import os  # Standard library
from discord.ext import commands  # 3rd party package
import bot.cal as cal
from stocks import stocks as s

from dotenv import load_dotenv
import robin_stocks as r


class BotCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        load_dotenv()

    @commands.command(name='commands')
    async def discord_commands(self, ctx):
        res = ""
        with open('doc/commands.txt', 'r') as file:
            for line in file:
                res += line
        await ctx.send("```" + res + "```")

    @commands.command(name='port')
    async def checkPort(self, ctx):
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


def setup(bot):
    bot.add_cog(BotCommands(bot))
