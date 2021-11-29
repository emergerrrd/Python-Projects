from discord.ext import commands
import discord
import requests
import pandas as pd
import bs4 as bs
import re
import asyncio

# Settings
command_pref = "group "

client = commands.Bot(command_prefix=command_pref)

@client.event
async def on_ready():
    await client.change_presence(status=discord.Status.online, game=discord.Game(name="Development", type=0))
    print("Ready to go!")

@client.command()
async def ping(ctx):
    await ctx.send("Pong!")

@client.command()
async def of(ctx, no_of_members, *args):
    no_of_members = int(no_of_members)
    agenda = ""
    for word in args:
        agenda += word+" "
    
    print("party", no_of_members, agenda)
    recruitment_msg = str(ctx.message.author)[:-5]+" is looking for "+str(no_of_members)+" people to "+agenda+"with.\nReact with a 👍 to this message to join!"
    await ctx.send(recruitment_msg)
    print(recruitment_msg)

    def check(reaction, user):
        return str(reaction.emoji) == '👍'

    count = 0

    try:
        reaction, user = await client.wait_for('reaction_add', check=check)
    except asyncio.TimeoutError:
        await ctx.send('👎')
    else:
        async for user in reaction.users():
            count += 1
            await ctx.send("```\n{0} joined {1}'s party ({2}/{3})\n```".format(str(user)[:-5], str(ctx.message.author)[:-5], count, no_of_members))
            if count >= no_of_members:
                await ctx.send(f"{ctx.message.author.mention}! Group is complete!")

TOKEN = "NTIwODQ2OTQ1OTA1MDE2ODQz.Duz0UA.mv8l1NoUYSTMO-5GxXDPpzh_fk4"
client.run(TOKEN)