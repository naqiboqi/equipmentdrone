"""
This module contains the `CountryView` class, which allows players to select their country 
in a Battleship game through an interactive Discord UI. The view provides players with a list 
of available countries, and updates the game's state accordingly when a selection is made.

### Key Features:
- **Country Selection**:
    - Players can choose their country from a list using a dropdown menu.
    - The selected country is assigned to each player's profile, impacting the game state.
  
- **Interactive View**:
    - Uses `discord.ui.View` to create an interactive select dropdown for players to choose a country.
    - The selected country is displayed in the embed message, reflecting each player's choice.

- **Data Management**:
    - The module loads country names and associated ship names from a JSON file (`ship_names.json`).
    - The file is loaded into memory when the module is initialized, and any errors in loading are caught and logged.

### Classes:
- **`CountryView`**:
    A custom `discord.ui.View` that allows players to select a country, which is then stored in 
    the corresponding `Player` object. The view interacts with both players and updates the 
    embed message showing the countries each player has chosen.

### Dependencies:
- **`discord`**: For creating and managing the interactive Discord UI components like `discord.ui.View` and `discord.ui.Select`.
- **`json`**: For loading and parsing the `ship_names.json` file, which contains the available countries.
- **`os`**: For managing file paths and ensuring proper access to the `ship_names.json` file.
- **`player`**: Imports the `Player` class, which represents players in the game and stores their country choice.

### Constants:
- **`SHIP_JSON_PATH`**: Path to the JSON file that stores the available ship names and countries.
- **`SHIP_NAMES`**: Dictionary containing the countries loaded from the `ship_names.json` file.
"""



import discord
import json
import os

from .player import Player



DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
SHIP_JSON_PATH = os.path.join(DATA_DIR, "ship_names.json")


def load_ship_names_() -> dict[str, dict[str, list[str]]]:
    """Loads a json file given a path and returns its content.
    
    Throws an error if the file does not exist or is not a valid json.
    """
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
"""Dictionary containing the countries loaded from `ship_names.json`."""


class CountryView(discord.ui.View):
    """
    A Discord UI View for selecting a country to play as in a Battleship-style game.

    This class provides an interactive interface where players can choose a country to represent 
    using a dropdown menu. The selected country is then assigned to each player, and their choices 
    are displayed in an embedded message. This interaction facilitates the game setup by assigning 
    countries to the players before starting the match.

    Attributes:
    -----------
        player_1 : Player
            The first player participating in the game.
        player_2 : Player
            The second player participating in the game.
    """
    def __init__(self, player_1: Player, player_2: Player, timeout=180):
        super().__init__(timeout=timeout)
        self.player_1 = player_1
        self.player_2 = player_2

    @discord.ui.select(
        placeholder="Select a country",
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
            return await interaction.response.defer()
        
        embed = discord.Embed(
            title="Select a country to lead to victory 🌎",
            description=f"""
                {self.player_1.member.mention}:
                {self.player_1.country if self.player_1 else 'No country chosen'}

                {self.player_2.member.mention}:
                {self.player_2.country if self.player_2 else 'No country chosen'}""",
            color=discord.Color.blue())

        await interaction.response.edit_message(embed=embed)
