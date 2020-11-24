import os  # Standard library
from discord.ext import commands, tasks  # 3rd party package
from stocks import stocks as s
from bot import cal as cal
import robin_stocks as r


class Background(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.background_loop.start()

    @tasks.loop(minutes=1)
    async def background_loop(self):
        """Runs on startup and every minute that the bot is running. [Specified in EST, but made in UTC]
        Task 1: If the US market is open (9AM[pre-market] - 8PM[after-hours] and not holiday), print a SPY chart``
         every 15 minutes.
        Task 2: Every 10 minutes (global time) write the stocks mentioned to 'stocks_mentioned.csv'.
        Task 3: If the US market is pre-market (9AM and weekday), but it's a holiday - make an announcement.

        :return:
        """
        await self.bot.wait_until_ready()
        channel = self.bot.get_channel(int(os.getenv('DISCORD_CHANNEL')))
        holidayDate = cal.getHolidays()

        if cal.getDay() < 5 and not self.bot.is_closed() and cal.getCurrentDay() not in holidayDate and \
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
        if cal.getCurrentDay() in holidayDate and cal.getHour() == 14 and cal.getMinute() == 0:
            await channel.send("Today is " + holidayDate[
                cal.getCurrentDay()] + " the market is closed. Enjoy your holiday!")


def setup(bot):
    bot.add_cog(Background(bot))

