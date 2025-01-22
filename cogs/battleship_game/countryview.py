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

### Dependencies:
- **`discord`**: For creating and managing the interactive Discord UI components like `discord.ui.View` and `discord.ui.Select`.
- **`player`**: For tracking country choice.
"""



import discord

from .player import Player
from .constants import ship_names



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
            for i, country in enumerate(ship_names.keys())])
    async def _select_country(
        self,
        interaction: discord.Interaction,
        select: discord.ui.Select):
        """Sets the player's country to the selected choice."""
        country_names = list(ship_names.keys())

        if self.player_1.member == interaction.user:
            self.player_1.country = country_names[int(select.values[0])]
        elif self.player_2.member == interaction.user:
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
