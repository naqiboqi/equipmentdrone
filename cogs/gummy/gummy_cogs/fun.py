import discord

from discord.ext import commands



class Fun(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command(name="ahoy")
    async def _say_ahoy(self, ctx: commands.Context):
        """Greets the user."""
        await ctx.send("Ahoy! 🏴‍☠️")


async def setup(bot: commands.Bot):
    await bot.add_cog(Fun(bot))