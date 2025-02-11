"""
This module integrates YouTube video playback into a Discord bot using the `discord.py` 
library and `yt-dlp`. It includes classes and functions to handle video playback, 
progress tracking, and embed generation for seamless user interaction.

Key Features:
- **YouTube Video Handling**:
    - Extract video metadata such as title, duration, and URL.
    - Support for single video links and playlists.
    - Prepare video streams using FFmpeg for Discord playback.

- **Discord Bot Integration**:
    - Create `Video` objects for managing audio playback.
    - Generate real-time embed messages showing playback progress, video details, and requester information.

- **Progress Tracking**:
    - Visualize video progress using a progress bar.
    - Manage playback states, including elapsed time and seeked positions.

- **Asynchronous Operations**:
    - Leverage asyncio for non-blocking operations.
    - Fetch video data and prepare audio streams.

### Classes:
- **`Video`**:
    Represents a YouTube video and includes attributes and methods to:
    - Store video metadata (title, duration, URL, thumbnail, etc.).
    - Prepare and manage audio streams.
    - Generate playback progress and now-playing embeds.

### Constants:
- **`YTDL_FORMATS`**:
    Configuration dictionary for `yt-dlp`, specifying formats and options for video extraction.

### Dependencies:
- **`asyncio`**: For asynchronous event handling.
- **`discord`**: For interacting with Discord APIs and sending embeds.
- **`time`**: For string formatting with time fields.
- **`functools`**: Provides utility functions, such as `partial`,
    used to create reusable function arguments for asynchronous tasks.
- **`pytube`**: For downloading and processing YouTube videos.
- **`yt_dlp`**: For playlist management.
- **`progress`**: For visual representing the progress a video.
"""



import asyncio
import discord
import time

from discord.ext import commands
from functools import partial
from pytube import Playlist
from yt_dlp import YoutubeDL
from .constants import emojis
from .progress import ProgressBar



sound_low = emojis.get("sound_low")
sound_on = emojis.get("sound_on")
playing = emojis.get("now_playing")
loop_one = emojis.get("repeat_one")
loop_all = emojis.get("repeat_all")
loop_none = emojis.get("repeat_none")


YTDL_FORMATS = {
    'format': 'bestaudio/best',
    'outtmpl': 'downloads/%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'
}
"""
Configuration settings for the `youtube_dl` (YTDL) instance, specifying various options for downloading 
audio and video content from online sources.

The settings define how the downloaded files should be named, which format should be chosen for audio, 
and other preferences related to error handling, logging, and connection behavior.
"""

ytdl = YoutubeDL(YTDL_FORMATS)



