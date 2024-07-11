import discord
from discord.ext import commands
from discord.ext.commands.core import Command

class Owner(commands.Cog):
    def __init__(self, client: discord.Client):
        self.client = client

    @commands.command()
    @commands.is_owner()
    async def reload (self, ctx: commands.Context, extension):
        "Reload lel"
        self.client.unload_extension(f"Cogs.{extension}")
        self.client.load_extension(f"Cogs.{extension}")
        await ctx.send(f"{extension} reloaded successfully")

def setup(client):
    client.add_cog(Owner(client))
