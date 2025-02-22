import aiohttp
import asyncio
import discord
import json
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
        """Continuously listens for messages sent to Gummy via stdin."""
        print("Listening.....")
        while True:
            try:
                message = (await asyncio.to_thread(sys.stdin.readline)).strip()
                if not message:
                    print("Did not receive message from Gummy!")
                    continue

                try:
                    message_data = json.loads(message)
                except json.JSONDecodeError as e:
                    raise InvalidGummyMessage(f"Invalid message format: {message} caused error {e}.")

                match(message_data.get("type")):
                    case "presence":
                        status = message_data.get("content")
                        await self.change_presence(activity=discord.Game(name=status))
                    case "command":
                        channel = self.get_channel(int(message_data.get("channel_id")))
                        if not channel:
                            raise InvalidGummyMessageChannel("Invalid channel id.")

                        content = message_data.get("content")
                        if content == "ahoy":
                            await channel.send("Ahoy! 🏴‍☠️")
                    case "message":
                        channel = self.get_channel(int(message_data.get("channel_id")))
                        if not channel:
                            raise InvalidGummyMessageChannel("Invalid channel id.")
                        await channel.send(message_data.get("content"))

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

    async def on_ready(self):
        self.loop.create_task(self.listen_for_messages())
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
