import sqlite3
import discord
import json
import requests
import sys
import traceback
import random
import time

sys.path.append('util/')

from discord.ext import commands
from secrets import *
from util import *
from datetime import datetime

from string_to_datetime import string_to_datetime
from string_to_date import string_to_date

conn     = sqlite3.connect("scrims.db")
c        = conn.cursor()
base_url = 'https://www.bungie.net/Platform'

description = 'A bot for the creation of D2 scrims'
bot         = commands.Bot(command_prefix='?', description=description)

@bot.event
async def on_ready():
    c.execute('''CREATE TABLE IF NOT EXISTS Scrims
            (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                time DATETIME,
                team_size INTEGER,
                creator INTEGER,
                FOREIGN KEY(creator) REFERENCES Players(id)
            );''')
    c.execute('''CREATE TABLE IF NOT EXISTS ScrimPlayers
            (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_id INTEGER,
                scrim_id INTEGER,
                FOREIGN KEY(scrim_id) REFERENCES Scrims(id),
                FOREIGN KEY(player_id) REFERENCES Players(id)
            );''')
    c.execute('''CREATE TABLE IF NOT EXISTS Players
            (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                psn_name TEXT UNIQUE,
                discord_name TEXT
            );''')
    conn.commit()


@bot.command(description='Creates a scrim', help="Takes your name as the host argument, put your time in double quotes. There is no validation.")
async def create(ctx, time, team_size):
    time = string_to_datetime(time)
    creator = ctx.author
    c.execute('''SELECT id, psn_name
                   FROM Players
                  WHERE discord_name = ?''', (str(creator),))
    try:
        row         = c.fetchall()[0]
        creatorid   = row[0]
        creatorname = row[1]
    except IndexError:
        await ctx.send('You need to register first using the `?register` command.')
        return


    c.execute('''INSERT INTO Scrims (time, team_size, creator)
                      VALUES (?, ?, ?);''', (time, int(team_size), creatorid))
    nextscrim = c.lastrowid
    c.execute('''INSERT INTO ScrimPlayers (player_id, scrim_id)
                      VALUES (?, ?);''', (creatorid, nextscrim))
    conn.commit()

    # Embed creation
    title = 'New Scrim: ' + str(nextscrim)
    color = 0xFFFFFF
    desc = 'Type `?join <id>` to join this scrim.'
    embed = discord.Embed(title=title, description=desc, color=color)

    # Player Iteration
    c.execute('''SELECT p.psn_name
                   FROM Players p
                   JOIN ScrimPlayers sp ON sp.player_id = p.id
                  WHERE sp.scrim_id = ?;''', (int(nextscrim),))
    rows = c.fetchall()
    counter = 1
    players = ""
    for row in rows:
        player = "%d. %s\n" % (counter, row[0])
        players = players + player
        counter = counter + 1

    embed.add_field(name='Time: ', value=time.strftime('%e-%b-%Y %H:%M'), inline=True)
    embed.add_field(name='Creator: ', value=creatorname, inline=True)
    embed.add_field(name='Team Size: ', value=team_size, inline=True)
    embed.add_field(name='Players: ', value=players, inline=False)

    await ctx.send(content=None, embed=embed)


@bot.command(description="Lists all scrims occuring on date", help="Takes a semantic date. Put date in double quotes")
async def list(ctx):
    creator = ctx.author

    c.execute('''SELECT s.id, s.time, p.psn_name
                   FROM Scrims s
                   JOIN Players p ON p.id = s.creator
                  WHERE s.time > date('now');''',())
    data = c.fetchall()

    # Send not scrims card if data is empty.
    if len(data) == 0:
        # Embed creation
        title = 'No scrims scheduled in the future. Schedule one now with `?create`'
        color = 0xFFFFFF
        embed = discord.Embed(title=title, color=color)
        await ctx.send(content=None, embed=embed)

    for _data in data:
        id = _data[0]
        game_time = datetime.strptime(_data[1], '%Y-%m-%d %H:%M:%S.%f')
        creator   = _data[2]
        # Embed creation
        title = 'New Scrim: ' + str(id)
        color = 0xFFFFFF
        desc  = 'Type `?join <id>` to join this scrim.'
        embed = discord.Embed(title=title, description=desc, color=color)

        # Player Iteration
        c.execute('''SELECT p.psn_name
                       FROM ScrimPlayers sp
                       JOIN Players p ON p.id = sp.player_id
                      WHERE scrim_id  = ?;''', (int(id),))
        rows = c.fetchall()
        counter = 1
        players = ""
        for row in rows:
            player = "%d. %s\n" % (counter, row[0])
            players = players + player
            counter = counter + 1

        embed.add_field(name='Time: ', value=game_time.strftime('%e-%b-%Y %H:%M')+('GMT'), inline=True)
        embed.add_field(name='Creator: ', value=creator, inline=True)
        embed.add_field(name='Players: ', value=players, inline=False)
        await ctx.send(content=None, embed=embed)


