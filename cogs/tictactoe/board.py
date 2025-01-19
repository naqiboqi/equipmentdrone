

OPEN = "⏹️"


class Board:
    def __init__(self, size: int=3):
        self.size = size
        self.grid = [[OPEN for _ in range(self.size)] for _ in range(self.size)]

    def is_full(self):
        return not any([OPEN in self.grid[i]] for i in range(self.size))
    
    def mark(self, y: int, x: int, symbol: str):
        self.grid[y][x] = symbol
        
    def __str__(self):
        board = ""
        for row in board:
            board += "".join(row)

        return board