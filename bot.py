import os  # Standard library

from discord.ext import commands  # 3rd party packages
from dotenv import load_dotenv
import robin_stocks as r

from stocks import stocks as s
from bot.commands import StockCommands as sc

bot = commands.Bot(command_prefix='.')
load_dotenv()
rhlogin = r.login(username=os.getenv('USER'), password=os.getenv('PASS'))

initExt = [
    'bot.commands.StockCommands',
    'bot.commands.OptionCommands',
    'bot.commands.BotCommands',
    'bot.tasks.Background',
]

"""
Watchlist for users up to 10-15 stock_tickers. Unique ID for user_id to guild_id.
> TODO: Add a column to the .wl to show price gain/loss since added.

id                  PRIMARY_KEY
user_id             character varying   NOT NULL
guild_id            character varying   NOT NULL
stock_ticker        character varying   NULL
price_since_added   character varying   NULL



> User attempts to use command .wl with a proper user_id, guild_id, no list, but *args.
    * User validated
    * Action: parse through *args for valid stock tickers.
    * Action: add (stock ticker & price_since_added) for all valid stock tickers.
    * Action: print watchlist.

> User attempts to use command .wl with a proper user_id, guild_id, list, but no *args.
    * User validated
    * Action: print watchlist.

> User attempts to use command .wl with a proper user_id, but no list or *args - possibly has another list in another server.
    * User validated.
    * "No list found for {user}. Feel free to initiate a watchlist by adding tickers after the command."

> User attempts to use command .wl with a proper user_id & guild_id, but no list and no *args.
    * User validated.
    * "No list found for {user}. Feel free to initiate a watchlist by adding tickers after the command."

> User attempts to use command .wl with a proper user_id & guild_id & list, but has *args after the command.
    * User validated.
    * Action: parse through *args for valid stock tickers. 
    * Action: delete duplicate (stock ticker & price_since_added) from DB.
    * Action: add (stock ticker & price_since_added) for all valid stock tickers.
    * Action: print watchlist.

"""

if __name__ == '__main__':
    for ext in initExt:
        try:
            bot.load_extension(ext)
        except Exception as e:
            print('Failed to load extension {}\n{}: {}'.format(ext, type(e).__name__, e))

    s.readStocksMentioned()  # Populate stocks_mentioned dictionary with .csv items
    sc.loadWatchlist()       # Populate wl_dict dictionary with .csv items
    # a.prepare_Anomalies()  # Populate option value for SPY friday option chain

    bot.run(os.getenv('DISCORD_TOKEN'))
