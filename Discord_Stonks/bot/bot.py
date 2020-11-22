import os  # Standard library

from discord.ext import commands, tasks  # 3rd party packages
from dotenv import load_dotenv
import robin_stocks as r

from Discord_Stonks.stocks import stocks as s
from Discord_Stonks.bot.tasks import Background as bg

bot = commands.Bot(command_prefix='.')
load_dotenv()
rhlogin = r.login(username=os.getenv('USER'), password=os.getenv('PASS'))

initExt = [
    'commands.StockCommands',
    'commands.OptionCommands',
    'commands.BotCommands',
    'tasks.Background'
]


@bot.event
async def on_ready():
    """Prints out start-up statuses to console for operator.

    :return:
    """
    if rhlogin:
        print("Created Robinhood instance.")
    else:
        print("Failed to create Robinhood instance.")
    print('Bot successfully launched!')

if __name__ == '__main__':
    # load in the credentials
    # config = loadFiles()

    # attempt to get the bot stuff
    # client.client_id = config['client_id']

    # Load db
    # loadDatabase()

    #Attempt to load the extensions
    for ext in initExt:
        try:
            bot.load_extension(ext)
        except Exception as e:
            print('Failed to load extension {}\n{}: {}'.format(ext, type(e).__name__, e))

    # cog = bot.get_cog('StockCommands')
    # commands = cog.get_commands()
    # print([c.name for c in commands])

    s.readStocksMentioned()  # Populate stocks_mentioned dictionary with .csv items
    # a.prepare_Anomalies()  # Populate option value for SPY friday option chain
    # bg.background_loop.start()  # Start up background_loop

    # Run the bot
    bot.run(os.getenv('DISCORD_TOKEN'))
