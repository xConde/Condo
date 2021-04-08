from discord.ext import commands
from dotenv import load_dotenv


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


def setup(bot):
    bot.add_cog(BotCommands(bot))
