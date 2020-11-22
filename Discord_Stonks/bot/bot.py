import os  # Standard library

from discord.ext import commands, tasks  # 3rd party packages
from dotenv import load_dotenv
import robin_stocks as r

from Discord_Stonks.stocks import stocks as s

bot = commands.Bot(command_prefix='.')
load_dotenv()
rhlogin = r.login(username=os.getenv('USER'), password=os.getenv('PASS'))

initExt = [
    'commands.StockCommands',
    'commands.OptionCommands',
    'commands.BotCommands',
    'tasks.Background',
]


if __name__ == '__main__':
    # load in the credentials
    # config = loadFiles()

    # attempt to get the bot stuff
    # client.client_id = config['client_id']

    # loadDatabase()

    for ext in initExt:
        try:
            bot.load_extension(ext)
        except Exception as e:
            print('Failed to load extension {}\n{}: {}'.format(ext, type(e).__name__, e))

    s.readStocksMentioned()  # Populate stocks_mentioned dictionary with .csv items
    # a.prepare_Anomalies()  # Populate option value for SPY friday option chain

    bot.run(os.getenv('DISCORD_TOKEN'))
