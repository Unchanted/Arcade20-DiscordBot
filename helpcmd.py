import discord
from discord.ext.commands import MinimalHelpCommand


class MyNewHelp(MinimalHelpCommand):
        async def send_pages(self):
            destination = self.get_destination()
            for page in self.paginator.pages:
                emby = discord.Embed(description=page, colour = 0xff0006)
                await destination.send(embed=emby)
