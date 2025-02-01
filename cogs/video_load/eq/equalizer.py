import discord

from discord.ext import commands
from ..constants import emojis



remain = emojis.get("remaining_line")
level = emojis.get("elapsed_line")



class Filter:
    """"""
    def __init__(self, name: str, settings: str):
        self.name = name
        self.settings = settings

    def __str__(self):
        return f"Filter: {self.name} ({self.settings})"

    @property
    def apply(self):
        """The applicable equalizer string to pass to ffmpeg."""
        return f"equalizer={self.settings}"

    @property
    def fields(self):
        """The settings of the filter in an easy to display format."""
        values = self.as_dict

        def display_gain(value, max_value: int=50, length: int=10):
            """Displays a bar to show the gain level."""
            try:
                value = float(value)
                num_filled = int((value / max_value) * length)
                return f"{level * num_filled}{remain * (length - num_filled)}"
            except ValueError:
                return value

        gain = values.get("g", 0)
        gain_level = display_gain(value=gain)

        width_type = values.get("width_type")
        if width_type == "h":
            width_unit = "Hz"
        elif width_type == "o":
            width_unit = "o"
        elif width_type == "q":
            width_unit = "q-factor"
        else:
            width_unit = ""

        fields = {
            "**Frequency:**" : f"`{values.get("f", "N/A")} Hz`",
            "**Width:**" : f"`{values.get("width", "N/A")} {width_unit}`",
            "**Gain: **" : f" {gain_level} `{gain} dB`"
        }

        return fields

    @property
    def as_dict(self):
        """The settings of the filter represented as a `dict`."""
        values: dict[str, str] = {}
        for setting in self.settings.split(":"):
            key, value = setting.split("=")
            values[key] = value

        return values


class Equalizer:
    """Representation of an equalizer for controlling ffmpeg settings.
    
    Attributes:
    -----------
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
            "flat": Filter("Flat", "f=1:width_type=h:width=200:g=0"),
            "super_bass_boost": Filter("Super Bass Boost", "f=60:width_type=h:width=200:g=30"),
            "bass_boost": Filter("Bass Boost", "f=60:width_type=h:width=200:g=10"),
            "treble_boost": Filter("Treble Boost", "f=1000:width_type=h:width=200:g=10"),
            "robot_voice": Filter("Robot Voice", "f=400:width_type=h:width=100:g=-10:f=3000:width_type=h:width=100:g=15"),
            "old_vinyl": Filter("Old Vinyl", "f=200:width_type=h:width=400:g=-15:f=5000:width_type=h:width=400:g=-10"),
            "echo_chamber": Filter("Echo Chamber", "f=500:width_type=h:width=300:g=10"),
            "underwater": Filter("Underwater", "f=500:width_type=h:width=500:g=-20"),
            "overdrive": Filter("Overdrive", "f=500:width_type=h:width=300:g=20"),
            "muffled": Filter("Muffled", "f=1000:width_type=h:width=1000:g=-15"),
            "lofi": Filter("Lo-Fi", "f=300:width_type=h:width=500:g=-10"),
            "airy": Filter("Airy", "f=12000:width_type=h:width=500:g=10"),
        }

        self.current_filter = self.filters.get("flat")

    @property
    def embed(self):
        """An embed showing the equalizer settings."""
        fields = self.current_filter.fields

        embed = discord.Embed(
            title=f"Equalizer: {self.filter_name}", 
            color=discord.Color.from_str("#dd7c1f"))

        for field_name, value in fields.items():
            embed.add_field(name=field_name, value=value)

        return embed

    @property
    def filter_name(self):
        """The current filters"s name."""
        return self.current_filter.name

    @property
    def is_connected(self):
        """If connected to a voice channel."""
        return self.ctx.voice_client

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
            "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 120",
            "options": "-vn -acodec pcm_s16le"
        }

        if seek_time != 0.00:
            ffmpeg_options["before_options"] += f" -ss {seek_time}"

        if self.current_filter:
            ffmpeg_options["options"] += f" -af {self.current_filter.apply}"

        return ffmpeg_options
