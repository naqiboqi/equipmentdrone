"""Includes the `is_winner(board, symbol)` function to check if any win conditions are met."""


from .connectfourboard import ConnectFourBoard



def is_winner(board: ConnectFourBoard, symbol: str):
    """Returns whether or not the given symbol has a winning sequence.
    
    Params:
    -------
        board : Board
            The game board.
        symbol : str
            The player's symbol to check.
    """
    board_size = board.size

    for row in range(board_size):
        for col in range(board_size - 3):
            if all(board[row][col + offset] == symbol for offset in range(4)):
                return True

    for row in range(board_size - 3):
        for col in range(board_size):
            if all(board[row + offset][col] == symbol for offset in range(4)):
                return True

    for row in range(board_size - 3):
        for col in range(board_size - 3):
            if all(board[row + offset][col + offset] == symbol for offset in range(4)):
                return True

    for row in range(3, board_size):
        for col in range(board_size - 3):
            if all(board[row - offset][col + offset] == symbol for offset in range(4)):
                return True

    return False