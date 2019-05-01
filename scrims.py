import sqlite3
import discord

from discord.ext import commands
from secrets import *

conn = sqlite3.connect("scrims.db")
c    = conn.cursor()

description = 'A bot for the creation of D2 scrims'
bot = commands.Bot(command_prefix='?', description=description)

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    c.execute('CREATE TABLE IF NOT EXISTS Scrims (gameid INTEGER PRIMARY KEY, playing TEXT, teamsize INTEGER);')
    c.execute('CREATE TABLE IF NOT EXISTS ScrimPlayers (name TEXT, scrim INTEGER, FOREIGN KEY(scrim) REFERENCES Scrims(gameid));')
    conn.commit()
    print('------')

@bot.command(description='Creates a scrim')
async def create(ctx, *choices: str):
    await ctx.send()

bot.run(token)
