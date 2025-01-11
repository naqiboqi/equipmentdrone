


import discord

from discord.ext import commands



class VideoPlayerView(discord.ui.View):
    def __init__(self, bot: commands.Bot, ctx: commands.Context, *, timeout=180):
        super().__init__(timeout=timeout)
        self.bot = bot
        self.ctx = ctx
        
    @discord.ui.button(label="⏮️", style=discord.ButtonStyle.blurple)
    async def backtrack_(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button):
        
        await interaction.response.defer()
    
    @discord.ui.button(label="⏸️", style=discord.ButtonStyle.blurple)
    async def pause_(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button):
        
        await self.ctx.invoke(self.bot.get_command("pause"))
        button.label = "▶️" if self.ctx.voice_client.is_paused() else "⏸️"
        await interaction.response.defer()
    
    @discord.ui.button(label="⏭️", style=discord.ButtonStyle.blurple)
    async def skip_(
        self,
        interaction: discord.Interaction):

        await self.ctx.invoke(self.bot.get_command("skip"))
        await interaction.response.defer()
    
    @discord.ui.button(label="⏹️", style=discord.ButtonStyle.blurple)
    async def stop_(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button):
        
        await self.ctx.invoke(self.bot.get_command("stop"))
        await interaction.response.defer()