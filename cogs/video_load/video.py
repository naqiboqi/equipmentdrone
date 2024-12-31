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
- **`asyncio`**: For asynchronous event handling and queue management.
- **`datetime`**: For tracking time and formatting strings.
- **`discord`**: For interacting with Discord APIs and sending embeds.
- **`time`**: For string formatting with time fields.
- **`functools`**: Provides utility functions, such as `partial`,
    used to create reusable function arguments for asynchronous tasks.
- **`pytube`**: For downloading and processing YouTube videos.
- **`yt_dlp`**: For playlist management.
- **`progress`**: For visual representing the progress a video
"""


import asyncio
import datetime
import discord
import time

from functools import partial
from pytube import Playlist
from yt_dlp import YoutubeDL

from .progress import ProgressBar



YTDL_FORMATS = {
    'format' : 'bestaudio/best',
    'outtmpl' : 'downloads/%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames' : True,
    'noplaylist' : True,
    'nocheckcertificate' : True,
    'ignoreerrors' : False,
    'logtostderr' : False,
    'quiet' : True,
    'no_warnings': True,
    'default_search' : 'auto',
    'source_address' : '0.0.0.0'
}


ytdl = YoutubeDL(YTDL_FORMATS)



async def get_ffmpeg_options(seek_time=0.00):
    """Returns the applicable ffmpeg options for the requested video.
    
    Params:
    -------
    `seek_time` (float): Time to seek to in the video, in seconds.
    """
    return {
        'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
        'options': f'-vn -ss {seek_time}'
    }


class Video(discord.PCMVolumeTransformer):
    """Represents a Youtube video, with applicable attributes to store the video metadata.
    
    Inherits from `PCMVolumeTransformer` to allow volume control of the source.

    Attributes:
    -----------
        `source` (FFmpegPCMAudio): The audio source obtained through ffmpeg.
        `data` (dict[str, str|int]): The metadata for the audio source.
        `title` (str): The title of the source video.
        `web_url` (str): The web url that the source video originated from.
        `video_id` (str): The video-id of the source video.
        `thumbnail` (str): The thumbnail url of the source video.
        `elapsed_time` (float): The elapsed time of the video, in seconds.
        `progress` (ProgressBar): Represents a video's progress bar with a slider denoting the elapsed time.
        `seeked_time` (float): The start/seek time of the video in seconds, defaults to 0.00.
        `start_time` (float): The start time of the video.
    """
    def __init__(
        self,
        source: discord.player.FFmpegPCMAudio,
        *, 
        data: dict[str, str|int], 
        requester: discord.member.Member, 
        duration: int):

        super().__init__(source)
        self.duration = duration
        self.requester = requester
        self.title = data.get('title')
        self.web_url = data.get('webpage_url')
        self.video_id = self.web_url.split("=", 1)[1]
        self.thumbnail = F"https://i1.ytimg.com/vi/{self.video_id}/hqdefault.jpg"

        self.elapsed_time = 0.00
        self.progress: ProgressBar = None
        self.seeked_time = 0.00
        self.start_time = 0.00


    def __getitem__(self, item: str):
        """Allows access to attributes similar to a dict."""
        return self.__getattribute__(item)

    @classmethod
    async def get_sources(
        cls, 
        ctx, 
        playlist: Playlist, 
        *, 
        loop: asyncio.AbstractEventLoop,
        download=False):
        """
        Gets the source object for each video in the playlist through its url.
        
        Params:
            `ctx` (Context): The current context associated with a command.
            `playlist` (pytube.Playlist): Contains the videos to obtain the sources from.
            `loop` (AbstractEventLoop): The event loop to use for asynchronous operations. 
                If not provided, the default event loop for the current thread will be used.
                
            `download` (bool): Whether to download the video or not.

        Note that any privated videos will be skipped.
        """
        tasks = [cls.get_source(ctx=ctx, search=url, loop=loop, download=download)
            for url in playlist.video_urls]

        return await asyncio.gather(*tasks)

    @classmethod
    async def get_source(
        cls, 
        ctx, 
        search: str, 
        *, 
        loop: asyncio.AbstractEventLoop, 
        download=False, 
        seek_time=0.00):
        """
        Gets the source for the video obtained from searching for the `string`, returning the first
        result from Youtube.
        
        Params:
            `ctx` (Context): The current context associated with a command.
            `playlist` (pytube.Playlist): Contains the videos to obtain the sources from.
            `loop` (AbstractEventLoop): The event loop to use for asynchronous operations.
                If not provided, the default event loop for the current thread will be used.

            `download` (bool): Whether to download the video or not.
            `seek_time` (float): The seek time of the video in seconds.
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

        options = await get_ffmpeg_options(seek_time=seek_time)
        return cls(
            discord.FFmpegPCMAudio(filename, **options),
            data=data,
            requester=ctx.author,
            duration=data['duration']
        )

    @classmethod
    async def prepare_stream(
        cls, 
        data: "Video", 
        *, 
        loop: asyncio.AbstractEventLoop):
        """
        Prepares a video stream for playing, and returns an instance of that video object.

        Params:
        -------
            `data` (Video): The video data object to prepare for streaming.
            `loop` (AbstractEventLoop): The event loop to use for asynchronous operations.
                If not provided, the default event loop for the current thread will be used.
        """
        loop = loop or asyncio.get_event_loop()
        requester = data['requester']
        duration = data['duration']

        to_run = partial(ytdl.extract_info, url=data['webpage_url'], download=False)
        data = await loop.run_in_executor(None, to_run)

        return cls(
            discord.FFmpegPCMAudio(data['url']), data=data, 
            requester=requester, duration=duration)

    def get_duration_datetime(self):
        """Returns the video duration as an amount in seconds."""
        return datetime.timedelta(seconds=self.duration).total_seconds()

    async def start(self, start_time: float, volume: float):
        """Initializes the settings for the video source object.
        
        Params:
        -------
            `start_time` (float): The start time of the video.
            `volume` (float): The current volume of the player as a percentage.
        """
        self.progress = ProgressBar(self.duration)
        self.start_time = start_time
        self.volume = volume

    async def display(self, elapsed_time=0.00):
        """Returns an embed containing the details of video source object.

        Params:
        -------
            `elapsed_time` (float): The elapsed time of the video, in seconds.
        """
        self.elapsed_time = elapsed_time
        elapsed_field = time.strftime('%H:%M:%S', time.gmtime(elapsed_time))
        duration_field = time.strftime('%H:%M:%S', time.gmtime(self.duration))
        desc_field = (F"""`{elapsed_field}`|`{duration_field}`
            **Requested by {(str(self.requester.mention))}**""")

        current_progress = self.progress.display(elapsed_time)
        now_playing_embed = discord.Embed(
            title=self.title, url=self.web_url,
            description=(F"\n\n{current_progress}\n\n{desc_field}"),
            color=0xa84300)

        now_playing_embed.set_footer(text=F"Volume: {self.volume * 100}%")
        now_playing_embed.set_thumbnail(url=self.thumbnail)

        return now_playing_embed
