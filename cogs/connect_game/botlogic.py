
import random

from .connect_board import ConnectFourBoard
from .game_utils import is_winner



OPEN = "⏹️"



class BotLogic:
    def __init__(self, board: ConnectFourBoard, symbol: str):
        self.board = board
        self.symbol = symbol

    def find_winning_col(self, symbol: str):
        for col in range(self.board.size):
            try:
                open_row = self.board.get_next_open(col)
                self.board[open_row][col] = symbol

                if is_winner(self.board, symbol):
                    self.board[open_row][col] = OPEN
                    return col

                self.board[open_row][col] = OPEN
            except IndexError:
                continue

        return None

    def find_cluster(self):
        best_cluster = -1
        best_col = -1

        for col in range(self.board.size):
            try:
                open_row = self.board.get_next_open(col)
                self.board[open_row][col] = self.symbol

                cluster = self.eval_cluster(open_row, col, self.symbol)
                if cluster > best_cluster:
                    best_cluster = cluster
                    best_col = col

                self.board[open_row][col] = OPEN
            except IndexError as e:
                print(f"Error when trying bot move at {open_row}, {open_row}: {e}")

        return best_col

    def eval_cluster(self, row: int, col: int, symbol: str):
        moves = [
            (0, 1),
            (1, 0),
            (1, 1),
            (1, -1)
        ]

        cluster_size = 0
        for dr, dc in moves:
            count = 0
            new_row, new_col = row + dr, col + dc
            while (0 <= new_row < self.board.size and 
                0 <= new_col < self.board.size and
                self.board[new_row][new_col] == symbol):

                count += 1
                new_row += dr
                new_col += dc

            new_row, new_col = row - dr, col - dc
            while (0 <= new_row < self.board.size and 
                0 <= new_col < self.board.size and
                self.board[new_row][new_col] == symbol):

                count += 1
                new_row -= dr
                new_col -= dc

            cluster_size += count

        return cluster_size

    def select_random_col(self):
        open_cols = [
            col for col in range(self.board.size)
            if OPEN in [row[col] for row in self.board]
        ]

        return random.choice(open_cols) if open_cols else -1