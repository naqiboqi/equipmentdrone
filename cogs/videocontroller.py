"""
This module implements a video player cog for a Discord bot, designed to manage video playback 
and user interaction within a server (guild). It utilizes the `discord.py` library to 
interact with Discord APIs, providing functionality for media playback, queue management, 
and detailed playback embeds.

### Key Features:
- **Video Playback**:
    - Manage playback of queued video sources.
    - Support for pausing, resuming, looping, and volume control.
    - Handling of YouTube video links and playlists.

- **Queue Management**:
    - Manage a queue of `Video` objects for seamless playback.
    - Add videos to the front of the queue or in order of requests.
    - Skip to the next video or replay videos in the queue.

- **Embed Generation**:
    - Generate real-time playback embeds displaying:
        - Video title, URL, and thumbnail.
        - Playback progress with a dynamic progress bar.
        - Volume level and requester information.
    - Update playback embeds as the video progresses.

- **Asynchronous Operations**:
    - Utilize `asyncio` for non-blocking queue and playback handling.
    - Manage playback state and elapsed time tracking efficiently.

### Classes:
- **`VoiceConnectionError`**:
    Custom exception class for handling connection errors.

- **`InvalidVoiceChannel`**:
    Exception for cases of invalid voice channels.

- **`VideoController`**:
    Manages video playback in a Discord guild. Handles:
    - Playback control (start, pause, resume, loop).
    - Queue operations and embed updates.
    - Resource cleanup upon playback end.

### Methods in `VideoController`:

- **`connect_`**:
    Connects the bot to the voice channel of the user who invoked the command.
    - If the user is not in a voice channel, the command does nothing.

- **`play_`**:
    Adds the video(s) to the end of the queue given a direct link or name to search for. 
    Handles playlists and private videos.

- **`add_playlist_to_queue`**:
    Adds all videos in the provided playlist URL to the queue.

- **`add_video_to_queue`**:
    Adds a single video to the end of the queue.

- **`now_playing_`**:
    Displays the current video being played along with its details in an embed format.

- **`pause_`**:
    Pauses or unpauses the currently playing video.

- **`lyrics_`**:
    Fetches and displays lyrics for the currently playing video or a provided song name.

- **`get_queue_`**:
    Displays the next up to ten videos in the queue.

- **`remove_`**:
    Removes a specific video from a given spot in the queue.

- **`shuffle_`**:
    Shuffles the queue, does not affect the currently playing video.

- **`skip_`**:
    Skips the currently playing video.

- **`stop_`**:
    Stops the currently playing video and cleans up the player.

- **`change_volume`**:
    Adjusts the player volume to the specified level (1-100).

### Dependencies:
- **`discord`**: For interacting with Discord APIs and sending embeds.
- **`asyncio`**: For asynchronous event handling and queue management.
- **`pytube`**: For downloading and processing YouTube videos.
- **`itertools`**: For creating and managing queues.
- **`typing`**: For type hinting and function signatures.
"""


import aiohttp
import discord
import datetime
import itertools
import pytube
import typing

from discord.ext import commands
from random import shuffle

from . import videoplayer
from . import video


LYRICS_URL = "https://some-random-api.ml/lyrics?title="



class VoiceConnectionError(commands.CommandError):
    """Custom Exception class for connection errors."""


class InvalidVoiceChannel(VoiceConnectionError):
    """Exception for cases of invalid voice channels."""


