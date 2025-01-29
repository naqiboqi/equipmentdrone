import discord

from ..game_elements import Board



class TTTBoard(Board):
    """Representation of the player's board in a Tic-tac-toe game.
    
    Attributes:
    -----------
        size : int
            The `y` and `x` sizes of the board.
        grid : list[list[str]]
            A 2D grid representing the board that shows the placed symbols.
    """
    def __init__(self, size: int=3):
        super().__init__(size=size)

    @property
    def embed(self):
        """An embed that shows the current state of the board."""
        embed = discord.Embed(
            title="🚩 Tic-Tac-Toe! 🚩",
            description=f"{self}",
            color=discord.Color.red())

        return embed

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
