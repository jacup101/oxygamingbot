import random

import discord
from discord.ext.tasks import loop
import asyncio

from discord.ext import commands
import json
import discord.utils as discUtils
import uuid


intents = discord.Intents.all()
intents.members = True
bot = commands.Bot(command_prefix="?oxy.!", intents=intents)

type_defs_list = None
welcome = None
type_defs = {}
messages = {}
class RoleEmote:
    role = "default"
    fileName = "default.mp3"
    type = "EmoteItem"

    def __init__(self, name, fileName, type):
        self.name = name
        self.fileName = fileName
        self.type = type

    def __str__(self):
        return "{name}".format(name=self.name)



@bot.event
async def on_connect():
    global type_defs, type_defs_list, welcome
    activity = discord.Game(name="games in LIB364", type=3)
    await bot.change_presence(status=discord.Status.idle,activity=activity)
    print("Bot is online\nReading Data")
    
    with open("type_defs.json") as f:
        type_defs_list = json.load(f)
    with open("welcome.json") as f:
        welcome = json.load(f)
    for type_def in type_defs_list:
        with open("{type}.json".format(type=type_def)) as f:
            type_defs[type_def] = json.load(f)
            messages[type_def] = await create_message(type_defs[type_def])


@bot.event
async def on_raw_reaction_add(payload):
    global bot, messages
    guild = bot.get_guild(payload.guild_id)
    author = guild.get_member(payload.user_id)
    channel = guild.get_channel(payload.channel_id)
    message = await channel.fetch_message(payload.message_id)
    
    for type_def in type_defs_list:
        if message.content in messages[type_def]:
            await handle_reaction(guild, author, payload, "add", type_def)
            break

@bot.event
async def on_raw_reaction_remove(payload):
    global bot, messages
    guild = bot.get_guild(payload.guild_id)
    author = guild.get_member(payload.user_id)
    channel = guild.get_channel(payload.channel_id)
    message = await channel.fetch_message(payload.message_id)
    
    for type_def in type_defs_list:
        if message.content in messages[type_def]:
            await handle_reaction(guild, author, payload, "remove", type_def)
            break

@bot.command()
async def setup(ctx):
    global type_defs_lists
    for type_def in type_defs_list:
        await send_message(ctx, type_defs[type_def])

@bot.command()
async def welcome(ctx):
    global welcome
    await ctx.send(welcome["message"])

async def handle_reaction(guild, user, payload, action, type_def):
    global type_defs
    emote = await check_for_emote(type_defs[type_def]["list"], payload)
    if emote is None:
        return
    role = discUtils.get(guild.roles, name=emote["role_name"])

    # TODO: Add check for roles, and removal of roles
    if role in user.roles and "remove" in action:
        await user.remove_roles(role)
    if role not in user.roles and "add" in action:
        await user.add_roles(role)

    #print(hasRole)
    #await user.add_roles(role)

async def send_message(context, type):
    message = await create_message(type)
    msg = await context.send(message)
    list = type["list"]
    await add_reactions(list, msg, 0, len(list))

async def create_message(type):
    msg = type["message"]
    linker = type["linker"]
    list = type["list"]
    listStr = ""
    for item in list:
        listStr += "{emote} {linker} {desc}\n".format(emote=item["emote"], linker=linker, desc=item["description"])
    
    finalMessage = "\n**{message}**\n{list}".format(message=msg, list=listStr)
    return finalMessage


# Payload not necessary here, but passed in anyway
async def check_for_emote(list, payload):
    finalItem = None
    for listItem in list:
        countItem = await react_get_count(listItem, payload)
        if countItem > 0:
            found = True
            finalItem = listItem
            break
    return finalItem


async def react_get_count(listItem, payload):
    if "yes" in listItem['is_custom']:

        countItem = payload.emoji.name.count(listItem['emote_name'])
    else:
        countItem = payload.emoji.name.count(listItem['emote'])
    return countItem


async def add_reactions(list, message, start, end):
    length = end - start
    for i in range(length):
        item = list[start+i]
        emote = item["emote"]
        await message.add_reaction(emote)

bot.run("MTAxNDM0ODk5ODY4Mjg4MjEyOA.GS6hBC.iXVJ_GleVQlJ5C3JGb_LoA4eDlbkXvQ_NgX96I")