class VideoController(commands.Cog):
    """Commands to represent media controls for the bot's video player."""
    def __init__(self, bot):
        self.bot = bot
        self.players = {}
        self.player_ctx = None


    async def cleanup(self, guild, ctx):
        """Cleans up the server's player and the ffmpeg client."""
        if ctx is None:
            ctx = self.player_ctx

        player = self.get_player(ctx)
        player.loop = False
        player.queue._queue = [] 

        try:
            await guild.voice_client.disconnect()
        except AttributeError as e:
            print(e)

        try:
            del self.players[guild.id]
        except KeyError as e:
            print(e)

    def get_player(self, ctx):
        """Retrieves the player for a guild, 
        or creates it if the guild does not have one.
        """
        try:
            player = self.players[ctx.guild.id]
        except AttributeError:
            player = videoplayer.Player(ctx)
            self.players[ctx.guild.id] = player
        except KeyError:
            player = videoplayer.Player(ctx)
            self.players[ctx.guild.id] = player

        return player

    @commands.hybrid_command(name='join', aliases=['connect'])
    async def connect_(self, ctx):
        """Connects the bot to your current voice channel."""
        if ctx.author.voice:
            channel = ctx.message.author.voice.channel
            await channel.connect()

    @commands.hybrid_command(name='play')
    async def play_(self, ctx, *, video_search: str):
        """Searches for a video and adds it to the queue. Can also add playlists given a link.
        
        Will also add all videos from a playlist in order,
        if the given link is for a playlist.
        
        Any privated videos will not be added.
        """
        vc = ctx.voice_client
        if not vc:
            await ctx.invoke(self.connect_)

        if not video_search:
            return await ctx.send(
                "Please provide a video to look for.",
                delete_after=10)

        player = self.get_player(ctx)
        self.player_ctx = ctx

        # Need to defer, as Discord will invalidate the interaction if it takes more
        # than 3 seconds to respond to the command.
        await ctx.defer()

        playlist_flag = "playlist?list=" in video_search
        seek_time = int(video_search.split("&t=")[-1]) if "&t=" in video_search else 0

        try:
            if playlist_flag:
                await self.add_playlist_to_queue(ctx, player, video_search)
            else:
                await self.add_video_to_queue(ctx, player, video_search, seek_time)

        # A likely result if the playlist is privated.
        except Exception as e:
            await ctx.send(f"An error occurred: {e}", delete_after=10)

    async def add_playlist_to_queue(
        self, 
        ctx, 
        player: videoplayer.Player, 
        playlist_url: str):
        """
        Adds all videos in the playlist at the given url to the queue.
        
        Any privated videos will not be added.
        """
        playlist = pytube.Playlist(playlist_url)
        sources = await video.Video.get_sources(
            ctx=ctx, playlist=playlist, loop=self.bot.loop, download=False)

        for source in sources:
            await player.queue.put(source)

        await ctx.send(
            f"Added {len(playlist)} videos from **{playlist.title}** to the queue.",
            delete_after=10)

    async def add_video_to_queue(
        self, 
        ctx, 
        player: videoplayer.Player, 
        video_search: str, 
        seek_time: int):
        """
        Adds a single video to the end of the queue.
        """
        source = await video.Video.get_source(
            ctx=ctx, search=video_search, 
            loop=self.bot.loop, 
            download=False, 
            seek_time=seek_time)

        await player.queue.put(source)
        await ctx.send(f"Added {source.title} to the queue.", delete_after=10)

    @commands.hybrid_command(name='now', aliases=['np'])
    async def now_playing_(self, ctx):
        """Sends a embed showing info for the current vidoe."""
        vc = ctx.voice_client
        player = self.get_player(ctx)

        if not vc or not vc.is_connected:
            return await ctx.send(
                "I am not currently playing anything!",
                delete_after=10)

        if player.now_playing_embed is not None:
            await player.now_playing_embed.delete()
            now_playing_embed = await player.current.display()
            player.now_playing_embed = await ctx.send(embed=now_playing_embed)

    @commands.hybrid_command(name='pause')
    async def pause_(self, ctx):
        """Pauses or unpauses the current video."""
        vc = ctx.voice_client
        player = self.get_player(ctx)

        if not vc or not vc.is_connected():
            return await ctx.send(
                "I am not currently playing anything!", delete_after=10)

        if player.paused:
            vc.resume()
            player.paused = False
            await ctx.send("Unpaused", delete_after=10)
        else:
            vc.pause()
            player.paused = True
            await ctx.send("Paused", delete_after=10)

    @commands.hybrid_command(name='lyrics', aliases=['lyric'])
    async def lyrics_(self, ctx, *, name: typing.Optional[str]):
        """Gets the lyrics for the current video or search for a video given a name.
        
        Uses the text obtained through some-random-api's lyric function.
        """
        vc = ctx.voice_client
        name = name or vc.source.title

        async with ctx.typing():
            async with aiohttp.request("GET", LYRICS_URL + name, headers={}) as response:
                if (not 200 <= response.status <= 299
                or response.content_type != "application/json"):
                    return await ctx.send("No lyrics found.")

                data = await response.json()
                try:
                    if len(data['lyrics']) > 2000:
                        await ctx.send(f"<{data['links']['genius']}>")
                except KeyError:
                    return await ctx.send("Couldn't find the lyrics for this video.")

                lyrics_embed = discord.Embed(
                    title=data["title"],
                    description=data["lyrics"],
                    color=0xa84300)

                lyrics_embed.set_thumbnail(url=data['thumbnail']['genius'])
                lyrics_embed.set_author(name=f"{data['author']}")
                await ctx.send(embed=lyrics_embed)

    @commands.hybrid_command(name='queue', aliases=['q', 'playlist'])
    async def get_queue_(self, ctx):
        """Shows the next 10 videos in the queue."""
        vc = ctx.voice_client
        if not vc or not vc.is_connected():
            return await ctx.send(
                "I am not currently connected to voice!", delete_after=10)

        player = self.get_player(ctx)
        if player.queue.empty():
            return await ctx.send("The queue is empty.")

        upcoming = list(itertools.islice(player.queue._queue, 0, 10))
        video_names = '\n'.join(
            f"{index + 1}. **{video['title']}** |"
            f"`{datetime.timedelta(
                seconds=video['duration'])}`"
                for index, video in enumerate(upcoming))

        queue_embed = discord.Embed(
            title=f"Upcoming - Next {len(upcoming)} videos",
            description=video_names,
            color=0x206694)

        await ctx.send(embed=queue_embed)

    @commands.hybrid_command(name='removevideo', aliases=['r'])
    async def remove_(self, ctx, *, spot: int):
        """Removes a video at the given spot in the queue."""
        player = self.get_player(ctx)
        videos_queue = player.queue._queue
        try:
            video_title = videos_queue[spot - 1]['title']
            del videos_queue[spot - 1]
        except IndexError:
            return await ctx.send(
                f"There is no video at spot {spot} in the queue.",
                delete_after=10)

        await ctx.send(
            f"Removed `{video_title}` from spot {spot} in the queue.", 
            delete_after=10)    

    @commands.hybrid_command(name='shuffle')
    async def shuffle_(self, ctx):
        """Shuffles all videos in the queue."""
        player = self.get_player(ctx)
        videos = player.queue._queue
        shuffle(videos)
        await ctx.send("Shuffled.", delete_after=10)

    @commands.hybrid_command(name='skip')
    async def skip_(self, ctx):
        """Skips the currently playing video."""
        vc = ctx.voice_client
        if not vc or not vc.is_connected():
            return await ctx.send(
                "I am not currently playing anything!", delete_after=10)
        elif not vc.is_playing():
            return

        vc.stop()
        await ctx.send("Skipped the video.", delete_after=10)

    @commands.hybrid_command(name='stop')
    async def stop_(self, ctx):
        """Stops the currently playing video."""
        vc = ctx.voice_client
        if not vc or not vc.is_connected():
            return await ctx.send("I am not currently playing anything!", delete_after=10)

        await self.cleanup(ctx.guild, ctx)
        await ctx.send("Stopped the video.", delete_after=10)

    @commands.hybrid_command(name='volume', aliases=['vol'])
    async def change_volume(self, ctx, *, vol: int):
        """Sets the player volume, must be between `1` and `100`."""
        vc = ctx.voice_client
        if not vc or not vc.is_connected():
            return await ctx.send(
                "I am not currently connected to voice!", delete_after=10)
        elif ((not 1 <= vol <= 100) or (vol is None)):
            return await ctx.send(
                "Please enter a value between 1 and 100.", delete_after=10)
        elif vc.source:
            vc.source.volume = vol / 100

        player = self.get_player(ctx)
        player.volume = vol / 100
        await ctx.send(f"Set the volume to {vol}%.", delete_after=10)


async def setup(bot):
    await bot.add_cog(VideoController(bot))
