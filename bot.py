import discord
import os
from loginRh import rh
from discord.ext import commands
from dotenv import load_dotenv

client = commands.Bot(command_prefix='.')


@client.event
async def on_ready():
    print('Bot is ready')
    rh.print_quote("ESTC")


load_dotenv()
client.run(os.getenv('TOKEN'))



