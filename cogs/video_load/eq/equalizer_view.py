"""
This module defines the `EqualizerView` class, which provides an interactive 
Discord UI View for controlling the equalizer settings of a video player. 
Users can select different equalizer presets through a dropdown interface to 
adjust the audio filters applied to the playback.

Key Features:
- **Interactive Equalizer Controls**:
    - Allows users to select and apply different equalizer presets.
    - Displays updated embed with the new filter settings upon selection.

- **Integration with Bot Commands**:
    - Each selection triggers an update of the equalizer settings.
    - Updates are seamlessly reflected in the ongoing video playback.

### Classes:
- **`EqualizerView`**:
    Represents the interactive UI for video player equalizer controls. Provides:
    - A dropdown menu to select different equalizer presets.
    - Integration with the bot's equalizer settings and video playback system.

### Dependencies:
- **`discord`**: Provides UI elements and bot interaction capabilities.
- **`discord.ext.commands`**: Enables integration with bot commands.
- **`equalizer`**: Manages the equalizer filters and settings for video playback.
"""



import discord

from discord.ext import commands
from .equalizer import Equalizer



class EqualizerView(discord.ui.View):
    """A Discord UI View for equalizer controls.

    This class provides an interactive interface where players can control a video player equalizer
    by selecting equalizer settings from a dropdown.

    Attributes:
    -----------
        bot : commands.Bot
            The bot instance.
        equalizer : Equalizer
            The equalizer with its filter options.
    """
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