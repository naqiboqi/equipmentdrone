import discord
import random

from asyncio import sleep
from discord.ext import commands
from .board import Board
from .player import Player



OPEN = "⏹️"



class InvalidColumnError(Exception):
    pass



class Game:
    def __init__(self, bot: commands.Bot, player_1: Player, player_2: Player, bot_player: bool):
        self.bot = bot
        self.player_1 = player_1
        self.player_2 = player_2
        self.bot_player = bot_player
        self.board = Board()

        self.current_player: Player = None
        self.winner: Player = None
        self.board_message: discord.Message = None
        self.turn_message: discord.Message = None

    @property
    def current_player_won(self):
        """If the current player won."""
        return self.won(self.current_player.symbol)

    @property
    def game_state(self):
        """The current state of the board, determines if the game should end.
        
        If the current player has won, returns `win`. If the board is full, returns `draw`.
        Otherwise, returns `ongoing` and the game continues.
        """
        if not self.current_player:
            return "ongoing"

        if self.current_player_won:
            return "win"

        if self.board.is_full:
            return "draw"

        return "ongoing"

    @property
    def is_bot_turn(self):
        """If it is currently the bot's turn, if the bot is in the game."""
        return self.current_player == self.player_2 and self.bot_player

    async def setup(self, ctx: commands.Context):
        """Sets the initial game state and sends the game board and turn message.
        
        Params:
            ctx : commands.Context
                The context for the current command.
        """
        self.current_player = self.player_1

        embed = self.board.embed
        self.board_message = await ctx.send(embed=embed)
        self.turn_message = await ctx.send(f"{self.current_player.mention}, you are going first!")

    async def cleanup(self):
        """Sends the final game state and cleans up the messages.."""
        try:
            await self.turn_message.delete()
        except discord.errors.NotFound as e:
            print(f"The turn message was not found: {e}")

        embed = self.board.embed
        embed.set_footer(text="This game has ended.")

        try:
            self.board_message = await self.board_message.edit(embed=embed)
        except discord.errors.NotFound as e:
            print(f"The board message was not found: {e}")

    def _get_player_from_id(self, player_id: int):
        """Returns the player object given a Discord member ID.
        
        Params:
        -------
            player_id : int
                The id to use for searching.
        """
        if self.player_1.member.id == player_id:
            return self.player_1

        if self.player_2.member.id == player_id:
            return self.player_2

    def _is_player_turn(self, player: Player):
        """Returns whether or not it is this player's turn.
        
        Params:
        -------
            player : Player
                The player to check.
        """
        return self.current_player == player

    async def player_turn(self, ctx: commands.Context, col: int, player_id: int):
        """Handles a player's turn after they call the `drop` command.
        
        Checks if it is the given player's turn and if the chosen column is valid, then
        drops a piece in that column. Otherwise, prompts the current player again.
        
        Params:
        -------
            ctx : commands.Context
                The context for the current command.
            col : int
                The column to drop in.
            player_id : int
                The Discord ID of the member who called the `drop` command.
        """
        player = self._get_player_from_id(player_id)
        if not self._is_player_turn(player):
            return await ctx.send("❌ It is not your turn!", delete_after=10)

        try:
            col_index = col - 1
            open_row = self.board.get_next_open(col_index)
        except IndexError as e:
            return await ctx.send(f"❌ {e}, please select a valid column!")

        symbol = player.symbol
        self.board.drop(open_row, col_index, symbol)

        await self._next_turn() 

    async def _do_bot_turn(self):
        """Represents the bot's turn."""
        bot_symbol = self.player_2.symbol
        col = self.find_winning_col(bot_symbol)

        if not col:
            player_symbol = self.player_1.symbol
            col = self.find_winning_col(player_symbol)

        if not col:
            col = self.find_cluster(bot_symbol)

        if not col:
            col = self.select_random_col()

        try:
            open_row = self.board.get_next_open(col)
            self.board.drop(open_row, col, bot_symbol)
        except IndexError as e:
            print(f"Bot attempted invalid drop at col {col}")

        await self._next_turn()

    def find_winning_col(self, symbol: str):
        for col in range(self.board.size):
            try:
                # Find the next open row in the column
                open_row = self.board.get_next_open(col)

                # Temporarily place the symbol to simulate the move
                self.board[open_row][col] = symbol

                # Check if this move results in a win
                if self.won(symbol):
                    # Undo the move and return this column as the best move
                    self.board[open_row][col] = OPEN
                    return col

                # Undo the move
                self.board[open_row][col] = OPEN
            except IndexError:
                # Skip full columns
                continue

        # No winning or blocking move found
        return None

    def find_cluster(self, symbol: str):
        best_cluster = -1
        best_col = -1

        for col in range(self.board.size):
            try:
                open_row = self.board.get_next_open(col)
                self.board[open_row][col] = symbol

                cluster = self.eval_cluster(open_row, col, symbol)
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

    def won(self, symbol: str):
        """Returns whether or not the current player has a winning sequence.
        
        Params:
            symbol : str
                The player's symbol.
        """
        board_size = self.board.size

        for row in range(board_size):
            for col in range(board_size - 3):
                if all(self.board[row][col + offset] == symbol for offset in range(4)):
                    return True

        for row in range(board_size - 3):
            for col in range(board_size):
                if all(self.board[row + offset][col] == symbol for offset in range(4)):
                    return True

        for row in range(board_size - 3):
            for col in range(board_size - 3):
                if all(self.board[row + offset][col + offset] == symbol for offset in range(4)):
                    return True

        for row in range(3, board_size):
            for col in range(board_size - 3):
                if all(self.board[row - offset][col + offset] == symbol for offset in range(4)):
                    return True

        return False

    async def _next_turn(self):
        """Checks the game's state to determine if the game should continue and move to the next turn.
        
        Also updates the board embed message and current turn message.
        """
        embed = self.board.embed
        self.board_message = await self.board_message.edit(embed=embed)

        state = self.game_state
        if state == "win":
            self.winner = self.current_player
            return await self.bot.get_cog("ConnectFour").end_game(game=self)
        elif state == "draw":
            return await self.bot.get_cog("ConnectFour").end_game(game=self)

        self.current_player = (
            self.player_1 if self.current_player == self.player_2 else self.player_2)

        await self._handle_turn_message()
        if self.is_bot_turn:
            await self._do_bot_turn()

    async def _handle_turn_message(self):
        """Sends a message indicating whose turn it is."""
        if self.is_bot_turn:
            self.turn_message = await self.turn_message.edit(content="It's now my turn!")
            await sleep(3)
        else:
            self.turn_message = await self.turn_message.edit(
                content=f"{self.current_player.mention}, it is now your turn!")
