import discord
import os
import re
import time
from rh import rh
from discord.ext import commands
from dotenv import load_dotenv
from datetime import datetime

client = commands.Bot(command_prefix='.')


@client.event
async def on_ready():
    print('Bot is ready')


@client.command(name='p')
async def priceCheck(ctx, arg1):
    if re.match(r'\b[a-zA-Z]{1,4}\b', arg1):
        temp = rh.get_quote_list(arg1.upper(), "symbol,last_trade_price")
        temp2 = rh.adjusted_previous_close(arg1.upper())
        prev_close = temp2[0]
        prev_close = round(float(prev_close[0]), 2)
        data = temp[0]
        data = round(float(data[1]), 2)
        percent = round(((data-prev_close)/prev_close*100), 2)
        await ctx.send(arg1.upper() + ": $" + str(data) + "    " + str(percent) + "%")


load_dotenv()
client.run(os.getenv('TOKEN'))






