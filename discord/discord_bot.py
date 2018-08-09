import random
import asyncio
import aiohttp
import json
from discord import Game
from discord.ext.commands import Bot
import os

from lib.diff_checker import get_new

BOT_PREFIX = ("?", "!")
BOT_TOKEN = os.environ.get("DISCORD_TOKEN")
client = Bot(command_prefix=BOT_PREFIX)


commands_list = [
    "!Help",
    "!Proposals",
    "!Test"
]


@client.command(name='!Proposals',
                description="Returns a list of currently passing proposals",
                brief="List proposals",
                aliases=['!props', '!proposals', '!list'],
                pass_context=True)
async def list_props(context):
    print("Attempting to list proposals")
    proposals = get_new()['proposals']

    props_list = []

    for prop in proposals:
        if prop['will_be_funded'] is True:
            props_list.append(str(prop['title'] + prop['dw_url'] + "\n"))

    await client.say(str(props_list) + "\n" + context.message.author.mention)


# For sending to the #proposals channel
# await client.send_message(client.get_channel('370342005785755650'), (str(props_list) + "\n" + context.message.author.mention))


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    reply = str()
    if message.content.upper().startswith('!HELP'):
        for command in commands_list:
            reply += (command + "\n")

        msg = "**Commands:** \n{}".format(reply).format(message)

        await client.send_message(message.channel, msg)


@client.event
async def on_ready():
    await client.change_presence(game=Game(name="Governance"))
    print("Logged in as " + client.user.name)


if __name__ == '__main__':
    client.run(BOT_TOKEN)
