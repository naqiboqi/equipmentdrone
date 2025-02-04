import asyncio
import discord
import io
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
        """Receives and prints a message from the Gummy subprocess' stdin.
        
        Params:
        -------
            stream : TextIOWrapper
                The stream to read from.
            prefix : str
                Prefix denoting the type of message:
                
                    [Gummy]
                    
                    [Gummy [message_here]]
                    
                    [Gummy Error]
        """
        if not stream:
            print(f"{prefix} stream is None!")
            return

        while self.gummy_active:
            line = await asyncio.to_thread(stream.readline)
            if not line:
                break

            print(f"{prefix} {line.strip()}")

    async def send_message(self, message: str, channel: Optional[discord.abc.Messageable]=None):
        """Sends a message to Gummy and tells him the channel the message is from.
        
        Params:
        -------
            channel : MessagableChannel
                The channel that the message came from, if any.
            message : str
                The message to send.
        """
        if self.gummy_active:
            try:
                if channel:
                    self.gummy.stdin.write(f"{channel.name}:{message}\n")
                else:
                    raise InvalidGummyMessageChannel("Could not find channel to send!")
                self.gummy.stdin.flush()
            except InvalidGummyMessageChannel as e:
                print(f"Error sending message to Gummy: {e}")
        else:
            print("Can't send message to Gummy, he is not online!")

    @commands.hybrid_command(name="ahoy")
    async def _say_ahoy(self, ctx: commands.Context):
        """Greets the user!"""
        await ctx.send("Ahoy! 🏴‍☠️")
        await self.send_message(channel=ctx.channel, message="ahoy")

    @commands.hybrid_command(name="gummy")
    async def _launch_gummy(self, ctx: commands.Context):
        """Creates a beautiful Gummy boy."""
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
        await ctx.send("Gummy is here!", delete_after=10)

    @commands.hybrid_command(name="killgummy")
    async def _kill_gummy(self, ctx: commands.Context):
        """Puts Gummy to sleep."""
        try:
            if not self.gummy_active:
                raise GummyNotRunning("Gummy is not running!")
        except GummyNotRunning as e:
            print(e)
            return await ctx.send(e, delete_after=10)

        self.gummy.terminate()
        print("Putting Gummy to sleep....")

        try:
            self.gummy.wait(timeout=5)
        except subprocess.TimeoutExpired:
            self.gummy.kill()
            print("Gummy would not go quietly....")

        self.gummy = None
        await ctx.send("Goodbye gummy!", delete_after=10) 


async def setup(bot: commands.Bot):
    await bot.add_cog(LaunchGummy(bot))