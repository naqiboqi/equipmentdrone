import aiohttp
import asyncio
import discord
import os
import sys

from discord.ext import commands
from dotenv import load_dotenv
from ..utils.errors import InvalidGummyMessage, InvalidGummyMessageChannel



class GummyBot(commands.Bot):
    """Representation of a Disord bot."""
    def __init__(self):
        super().__init__(command_prefix="?", intents=discord.Intents.all())
        self.inital_extensions = [
            "battleship",
            "connectfour",
            "dnd",
            "tictactoe",
            "videocontroller"
        ]

    async def listen_for_messages(self):
        while True:
            try:
                message = (await asyncio.to_thread(sys.stdin.readline)).strip()
                if not message:
                    print("Did not receive message!")

                if "change_presence=" in message:
                    game_status = message.split("=")[1]
                    return await self.change_presence(activity=discord.Game(name=game_status))

                message_data = message.split(":")
                if len(message_data) == 2:
                    [channel_name, command] = message_data
                elif len(message_data) == 1:
                    command = message_data[0]
                else:
                    raise InvalidGummyMessage(f"Message is missing data {":".join(message_data)}")

                await asyncio.sleep(1.5)
                if command == "ahoy":
                    channel = discord.utils.get(self.get_all_channels(), name=channel_name)
                    if channel:
                        await channel.send("Ahoy! 🏴‍☠️")
                    else:
                        raise InvalidGummyMessageChannel(
                            f"Could not find channel to send message {channel_name}")

                print(f"Gummy received command: {command}")
            except InvalidGummyMessage as e:
                print(f"[Gummy Error] {e}")

    async def setup_hook(self):
        self.session = aiohttp.ClientSession()

        print("Loading extensions...\n")
        await self.load_extension("cogs.gummy.gummy_settings")
        for filename in self.inital_extensions:
            try:
                await self.load_extension(f"cogs.{filename}")
            except commands.errors.ExtensionNotFound as e:
                print(f"Error loading {filename}: {e}")

        self.loop.create_task(self.listen_for_messages())

    async def on_ready(self):
        print(f"\n{self.user.name} is now online!")

    async def close(self):
        await super().close()
        await self.session.close()


def main():
    load_dotenv()
    TOKEN = os.getenv("GUMMY_TOKEN")

    bot = GummyBot()
    bot.run(TOKEN)


if __name__ == "__main__":
    main()
