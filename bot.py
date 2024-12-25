import asyncio
import aiohttp
import discord
import os

from discord.ext import commands, tasks
from dotenv import load_dotenv

from misc import status



class MyBot(commands.Bot):
    """Initialize the bot and it's starting attributes."""
    def __init__(self):
        super().__init__(command_prefix="!", intents=discord.Intents.all())
        self.inital_extensions = [
            "battleship",
            "misc",
            "videocontroller",
        ]
        
    async def setup_hook(self):
        self.background_task.start()
        self.session = aiohttp.ClientSession()
        
        print("Loading extensions...\n")
        for filename in self.inital_extensions:
            await self.load_extension(f"cogs.{filename}")
        
    async def close(self):
        await super().close()
        await self.session.close()
        
    @tasks.loop(minutes=10)
    async def background_task(self):
        """Essentially just a heartbeat print."""
        print("Running background task")
        
    async def on_ready(self):
        print(F"\n{self.user.name} is now online!")
        
        while True:
            game_status = await status.choose_game()
            await self.change_presence(activity = discord.Game(name=game_status))
            await asyncio.sleep(7200)   


def main():
    load_dotenv()
    TOKEN = os.getenv("DISCORD_TOKEN")
    
    bot = MyBot()
    bot.run(TOKEN)

if __name__ == "__main__":
    main()
    