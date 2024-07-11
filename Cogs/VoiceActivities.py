import discord
from discord.ext import commands
from discord.commands import Option, slash_command

class VoiceActivities(commands.Cog):
    def __init__(self, client: discord.Client):
        self.client = client
    
    @slash_command(description = "Starts a Discord Embedded Activity")
    async def vc(
        self,
        ctx,
        channel: Option(discord.VoiceChannel, "Choose a voice channel"),
        activity: Option(str, "Choose an activity", choices=['Watch Together', 'Poker Night', 'Betrayal.io', 'Fishington.io', 'Chess in the Park', 'Checkers in the Park', 'Letter Tile', 'Word Snack', 'Doodle Crew', 'Awkword', 'SpellCast'])
    ):
        act_type = self.client.vc_act[activity]
        channel_invite = await channel.create_activity_invite(act_type)
        await ctx.respond(f"[Click to open {activity} in {channel}]({str(channel_invite)})")


def setup(client):
    client.add_cog(VoiceActivities(client))