@bot.command(description="Join a scrim with a specific ID", help="Takes a scrim ID. You must be registered using `?register` first.")
async def join(ctx, scrim_id):
    creator = ctx.author

    # Get the player ID
    c.execute('''SELECT id
                   FROM Players
                  WHERE discord_name = ?;''', (str(creator),))

    try:
        player_id = c.fetchall()[0][0]
    except IndexError:
        await ctx.send('You are not registered. Please register with `?register`.')
        return

    # Get the scrim ID
    c.execute('''SELECT id, team_size
                   FROM Scrims
                  WHERE id = ?;''', (scrim_id,))
    try:
        scrim_row = c.fetchall()[0]
    except IndexError:
        await ctx.send('This is not an active scrim id. Create one with `?create`.')
        return

    # How many people are already registered for this scrim?
    c.execute('''SELECT Count(*)
                   FROM ScrimPlayers
                  WHERE scrim_id = ?;''', (scrim_id,))

    player_count = c.fetchall()[0][0]

    if player_count >= (scrim_row[1] * 2):
        await ctx.send('This scrim is full. Either see if someone leaves, or create one with `?create`.')
        return

    # How many people are already registered for this scrim?
    c.execute('''SELECT Count(*)
                   FROM ScrimPlayers
                  WHERE scrim_id = ?
                    AND player_id = ?;''', (scrim_id,player_id))

    is_here = (c.fetchall()[0][0] != 0)

    if is_here:
        await ctx.send('You already joined this scrim. Leave with `?leave`.')
        return

    # Join the scrim, doesn't matter if they already did.
    c.execute('''INSERT INTO ScrimPlayers (player_id, scrim_id)
                       VALUES (?, ?);''', (player_id, scrim_id))
    conn.commit()

    # Embed creation
    title = 'Joined Scrim: ' + str(scrim_id)
    color = 0xFFFFFF
    desc = 'Type `?join <id>` to join this scrim.'
    embed = discord.Embed(title=title, description=desc, color=color)

    c.execute('''SELECT p.psn_name, s.time
                   FROM Players p
                   JOIN Scrims s ON s.creator = p.id
                  WHERE s.id = ?;''', (scrim_id,))

    creator_and_time = c.fetchall()[0]
    creatorname      = creator_and_time[0]
    time             = creator_and_time[1]

    # Player Iteration
    c.execute('''SELECT p.psn_name
                   FROM Players p
                   JOIN ScrimPlayers sp ON sp.player_id = p.id
                  WHERE sp.scrim_id = ?;''', (int(scrim_id),))
    rows = c.fetchall()
    counter = 1
    players = ""
    for row in rows:
        player = "%d. %s\n" % (counter, row[0])
        players = players + player
        counter = counter + 1

    embed.add_field(name='Time: ', value=time, inline=True)
    embed.add_field(name='Creator: ', value=creatorname, inline=True)
    embed.add_field(name='Players: ', value=players, inline=False)

    await ctx.send(content=None, embed=embed)


@bot.command(description='Pulls the most recent private match you played. This is probably a scrim', help="This uses the API, and requires you to have used `?register`. Without it, you will get back an error message.")
async def match(ctx):
    creator = ctx.author

    # Player Iteration
    c.execute('SELECT psn_name from Players WHERE discord_name  = ?;', (str(creator),))
    player = c.fetchall()[0][0]

    if player == None:
        await ctx.send('You are not registered. Please register with `?register`.')

    # Get user id by PSN
    search_user = '/Destiny2/SearchDestinyPlayer/2/' + player + '/'
    r           = json.loads(requests.get(base_url + search_user, headers = headers).content)

    d2_membership_id = r['Response'][0]['membershipId']

    profile   = '/Destiny2/2/Profile/' + d2_membership_id + '/?components=100'
    r         = json.loads(requests.get(base_url + profile, headers = headers).content)
    characters = r['Response']['profile']['data']['characterIds']

    date_instances = {}

    for character in characters:
        matches = '/Destiny2/2/Account/' + d2_membership_id + '/Character/' + character + '/Stats/Activities/?mode=32&count=1'
        r       = json.loads(requests.get(base_url + matches, headers = headers).content)

        if 'activities' in r['Response']:
            for match in r['Response']['activities']:
                date     = match['period']
                mode     = modes_dict[match['activityDetails']['mode']]
                map_name = maps_dict[match['activityDetails']['referenceId']]
                instance = match['activityDetails']['instanceId']

                dateobject = datetime.strptime(date, '%Y-%m-%dT%H:%M:%SZ')
                date_instances[dateobject] = instance

    sorted_dates = sorted(date_instances.keys())
    instance = date_instances[sorted_dates.pop()]

    if instance == None:
        await ctx.send("Why the hell are you using this if you don't play private matches")
        return

    activity_url = '/Destiny2/Stats/PostGameCarnageReport/' + instance
    r            = json.loads(requests.get(base_url + activity_url, headers = headers).content)

    # Creates the match embed
    title = 'Scrim Post Game Report for : ' + str(creator)
    color = 0xFFFFFF
    desc  = mode + ' on ' + map_name
    embed = discord.Embed(title=title, description=desc, color=color)

    dateobject = datetime.strptime(date, '%Y-%m-%dT%H:%M:%SZ')
    date       = dateobject.strftime('%m-%d-%Y')
    embed.add_field(name='Time: ', value=date, inline=True)

    players_table = ""
    # Get the players and their individual stats
    players = r['Response']['entries']
    for player in players:
        standing = player['standing'] + 1
        name    = player['player']['destinyUserInfo']['displayName']
        score   = player['values']['score']['basic']['displayValue']
        kills   = player['values']['kills']['basic']['displayValue']
        deaths  = player['values']['deaths']['basic']['displayValue']
        assists = player['values']['assists']['basic']['displayValue']
        kdr     = player['values']['killsDeathsRatio']['basic']['displayValue']
        new_row = '**' + str(standing) + '.** ' + name + ' - ' + score +  ' (' + kills + '/' + deaths + '/' + assists + ')\n'
        players_table = players_table + new_row

    embed.add_field(name='Players: ', value=players_table, inline=False)

    await ctx.send(content=None, embed=embed)


