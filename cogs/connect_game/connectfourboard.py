import discord

from ..game_elements import Board


OPEN = "⏹️"



class ConnecFourBoard(Board):
    def __init__(self, size: int=8):
        super().__init__(size=size)

    @property
    def embed(self):
        """An embed the shows the current state of the board."""
        return discord.Embed(
            title="Connect Four!",
            description=f"{self}",
            color=discord.Color.red())

    def get_next_open(self, col: int):
        """Returns the next open row in the column, closest to the bottom of the board.
        
        Params:
        -------
            col : int
                The column number to check.
        
        Throws an `IndexError` if the column number is invalid or if the column is full."""
        if not 0 <= col < self.size:
            raise IndexError(f"The column {col} is not valid.")

        try:
            return next(row for row in range(self.size - 1, -1, -1) 
                if self[row][col] == OPEN)
        except StopIteration:
            raise IndexError(f"The column {col} is full.")

    def drop(self, row: int, col: int, symbol: str):
        """Drops a piece to the lowest position in the given column.
        
        Params:
        -------
            open_row : int
                The lowest open row in the board.
            col : int
                The column to drop into.
            symbol : str
                The player's symbol.
        """
        self[row][col] = symbol
