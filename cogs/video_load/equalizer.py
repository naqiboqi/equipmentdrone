from discord.ext import commands



class Filter:
    def __init__(self, name: str, settings: str):
        self.name = name
        self.settings = settings

    def __str__(self):
        return f"Filter: {self.name} ({self.settings})"

    @property
    def apply(self):
        return f"equalizer={self.settings}"



class Equalizer:
    """Representation of an equalizer for controlling ffmpeg settings.
    
    Attributes:
        ctx : commands.Context
            The current context.
        filters : dict[str, str].
            The possible presets and their settings.
        current_filter : Filter
            The current filter.
    """
    def __init__(self, ctx: commands.Context):
        self.ctx = ctx
        self.filters = {
            "super_bass_boost": Filter("Super Bass Boost", "f=60:width_type=h:width=200:g=30"),
            "bass_boost": Filter("Bass Boost", "f=60:width_type=h:width=200:g=10"),
            "treble_boost": Filter("Treble Boost", "f=1000:width_type=h:width=200:g=10"),
            "flat": Filter("Flat", "f=1:width_type=h:width=200:g=0"),
        }

        self.current_filter = self.filters.get("flat")

    @property
    def in_voice(self):
        """If connected to a voice channel."""
        return self.ctx.voice_client

    @property
    def filter_name(self):
        """The current filters"s name."""
        return self.current_filter.name

    def set_filter(self, filter_name: str):
        """Sets the currently active filter.
        
        Params:
        -------
            filter_name : str
                The name of the filter to set.
        """
        filter = self.filters.get(filter_name)
        if not filter:
            print(f"uh oh! no filer found with name {filter_name}")

        self.current_filter = filter

    def build_ffmpeg_options(self, seek_time: float=0.00):
        """Returns the applicable ffmpeg options built from the equalizer settings.

        Params:
        -------
        seek_time : float
            Time to seek to in the video, in seconds.
        """
        ffmpeg_options = {
            "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
            "options": "-vn -acodec pcm_s16le"
        }

        if seek_time != 0.00:
            ffmpeg_options["before_options"] += f" -ss {seek_time}"

        if self.current_filter:
            ffmpeg_options["options"] += f" -af {self.current_filter.apply}"

        print(ffmpeg_options)
        return ffmpeg_options
