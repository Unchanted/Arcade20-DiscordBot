import discord
from discord.ext import commands
import asyncpg
import asyncio
import os
from helpcmd import MyNewHelp
import asyncpraw

async def dbconnect():
    client.dbp = await asyncpg.create_pool(dsn = os.environ['DATABASE_URL'])

DEFAULT_PREFIX = ","
default_cd = float(2)

async def get_prefix(client: discord.Client, message: discord.Message):
    if not message.guild:
        return commands.when_mentioned_or(DEFAULT_PREFIX)(client,message)
    prefix = await client.dbp.fetch("SELECT prefix FROM server_details WHERE guild_id=($1)", message.guild.id)

    if len(prefix) == 0:
        await client.dbp.execute("INSERT INTO server_details VALUES ($1, $2, $3, $4, $5)", message.guild.id, DEFAULT_PREFIX, "", "", default_cd)
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
    # Credits to RemyK888
    'Watch Together': 880218394199220334,
    'Poker Night': 755827207812677713,
    'Betrayal.io': 773336526917861400,
    'Fishington.io': 814288819477020702,
    'Chess in the Park': 832012774040141894,
    # Credits to awesomehet2124
    'Letter Tile': 879863686565621790,
    'Word Snack': 879863976006127627,
    'Doodle Crew': 878067389634314250,
    'Awkword': 879863881349087252,
    'Checkers in the Park': 832013003968348200,
    'SpellCast': 852509694341283871
}

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
asyncio.run(client.dbp.close())
