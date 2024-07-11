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
    
    # @commands.command()
    # @commands.is_owner()
    # async def bumptesting(self, ctx: commands.Context, message: discord.Message):
    #     if message.author.id != 302050872383242240:
    #         return
        
    #     eml = message.embeds
    #     print("Em list: ", eml)
    #     em = eml[0]
    #     print("Em: ", em)
    #     print("Em desc", em.description)
    #     bump_verify = re.search("Bump done!", em.description)
    #     print("BV: ", bump_verify)
    #     if not bump_verify:
    #         return

    #     user_id = int(re.search("[0-9]+", em.description).group())
    #     print("User id:", user_id)

    #     async with self.client.tlock:
    #         await self.client.dbc.execute("SELECT user_count FROM bump_lb WHERE guild_id=:guild_id AND user_id=:user_id", {'guild_id': message.guild.id, 'user_id': user_id})
    #         user_count = await self.client.dbc.fetchall()
    #         print(user_count)
    #         if not user_count:
    #             await self.client.dbc.execute("INSERT INTO bump_lb VALUES (?, ?, ?)", (ctx.guild.id, user_id, 0))
    #             await self.client.db.commit()
    #             user_count = [(0,)]

    #         user_count = int(user_count[0][0])+1
    #         await self.client.dbc.execute("UPDATE bump_lb SET user_count=:user_count WHERE guild_id=:guild_id AND user_id=:user_id", {'user_count': user_count, 'guild_id': message.guild.id, 'user_id': user_id})
    #         await self.client.db.commit()

def setup(client):
    client.add_cog(Owner(client))
