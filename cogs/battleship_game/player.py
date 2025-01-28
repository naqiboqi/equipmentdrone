"""
This module contains the `Player` class, which represents a player in a `Battleship` game.
A `player` has a `defense_board` to place their `ships`, a `tracking_board` to record hits 
and misses on their opponent's ships, a fleet of `ships`, and the associated Discord member.

### Key Features:
- **Ship Placement**:
    - Players can choose ship placements via buttons and dropdowns, which are reflected in 
      a personalized Discord embed.
    - Ships can also be randomly placed on the board.

- **Board Management**:
    - Each player has a `defense_board` for placing ships and an `attack_board` for tracking 
      hits and misses during the game.
    - The boards are updated and sent to players in direct messages (DMs), allowing 
      real-time feedback.

- **Fleet Handling**:
    - Each player starts with a fleet of ships with predefined sizes.
    - Players can name their ships based on the provided ship class names.

- **Victory Condition**:
    - The game tracks whether a player is defeated by checking if all of their ships are sunk.

### Classes:
- **`Player`**:
    Represents a player in the Battleship game. The player has boards for defense and 
    tracking hits, a fleet of ships, and a connection to a Discord member for interaction.
    
### Dependencies:
- **`discord`**: For interacting with Discord's API and sending messages to players.
- **`random`**: For randomly assigning ship names and placing ships on the board.
- **`asyncio`**: For handling asynchronous tasks, such as waiting for the player to place ships.
- **`discord.ext.commands`**: For building the command structure and managing the game flow.
- **`board`**: Contains the `AttackBoard` and `DefenseBoard` classes to manage the player's 
  boards.
- **`ship`**: Defines the `Ship` class used to represent individual ships in the player's fleet.
- **`boardview`**: Provides a `BoardView` class for displaying the game board and interacting 
  with it through Discord views.
"""



import discord
import random

from asyncio import sleep
from discord.ext import commands
from .board import AttackBoard, DefenseBoard
from .ship import Ship
from .boardview import BoardView



class Player():
    """Representation of a player in a Battleship game.
    
    Each player has a board of their own ships showing their fleet,
    and a board to track the hits or misses on their opponent's ships.
    
    Attributes:
    -----------
        defense_board : DefenseBoard 
            Used to store the player's ships.
        attack_board : AttackBaord
            Used to store the player's hits and misses.
        fleet : list[Ship]
            The player's ships.
        member : discord.Member
            The Discord Member object associated with the player.
        country : str
            The player's chosen country
        placement_board_message: discord.Message
            The Discord messaged used to allow the player to place ships.
        defense_board_message : discord.Message
            The Discord message used to send and edit the player's fleet when hit.
        attack_board_message : discord.Message
            The Discord message used to send and edit the player's hits and misses on the enemy.
    """
    def __init__(self, member: discord.Member):
        self.defense_board = DefenseBoard()
        self.attack_board = AttackBoard()
        self.fleet = [Ship(size) for size in [2, 3, 3, 4, 5]]
        self.member = member

        self.country: str = None
        self.placement_message: discord.Message = None
        self.defense_board_message: discord.Message = None
        self.attack_board_message: discord.Message = None

    def __eq__(self, other: "Player"):
        return self.member == other.member

    @property
    def mention(self):
        """Mention the player."""
        return self.member.mention

    @property
    def name(self):
        """The player's Discord name."""
        return self.member.name

    @property
    def is_defeated(self):
        """If the player has no remaining ships."""
        return all(ship.is_sunk for ship in self.fleet)

    def set_ship_names(self, names: dict[str, list[str]]):
        """Sets the names of the ships in the player's fleet.
        
        Names for each ship are determinzed by its `ship_class` and are randomized.
        
        Params:
        -------
            names: dict[str, list[str]]
                The possible ship names `(list)` associated with each ship type `(str)`.
        """
        for i, ship_class in enumerate(names):
            ship = self.fleet[i]
            ship.ship_class = ship_class
            ship.name = random.choice(names[ship_class])

    async def choose_ship_placement(self, ctx: commands.Context):
        """Handles the player's ship placement by using buttons and a dropdown for ship selection.
        
        Params:
        ------
            ctx: commands.Context
                The current context associated with a command.
        """
        embed = self.defense_board.get_ship_placement_embed()
        view = BoardView(self.defense_board, self.fleet)

        try:
            self.placement_message = await self.member.send(embed=embed, view=view)
        except discord.errors.Forbidden:
            await ctx.send(f"Could not send the game board to {self.member.mention}, "
                f"please check you DM settings.")

        while not (all(ship.confirmed for ship in self.fleet)):
            await sleep(5)

        await self.placement_message.delete()
        await sleep(2)

    def random_place_ships(self, bot_player: bool=False):
        """Randomly place ships on the player's board.
        
        Params:
        -------
        bot_player : bool
            If the placing player is a bot or not."""
        self.defense_board.random_place_ships(self.fleet, bot_player)

    async def send_board_states(self):
        """Sends the player's boards as a direct message."""
        fleet_embed = self.defense_board.embed
        tracking_embed = self.attack_board.embed
        self.defense_board_message = await self.member.send(embed=fleet_embed)
        self.attack_board_message = await self.member.send(embed=tracking_embed)

    async def update_board_states(self):
        """Updates the boards in the player's direct messages."""
        fleet_embed = self.defense_board.embed
        tracking_embed = self.attack_board.embed
        self.defense_board_message = await self.defense_board_message.edit(embed=fleet_embed)
        self.attack_board_message = await self.attack_board_message.edit(embed=tracking_embed)

    def get_ship_at(self, y: int, x: int):
        """Returns the player's ship that is at the given `(y, x)` location.
        
        Params:
        -------
            y : int
                The y coordinate to look at.
            x : int
                The x coordinate to look at.
        """
        loc = (y, x)
        for ship in self.fleet:
            if loc in ship.locs:
                return ship

        return None
