import os  # Standard library
from discord.ext import commands, tasks  # 3rd party package
from stocks import stock_controller as s
from stocks.misc.stocktwits import sweepcast
from bot import cal as cal
import robin_stocks as r


class Background(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.background_loop.start(bot)

    @tasks.loop(minutes=1)
    async def background_loop(self, bot):
        """Runs on startup and every minute that the bot is running. [Specified in EST, but made in UTC]
        Task 1: If the US market is open (9AM[pre-market] - 8PM[after-hours] and not holiday), print a SPY chart``
         every 15 minutes.
        Task 2: Every 10 minutes (global time) write the stocks mentioned to 'stocks_mentioned.csv'.
        Task 3: If the US market is pre-market (9AM and weekday), but it's a holiday - make an announcement.

        :return:
        """
        await self.bot.wait_until_ready()
        channel = self.bot.get_channel(int(os.getenv('DISCORD_CHANNEL')))
        altchannel = self.bot.get_channel(int(os.getenv('DISCORD_CHANNEL_ALT')))
        holidayDate = cal.getHolidays()

        if cal.getDay() < 5 and not self.bot.is_closed() and cal.getCurrentDay() not in holidayDate and \
                (12 <= cal.getHour() <= 23):
            if cal.getMinute() % 15 == 0:
                res = s.autoPull()
                await channel.send("```" + res + "```")
            if cal.getMinute() % 5 == 0:
                if not s.validateTicker('SPY'):
                    user = await bot.fetch_user(int(os.getenv('ROBINHOOD_USER_ACCOUNT')))
                    await channel.send(user.mention + " API key expired.")
                    if r.login(username=os.getenv('RH_USER'), password=os.getenv('RH_PASS')):
                        await channel.send("```" + 'Restarted Robinhood instance successfully.' + "```")
                        print("Restarted Robinhood instance successfully.")
                    else:
                        await channel.send(
                            "```" + 'Failed to create Robinhood instance. Bot owner has been sent an SMS.' + "```")
                        print("Failed to create Robinhood instance.")
                s.stocks_mentioned['SPY'] = s.stocks_mentioned.get('SPY', 0) - 1
            if cal.getMinute() % 1 == 0:
                msg, found = sweepcast()
                if found:
                    print('Option whales spotted')
                    await channel.send("```" + msg + "```")
                    await altchannel.send("```" + msg + "```")

        if cal.getMinute() % 10 == 0:
            s.writeStocksMentioned()
        if cal.getCurrentDay() in holidayDate and cal.getHour() == 14 and cal.getMinute() == 0:
            await channel.send("Today is " + holidayDate[
                cal.getCurrentDay()] + " the market is closed. Enjoy your holiday!")


def setup(bot):
    bot.add_cog(Background(bot))

