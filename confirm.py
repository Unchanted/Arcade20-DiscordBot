import discord
from discord.ext import commands


class Confirm(discord.ui.View):
    def __init__(self, author_id):
        super().__init__()
        self.value = None
        self.author_id = author_id

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.blurple)
    async def confirm(self, button: discord.ui.Button, interaction: discord.Interaction):
        if interaction.user.id != self.author_id:
            await interaction.response.send_message("Your are not authorised to do this.", ephemeral=True)
        else:
            await interaction.response.send_message("Confirming this process...", ephemeral=True)
            self.value = True
            for child in self.children:
                child.disabled=True
            self.stop()

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red)
    async def cancel(self, button: discord.ui.Button, interaction: discord.Interaction):
        if interaction.user.id != self.author_id:
            await interaction.response.send_message("Your are not authorised to do this.", ephemeral=True)
        else:
            await interaction.response.send_message("Cancelling this process...", ephemeral=True)
            self.value = False
            for child in self.children:
                child.disabled=True
            self.stop()
