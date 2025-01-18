


import discord

from discord.ext import commands
from .constants import emojis


stop_emoji = emojis.get("stop")
prev_emoji = emojis.get("prev")
next_emoji = emojis.get("next")
pause_emoji = emojis.get("pause")
play_emoji = emojis.get("play")
resume_emoji = emojis.get("resume")
repeat_all = emojis.get("repeat_all")
repeat_one = emojis.get("repeat_one")



class VideoPlayerView(discord.ui.View):
    """
    A Discord UI View for media controls.

    This class provides an interactive interface where players can control a video player
    with actions such as pausing or playing, or skipping to the next or previous track.

    Attributes:
    -----------
        bot : commands.Bot
            The bot instance.
        ctx: commands.Context:
            The current context for the view.
    """
    def __init__(self, bot: commands.Bot, ctx: commands.Context, *, timeout=None):
        super().__init__(timeout=timeout)
        self.bot = bot
        self.ctx = ctx
        
    @discord.ui.button(emoji=stop_emoji, style=discord.ButtonStyle.blurple)
    async def _stop(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button):
        """Stops the player by invoking the `stop` command."""
        await interaction.response.defer()
        await self.ctx.invoke(self.bot.get_command("stop"))

    @discord.ui.button(emoji=prev_emoji, style=discord.ButtonStyle.blurple)
    async def _prev(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button):
        """Plays the previous video by invoking the `previous` command."""
        await interaction.response.defer()
        await self.ctx.invoke(self.bot.get_command("previous"))

    @discord.ui.button(emoji=pause_emoji, style=discord.ButtonStyle.blurple)
    async def _pause(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button):
        """Pauses or unpauses the current video by invoking the `pause` command."""
        await interaction.response.defer()
        await self.ctx.invoke(self.bot.get_command("pause"))

        button.emoji = resume_emoji if self.ctx.voice_client.is_paused() else pause_emoji
        await interaction.message.edit(view=self)
    
    @discord.ui.button(emoji=next_emoji, style=discord.ButtonStyle.blurple)
    async def _skip(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button):
        """Skips to the next video by invoking the `skip` command."""
        await interaction.response.defer()
        await self.ctx.invoke(self.bot.get_command("skip"))

    @discord.ui.button(emoji=repeat_one, style=discord.ButtonStyle.blurple)
    async def _loop_one(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button):
        """Loops the currently playing video by invoking the `loop_one` command."""
        await interaction.response.defer()
        await self.ctx.invoke(self.bot.get_command("loopone"))
