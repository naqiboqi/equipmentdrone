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
- **`VideoController`**:
    Manages video playback in a Discord guild. Handles:
    - Playback control (start, pause, resume, loop).
    - Queue operations and embed updates.
    - Resource cleanup upon playback end.

### Constants:
- **`LYRICS_URL`**: The api url for obtaining video lyrics.

### Dependencies:
- **`asyncio`**: For asynchronous event handling and queue management.
- **`discord`**: For interacting with Discord APIs and sending embeds.

- **`itertools`**: For creating and managing queues.
- **`pytube`**: For downloading and processing YouTube videos.
- **`typing`**: For type hinting and function signatures.
- **`discord.ext`**: For Discord bot command usage.
- **`random`**: For shuffling the queue.
- **`video`**: For representing video sources.
- **`videoplayer`**: For playing queued videos.
"""



import aiohttp
import discord

from discord.ext import commands
from random import shuffle
from typing import Optional
from .video_load import VideoPlayer
from .video_load import LYRICS_URL
from .utils import PageView



class VideoController(commands.Cog):
    """Commands to represent media controls for the bot's video player.
    
    Attributes:
    -----------
        bot : commands.Bot
            The bot instance.
        players : dict[int, VideoPlayer]
            The video players associated with each guild's id.
        player_ctx : commands.Context
            The most recently invoked context.
    """
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.players: dict[int, VideoPlayer] = {}
        self.player_ctx: commands.Context = None

    async def cleanup(self, guild: discord.Guild, ctx: commands.Context):
        """Cleans up the server's player and the ffmpeg client.
        
        Params:
        -------
            guild : discord.Guild
                The guild the command was invoked in.
            ctx : commands.Context
                The current context associated with a command.
            """
        if ctx is None:
            ctx = self.player_ctx

        player = self.get_player(ctx)
        player.video_playlist.cleanup() 

        try:
            await guild.voice_client.disconnect()
        except AttributeError as e:
            print(e)

        try:
            del self.players[guild.id]
        except KeyError as e:
            print(e)

    def get_player(self, ctx: commands.Context):
        """Retrieves the player for a guild given, 
        otherwise creates it if that guild has no player.
        
        Params:
        -------
            ctx : commands.Context
                The current context associated with a command.
        """
        try:
            player = self.players[ctx.guild.id]
        except AttributeError:
            player = VideoPlayer(ctx)
            self.players[ctx.guild.id] = player
        except KeyError:
            player = VideoPlayer(ctx)
            self.players[ctx.guild.id] = player

        return player

    @commands.hybrid_command(name='join', aliases=['connect'])
    async def _connect(self, ctx: commands.Context):
        """Connects the bot to your current voice channel.
        
        Params:
        -------
            ctx : commands.Context
                The current context associated with a command.
        """
        if ctx.author.voice:
            channel = ctx.message.author.voice.channel
            return await channel.connect()

        await ctx.send("You must be in a voice channel!", delete_after=10)

    @commands.hybrid_command(name='play')
    async def _play(self, ctx: commands.Context, *, video_search: str):
        """Searches for a video and adds it to the queue.
        
        Will also add all videos from a playlist in order, if the given link is for a playlist.
        
        Params:
        -------
            ctx : commands.Context
                The current context associated with a command.
            video_search : str
                The video title to search for, or a direct link to a video or playlist.
        """
        vc = ctx.voice_client
        if not vc:
            await ctx.invoke(self._connect)

        if not video_search:
            return await ctx.send(
                "Please provide a video to look for.", delete_after=10)

        player = self.get_player(ctx)
        self.player_ctx = ctx

        # Need to defer, as Discord will invalidate the interaction if it takes more
        # than 3 seconds to respond to the command.
        await ctx.defer()

        is_playlist = "playlist?list=" in video_search
        seek_time = int(video_search.split("&t=")[-1]) if "&t=" in video_search else 0.00

        try:
            if is_playlist:
                await player.add_videos_to_playlist(ctx, video_search)
            else:
                await player.add_video_to_playlist(ctx, video_search, seek_time)
        # A likely result if the playlist is privated.
        except Exception as e:
            await ctx.send(f"An error occurred: {e}", delete_after=10)

    @commands.hybrid_command(name='now', aliases=['np'])
    async def _now_playing(self, ctx: commands.Context):
        """Sends a embed showing info for the current video.
        
        Params:
        -------
            ctx : commands.Context
                The current context associated with a command.
        """
        vc = ctx.voice_client
        if not vc or not vc.is_connected:
            return await ctx.send(
                "I am not currently playing anything!",
                delete_after=10)
            
        player = self.get_player(ctx)
        if player.now_playing_message:
            await player.now_playing_message.delete()
            now_playing_embed = player.current.get_embed()
            player.now_playing_message = await ctx.send(embed=now_playing_embed)

    @commands.hybrid_command(name='playlist')
    async def _show_upcoming(self, ctx: commands.Context):
        """Displays the next 10 videos in the queue within an embed.
        
        Params:
            ctx : commands.Context
                The current context associated with a command.
        """
        vc = ctx.voice_client
        if not vc or not vc.is_connected():
            return await ctx.send(
                "I am not currently connected to voice!", delete_after=10)

        player = self.get_player(ctx)
        view = PageView(
            f"Upcoming Videos {player.video_playlist}",
            player.video_playlist.get_upcoming())
        
        player.playlist_message = await ctx.send(embed=view.pages[0], view=view)
    
    @commands.hybrid_command(name='pause')
    async def _pause(self, ctx: commands.Context):
        """Pauses or unpauses the current video.
        
        Params:
        -------
            ctx : commands.Context
                The current context associated with a command.
        """
        vc = ctx.voice_client
        if not vc or not vc.is_connected():
            return await ctx.send(
                "I am not currently playing anything!", delete_after=10)

        player = self.get_player(ctx)
        if player.paused:
            vc.resume()
            player.paused = False
        else:
            vc.pause()
            player.paused = True
            
        await ctx.send("Paused the video" if player.paused else "Unpaused the video.", delete_after=10)

    @commands.hybrid_command(name='skip')
    async def _skip(self, ctx: commands.Context):
        """Skips to the next video.
        
        Params:
        -------
            ctx : commands.Context
                The current context associated with a command.
        """
        vc = ctx.voice_client
        if not vc or not vc.is_connected():
            return await ctx.send(
                "I am not currently playing anything!", delete_after=10)

        vc.stop()
        await ctx.send("Skipped the video.", delete_after=10)

    @commands.hybrid_command(name='stop')
    async def _stop(self, ctx: commands.Context):
        """Stops the currently playing video.
        
        Params:
        -------
            ctx : commands.Context
                The current context associated with a command.
        """
        vc = ctx.voice_client
        if not vc or not vc.is_connected():
            return await ctx.send(
                "I am not currently playing anything!", delete_after=10)

        await self.cleanup(ctx.guild, ctx)
        await ctx.send("Stopped the player.", delete_after=10)

    @commands.hybrid_command(name='volume', aliases=['vol'])
    async def _change_volume(self, ctx: commands.Context, *, vol: int):
        """Sets the player volume to the given value.
        
        Params:
            ctx : commands.Context
                The current context associated with a command.
            vol : int
                The new volume level, must be between `1` and `100`.
        """
        vc = ctx.voice_client
        if not vc or not vc.is_connected():
            return await ctx.send(
                "I am not currently connected to voice!", delete_after=10)
        elif (not 1 <= vol <= 100) or (vol is None):
            return await ctx.send(
                "Please enter a value between 1 and 100.", delete_after=10)
        elif vc.source:
            vc.source.volume = vol / 100

        player = self.get_player(ctx)
        player.volume = vol / 100
        await ctx.send(f"Set the volume to {vol}%.", delete_after=10)
        
    @commands.command(name="loop")
    async def _loop(self, ctx: commands.Context):
        pass
        
        
    @commands.hybrid_command(name='removevideo', aliases=['rremove'])
    async def _remove(self, ctx: commands.Context, *, spot: int):
        """Removes a video at the given spot in the queue.
        
        Params:
        -------
            ctx : commands.Context
                The current context associated with a command.
            spot : int
                The index of the video to remove.
        """
        player = self.get_player(ctx)
        try:
            source = player.video_playlist.remove(spot)
        except IndexError:
            return await ctx.send(
                f"There is no video at spot {spot} in the queue.", delete_after=10)

        await ctx.send(
            f"Removed `{source.title}` from spot {spot} in the queue.", 
            delete_after=10)    

    @commands.hybrid_command(name='shuffle')
    async def _shuffle(self, ctx: commands.Context):
        """Shuffles all videos in the queue.
        
        Params:
        -------
            ctx : commands.Context
                The current context associated with a command.
        """
        player = self.get_player(ctx)
        player.video_playlist.shuffle()
        await ctx.send("Shuffled the playlist.", delete_after=10)
        
    @commands.hybrid_command(name='lyrics', aliases=['lyric'])
    async def _lyrics(
        self, 
        ctx: commands.Context, 
        *, 
        video_search: Optional[str]):
        """
        Gets the lyrics for the current video or search for a video given a name.
        
        Uses the text obtained through some-random-api's lyric function.
        
        Params:
        -------
            ctx : commands.Context
                The current context associated with a command.
            video_search : str
                The title whose lyrics to search for.
        """
        vc = ctx.voice_client
        if not vc or vc.is_connected():
            return await ctx.send(
                "I am not currently playing anything!", delete_after=10)

        video_search = video_search or vc.source.title
        async with ctx.typing():
            try:
                async with aiohttp.request(
                    "GET", LYRICS_URL + video_search, headers={}) as response:
                    if (not 200 <= response.status <= 299
                    or response.content_type != "application/json"):
                        return await ctx.send("No lyrics found.")

                    data = await response.json()

                # Split the message to stay within the 2000 character limit.
                lyrics = data["lyrics"]
                if len(lyrics) > 2000:
                    for chunk in [lyrics[i : i + 2000] for i in range(0, len(lyrics), 2000)]:
                        await ctx.send(chunk)
                        
                    return

                lyrics_embed = discord.Embed(
                    title=data["title"],
                    description=lyrics,
                    color=0xa84300)

                lyrics_embed.set_thumbnail(url=data['thumbnail']['genius'])
                lyrics_embed.set_author(name=f"{data['author']}")
                await ctx.send(embed=lyrics_embed)

            except aiohttp.ClientError:
                return await ctx.send("Failed to connect to the lyrics API.", delete_after=10)
            except Exception as e:
                return await ctx.send(f"An unknown error occured: {e}")


async def setup(bot: commands.Bot):
    await bot.add_cog(VideoController(bot))
