import subprocess

from discord.ext import commands



class LaunchGummy(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.gummy: subprocess.Popen[bytes] = None

    @commands.hybrid_command(name="gummy")
    async def _launch_gummy(self, ctx: commands.Context):
        """Creates a beautiful Gummy boy."""
        try:
            self.gummy = subprocess.Popen(["Python", "./cogs/gummy/gummy_bot.py"])
            await ctx.send("Gummy is here!")
        except Exception as e:
            print(f"error making gummy :( {e}")

    @commands.hybrid_command(name="killgummy")
    async def _kill_gummy(self, ctx: commands.Context):
        """Puts Gummy to sleep."""
        if not self.gummy:
            return await ctx.send("Gummy is asleep right now.", delete_after=10)
        
        self.gummy.terminate()
        await ctx.send("Goodbye gummy!", delete_after=10) 

async def setup(bot: commands.Bot):
    await bot.add_cog(LaunchGummy(bot))