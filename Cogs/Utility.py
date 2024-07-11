import discord
from discord.ext import commands
import re
# from datetime import datetime

class Utility(commands.Cog):
    def __init__(self, client: discord.Client):
        self.client = client

    # @commands.command()
    # async def bump_toggle(self, ctx: commands.Context):
    #     async with self.client.tlock():
    #         await self.client.dbc.execute("SELECT bump_check FROM server_details WHERE guild_id=:guild_id", {'guild_id': ctx.guild.id})
    #         bump_bool= await self.client.dbc.fetchall()
    #         if bump_bool == "True":
    #             await self.client.dbc.execute("UPDATE TABLE bump_server SET bump_check=:bump_check WHERE guild_id=:guild_id", {'bump_check': 'False', 'guild_id': ctx.guild.id})
    #             await ctx.reply("Turned off the bump counter.")
    #         else:
    #             await self.client.dbc.execute("UPDATE TABLE bump_server SET bump_check=:bump_check WHERE guild_id=:guild_id", {'bump_check': 'True', 'guild_id': ctx.guild.id})
    #             await ctx.reply("Turned on the bump counter.")
    #         await self.client.db.commit()

    @commands.command()
    async def bumplb(self, ctx: commands.Context):
        lb = dict()
        emdesc = str()
        bump_history = await self.client.dbp.fetch("SELECT user_id,user_count FROM bump_lb WHERE guild_id=($1) ORDER BY user_count DESC LIMIT 20", ctx.guild.id)
        lb = dict(bump_history)
        for key, val in lb.items():
            emdesc = f"{emdesc}<@{key}>: {val} \n"

        em = discord.Embed(title=f"__Bump Leaderboard for **{ctx.guild.name}**__", colour=discord.Colour.random())

        em.description = emdesc

        await ctx.reply(embed = em)
        
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.id != 302050872383242240:
            return
        
        eml = message.embeds
        em = eml[0]
        bump_verify = re.search("Bump done!", em.description)
        if not bump_verify:
            return

        user_id = int(re.search("[0-9]+", em.description).group())

        user_count = await self.client.dbp.fetch("SELECT user_count FROM bump_lb WHERE guild_id=($1) AND user_id=($2)", message.guild.id, user_id)
        
        if not user_count:
            await self.client.dbp.execute("INSERT INTO bump_lb VALUES ($1, $2, $3)", message.guild.id, user_id, 1)
            return

        user_count = int(user_count[0][0])+1
        await self.client.dbp.execute("UPDATE bump_lb SET user_count=($1) WHERE guild_id=($2) AND user_id=($3)", user_count, message.guild.id, user_id)

    # @commands.Cog.listener()
    # async def on_message_delete(self, message: discord.Message):
    #     dellog = None
    #     async for entry in message.guild.audit_logs(limit = 1, action = discord.AuditLogAction.message_delete):
    #         if not float(datetime.timestamp(datetime.utcnow())-datetime.timestamp(entry.created_at)) <= 1.5:
    #             continue

    #         if entry.target.id == message.author.id and entry.extra.channel.id == message.channel.id:
    #             dellog = entry
    #             break

    #     if dellog:
    #         deleted_by = dellog.user
    #     else:
    #         deleted_by = message.author

    #     em = discord.Embed(title = f"Message Deleted by <@{deleted_by.id}>", 
    #     description = f"""**Content:** {message.content}
    #     **Author:** <@{message.author.id}>""")
    #     em.set_author(name = message.author.display_name, icon_url = message.author.avatar.url)
    #     await message.channel.send(embed = em)

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        await self.client.dbp.execute("INSERT INTO server_details VALUES ($1, $2, $3, $4, $5)", guild.id, ",", "", "", float(2))

    @commands.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild):    
        await self.client.dbp.execute("DELETE FROM server_details WHERE guild_id=($1)", guild.id)

def setup(client: discord.Client):
    client.add_cog(Utility(client))
