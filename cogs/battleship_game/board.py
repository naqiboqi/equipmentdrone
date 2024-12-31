"""
This module defines the `Board` class, which represents a player's board
in the `Battleship` game.
"""


import random

from .ship import Ship



OPEN = "🟦"
SHIP = "⏹️"



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

    def is_valid_loc_(self, ship: Ship, y: int, x: int, direction: str):
        dy, dx = (0, 1) if direction == "H" else (1, 0)

        for i in range(ship.size):
            ny, nx = y + dy * i, x + dx * i
            if ny >= self.size or nx >= self.size or self.grid[ny][nx] != OPEN:
                return False

        return True

    def place_ship_(self, ship: Ship, y: int, x: int, direction: str):
        """Places a ship at a given location on the board.
        
        Since all ships take up multiple portions, spaces on the board occupied by a ship
        are labeled by `S`.
        
        A ship present at those locations will also have its
        `self.locs` array appended to store the locations that it occupies.
        """
        dy, dx = (0, 1) if direction == "H" else (1, 0)
        for i in range(ship.size):
            ny, nx = y + dy * i, x + dx * i
            ship.locs.append((ny, nx))
            self.grid[ny][nx] = SHIP

    def random_place_ships(self, fleet: list[Ship]):
        """Attemps to randomly place each ship from a player's fleets onto the board.
        
        Makes sure that no ships intersect and are within the bounds of the board.
        """
        for ship in fleet:
            placed = False
            while not placed:
                x, y = random.randint(0, self.size - 1), random.randint(0, self.size - 1)
                direction = random.choice(["H", "V"])
                if self.is_valid_loc_(ship, y, x, direction):
                    self.place_ship_(ship, y, x, direction)
                    placed = True

    def __str__(self):
        board = ""
        for row in self.grid:
            board += " ".join(spot for spot in row) + "\n"
        return board
