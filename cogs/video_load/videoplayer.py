"""
This module implements an audio player for a Discord bot, designed to handle media 
playback and user interaction within a server (guild). It utilizes the `discord.py` 
library for bot functionality and provides features like queue management, 
progress tracking, and detailed playback embeds.

Key Features:
- **Audio Playback**:
    - Manage playback of queued audio sources.
    - Support for pausing, resuming, and looping.
    - Adjust playback volume dynamically.

- **Queue Management**:
    - Handle a queue of `Video` objects for seamless playback.
    - Add videos to the front of the queue or in order of requests.

- **Embed Generation**:
    - Create real-time playback embeds displaying:
        - Video title, URL, and thumbnail.
        - Playback progress with a dynamic progress bar.
        - Volume level and requester information.
    - Update existing embeds as playback progresses.

- **Asynchronous Operations**:
    - Use asyncio for efficient non-blocking queue and playback handling.
    - Manage playback state and time tracking.

### Classes:
- **`Player`**:
    Represents the media player for a Discord server. Manages:
    - Playback control, including start, pause, resume, and loop.
    - Queue operations and embed updates.
    - Cleanup and resource management when playback ends.

### Dependencies:
- **`asyncio`**: For asynchronous event handling and queue management.
- **`discord`**: For interacting with Discord APIs and sending embeds.
- **`time`**: For tracking playback and elapsed time.
- **`video`**: Represents the media source for playback.
"""


import asyncio
import discord
import time

from discord.ext import commands
from .video import Video



class VideoPlayer:
    """Represents a video player that awaits recieving `Video` objects
    from a queue and playing them as needed.
    
    Is created when the `bot` joins a voice channel, and is destroyed when
    the `bot` leaves the voice channel. Each `Guild` will have its own `Player`.

    Attributes:
    -----------
        bot : commands.Bot
            The bot instance.
        channel : discord.MessagableChannel
            The channel associated with a command.
        cog : discord.commands.Cog
            The cog associated with the current context's command.
        ctx : commands.Context
            The current context associated with a command.
        guild : discord.Guild
            The current guild associated with a command.
        next : asyncio.Event
            The signal to start the next video in the queue.
        queue : asyncio.Queue
            The queue storing upcoming videos.
        current : Video
            The currently playing video.
        now_playing_embed : discord.Embed
            The embed storing the player's current information.
        queue_embed : discord.Embed
            The embed storing the upcoming videos' information.
        loop : bool
            Whether the player is looping the current video.
        paused : bool
            Whether the player is paused.
        volume : float
            The current volume of the player as a percentage.
    """
    def __init__(self, ctx: commands.Context):
        self.bot: commands.bot = ctx.bot
        self.channel = ctx.channel
        self.cog = ctx.cog
        self.ctx = ctx
        self.guild = ctx.guild
        self.next = asyncio.Event()
        self.queue = asyncio.Queue()

        self.current: Video = None
        self.now_playing_embed: discord.Embed = None
        self.queue_embed: discord.Embed = None
        self.loop = False
        self.paused = False
        self.volume = .25

        ctx.bot.loop.create_task(self.player_loop())

    async def timer(self, start_time: float):
        """Keeps track of the video's runtime, and calls update_player_details()
        with the current time.
        
        Additionally tracks when the video is paused.

        Params:
        -------
            start_time : float 
                The start time of the video.
        """
        paused_time = 0.00
        while True:
            await asyncio.sleep(1.00)
            if self.guild.voice_client.is_playing():
                elapsed_time = time.perf_counter() - (start_time + paused_time)
                await self.update_player_details(elapsed_time)

            elif self.paused:
                paused_time += 1.00
            else:
                # Case for when the video is finished playing
                elapsed_time = time.perf_counter() - (start_time + paused_time)
                await self.update_player_details(elapsed_time)
                break    

    async def show_player_details(self):
        """Creates and sends an embed showing the current details of the player:
        
        * The current video title and link
        * The progress bar
        * The current volume
        * The user who requested the video
        
        If the embed already exists, updates the current embed.
        """
        now_playing_embed = await self.current.get_video_details()

        try:
            self.now_playing_embed = await self.now_playing_embed.edit(embed=now_playing_embed)
        except Exception as e:
            self.now_playing_embed = await self.channel.send(embed=now_playing_embed)

    async def update_player_details(self, elapsed_time: float):
        """Updates the current embed with the new elapsed time.

        Params:
        -------
            elapsed_time : float
                The elapsed time of the video, in seconds.
        """
        now_playing_embed = await self.current.get_video_details(elapsed_time)
        await self.now_playing_embed.edit(embed=now_playing_embed)

    async def player_loop(self):
        """The main loop for the media player. Runs as long as the bot is in a voice channel.

        When a `Video` is waiting in the queue, gets the start time for the `Video` and plays it in the bot's
        current voice channel. Sends the player details embed to the text channel which the play command from
        `videocontroller` was sent through.

        Times out after 1200 seconds of inactivity, after which the `Player`
        will be reset by calling `self.destroy()`.
        """
        await self.bot.wait_until_ready()

        while not self.bot.is_closed():
            self.next.clear()
            try:
                async with asyncio.timeout(1200):
                    source = await self.queue.get()
            except asyncio.TimeoutError:
                return self.destroy(self.guild)
            except asyncio.exceptions.CancelledError:
                return self.destroy(self.guild) 

            if not isinstance(source, Video):
                try:
                    source = await Video.prepare_stream(source, loop=self.bot.loop)
                except Exception as e:
                    await self.channel.send("There was an error processing your song.")
                    print(F"Error processing song {e}")
                    continue

            start_time = time.perf_counter() - source.seeked_time
            await source.start(start_time, self.volume)

            self.current = source
            self.guild.voice_client.play(
                source, 
                after=lambda song:self.bot.loop.call_soon_threadsafe(self.next.set))

            await self.show_player_details()      
            await self.timer(self.current.start_time)

            source.cleanup()
            self.current = None

    def destroy(self, guild: discord.Guild):
        """Disconnects and cleans the player.
        Useful if there is a timeout, or if the bot is no longer playing.
        """
        print("Destroying player instance.")
        return self.bot.loop.create_task(self.cog.cleanup(guild, None))
