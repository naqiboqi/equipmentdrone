"""
This module defines the `Board` class, which represents a player's board
in the `Battleship` game.
"""


import discord
import random

from typing import Optional
from .ship import Ship



OPEN = "🟦"
CURRENT_SHIP = "🟩"
CONFIRMED_SHIP = "⏹️"
SHIP_NOT_CONFIRMED = "🟥"



class Board():
    """Representation of a player's board in a game. 
    
    Handles location validation for player hits and misses on ships.
    
    Attributes:
    ----------
        `size` (int): The x and y sizes of the board
        `grid` (list[list[str]]): Keeps track of the player's ships if it is the fleet board,
        or their hits and misses if it is a tracking board.
    """
    def __init__(self):
        self.size = 10
        self.grid = [[OPEN for _ in range(self.size)] for _ in range(self.size)]
    
    async def random_place_ships(self, fleet: list[Ship]):
        """Attemps to randomly place each ship from a player's fleets onto the board.
        
        Makes sure that no ships intersect and are within the bounds of the board.

        Params:
        -------
            `fleet` (list[Ship]): The player's ships
        """
        for ship in fleet:
            placed = False
            while not placed:
                x, y = random.randint(0, self.size - 1), random.randint(0, self.size - 1)
                direction = random.choice(["H", "V"])
                if self.is_valid_loc_(ship, y, x, direction):
                    self.place_ship_(ship, y, x, direction)
                    placed = True

    def is_valid_loc_(self, ship: Ship, y: int, x: int, direction: str):
        """Returns whether or not the given location is a valid placement for a ship.
        
        A location is valid if all locations occupied by the ship are only open water.
        
        Params:
        -------
            `ship` (Ship): The current ship to check
            `y` (int): The y coordinate to test the ship
            `x` (int): The x coordinate to test the ship
            `direction` (str): The ships's direction, either facing vertically or diagonally.
        """
        dy, dx = (0, 1) if direction == "H" else (1, 0)

        for i in range(ship.size):
            ny, nx = y + dy * i, x + dx * i
            if ny >= self.size or nx >= self.size or self.grid[ny][nx] != OPEN:
                return False

        return True
    
    def place_ship_(self, ship: Ship, y: int, x: int, direction: str):
        """Places a ship at a given location on the board.
        
        When placed, the `self.locs` for the `ship` are updated as well as the squares
        on the board.

        Params:
        -------
            `ship` (Ship): The current ship to place
            `y` (int): The y coordinate to place at
            `x` (int): The x coordinate to place at
            `direction` (str): The direction for the ship to face
        """
        dy, dx = (0, 1) if direction == "H" else (1, 0)
        for i in range(ship.size):
            ny, nx = y + dy * i, x + dx * i
            ship.locs.append((ny, nx))
            self.grid[ny][nx] = SHIP_NOT_CONFIRMED
    
    def is_valid_move_loc(self, ship: Ship, dy: int=0, dx: int=0):
        """Returns whether or not the given movement will result in a valid location for the ship.
        
        A location is valid if all locations occupied by the ship are only open water.
        
        Params:
        -------
            `ship` (Ship): The current ship to check
            `dy` (int): The change in y coordinate to test the ship
            `dx` (int): The change x coordinate to test the ship
        """
        for loc in ship.locs:
            y, x = loc
            ny, nx = y + dy, x + dx
            if (not 0 <= ny < self.size) or (not 0 <= nx < self.size):
                return False
            if (self.grid[ny][nx] != OPEN and (ny, nx) not in ship.locs):
                return False

        return True

    def move_ship(self, ship: Ship, dy: int=0, dx: int=0):
        """Moves the `ship` to a new location given a change in y or x coordinate.
        
        Params:
        -------
            `ship` (Ship): The current ship to move
            `dy` (int): The change in y coordinate to move the ship
            `dx` (int): The change x coordinate to move the ship
        """
        for y, x in ship.locs:
            self.grid[y][x] = OPEN

        for i in range(len(ship.locs)):
            y, x = ship.locs[i]
            ny, nx = y + dy, x + dx

            ship.locs[i] = (ny, nx)
            self.grid[ny][nx] = CURRENT_SHIP

    def is_valid_rotation(self, ship: Ship, direction: str):
        """Returns whether or not rotating the `ship` will be a valid location.
        
        A location is valid if all locations occupied by the `ship` are open water.
        
        Params:
        -------
            `ship` (Ship): The current ship to check
            `direction` (str): The direction for the ship to face
        """
        rotate_point = ship.locs[0]
        y, x = rotate_point
        
        dy, dx = (0, 1) if direction == "H" else (1, 0)
        for i in range(ship.size): 
            ny, nx = y + dy * i, x + dx * i
            if not (0 <= ny < self.size) or not (0 <= nx < self.size):
                return False
            if self.grid[ny][nx] != OPEN and (ny, nx) not in ship.locs:
                return False

        return True

    def rotate_ship(self, ship: Ship, direction: str):
        """Rotates the `ship` in the given direction.
        
        Params:
        -------
            `ship` (Ship): The current ship to rotate
            ``direction` (str): The direction for the ship to face
        """
        for y, x in ship.locs:
            self.grid[y][x] = OPEN

        rotate_point = ship.locs[0]
        y, x = rotate_point

        dy, dx = (0, 1) if direction == "H" else (1, 0)
        for i in range(ship.size): 
            ny, nx = y + dy * i, x + dx * i

            ship.locs[i] = (ny, nx)
            self.grid[ny][nx] = CURRENT_SHIP
            
    def confirm_ship(self, ship: Ship):
        """Confirms the placement of the given `ship`
        
        Params:
        -------
            `ship` (Ship): The ship to confirm
        """
        for y, x in ship.locs:
            self.grid[y][x] = CONFIRMED_SHIP
            
        ship.placed = True
        
    def select_ship(self, ship: Ship):
        """Selects and highlights the given `ship` so that the player may choose its location.
        
        Params:
        -------
            `ship` (Ship): The ship to select
        """
        for y, x in ship.locs:
            self.grid[y][x] = CURRENT_SHIP
            
        ship.placed = False
            
    def deselect_ship(self, ship: Ship):
        """Deselects the given `ship` for placement.
        
        Params:
        -------
            `ship` (Ship): The ship to deselect
        """
        for y, x in ship.locs:
            self.grid[y][x] = SHIP_NOT_CONFIRMED

    def get_ship_placement_embed(self, current_ship: Optional[Ship]):
        """Returns an `embed` showing the currently selected `ship` and
        the player's `fleet` on the board.
        
        Params:
        -------
            `current_ship` (Ship): The currently selected ship
        """
        embed = discord.Embed(
            title="Place your ships!",
            description=f"```{self.__str__()}```",
            color=discord.Color.fuchsia(),
        )

        embed.add_field(
            name=f"{'Currently placing: ' if current_ship else 'Select a ship!'}",
            value=f"{current_ship if current_ship else '....'}"
        )

        embed.set_footer(
            text="Use the buttons to move the current ship, then click ✅ when you are done!")
        
        return embed
    
    def get_fleet_embed(self):
        """Returns an embed that shows the player's finalized `ship` placements on the `board`.
        
        Once the game begins, will show the health of the player's ships.
        """
        embed = discord.Embed(
            title="Your fleet: ",
            description=f"```{self.__str__()}```",
            color=discord.Color.dark_magenta()
        )

        embed.add_field(name="These are your ships. Guard them with your life!")
        embed.add_field(name="Healthy ships have their sections marked as ⏹️")
        embed.add_field(name="Damaged ships have their sections marked as 🟥")
        return embed
    
    def get_tracking_embed(self):
        """Returns an embed that shows the player's `tracking board` that keeps track of their
        hits and misses on enemy ships.
        """
        embed = discord.Embed(
            title="These are your hits and misses. Try not to miss too much!",
            description=f"```{self.__str__()}```",
            color=discord.Color.red()
        )

        embed.add_field(name="Your hits on enemy ships are marked with 🟥")
        embed.add_field(name="Your misses are marked with ⬜")
        return embed

    def __str__(self):
        """Returns a string representation of the board."""
        board = ""
        for row in self.grid:
            board += "|".join(spot for spot in row) + "\n"
        return board
