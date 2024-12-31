"""
This module contains the `Player` class, which represents a player in a `Battleship` game.
A `player` has a `board` to place `ships`, a `tracking board` to record hits and misses,
a fleet of `ships`, and the associated Discord member.
"""


import discord

from .board import Board
from .ship import Ship



class Player():
    """Representation of a player in a Battleship game.
    
    Each player has a board of their own ships and an associated fleet array,
    and a board to track the hits or misses on their opponent's ships.
    
    Attributes:
    ----------
        `board` (Board): Used to store the player's ships
        `tracking_board` (Board): Used to store the player's hits and misses
        `fleet` (list[Ship]): The player's ships
        `member` (discord.Member): The Discord member object associated with the player
        `fleet_msg` (discord.Message): The Discord message used to send and edit the player's fleet
        `track_msg` (discord.Message): The Discord message used to send and edit the player's hits and misses
    """
    def __init__(self, member: discord.Member):
        self.board = Board()
        self.tracking_board = Board()
        self.fleet = [Ship(size) for size in [2, 3, 3, 4, 5]]
        self.member = member

        self.fleet_msg: discord.Message = None
        self.track_msg: discord.Message = None

    def __eq__(self, other: "Player"):
        return self.member == other.member

    def get_ship_at(self, y: int, x: int):
        """Returns the player's ship that is at the given `(y, x)` location."""
        loc = (y, x)
        for ship in self.fleet:
            if loc in ship.locs:
                return ship

    def place_ships(self):
        """Randomly place ships on the player's board."""
        self.board.random_place_ships(self.fleet)

    def is_defeated(self):
        """Returns whether all of the player's ships are sunk."""
        return all(ship.is_sunk() for ship in self.fleet)