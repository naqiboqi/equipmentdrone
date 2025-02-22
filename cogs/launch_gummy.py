import asyncio
import discord
import io
import json
import os
import subprocess
import sys

from typing import Optional
from discord.ext import commands
from cogs.utils.errors.gummy_errors import (
    GummyAlreadyRunning,
    GummyNotRunning, 
    GummyInitializeError,
    InvalidGummyMessageChannel
)



class LaunchGummy(commands.Cog):
    """Commands related to handling the Gummy bot's subprocess.
    
    Attributes:
    ----------
        bot : commands.Bot
            The bot instance.
        gummy : Popen|None
            The current Gummy subprocess.
    """
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.gummy: subprocess.Popen = None

    @property
    def gummy_active(self):
        """Whether or not the Gummy bot is online."""
        return self.gummy and self.gummy.poll() is None

    async def print_message(self, stream: io.TextIOWrapper, prefix: str):
        """Reads and prints output from the Gummy process. 
        Runs continously while the process is active.

        Params:
        -------
        stream : TextIOWrapper
            The stream to read from (stdout or stderr of Gummy's process).
        prefix : str
            A prefix to label the output type. Example outputs:

            - `[Gummy] Gummy is now online!`
            - `[Gummy Error] Could not read message`
        """
        if not stream:
            print(f"{prefix} stream is None!")
            return

        while self.gummy_active:
            line = await asyncio.to_thread(stream.readline)
            if not line:
                break

            print(f"{prefix} {line.strip()}")

    async def send_message(
        self, 
        message_type: str, 
        content: Optional[str]=None, 
        channel: Optional[discord.TextChannel]=None):
        """
        Sends a message to Gummy, optionally specifying a channel.
        
        Params:
        -------
            message : str
                The message to send to Gummy.
            channel : Optional[discord.TextChannel]
                The channel where the message originated, if applicable.
        """
        if self.gummy_active:
            message_data = {"type" : message_type, "content" : content}
            if channel:
                message_data["channel_id"] = str(channel.id)

            message_json = json.dumps(message_data)
            self.gummy.stdin.write(f"{message_json}\n")
            self.gummy.stdin.flush()
        else:
            print("Can't send message to Gummy, he is not online!")

    @commands.hybrid_command(name="ahoy")
    async def _say_ahoy(self, ctx: commands.Context):
        """Greets the user!"""
        await ctx.send("Ahoy! 🏴‍☠️")
        await self.send_message(message_type="command", content="ahoy", channel=ctx.channel)

    @commands.hybrid_command(name="gummy")
    async def _launch_gummy(self, ctx: commands.Context):
        """Creates a beautiful Gummy boy!"""
        try:
            if self.gummy_active:
                raise GummyAlreadyRunning("Gummy is running already!")

            env = {**os.environ, "PYTHONUNBUFFERED": "1"}
            self.gummy = subprocess.Popen(
                [sys.executable, "-m", "cogs.gummy.gummy_bot"],
                bufsize=1,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                universal_newlines=True,
                env=env)

        except (GummyAlreadyRunning, GummyInitializeError) as e:
            print(e)
            return await ctx.send(e, delete_after=10)

        asyncio.create_task(self.print_message(self.gummy.stdout, "[Gummy]"))
        asyncio.create_task(self.print_message(self.gummy.stderr, "[Gummy]"))

        await asyncio.sleep(2)
        await self.send_message(message_type="presence", content=self.bot.game_status)

        await ctx.send("Gummy is here!", delete_after=10)

    @commands.hybrid_command(name="sleepgummy")
    async def _sleep_gummy(self, ctx: commands.Context):
        """Puts Gummy to sleep."""
        try:
            if not self.gummy_active:
                raise GummyNotRunning("Gummy is not running!")
        except GummyNotRunning as e:
            print(e)
            return await ctx.send(e, delete_after=10)

        print("Putting Gummy to sleep....")
        self.gummy.terminate()

        try:
            self.gummy.wait(timeout=5)
        except subprocess.TimeoutExpired:
            print("Gummy would not go quietly....")
            self.gummy.kill()

        self.gummy = None
        await ctx.send("Goodbye gummy!", delete_after=10)
        print("Goodbye Gummy!")


async def setup(bot: commands.Bot):
    await bot.add_cog(LaunchGummy(bot))
