


import discord

from discord.ext import commands
from .constants import emojis



prev_emoji = emojis.get("prev")
next_emoji = emojis.get("next")
pause_emoji = emojis.get("pause")
play_emoji = emojis.get("play")
resume_emoji = emojis.get("resume")
stop_emoji = emojis.get("stop")



class VideoPlayerView(discord.ui.View):
    def __init__(self, bot: commands.Bot, ctx: commands.Context, *, timeout=180):
        super().__init__(timeout=timeout)
        self.bot = bot
        self.ctx = ctx
        
    @discord.ui.button(emoji=prev_emoji, style=discord.ButtonStyle.red)
    async def _prev(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button):
        await interaction.response.defer()
        await self.ctx.invoke(self.bot.get_command("previous"))
    
    @discord.ui.button(emoji=pause_emoji, style=discord.ButtonStyle.red)
    async def _pause(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button):
        await interaction.response.defer()
        await self.ctx.invoke(self.bot.get_command("pause"))
        
        button.emoji = resume_emoji if self.ctx.voice_client.is_paused() else pause_emoji
        await interaction.message.edit(view=self)
    
    @discord.ui.button(emoji=next_emoji, style=discord.ButtonStyle.red)
    async def _skip(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button):
        await interaction.response.defer()
        await self.ctx.invoke(self.bot.get_command("skip"))
    
    @discord.ui.button(emoji=stop_emoji, style=discord.ButtonStyle.red)
    async def _stop(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button):
        await interaction.response.defer()
        await self.ctx.invoke(self.bot.get_command("stop"))