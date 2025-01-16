"""
This module implements an audio player for a Discord bot, designed to handle media 
playback and user interaction within a server (guild). It utilizes the `discord.py` 
library for bot functionality and provides features like playlist management, 
progress tracking, and detailed playback embeds.

Key Features:
- **Audio Playback**:
    - Manage playback of playlistd audio sources.
    - Support for pausing, resuming, and looping.
    - Adjust playback volume dynamically.

- **playlist Management**:
    - Handle a playlist of `Video` objects for seamless playback.
    - Add videos to the front of the playlist or in order of requests.

- **Embed Generation**:
    - Create real-time playback embeds displaying:
        - Video title, URL, and thumbnail.
        - Playback progress with a dynamic progress bar.
        - Volume level and requester information.
    - Update existing embeds as playback progresses.

- **Asynchronous Operations**:
    - Use asyncio for efficient non-blocking playlist and playback handling.
    - Manage playback state and time tracking.

### Classes:
- **`Player`**:
    Represents the media player for a Discord server. Manages:
    - Playback control, including start, pause, resume, and loop.
    - playlist operations and embed updates.
    - Cleanup and resource management when playback ends.

### Dependencies:
- **`asyncio`**: For asynchronous event handling and playlist management.
- **`discord`**: For interacting with Discord APIs and sending embeds.
- **`time`**: For tracking playback and elapsed time.
- **`video`**: Represents the media source for playback.
"""



import asyncio
import discord
import pytube
import time

from discord.ext import commands
from .constants import emojis
from .video import Video
from .videoplaylist import VideoPlaylist
from .videoplayerview import VideoPlayerView



playlist_emoji = emojis.get("playlist")



class VideoPlayer:
    """Represents a video player that awaits recieving `Video` objects
    from a playlist and playing them as needed.
    
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
            The signal to start the next video in the playlist.
        playlist : asyncio.playlist
            The playlist storing upcoming videos.
        current : Video
            The currently playing video.
        now_playing_embed : discord.Message
            The embed storing the player's current information.
        playlist_embed : discord.Message
            The embed storing the upcoming videos' information.
        loop : bool
            Whether the player is looping the current video.
        paused : bool
            Whether the player is paused.
        volume : float
            The current volume of the player as a percentage.
    """
    def __init__(self, ctx: commands.Context):
        self.bot = ctx.bot
        self.channel = ctx.channel
        self.cog = ctx.cog
        self.ctx = ctx
        self.guild = ctx.guild
        self.next = asyncio.Event()
        self.video_playlist = VideoPlaylist()

        self.current: Video = None
        self.now_playing_message: discord.Message = None
        self.playlist_message: discord.Message = None
        self.paused = False
        self.volume = .30

        ctx.bot.loop.create_task(self.player_loop())
        
    async def player_loop(self):
        await self.bot.wait_until_ready()

        while not self.bot.is_closed():
            await self.video_playlist.ready.wait()

            self.next.clear()
            source = self.video_playlist.now_playing.content
            print(source)
            
            if not isinstance(source, Video):
                print(f"Error: The next video is not valid: {source}")
                continue

            self.current = source
            start_time = time.perf_counter() - source.seeked_time
            source.start(start_time, self.volume)

            if self.current is not None and isinstance(self.current, discord.AudioSource):
                print(f"playing {self.current.title}")
                self.guild.voice_client.play(self.current, after=self.handle_after_play)
            else:
                print(f"Error: Invalid audio source {self.current}")

            await self.show_player_details()
            await self.timer(self.current.start_time)
            print("timer done!")
            
            if not self.video_playlist.loop_one:
                source.cleanup()
                
            self.current = None

    def handle_after_play(self, error):
        if error:
            print(f"Error playing video {error}")
            
        if self.video_playlist.loop_one:
            print("replaying")
            self.guild.voice_client.play(self.current)
        else:
            print("advancing")
            self.video_playlist.advance()
        

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
                await self.show_player_details(elapsed_time)
            elif self.paused:
                paused_time += 1.00
            else:
                # Case for when the video is finished playing
                elapsed_time = time.perf_counter() - (start_time + paused_time)
                await self.show_player_details(elapsed_time)
                break

    async def show_player_details(self, elapsed_time: float=0.00):
        """Creates and sends an embed showing the current details of the player:
        
        * The current video title and link
        * The progress bar
        * The current volume
        * The user who requested the video
        
        If the embed already exists, updates the current embed.
        
        Params:
        -------
            elapsed_time : float
                The elapsed time of the video, in seconds.
        """
        now_playing_embed = self.current.get_embed(elapsed_time=elapsed_time)

        try:
            self.now_playing_message = await self.now_playing_message.edit(embed=now_playing_embed)
        except AttributeError as e:
            view = VideoPlayerView(self.bot, self.ctx)
            self.now_playing_message = await self.channel.send(embed=now_playing_embed, view=view)
            print(f"Error {e}")

    async def add_videos_to_playlist(
        self, 
        ctx: commands.Context, 
        playlist_url: str):
        """
        Adds all videos in the playlist at the given url to the playlist.
        
        Params:
        -------
            ctx : commands.Context
                The current context associated with a command.
            playlist_url : str
                The url for the `Playlist` to pull sources from.
        """
        playlist = pytube.Playlist(playlist_url)
        sources = await Video.get_sources(
            ctx=ctx, playlist=playlist, loop=self.bot.loop, download=False)

        for source in sources:
            await self.video_playlist.add_to_end(source)

        await ctx.send(
            f"Added {len(playlist)} videos from **{playlist.title}** to the playlist {playlist_emoji}",
            delete_after=10)

    async def add_video_to_playlist(
        self, 
        ctx: commands.Context,
        video_search: str, 
        seek_time: int):
        """
        Adds a single video to the end of the playlist.
        
        Params:
            ctx : commands.Context
                The current context associated with a command.
            video_search : str
                The title to search for.
            seek_time : float
                The time to start the video at.
        """
        source = await Video.get_source(
            ctx=ctx, search=video_search, 
            loop=self.bot.loop, 
            download=False, 
            seek_time=seek_time)

        await self.video_playlist.add_to_end(source)
        await ctx.send(f"Added {source.title} to the playlist {playlist_emoji}", delete_after=10)
            
    async def cleanup(self):
        try:
            await self.now_playing_message.delete()
            await self.playlist_message.delete()
        except AttributeError as e:
            print(e)

    def destroy(self, guild: discord.Guild):
        """Disconnects and cleans the player.
        Useful if there is a timeout, or if the bot is no longer playing.
        """
        print("Destroying player instance.")
        return self.bot.loop.create_task(self.cog.cleanup(guild, None))
