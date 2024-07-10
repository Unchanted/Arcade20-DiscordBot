import discord
from discord.ext import commands


class Confirm(discord.ui.View):
    def __init__(self, author_id):
        super().__init__()
        self.value = None
        self.author_id = author_id

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.green)
    async def confirm(self, button: discord.ui.Button, interaction: discord.Interaction):
        # if ctx.author != interaction.user:
        #     await interaction.response.send_message("You aren't authorised", ephemeral=True)
        #     return
        if interaction.user.id != self.author_id:
            await interaction.response.send_message("Your are not authorised to do this.", ephemeral=True)
        else:
            await interaction.response.send_message("Confirming this process...", ephemeral=False)
            self.value = True
            for child in self.children:
                child.disabled=True
            self.stop()

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red)
    async def cancel(self, button: discord.ui.Button, interaction: discord.Interaction):
        # if ctx.author != interaction.user:
        #     await interaction.response.send_message("You aren't authorised", ephemeral=True)
        #     return
        if interaction.user.id != self.author_id:
            await interaction.response.send_message("Your are not authorised to do this.", ephemeral=True)
        else:
            await interaction.response.send_message("Cancelling this process...", ephemeral=False)
            self.value = False
            for child in self.children:
                child.disabled=True
            self.stop()
