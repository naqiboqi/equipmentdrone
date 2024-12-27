from discord.ext import commands



class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command(name="sync")
    @commands.is_owner()
    @commands.guild_only()
    async def sync_commands_(self, ctx):
        """Only needs to be used when new hybrid commands are added."""
        try:
            synced = await self.bot.tree.sync()
            print(f"Loaded {len(synced)} commands!")
            await ctx.message.add_reaction("✅")
        except Exception as e:
            print(e)
    
    
async def setup(bot):
    await bot.add_cog(Misc(bot))
