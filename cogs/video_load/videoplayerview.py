


import discord

from discord.ext import commands



PAUSE = "<:pause:1328887225252970508>" 
PLAY = "<:play:1328887026883498014>" 
RESUME = "<:resume:1328887091094098043>" 
STOP = "<:stop:1328887072328650804>"
NEXT = "<:next:1328887052405833781>"
PREV = "<:prev:1328887060807028786>"



class VideoPlayerView(discord.ui.View):
    def __init__(self, bot: commands.Bot, ctx: commands.Context, *, timeout=180):
        super().__init__(timeout=timeout)
        self.bot = bot
        self.ctx = ctx
        
    @discord.ui.button(emoji=PREV, style=discord.ButtonStyle.blurple)
    async def _prev(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button):
        await interaction.response.defer()
        await self.ctx.invoke(self.bot.get_command("previous"))
    
    @discord.ui.button(emoji=PAUSE, style=discord.ButtonStyle.blurple)
    async def _pause(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button):
        await interaction.response.defer()
        await self.ctx.invoke(self.bot.get_command("pause"))
        
        button.emoji = RESUME if self.ctx.voice_client.is_paused() else PAUSE
        await interaction.message.edit(view=self)
    
    @discord.ui.button(emoji=NEXT, style=discord.ButtonStyle.blurple)
    async def _skip(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button):
        await interaction.response.defer()
        await self.ctx.invoke(self.bot.get_command("skip"))
    
    @discord.ui.button(emoji=STOP, style=discord.ButtonStyle.blurple)
    async def _stop(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button):
        await interaction.response.defer()
        await self.ctx.invoke(self.bot.get_command("stop"))