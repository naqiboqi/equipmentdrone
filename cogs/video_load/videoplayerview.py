


import discord

from discord.ext import commands



class VideoPlayerView(discord.ui.View):
    def __init__(self, bot: commands.Bot, ctx: commands.Context, *, timeout=180):
        super().__init__(timeout=timeout)
        self.bot = bot
        self.ctx = ctx
        
    @discord.ui.button(label="⏮️", style=discord.ButtonStyle.blurple)
    async def _backtrack(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button):
        
        await interaction.response.defer()
    
    @discord.ui.button(label="⏸️", style=discord.ButtonStyle.blurple)
    async def _pause(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button):
        
        await self.ctx.invoke(self.bot.get_command("pause"))
        button.label = "▶️" if self.ctx.voice_client.is_paused() else "⏸️"
    
    @discord.ui.button(label="⏭️", style=discord.ButtonStyle.blurple)
    async def _skip(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button):

        await self.ctx.invoke(self.bot.get_command("skip"))
    
    @discord.ui.button(label="⏹️", style=discord.ButtonStyle.blurple)
    async def _stop(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button):
        
        await self.ctx.invoke(self.bot.get_command("stop"))