@bot.command(description='Starts a scrim. Auto creates teams.', help="If you are the creator of a scrim, randomly generates the teams and starts it.")
async def start(ctx, scrim_id):
    creator = ctx.author

    # Get the scrim ID
    c.execute('''SELECT id, team_size, creator
                   FROM Scrims
                  WHERE id = ?;''', (scrim_id,))
    try:
        scrim_row = c.fetchall()[0]
    except IndexError:
        await ctx.send('This is not an active scrim id. Create one with `?create`.')
        return

    team_size = scrim_row[1]

    # How many people are already registered for this scrim?
    c.execute('''SELECT Count(*)
                   FROM ScrimPlayers
                  WHERE scrim_id = ?;''', (scrim_id,))

    player_count = c.fetchall()[0][0]

    if player_count != (team_size * 2):
        await ctx.send('This scrim is not full. More people need to join with `?join`.')
        return

    # Embed creation
    title = 'Scrim ' + str(scrim_id) + ' beginning now'
    color = 0xFFFFFF
    desc = "Join the creator's party unless otherwise specified."
    embed = discord.Embed(title=title, description=desc, color=color)

    c.execute('''SELECT p.psn_name
                   FROM Players p
                   JOIN Scrims s ON s.creator = p.id
                  WHERE s.id = ?;''', (scrim_id,))

    creator_and_time = c.fetchall()[0]
    creatorname      = creator_and_time[0]
    
    embed.add_field(name='Creator: ', value=creatorname, inline=False)

    # Player Iteration
    c.execute('''SELECT sp.player_id, p.psn_name
                   FROM ScrimPlayers sp
                   JOIN Players p ON p.id = sp.player_id
                  WHERE sp.scrim_id = ?;''', (scrim_id,))

    player_row = c.fetchall()

    random.shuffle(player_row)
    alpha = player_row[:(team_size)]
    bravo = player_row[(team_size):]

    counter = 1
    alpha_team = ""
    for player in alpha:
        a_player = "%d. %s\n" % (counter, player[1])
        alpha_team = alpha_team + a_player
        counter = counter + 1
    
    counter = 1
    bravo_team = ""
    for player in bravo:
        b_player = "%d. %s\n" % (counter, player[1])
        bravo_team = bravo_team + b_player
        counter = counter + 1

    embed.add_field(name='Alpha: ', value=alpha_team, inline=True)
    embed.add_field(name='Bravo: ', value=bravo_team, inline=True)

    await ctx.send(content=None, embed=embed)


@bot.command(description='Registers your PSN with your Discord', help="Takes your psn name as the psn argument.")
async def register(ctx, psn):
    creator = ctx.author
    c.execute('REPLACE INTO Players (psn_name, discord_name) VALUES(?, ?);', (psn, str(creator)))
    conn.commit()
    await ctx.send('`Registered %s with the PSN as %s. If this was done in error use ?register again.`' % (creator, psn))


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.DisabledCommand):
        await ctx.send(ctx.message.author, "I'm Sorry. This command is disabled and it can't be used.")
    elif isinstance(error, commands.CommandInvokeError):
        print('In {0.command.qualified_name}:'.format(ctx), file=sys.stderr)
        traceback.print_tb(error.original.__traceback__)
        print('{0.__class__.__name__}: {0}'.format(error.original), file=sys.stderr)
    elif isinstance(error, commands.CommandNotFound):
        await ctx.send(ctx.message.channel, "It seems you are trying to use a command that does not exist.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("It seems you are missing required argument(s). Try again if you have all the arguments needed.")
    elif isinstance(error, KeyError):
        await ctx.send("This is a KeyError cause the developers are idiots. Shoot them a message.")


bot.run(token)
