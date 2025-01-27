import discord

from .player import Player



OPEN = "⏹️"



class Board:
    """Representation of the player's board in a Tic-tac-toe game.
    
    Attributes:
    -----------
        size : int
            The `y` and `x` sizes of the board.
        grid : list[list[str]]
            A 2D grid representing the board that shows the placed symbols.
    """
    def __init__(self, size: int=3):
        self.size = size
        self.grid = [[OPEN for _ in range(self.size)] for _ in range(self.size)]

    def __getitem__(self, index: int):
        return self.grid[index]

    def __setitem__(self, index: int, val: str):
        self.grid[index] = val

    def __str__(self):
        """Returns a string representation of the board."""
        board = ""
        for row in self.grid:
            board += f"{''.join(row)}\n"

        return board

    @property
    def embed(self):
        """An embed that shows the current state of the board."""
        embed = discord.Embed(
            title="🚩 Tic-Tac-Toe! 🚩",
            description=f"{self}",
            color=discord.Color.red())

        return embed

    @property
    def is_full(self):
        """If the board is full."""
        return not any(OPEN in row for row in self.grid)

    def mark(self, y: int, x: int, symbol: str):
        """Marks the given location with the player's symbol.

        Params:
        --------
            y : int
                The `y` location to mark.
            x : int
                The `x` location to mark.
            symbol : str
                The player's symbol to place.
        """
        self[y][x] = symbol
