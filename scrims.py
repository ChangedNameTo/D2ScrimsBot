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
    c.execute('CREATE TABLE IF NOT EXISTS Scrims (gameid INTEGER PRIMARY KEY AUTOINCREMENT, playing TEXT, teamsize INTEGER, creator TEXT);')
    c.execute('CREATE TABLE IF NOT EXISTS ScrimPlayers (name TEXT, scrim INTEGER, FOREIGN KEY(scrim) REFERENCES Scrims(gameid));')
    conn.commit()
    print('------')

@bot.command(description='Creates a scrim', help="Takes your name as the host argument, put your time in double quotes. There is no validation.")
async def create(ctx, time, teamsize):
    creator = ctx.author
    c.execute('INSERT INTO Scrims (playing, teamsize, creator) VALUES(?, ?, ?);', (time, int(teamsize), str(creator)))
    nextscrim = c.lastrowid
    c.execute('INSERT INTO ScrimPlayers (name, scrim) VALUES(?, ?);', (str(creator), nextscrim))
    conn.commit()

    # Embed creation
    title = 'New Scrim: ' + str(nextscrim)
    color = 0xFFFFFF
    desc = 'Type `?join <id>` to join this scrim.'
    embed = discord.Embed(title=title, description=desc, color=color)

    # Player Iteration
    c.execute('SELECT name from ScrimPlayers WHERE scrim  = ?;', (int(nextscrim),))
    rows = c.fetchall()
    counter = 1
    players = ""
    for row in rows:
        player = "%d. %s\n" % (counter, row[0])
        players = players + player
        counter = counter + 1

    embed.add_field(name='Time: ', value=time, inline=True)
    embed.add_field(name='Creator: ', value=creator, inline=True)
    embed.add_field(name='Players: ', value=players, inline=False)

    await ctx.send(content=None, embed=embed)

bot.run(token)
