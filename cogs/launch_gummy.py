import discord
import subprocess

from discord.ext import commands



class LaunchGummy(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.gummy = None
    
    @commands.hybrid_command(name="gummy")
    async def _launch_gummy(self, ctx: commands.Context):
        """Creates a beautiful gummy boy."""
        try:
            subprocess.Popen(["Python", "python ./cogs/gummy/gummy_bot.py"])
            await ctx.send("Gummy is here!")
        except Exception as e:
            print(f"error making gummy :( {e}")


async def setup(bot: commands.Bot):
    await bot.add_cog(LaunchGummy(bot))