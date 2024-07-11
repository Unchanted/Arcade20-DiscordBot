import discord
from discord.ext import commands, tasks
import random

class Reddit(commands.Cog):
    def __init__(self, client: discord.Client):
        self.client = client

    all_memes = []
    new_memes = []
    all_animals = []
    new_animals = []

    @tasks.loop(seconds = 1200)
    async def fetch_memes(self):
        subreddit = await self.client.reddit.subreddit("BikiniBottomTwitter+memes+2meirl4meirl+deepfriedmemes+MemeEconomy+dankmemes")
        hot = subreddit.hot(limit = 300)
        new = subreddit.new(limit = 300)
        async for submission in hot:
            if submission.url.startswith("https://i.redd.it/"):
                self.new_memes.append(submission)
        async for submission in new:
            if submission.url.startswith("https://i.redd.it/"):
                self.new_memes.append(submission)

        self.all_memes = self.new_memes
        self.new_memes = []

        del hot
        del new
        del subreddit

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def meme(self, ctx: commands.Context):
        "Memes from r/memes and r/dankmemes"
        random_sub = random.choice(self.all_memes)

        if random_sub.over_18 != True and ctx.channel.is_nsfw() != False:
            await ctx.send("That meme turned out to be NSFW 😳 \nMark this channel as NSFW to bypass this")

        else:
            name = random_sub.title
            url = random_sub.url
            author = random_sub.author.name
            link = "https://www.reddit.com"+random_sub.permalink
            score = str(random_sub.score)
            em = discord.Embed(title = name, url = link, colour = 0xff0006)
            em.set_image(url = url)
            em.set_footer(text = "u/"+author+" | 👍 "+score)
            await ctx.send(embed = em)

            del name
            del url
            del em
            del author
            del link
            del score
        del random_sub


    @tasks.loop(minutes=30)
    async def fetch_animals(self):
        subreddit = await self.client.reddit.subreddit("aww+AnimalsBeingBros+eyebleach+Incorgnito+cats+AnimalsBeingDerps")
        hot = subreddit.hot(limit = 200)
        new = subreddit.new(limit = 200)
        rising = subreddit.rising(limit = 200)
        async for submission in hot:
            self.new_animals.append(submission)
        async for submission in new:
            self.new_animals.append(submission)
        async for submission in rising:
            self.new_animals.append(submission)

        self.all_animals = self.new_animals
        self.new_animals = []

        del hot
        del new
        del rising
        del subreddit


    @commands.command(aliases = ['floof'])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def animals(self, ctx: commands.Context):
        random_sub = random.choice(self.all_animals)

        if random_sub.over_18:
            await ctx.send("Why was this animals post marked NSFW 🤔")
            return
        
        if random_sub.url.startswith("https://i.redd.it/"):
            link = "https://www.reddit.com"+random_sub.permalink
            em = discord.Embed(title = random_sub.title, url = link, colour = discord.Colour.random())
            em.set_image(url = random_sub.url)
            em.set_footer(text = "u/"+random_sub.author.name+" | 👍 "+str(random_sub.score))
            await ctx.send(embed = em)
            del em
            del link

        else:
            await ctx.reply("https://www.reddit.com"+random_sub.permalink, mention_author = True)
            
        


    @commands.command()
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def reddit(self, ctx: commands.Context, subname: str, sorttype: str = "hot"):
        subreddit = await self.client.reddit.subreddit(subname)
        sorttype = sorttype.lower()
        if sorttype == "hot":
            subs = subreddit.hot(limit = 1)
        elif sorttype == "new":
            subs = subreddit.new(limit = 1)
        elif sorttype == "top":
            subs = subreddit.top(limit = 1)
        elif sorttype == "rising":
            subs = subreddit.rising(limit = 1)
        else:
            await ctx.send("Invalid Sort Type Specified. \nThe possible types are `Hot`, `New`, `Top`, `Rising`")
            return
            
        async for submission in subs:
            if submission.over_18 != True and ctx.channel.is_nsfw() != False:
                await ctx.send("That post turned out to be NSFW 😳 \n Mark this channel as NSFW to bypass this")
                return

            if submission.url.startswith("https://i.redd.it/"):
                link = "https://www.reddit.com"+submission.permalink
                em = discord.Embed(title = submission.title, url = link, colour = discord.Colour.random())
                em.set_image(url = submission.url)
                em.set_footer(text = "u/"+submission.author.name+" | 👍 "+str(submission.score))
                await ctx.send(embed = em)
                del em
                del link
            
            else:
                await ctx.send(f"https://www.reddit.com{submission.permalink}")
        
        del sorttype
        del subreddit
        del subs

    @commands.Cog.listener()
    async def on_ready(self):
        self.fetch_memes.start()
        print("Getting Memes...")
        self.fetch_animals.start()
        print("Getting Floof...")




def setup(client: discord.Client):
    client.add_cog(Reddit(client))
