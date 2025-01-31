import discord

from discord.ext import commands
from .equalizer import Equalizer



class EqView(discord.ui.View):
    def __init__(self, bot: commands.Context, equalizer: Equalizer, timeout=None):
        super().__init__(timeout=timeout)
        self.bot = bot
        self.equalizer = equalizer

        menu = discord.ui.Select(
            placeholder="Select a preset",
            options=[
                discord.SelectOption(
                    label=filter.name, value=filter_name)
                    for filter_name, filter in (self.equalizer.filters.items())])

        menu.callback = self._select_option
        self.add_item(menu)

    async def _select_option(self, interaction: discord.Interaction):
        """Callback function for the dropdown."""
        if not self.equalizer.in_voice:
            return await interaction.response.defer()

        filter_name = interaction.data["values"][0]
        self.equalizer.set_filter(filter_name=filter_name)

        await interaction.response.edit_message(view=self)