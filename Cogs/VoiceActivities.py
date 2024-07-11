import discord
from discord.ext import commands
from discord.commands import Option, slash_command

class VoiceActivities(commands.Cog):
    def __init__(self, client: discord.Client):
        self.client = client
    
    @slash_command(guild_ids=[743063397062541372, 894530635631329290, 862972481140162580, 806762689883406366], description = "Start a Discord Embedded Activity")
    async def vc(
        self,
        ctx,
        channel: Option(discord.VoiceChannel, "Choose a voice channel"),
        activity: Option(str, "Choose an activity", choices=["Watch Together", "Poker Night", "Betrayal.io", "Fishington.io", "Chess in the Park", "Word Snack", "Doodle Crew"])
    ):
        if not channel.type == discord.ChannelType.voice:
            await ctx.respond(f"{channel} is not a voice channel. Please select only voice channels")
            return
        act_type = self.client.vc_act[activity]
        channel_invite = await channel.create_activity_invite(act_type)
        await ctx.respond(f"[Click to open {activity} in {channel}]({str(channel_invite)})")


def setup(client):
    client.add_cog(VoiceActivities(client))
