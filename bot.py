import discord
from discord.ext import commands
#import aiosqlite
import asyncpg
import asyncio
import os
from helpcmd import MyNewHelp
# from confirm import Confirm
import asyncpraw
# from discord.commands import Option
# import threading


async def dbconnect():
    client.dbp = await asyncpg.create_pool(dsn = os.environ['DATABASE_URL'])

DEFAULT_PREFIX = ","
default_cd = float(2)


async def get_prefix(client: discord.Client, message: discord.Message):
    if not message.guild:
        return commands.when_mentioned_or(DEFAULT_PREFIX)(client,message)
    async with client.dbp.acquire() as dbc:
        prefix = await dbc.fetch("SELECT prefix FROM server_details WHERE guild_id=($1)", message.guild.id)

        if len(prefix) == 0:
            await dbc.execute("INSERT INTO server_details VALUES ($1, $2, $3, $4, $5)", message.guild.id, DEFAULT_PREFIX, "", "", default_cd)
            prefix = DEFAULT_PREFIX
        else:
            prefix = prefix[0][0]
    
    return commands.when_mentioned_or(prefix)(client, message)

client = commands.Bot(command_prefix = get_prefix)
client.help_command = MyNewHelp()
client.reddit = asyncpraw.Reddit(client_id = "hG6NFmSD1r4flaGeP0LkjQ",
                     client_secret = os.environ['RED_SECRET'],
                     username = "DH_Bot",
                     password = os.environ['RED_PASS'],
                     user_agent = "memebot")
client.vc_act = {
    # 'Watch Together': discord.EmbeddedActivity.youtube,
    # 'Poker Night': discord.EmbeddedActivity.poker,
    # 'Betrayal.io': discord.EmbeddedActivity.betrayal,
    # 'Fishington.io': discord.EmbeddedActivity.fishing,
    # 'Chess in the Park': discord.EmbeddedActivity.chess,
    # Credits to RemyK888
    'Watch Together': 880218394199220334,
    'Poker Night': 755827207812677713,
    'Betrayal.io': 773336526917861400,
    'Fishington.io': 814288819477020702,
    'Chess in the Park': 832012774040141894,
    # Credits to awesomehet2124
    # 'Letter Tile': 87986368656562179,
    'Word Snack': 879863976006127627,
    'Doodle Crew': 878067389634314250
}

# @client.slash_command(guild_ids=[743063397062541372, 894530635631329290, 862972481140162580, 806762689883406366], description = "Start a Discord Embedded Activity")
# async def vc(
#     ctx,
#     channel: Option(discord.abc.GuildChannel, "Choose a voice channel"),
#     activity: Option(str, "Choose an activity", choices=["Watch Together", "Poker Night", "Betrayal.io", "Fishington.io", "Chess in the Park", "Word Snack", "Doodle Crew"])
# ):
#     if not channel.type == discord.ChannelType.voice:
#         await ctx.respond(f"{channel} is not a voice channel. Please select only voice channels")
#         return
#     act_type = client.vc_act[activity]
#     channel_invite = await channel.create_activity_invite(act_type)
#     await ctx.respond(f"[Click to open {activity} in {channel}]({str(channel_invite)})")

for filename in os.listdir("./Cogs"):
    if filename.endswith(".py"):
        try:
            client.load_extension(f"Cogs.{filename[:-3]}")
            print(f"-----------{filename[:-3]} Loaded-----------")
        except:
            raise

@client.event
async def on_ready():
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=f"{DEFAULT_PREFIX}help"))
    print("Logged in as {0.user}".format(client))
    print("----------------------------")

client.loop.create_task(dbconnect())
client.run(os.environ['DISCORD_TOKEN'])
asyncio.run(client.db.close())
