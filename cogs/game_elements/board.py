OPEN = "⏹️"



class Board:
    """Base representation of a game board.
    
    Attributes:
    ----------
        size : int
            The size of the board.
        grid : list[list[str]]
            A 2D grid representing the board.
    """
    def __init__(self, size: int=8):
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
            board += f"{''.join(col for col in row)}\n"

        return board

    @property
    def is_full(self):
        """If the board is full."""
        return not any(OPEN in row for row in self.grid)