class Video(discord.PCMVolumeTransformer):
    """Represents a Youtube video, with applicable attributes to store the video data.

    Attributes:
    -----------
    source : discord.FFmpegPCMAudio
        The audio source obtained through ffmpeg.
    duration : int
        The length of the video in seconds.
    title : str
        The title of the video.
    web_url : str
        The web URL that the video originated from.
    video_id : str
        The video-id of the video.
    thumbnail : str
        The thumbnail URL of the video.
    elapsed_time : float
        The elapsed time of the video in seconds.
    start_time : float
        The start time of the video.
    seeked_time : float
        The seeked time of the video in seconds.
    progress : ProgressBar
        Represents a video's progress bar with a slider denoting the elapsed time.
    """
    def __init__(
        self,
        source: discord.FFmpegPCMAudio,
        *,
        data: dict[str, str|int],
        requester: discord.member.Member):
        super().__init__(source)
        self.duration = data.get('duration')
        self.title  = data.get('title')
        self.uploader = data.get('uploader')
        self.web_url = data.get('webpage_url')
        self.video_id = self.web_url.split("=", 1)[1]
        self.thumbnail = f"https://i1.ytimg.com/vi/{self.video_id}/hqdefault.jpg"
        self.requester = requester

        self.elapsed_time = 0.00
        self.start_time = 0.00
        self.seek_time = 0.00
        self.progress: ProgressBar = None

    def __getitem__(self, item_name: str):
        """Allows access to attributes similarly to a dict.
        
        Params:
        -------
        item_name : str
            The attribute name to access.
        """
        return self.__getattribute__(item_name)

    @classmethod
    async def get_sources(
        cls,
        ctx: commands.Context,
        playlist: Playlist,
        *,
        loop: asyncio.AbstractEventLoop,
        options: dict[str, str]):
        """Gets the source object for each video in the playlist through its URL.

        Params:
        -------
        ctx : commands.Context
            The current context associated with a command.
        playlist : Playlist
            The videos to obtain the sources from.
        loop : asyncio.AbstractEventLoop
            The event loop to use for asynchronous operations. If not provided, 
            the default event loop for the current thread will be used.
        options : dict[str, str]
            The ffmpeg options to apply.
        """
        tasks = [
            cls.get_source(ctx=ctx, search=url, loop=loop, options=options)
            for url in playlist.video_urls]

        return await asyncio.gather(*tasks)

    @classmethod
    async def get_source(
        cls,
        ctx: commands.Context,
        search: str,
        *,
        loop: asyncio.AbstractEventLoop,
        download: bool=False,
        options: dict[str, str]):
        """Gets the source for the video obtained from searching for the `string`,
        returning the first result from YouTube.

        Params:
        -------
        ctx : commands.Context
            The current context associated with a command.
        search : str
            The string to search for.
        loop : asyncio.AbstractEventLoop
            The event loop to use for asynchronous operations. If not provided, 
                the default event loop for the current thread will be used.
        download : bool
            Whether to download the video or not.
        options : dict[str, str]
            The ffmpeg options to apply.
        """
        loop = loop or asyncio.get_event_loop()
        to_run = partial(ytdl.extract_info, url=search, download=download)
        data = await loop.run_in_executor(None, to_run)

        if 'entries' in data:
            data = data['entries'][0]

        if download:
            filename = ytdl.prepare_filename(data)
        else:
            filename = data['url']

        return cls(
            discord.FFmpegPCMAudio(filename, **options),
            data=data,
            requester=ctx.author)

    def start(self, start_time: float, volume: float):
        """Initializes the settings for the video source object.

        Params:
        -------
        start_time : float
            The start time of the video.
        volume : float
            The current volume of the player as a percentage.
        """
        self.progress = ProgressBar(self.duration)
        self.start_time = start_time
        self.volume = volume

    def get_embed(self, elapsed_time: float=0.00, loop: str=None):
        """Returns an embed containing the details of the video source object.

        Params:
        -------
        elapsed_time : float
            The elapsed time of the video, in seconds.
        loop : str
            The type of loop, if the player is looping. Can be `all`, `one` or `none`.
        """
        self.elapsed_time = elapsed_time
        elapsed = time.strftime('%H:%M:%S', time.gmtime(elapsed_time))
        duration = time.strftime('%H:%M:%S', time.gmtime(self.duration))
        time_field = f"`{elapsed}|{duration}`"

        current_progress = self.progress.get_progress(elapsed_time)
        vol_emoji = sound_low if self.volume <= 0.40 else sound_on
        volume_field = f"{vol_emoji}: {self.volume * 100}%"

        if loop == "all":
            loop_emoji = loop_all
        elif loop == "one":
            loop_emoji = loop_one
        else:
            loop_emoji = loop_none

        now_playing_embed = discord.Embed(
            title=f"{emojis.get('now_playing')}  NOW PLAYING",
            description=f"""

            [{self.title}]({self.web_url}) **by** `{self.uploader}`

            {time_field}
            {current_progress}""",
            color=discord.Color.from_str("#dd7c1f"))

        now_playing_embed.add_field(
            name=f"** **", 
            value=f"Volume: {volume_field}", 
            inline=True)

        now_playing_embed.add_field(
            name=f"** **", 
            value=f"Looping: {loop_emoji}", 
            inline=True)

        now_playing_embed.set_thumbnail(url=self.thumbnail)
        now_playing_embed.set_footer(text=f"Requested by: {self.requester.name}")

        return now_playing_embed
