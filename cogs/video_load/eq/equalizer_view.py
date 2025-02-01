import discord

from discord.ext import commands
from .equalizer import Equalizer



class EqualizerView(discord.ui.View):
    def __init__(self, bot: commands.Bot, equalizer: Equalizer, timeout=None):
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
        if not self.equalizer.is_connected:
            return await interaction.response.defer()

        filter_name = interaction.data["values"][0]
        self.equalizer.set_filter(filter_name=filter_name)
        embed = self.equalizer.embed

        await interaction.response.edit_message(embed=embed, view=self)
        await self.bot.get_cog("VideoController").apply_eq(ctx=self.equalizer.ctx)