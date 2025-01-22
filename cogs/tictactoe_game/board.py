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

    def is_full(self):
        """Returns whether or not the board is full."""
        return not any([OPEN in self.grid[i]] for i in range(self.size))

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
        self.grid[y][x] = symbol

    def get_embed(self, current_player: Player):
        """Returns an embed the shows the current state of the board.
        
        Params:
        -------
            current_player : Player
                The player whose turn it is.
        """
        embed = discord.Embed(
            title="Tic-Tac-Toe!",
            description=f"{self}",
            color=discord.Color.red()
        )

        embed.set_footer(text=f"Currently {current_player.member.name}'s turn.")
        return embed

    def __str__(self):
        """Returns a string representation of the board."""
        board = ""
        for row in self.grid:
            board += f"{''.join(row)}\n"

        return board
