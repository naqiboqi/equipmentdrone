from discord.ext import commands


class Eq:
    def __init__(self, ctx: commands.Context):
        self.ctx = ctx
        self.current_preset = "flat"
        self.preset_options = {
            "bass_boost": "f=60:width_type=h:width=200:g=10",
            "treble_boost": "f=6000:width_type=h:width=200:g=10",
            "flat": "f=1:width_type=h:width=200:g=0",
        }

    @property
    def preset_name(self):
        return self.current_preset

    @property
    def preset_setting(self):
        return self.preset_options.get(self.current_preset)

    def set_preset(self, name: str):
        if name == self.current_preset:
            self.current_preset = "flat"
            return False

        preset = self.preset_options.get(name)
        if not preset:
            raise ValueError

        self.current_preset = name
        return True
