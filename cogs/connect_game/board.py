import discord



OPEN = "⏹️"



class Board():
    def __init__(self, size: int=8):
        self.size = size
        self.grid = [[OPEN for _ in range(self.size)] for _ in range(self.size)]

    def __str__(self):
        """Returns a string representation of the board."""
        board = ""
        for row in self.grid:
            board += f"{''.join(col for col in row)}\n"

        return board

    @property
    def embed(self):
        """An embed the shows the current state of the board."""
        return discord.Embed(
            title="Connect Four!",
            description=f"{self}",
            color=discord.Color.red())

    @property
    def is_full(self):
        """If the board is full."""
        return not any(OPEN in row for row in self.grid)

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
                if self.grid[row][col] == OPEN)
        except StopIteration:
            raise IndexError(f"The column {col} is full.")

    def drop(self, col: int, open_row: int, symbol: str):
        """Drops a piece to the lowest position in the given column.
        
        Params:
        -------
            col : int
                The column to drop into.
            open_row : int
                The lowest open row in the board.
            symbol : str
                The player's symbol.
        """
        self.grid[open_row][col] = symbol

