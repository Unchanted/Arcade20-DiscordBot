import discord
from discord.ext import commands, tasks
import asyncio
from confirm import Confirm
import random

class Misc(commands.Cog):
    def __init__(self, client: discord.Client):
        self.client = client

    all_subs = None

    @commands.group()
    @commands.cooldown(1, 5, commands.BucketType.guild)
    async def set(self, ctx: commands.Context):
        "Setup and Modify the Permmisions for the Bot"
        if ctx.invoked_subcommand is None:
            await ctx.send("Please invoke a subcommand!", delete_after=10)
    
    @set.command()
    async def admins(self, ctx: commands.Context, roleIDs: list):
        async with self.client.tlock:
            await self.client.dbc.execute("SELECT adminroles FROM server_details WHERE guild_id=:guild", {'guild':ctx.guild.id})
            oldAdmins = await self.client.dbc.fetchall()
        view = Confirm(author_id=ctx.author.id)
        if oldAdmins:
            oldAdmins = oldAdmins[0][0]
            confirm_msg = await ctx.send(f"The Existing Admin Roles are ({oldAdmins}). \nAre you sure you want to replace them with ({roleIDs}) \n**WARNING:** This can potentially break the permissions in the server. Procceed with caution <a:waiting:872458278536368158>", view = view)
            await view.wait()
            await confirm_msg.edit(f"The Existing Admin Roles are ({oldAdmins}). \nAre you sure you want to replace them with ({roleIDs}) \n**WARNING:** This can potentially break the permissions in the server. Procceed with caution <a:waiting:872458278536368158>", view = view)
        else:
            confirm_msg = await ctx.send(f"Do you want to set the Admin Roles to ({roleIDs}) \n**WARNING:** This can potentially break the permissions in the server. Procceed with caution <a:waiting:872458278536368158>", view = view)
            await view.wait()
            await confirm_msg.edit(f"Do you want to set the Admin Roles to ({roleIDs}) \n**WARNING:** This can potentially break the permissions in the server. Procceed with caution <a:waiting:872458278536368158>", view = view)
        if view.value is None:
            await ctx.channel.send("Timed out...")
            return
        elif view.value == False:
            return

        async with self.client.tlock:
            await self.client.dbc.execute(f"UPDATE server_details SET adminroles=:rolelist WHERE guild_id=:guild_id", {'guild_id':ctx.guild.id, 'rolelist':roleIDs})
            await self.client.db.commit()
        await ctx.send(f"The Admin Roles Have been Updated as {roleIDs}")

    @set.command()
    async def mods(self, ctx: commands.Context, roleIDs: list):
        async with self.client.tlock:
            await self.client.dbc.execute("SELECT modroles FROM server_details WHERE guild_id=:guild", {'guild':ctx.guild.id})
            oldMods = await self.client.dbc.fetchall()
        view = Confirm(author_id=ctx.author.id)
        if oldMods:
            oldMods = oldMods[0][0]
            confirm_msg = await ctx.send(f"The Existing Mod Roles are ({oldMods}). \nAre you sure you want to replace them with ({roleIDs}) \n**WARNING:** This can potentially break the permissions in the server. Procceed with caution <a:waiting:872458278536368158>", view = view)
            await view.wait()
            await confirm_msg.edit(f"The Existing Mod Roles are ({oldMods}). \nAre you sure you want to replace them with ({roleIDs}) \n**WARNING:** This can potentially break the permissions in the server. Procceed with caution <a:waiting:872458278536368158>", view = view)
        else:
            confirm_msg = await ctx.send(f"Do you want to set the Mod Roles to ({roleIDs}) \n**WARNING:** This can potentially break the permissions in the server. Procceed with caution <a:waiting:872458278536368158>", view = view)
            await view.wait()
            await confirm_msg.edit(f"Do you want to set the Mod Roles to ({roleIDs}) \n**WARNING:** This can potentially break the permissions in the server. Procceed with caution <a:waiting:872458278536368158>", view = view)
        if view.value is None:
            await ctx.channel.send("Timed out...")
            return
        elif view.value == False:
            return

        async with self.client.tlock:
            await self.client.dbc.execute(f"UPDATE server_details SET modroles=:rolelist WHERE guild_id=:guild_id", {'guild_id':ctx.guild.id, 'rolelist':roleIDs})
            await self.client.db.commit()
        await ctx.send(f"The Mod Roles Have been Updated as {roleIDs}")

    @set.command()
    async def prefix(self, ctx: commands.Context, newPrefix: str):
        async with self.client.tlock:
            await self.client.dbc.execute("SELECT prefix FROM server_details WHERE guild_id=:id", {'id':ctx.guild.id})
            oldPrefix = await self.client.dbc.fetchall()
        oldPrefix = oldPrefix[0][0]
        if oldPrefix == newPrefix:
            await ctx.send("The New Prefix Is Same As The Current Prefix Set For This Server!")
            return
        view = Confirm(author_id=ctx.author.id)
        confirm_msg = await ctx.send(f"The old prefix is `{oldPrefix}` \nDo you wish to change it to `{newPrefix}` ? Mentioning the bot will still work as a prefix.", view = view)
        view.wait()
        await confirm_msg.edit(f"The old prefix is `{oldPrefix}` \nDo you wish to change it to `{newPrefix}` ? Mentioning the bot will still work as a prefix.", view = view)
        if view.value is None:
            await ctx.channel.send("Timed out...")
            return
        elif view.value == False:
            return
        async with self.client.tlock:
            await self.client.dbc.execute(f"UPDATE server_details SET prefix=:newPrefix WHERE guild_id=:guild_id", {'guild_id':ctx.guild.id, 'newPrefix':newPrefix})
            await self.client.db.commit()
        await ctx.send(f"Prefix successfully updated to `{newPrefix}`")
    
    # @set.command()
    # async def trig_cooldown(self, ctx, cd: float):
    #     "Update the cooldownn for Triggers"
    #     async with self.client.tlock:
    #         await self.client.dbc.execute("SELECT cooldown FROM server_details WHERE guild_id=:id", {'id':ctx.guild.id})
    #         oldCd = await self.client.dbc.fetchall()
    #     oldCd = oldCd[0][0]
        view = Confirm(author_id=ctx.author.id)
    #     confirm_msg = await ctx.message.reply(f"The existing cooldown is {oldCd}s \nDo you wish to update it to {cd}s?", view = view, mention_author = False)
    #     await view.wait()
    #     await confirm_msg.edit(f"The existing cooldown is {oldCd}s \nDo you wish to update it to {cd}s?", view = view)
    #     if view.value is None:
    #         await ctx.channel.send("Timed out...")
    #         return
    #     elif view.value == False:
    #         return
    #     async with self.client.tlock:
    #         await self.client.dbc.execute("UPDATE server_details SET cooldown=:cooldown WHERE guild_id=:id", {'cooldown':cd, 'id':ctx.guild.id})
    #         await self.client.db.commit()
    #         await self.client.dbc.execute("UPDATE channel_triggered SET cooldown=:cooldown WHERE guild_id=:id", {'cooldown':cd, 'id':ctx.guild.id})
    #         await self.client.db.commit()
    #     await ctx.send(f"Sucessfully updated the Trigger cooldown for this server to {cd}")
    
    @tasks.loop(seconds = 1200)
    async def fetch_memes(self):
        self.all_subs = []
        subreddit = await self.client.reddit.subreddit("memes+dankmemes")
        hot = subreddit.hot(limit = 200)
        new = subreddit.new(limit = 100)
        async for submission in hot:
            if submission.url.startswith("https://i.redd.it/"):
                self.all_subs.append(submission)
        async for submission in new:
            if submission.url.startswith("https://i.redd.it/"):
                self.all_subs.append(submission)


        del hot
        del new
        del subreddit

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def meme(self, ctx: commands.Context):
        "Memes from r/memes and r/dankmemes"
        random_sub = random.choice(self.all_subs)

        if random_sub.over_18 == False:
            name = random_sub.title
            url = random_sub.url
            author = random_sub.author.name
            link = "https://www.reddit.com"+random_sub.permalink
            score = str(random_sub.score)
            em = discord.Embed(title = name, url = link, colour = 0xff0006)
            
            if url.startswith("https://i.redd.it/"):
                em.set_image(url = url)
                em.set_footer(text = "u/"+author+" | 👍 "+score)
                await ctx.send(embed = em)

            del name
            del url
            del em
            del author
            del link
            del score
        else:
            await ctx.send("Oops! That meme was NSFW 😳")
            return

        self.all_subs.remove(random_sub)
        del random_sub

    @commands.Cog.listener()
    async def on_ready(self):
        self.fetch_memes.start()

    # @commands.Cog.listener()
    # async def on_message_delete(self, message):
    #     dellog = None
    #     async for entry in message.guild.audit_logs(limit = 1, action = discord.AuditLogAction.message_delete):
    #         if entry.target.id == message.author.id:
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

def setup(client: discord.Client):
    client.add_cog(Misc(client))
