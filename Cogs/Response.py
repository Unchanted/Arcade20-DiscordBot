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
        adminroles = await self.client.dbp.fetch("SELECT adminroles FROM server_details WHERE guild_id=($1)", guild_id)
        adminroles = adminroles[0][0]
        return commands.has_any_role(adminroles)

    @commands.check
    async def modrolefind(self, ctx):
        guild_id = ctx.guild.id
        modroles = await self.client.dbp.fetch("SELECT modroles FROM server_details WHERE guild_id=($1)", guild_id)
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
        details = await self.client.dbp.fetch("SELECT * FROM trigger_response WHERE guild_id=($1) AND trigger=($2)", guild_id, trigger)
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


    @ar.command()
    @commands.check_any(commands.has_permissions(ban_members = True), modrolefind)
    # @commands.cooldown(1, 5, commands.BucketType.server)
    async def add(self, ctx: commands.Context, typ: str, trigger: str, res: str):
        "Add a Trigger Statement with a Response of a message or a reaction."
        guild_id = ctx.guild.id
        trigger = trigger.lower()
        trigger = re.sub("!", "", trigger)
        typ = typ.lower()

        find_msg = await self.find_ar(ctx, trigger)
        if find_msg:
            await ctx.send("Trigger already added. Delete and readd if you wish to change.", embed = find_msg)
            return

        if trigger in bl_words:
            await ctx.send("You entered a blacklisted trigger‼️")
            return

        if res in bl_words:
            await ctx.send("You entered a blacklisted response‼️")
            return

        view = Confirm(author_id=ctx.author.id)
        confirm_msg = await ctx.send(f"Are you sure you want to add the trigger {trigger}? <a:AreYouSure:892060354492891226>", view=view)
        await view.wait()
        await confirm_msg.edit(f"Are you sure you want to add the trigger {trigger}? <a:AreYouSure:892060354492891226>", view=view)
        
        if view.value is None:
            await ctx.channel.send("Timed out...")
            return

        elif view.value == False:
            return

        if (typ in rea):
            try:
                await ctx.message.add_reaction(res)
                await self.client.dbp.execute("INSERT INTO trigger_response VALUES ($1, $2, $3, $4, $5, $6)", guild_id, trigger, res, "Reaction", ctx.author.id, time.time())
            except discord.HTTPException:
                await ctx.send("Make sure the bot can use that emoji")
                return

        elif (typ in messa):
            await self.client.dbp.execute("INSERT INTO trigger_response VALUES ($1, $2, $3, $4, $5, $6)", guild_id, trigger, res, "Message", ctx.author.id, time.time())
        else:
            await ctx.send("Please enter a vaild Response Type...")
            return

        em = discord.Embed(title = "Success!! <a:tick_yes:888740287386628168>", description = f"A response has been created for the trigger **{trigger}**", colour = discord.Color.dark_green())
        added_by = ctx.author
        added_at = round(time.time())

        em.set_author(name = ctx.author.display_name, icon_url = ctx.author.avatar.url)
        em.set_thumbnail(url=self.client.user.avatar.url)
        em.add_field(name="Trigger:" , value=f"`{trigger}`", inline=True)
        em.add_field(name="Type:" , value=f"`{typ}`", inline=True)
        em.add_field(name="Response:" , value=f"`{res}`", inline=False)
        em.add_field(name="Added By:" , value=f"<@{added_by.id}> \n `<@{added_by.id}>`", inline=True)
        em.add_field(name="Added At:" , value=f"<t:{added_at}>", inline=True)

        await ctx.send(embed = em)

        del guild_id
        del trigger
        del typ

    @ar.command()
    @commands.check_any(commands.has_permissions(ban_members = True), modrolefind)
    # @commands.cooldown(1, 5, commands.BucketType.server)
    async def delete(self, ctx: commands.Context, trigger: str):
        "Delete a Trigger from this Server"
        guild_id = ctx.guild.id
        trigger = trigger.lower()
        trigger = re.sub("!", "", trigger)
        
        find_msg = await self.find(ctx, trigger)
        if not find_msg:
            return
        view = Confirm(author_id=ctx.author.id)
        view_msg: discord.Message = await find_msg.reply("Do you wish to delete this trigger?", view=view, mention_author = False)
        await view.wait()
        await view_msg.edit("Do you wish to delete this trigger?", view=view)
        if view.value is None:
            await ctx.channel.send("Timed out...")
            return

        elif view.value == False:
            return
        
        await self.client.dbp.execute("DELETE FROM trigger_response WHERE guild_id=($1) AND trigger=($2)", guild_id, trigger)
        
        await ctx.send(f"Successfully deleted the trigger {trigger}")

    @ar.command()
    @commands.check_any(commands.has_permissions(administrator = True), adminrolefind)
    # @commands.cooldown(1, 5, commands.BucketType.server)
    async def get_all(self, ctx: commands.Context):
        "Get all the Trigger, Responses and Types for this Server"
        guild_id = ctx.guild.id
        rdata = await self.client.dbp.fetch("SELECT * FROM trigger_response WHERE guild_id=($1)", guild_id)
        for i in rdata:
            j = list(i)
            tm = int(j[5])
            j[5] = datetime.datetime.utcfromtimestamp(tm).strftime("%d-%m-%Y %H:%M:%S")
            i = tuple(j)
        with open('dump.csv', 'w+', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(header)
            writer.writerows(rdata)
        with open('dump.csv', 'r', newline='') as d:
            file1 = discord.File(d)
        await ctx.send("Please check your DMs 😊")
        await ctx.author.send(file=file1)
        del rdata
        del file1

    @ar.command()
    @commands.check_any(commands.has_permissions(administrator = True), adminrolefind)
    async def cooldown(self, ctx: commands.Context, cd: float):
        "Update the cooldown for Triggers"
        oldCd = await self.client.dbp.fetch("SELECT cooldown FROM server_details WHERE guild_id=($1)", ctx.guild.id)
        oldCd = oldCd[0][0]
        view = Confirm(author_id=ctx.author.id)
        confirm_msg = await ctx.message.reply(f"The existing cooldown is {oldCd}s \nDo you wish to update it to {cd}s?", view = view, mention_author = False)
        await view.wait()
        await confirm_msg.edit(f"The existing cooldown is {oldCd}s \nDo you wish to update it to {cd}s?", view = view)
        if view.value is None:
            await ctx.channel.send("Timed out...")
            return
        elif view.value == False:
            return
        self.client.g_cd[ctx.guild.id] = commands.CooldownMapping.from_cooldown(1, cd, commands.BucketType.channel)
        await self.client.dbp.execute("UPDATE server_details SET cooldown=($1) WHERE guild_id=($2))", cd, ctx.guild.id)
        await ctx.send(f"Sucessfully updated the Trigger cooldown for this server to {cd}s")


    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return
        guild_id = message.guild.id
        new_msg = message.content.lower()
        new_msg = re.sub("!", "", new_msg)
        retry_after = self.ratelimit_check(guild_id, message)
        if retry_after is not None:
            return
        all_triggers = await self.client.dbp.fetch("SELECT * FROM trigger_response WHERE guild_id=($1)", guild_id)
        for at1 in all_triggers:
            trigger = at1[1]
            res = re.search(trigger, new_msg)
            if res != None:
                t_type = at1[3]
                response = at1[2]
                if t_type == "Reaction":
                    await message.add_reaction(response)
                else:
                    await message.reply(response, mention_author = False, allowed_mentions = discord.AllowedMentions.none())
                break

    @commands.Cog.listener()
    async def on_ready(self):
        self.client.g_cd = {}
        cd_data = await self.client.dbp.fetch("SELECT guild_id, cooldown FROM server_details")
        for i in cd_data:
            self.client.g_cd[i[0]] = commands.CooldownMapping.from_cooldown(1, i[1], commands.BucketType.channel)
            
def setup(client: discord.Client):
    client.add_cog(Response(client))
