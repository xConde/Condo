import os  # Standard library
import psycopg2
from dotenv import load_dotenv

load_dotenv()

conn = None
cursor = None

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

try:
    conn = psycopg2.connect(user=os.getenv('DB_USER'),
                            password=os.getenv('DB_PASS'),
                            host=os.getenv('DB_HOST'),
                            port="5432",
                            database=os.getenv('DB_NAME'))

    cursor = conn.cursor()

    CREATE ROLE valepy WITH LOGIN PASSWORD 'your_password';
    CREATE DATABASE valepy OWNER valepy;
    CREATE EXTENSION pg_trgm;

    create_table_query = '''
    CREATE TABLE watchlist
    (ID INT PRIMARY KEY     NOT NULL,
    DISCORDId           TEXT    NOT NULL,
    PRIC         REAL); '''

    cursor.execute(create_table_query)
    conn.commit()
    print("Table created successfully in PostgreSQL ")
except (Exception, psycopg2.Error) as error:
    print("Error while connecting to PostgreSQL", error)
finally:
    cursor.close()
    conn.close()
    print("PostgreSQL connection is closed")


