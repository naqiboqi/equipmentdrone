import discord
import json
import os

from .player import Player



DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
SHIP_JSON_PATH = os.path.join(DATA_DIR, "ship_names.json")


def load_ship_names_() -> dict[str, dict[str, list[str]]]:
    """Loads a json file given a path and returns its content."""
    try: 
        with open(SHIP_JSON_PATH) as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"The file {SHIP_JSON_PATH} does not exist.")
        return {}
    except json.JSONDecodeError:
        print(f"The file {SHIP_JSON_PATH} is not a valid json.")
        return {}


SHIP_NAMES = load_ship_names_()



class CountryView(discord.ui.View):
    def __init__(self, player_1: Player, player_2: Player, timeout=180):
        super().__init__(timeout=timeout)
        self.player_1 = player_1
        self.player_2 = player_2

    @discord.ui.select(
        placeholder="Select a country to play as",
        options=[
            discord.SelectOption(label=country, value=str(i))
            for i, country in enumerate(SHIP_NAMES.keys())])
    async def select_country_(
        self,
        interaction: discord.Interaction,
        select: discord.ui.Select):

        member = interaction.user
        country_names = list(SHIP_NAMES.keys())

        if self.player_1.member == member:
            self.player_1.country = country_names[int(select.values[0])]
        elif self.player_2.member == member:
            self.player_1.country = country_names[int(select.values[0])]
        else:
            return await interaction.defer()
        
        embed = discord.Embed(
            title="Select a country to lead to victory 🌎",
            description=f"""
                {self.player_1.member.mention}:
                {self.player_1.country if self.player_1 else 'No country chosen'}

                {self.player_2.member.mention}:
                {self.player_2.country if self.player_2 else 'No country chosen'}""",
            color=discord.Color.blue())

        await interaction.response.edit_message(embed=embed)
