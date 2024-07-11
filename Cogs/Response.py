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


    @ar.command()
    @commands.check_any(commands.has_permissions(ban_members = True), modrolefind)
    # @commands.cooldown(1, 5, commands.BucketType.server)
    async def add(self, ctx: commands.Context, typ: str, trigger: str, res: str):
        "Add a Trigger Statement with a Response of a message or a reaction."
        guild_id = ctx.guild.id
        trigger = trigger.lower()
        trigger = re.sub("!", "", trigger)
        typ = typ.lower()
        # async with self.client.tlock:
        #     await self.client.dbc.execute("SELECT * FROM trigger_response WHERE guild_id=:guild_id AND trigger=:trigger", {"guild_id":guild_id, "trigger":trigger})
        #     details = await self.client.dbc.fetchall()
        # if details:
        #     await self.find(ctx, trigger)
        #     return

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
                async with self.client.tlock:
                    await self.client.dbc.execute("INSERT INTO trigger_response VALUES (?, ?, ?, ?, ?, ?)", (guild_id, trigger, res, "Reaction", ctx.author.id, time.time()))
                    await self.client.db.commit()
            except discord.HTTPException:
                await ctx.send("Make sure the bot can use that emoji")
                return

        elif (typ in messa):
            async with self.client.tlock:
                await self.client.dbc.execute("INSERT INTO trigger_response VALUES (?, ?, ?, ?, ?, ?)", (guild_id, trigger, res, "Message", ctx.author.id, time.time()))
                await self.client.db.commit()
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
        
        async with self.client.tlock:
            await self.client.dbc.execute("DELETE FROM trigger_response WHERE guild_id=:guild_id AND trigger=:trigger", {"guild_id":guild_id, "trigger":trigger})
            await self.client.db.commit()
        
        await ctx.send(f"Successfully deleted the trigger {trigger}")

    @ar.command()
    @commands.check_any(commands.has_permissions(administrator = True), adminrolefind)
    # @commands.cooldown(1, 5, commands.BucketType.server)
    async def get_all(self, ctx: commands.Context):
        "Get all the Trigger, Responses and Types for this Server"
        guild_id = ctx.guild.id
        async with self.client.tlock:
            await self.client.dbc.execute("SELECT * FROM trigger_response WHERE guild_id=:guild_id", {"guild_id":guild_id})
            rdata = await self.client.dbc.fetchall()
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
        async with self.client.tlock:
            await self.client.dbc.execute("SELECT cooldown FROM server_details WHERE guild_id=:id", {'id':ctx.guild.id})
            oldCd = await self.client.dbc.fetchall()
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
        async with self.client.tlock:
            await self.client.dbc.execute("UPDATE server_details SET cooldown=:cooldown WHERE guild_id=:id", {'cooldown':cd, 'id':ctx.guild.id})
            await self.client.db.commit()
        await ctx.send(f"Sucessfully updated the Trigger cooldown for this server to {cd}s")


    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return
        guild_id = message.guild.id
        new_msg = message.content.lower()
        new_msg = re.sub("!", "", new_msg)
        retry_after = self.ratelimit_check(guild_id, message)

        async with self.client.tlock:
            await self.client.dbc.execute("SELECT * FROM trigger_response WHERE guild_id=:guild_id", {"guild_id":guild_id})
            all_triggers = await self.client.dbc.fetchall()

        if retry_after is not None:
            return

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
        async with self.client.tlock:
            await self.client.dbc.execute("SELECT guild_id, cooldown FROM server_details")
            cd_data = await self.client.dbc.fetchall()
        for i in cd_data:
            self.client.g_cd[i[0]] = commands.CooldownMapping.from_cooldown(1, i[1], commands.BucketType.channel)
            

    

def setup(client: discord.Client):
    client.add_cog(Response(client))
