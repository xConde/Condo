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
        data = temp[0]
        await ctx.send(arg1.upper() + ": $" + str(round(float(data[1]), 2)))


load_dotenv()
client.run(os.getenv('TOKEN'))






