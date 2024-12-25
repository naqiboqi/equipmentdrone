import asyncio
import datetime
import discord
import time

from functools import partial
from yt_dlp import YoutubeDL

from . import progress


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


async def get_ffmpeg_options(seek_time=0):
    """Returns the applicable ffmpeg options for the requested seek time."""
    return {
        'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
        'options': f'-vn -ss {seek_time}'
    }


class Video(discord.PCMVolumeTransformer):
    """Represents a Youtube video, with applicable attributes to store the video details."""
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
        self.progress = None
        self.seeked_time = 0.00
        self.start_time = 0.00


    def __getitem__(self, item: str):
        """Allows access to attributes similar to a dict."""
        return self.__getattribute__(item)
    
    @classmethod
    async def get_sources(
        cls, 
        ctx, 
        playlist, 
        *, 
        loop: asyncio.AbstractEventLoop,
        download=False):
        """
        Gets the source objects for each video link in the playlist.
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
        seek_time=0):
        """
        Gets the source object for the link of the requested video.
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
        Prepares a video stream for playing, and returns an instance of the video source object.
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
        """Returns the duration as an amount in seconds."""
        return datetime.timedelta(seconds=self.duration).total_seconds()
        
    async def start(self, start_time: float, volume: int):
        """Sets the intital settings for the video source object."""
        self.progress = progress.ProgressBar(self.duration)
        self.start_time = start_time
        self.volume = volume
        
    async def display(self, elapsed_time=0.00):
        """Returns an embed containing the details of video source object,
        to be used for the now-playing embed.
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