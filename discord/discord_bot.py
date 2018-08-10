from discord import Game
from discord.ext.commands import Bot
import os
import datetime

from lib.diff_checker import get_new, props_sorted
from lib.cycle_checker import get_cycle_info

BOT_PREFIX = ("?", "!")
BOT_TOKEN = os.environ.get("DISCORD_TOKEN")
client = Bot(command_prefix=BOT_PREFIX)


commands_list = [
    "!GovHelp",
    "!Proposals",
    "!Cycle"
    "!Countdown"
]

# For sending to the #proposals channel

# await client.send_message(client.get_channel('370342005785755650'),
# (str(props_list) + "\n" + context.message.author.mention))


@client.event
async def on_message(message):
    print("Triggered message")
    if message.author == client.user:
        return

    # Help information
    reply = str()
    if message.content.upper().startswith('!GOVHELP'):
        for command in commands_list:
            reply += (command + "\n")

        msg = "**Commands:** \n{}".format(reply).format(message)

        await client.send_message(message.channel, msg)

    # Cycle information
    if message.content.upper().startswith('!CYCLE'):
        cycle_info = get_new()['budget']

        # print(cycle_info)

        available_funds = float(cycle_info['total_amount']) - cycle_info['alloted_amount']
        payment_date = datetime.datetime.strptime(cycle_info['payment_date'], "%Y-%m-%d %H:%M:%S")
        voting_close = payment_date - datetime.timedelta(days=3.0245)

        fancy_message = str()

        fancy_message += "Voting Freeze: **{:%B, %d, %Y @ %H:%M:%S} UTC**".format(voting_close)
        fancy_message += "\n"
        fancy_message += "Proposal Payments: **{:%B, %d, %Y @ %H:%M:%S} UTC**".format(payment_date)
        fancy_message += "\n"
        fancy_message += "Remaining Funds Available: **{}/{}**".format(round(available_funds, 2), round(float(cycle_info['total_amount']), 2))

        await client.send_message(message.channel, ("**Current Cycle Information:** \n \n" +
                                                    str(fancy_message) + "\n"))


        """
        await client.send_message(message.channel, ("**Current Cycle Information:** \n \n" +
                                                    str(fancy_message) + "\n" + "@{}".format(message.author)))
        """

    # Proposals
    if message.content.upper().startswith('!PROPOSALS'):
        proposals = props_sorted()
        print(proposals)
        mn_count = get_cycle_info()['general']['consensus_masternodes']

        props_list = []

        for prop in proposals:
            if prop['will_be_funded'] is True:
                abs_votes = prop['yes'] - prop['no']
                percentage = round(((abs_votes/mn_count) * 100), 2)
                props_list.append((prop['title'], prop['dw_url'], abs_votes, percentage))

        fancy_message = str()

        for prop in props_list:
            fancy_message += "**Title:** {}".format(prop[0])
            fancy_message += '\n'
            fancy_message += "**Absolute Votes:** {} -> _{}%_".format(prop[2], prop[3])
            fancy_message += "\n"
            fancy_message += "**Link:** <{}>".format(prop[1])
            fancy_message += '\n \n'

        await client.send_message(message.channel, ("**Proposals that will be funded:** \n \n" +
                                                    str(fancy_message) + "\n"))
        """
        await client.send_message(message.channel, ("**Proposals that will be funded:** \n \n" +
                                                    str(fancy_message) + "\n" + "@{}".format(message.author)))
        """

@client.event
async def on_ready():
    await client.change_presence(game=Game(name="!GovHelp to list commands", type=1))
    print("Logged in as " + client.user.name)


if __name__ == '__main__':
    client.run(BOT_TOKEN)