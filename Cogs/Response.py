
import csv
import discord
from discord.ext import commands, tasks
# import asyncio
import datetime
import time
import re

from confirm import Confirm

rem = ["<","!","@","#","&",">"]
rea = ["r","reaction", "R", "Reaction"]
messa = ["m","msg","message", "M", "Message"]
bl_words = ["@everyone", "@here"]
header = ["Guild ID","Trigger", "Response", "Type", "User ID", "Added Time UTC (DD-MM-YYYY HH:MM:SS)"]


class Response(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.client.g_cd = {}
        # self._cd = commands.CooldownMapping.from_cooldown(1, 3, commands.BucketType.channel)

    def ratelimit_check(self, guild_id: int, message):
        """Returns the ratelimit left"""
        try:
            cdm = self.client.g_cd[guild_id]
        except KeyError:
            self.client.g_cd[guild_id] = commands.CooldownMapping.from_cooldown(1, 3, commands.BucketType.channel)
            cdm = self.client.g_cd[guild_id]
        bucket = cdm.get_bucket(message)
        return bucket.update_rate_limit()

    @commands.check
    async def adminrolefind(self, ctx):
        guild_id = ctx.guild.id
        async with self.client.tlock:
            self.client.dbc.execute("SELECT adminroles FROM server_details WHERE guild_id=:guild_id", {"guild_id":guild_id})
            adminroles = self.client.dbc.fetchall()
        adminroles = adminroles[0][0]
        return commands.has_any_role(adminroles)

    @commands.check    
    async def modrolefind(self, ctx):
        guild_id = ctx.guild.id
        async with self.client.tlock:
            self.client.dbc.execute("SELECT modroles FROM server_details WHERE guild_id=:guild_id", {"guild_id":guild_id})
            modroles = self.client.dbc.fetchall()
        modroles = modroles[0][0]
        return commands.has_any_role(modroles)

    @commands.group()
    @commands.cooldown(1, 5, commands.BucketType.guild)
    @commands.check_any(commands.has_permissions(ban_members = True), modrolefind)
    async def ar(self, ctx: commands.Context):
        "Customizable Responses For Triggers being Either a Reaction or a Message"
        if ctx.invoked_subcommand is None:
            await ctx.message.reply("Please invoke a subcommand!")

    async def find_ar(self, ctx, trigger: str):
        "Find Triggers added for this Server"
        trigger = trigger.lower()
        trigger = re.sub("!", "", trigger)
        guild_id = ctx.guild.id
        async with self.client.tlock:
            await self.client.dbc.execute("SELECT * FROM trigger_response WHERE guild_id=:guild_id AND trigger=:trigger", {"guild_id":guild_id, "trigger":trigger})
            details = await self.client.dbc.fetchall()
        if details:
            typ = details[0][3]
            res = details[0][2]
            added_by = details[0][4]
            added_at = round(float(details[0][5]))

            em = discord.Embed(title = "Trigger in Database", description = f"A match has been found for **{trigger}**", colour = discord.Color.blue())

            em.set_author(name = self.client.user.display_name, icon_url = self.client.user.avatar.url)
            em.add_field(name="Trigger:" , value=f"`{trigger}`", inline=True)
            em.add_field(name="Type:" , value=f"`{typ}`", inline=True)
            em.add_field(name="Response:" , value=f"`{res}`", inline=False)
            em.add_field(name="Added At:" , value=f"<t:{added_at}>", inline=True)
            em.add_field(name="Added By:" , value=f"<@{added_by}> \n`<@{added_by}>`", inline=False)
            
            del typ
            del res
            del added_by
            del added_at
            return em

        else: 
            return None

    @ar.command()
    @commands.check_any(commands.has_permissions(ban_members = True), modrolefind)
    async def find(self, ctx: commands.Context, trigger: str):
        em = await self.find_ar(ctx, trigger)
        await ctx.send(embed = em)
