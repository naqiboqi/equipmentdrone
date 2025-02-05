import aiohttp
import discord
import os

from discord.ext import commands, tasks
from dotenv import load_dotenv
from cogs.utils import choose_game



class MyBot(commands.Bot):
    """Representation of a Disord bot."""
    def __init__(self):
        super().__init__(command_prefix="!", intents=discord.Intents.all())
        self.inital_extensions = [
            "battleship",
            "connectfour",
            "dnd",
            "launch_gummy",
            "settings",
            "tictactoe",
            "videocontroller",
        ]

    @tasks.loop(hours=2)
    async def update_status_task(self):
        try:
            game_status = choose_game()
            await self.change_presence(activity=discord.Game(name=game_status))

            gummy_cog = self.get_cog("LaunchGummy")
            if gummy_cog.gummy_active:
                await gummy_cog.send_message(f"change_presence={game_status}")

            print(f"I'm now playing {game_status}!")
        except TypeError as e:
            print(f"Error updating status: {e}")

    async def setup_hook(self):
        self.session = aiohttp.ClientSession()
        self.update_status_task.start()

        print("Loading extensions...\n")
        for filename in self.inital_extensions:
            try:
                await self.load_extension(f"cogs.{filename}")
            except commands.errors.ExtensionNotFound as e:
                print(f"Error loading {filename}: {e}")

    async def on_ready(self):
        print(f"\n{self.user.name} is now online!")

    @update_status_task.before_loop
    async def before_update_status(self):
        await self.wait_until_ready()

    async def close(self):
        await super().close()
        await self.session.close()


def main():
    load_dotenv()
    TOKEN = os.getenv("DISCORD_TOKEN")

    bot = MyBot()
    bot.run(TOKEN)

if __name__ == "__main__":
    main()
