"""
This module contains the `Player` class, which represents a player in a `Battleship` game.
A `player` has a `board` to place `ships`, a `tracking board` to record hits and misses,
a fleet of `ships`, and the associated Discord member.
"""


import discord
import random

from asyncio import sleep
from discord.ext import commands
from .board import Board
from .ship import Ship
from .boardview import BoardView



class Player():
    """Representation of a player in a Battleship game.
    
    Each player has a board of their own `ships` and an associated `fleet` array,
    and a board to track the hits or misses on their opponent's `ships`.
    
    Attributes:
    -----------
        `fleet_board` (Board): Used to store the player's `ships`
        `tracking_board` (Board): Used to store the player's hits and misses
        `fleet` (list[Ship]): The player's `ships`
        `member` (discord.Member): The Discord Member object associated with the player
        `country` (str): The player's chosen country
        `place_msg` (discord.Message): The Discord messaged used to allow the player
        to choose `ship` placement
        `fleet_msg` (discord.Message): The Discord message used to send and
        edit the player's `fleet` when hit
        `track_msg` (discord.Message): The Discord message used to send and
        edit the player's hits and misses on the enemy
    """
    def __init__(self, member: discord.Member):
        self.fleet_board = Board()
        self.tracking_board = Board()
        self.fleet = [Ship(size) for size in [2, 3, 3, 4, 5]]
        self.member = member
    
        self.country: str = None
        self.place_msg: discord.Message = None
        self.fleet_msg: discord.Message = None
        self.track_msg: discord.Message = None

    def __eq__(self, other: "Player"):
        return self.member == other.member
    
    def set_ship_names(self, names: dict[str, list[str]]):
        for i, ship_class in enumerate(names):
            ship = self.fleet[i]
            ship.ship_class = ship_class
            ship.name = random.choice(names[ship_class])
    
    async def choose_ship_placement(self, ctx: commands.Context):
        """Handles the player's `ship` placement by using buttons and a dropdown for ship selection.
        
        Params:
        ------
            `ctx` (commands.Context): The current `context` associated with a command
        """
        embed = self.fleet_board.get_ship_placement_embed()
        view = BoardView(self.fleet_board, self.fleet)
        
        try:
            self.place_msg = await self.member.send(embed=embed, view=view)
        except discord.errors.Forbidden:
            await ctx.send(f"Could not send the game board to {self.member.mention}, "
                f"please check you DM settings.")
        
        # Don't exit until all ships are placed
        while not (all(ship.final_placed for ship in self.fleet)):
            await sleep(5)

        await self.place_msg.delete()

    async def random_place_ships(self):
        """Randomly place ships on the player's board."""
        await self.fleet_board.random_place_ships(self.fleet)
        
    async def send_board_states(self):
        """Sends the player's boards as a direct message."""
        fleet_embed = self.fleet_board.get_fleet_embed()
        tracking_embed = self.tracking_board.get_tracking_embed()
        self.fleet_msg = await self.member.send(embed=fleet_embed)
        self.track_msg = await self.member.send(embed=tracking_embed)

    def get_ship_at(self, y: int, x: int):
        """Returns the player's `ship` that is at the given `(y, x)` location.
        
        Params:
        -------
            `y` (int): The y coordinate to look at
            `x` (int): The x coordinate to look at
        """
        loc = (y, x)
        for ship in self.fleet:
            if loc in ship.locs:
                return ship

    def is_defeated(self):
        """Returns whether all of the player's ships are sunk."""
        return all(ship.is_sunk() for ship in self.fleet)
