import discord

from asyncio import sleep
from discord.ext import commands
from .board import Board
from .player import Player


class InvalidPlayerError(Exception):
    pass


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

    async def setup(self, ctx: commands.Context):
        """Sets the initial game state and sends the game board and turn message.
        
        Params:
            ctx : commands.Context
                The context for the current command.
        """
        self.current_player = self.player_1

        embed = self.board.get_embed()
        self.board_message = await ctx.send(embed=embed)
        self.turn_message = await ctx.send(f"{self.current_player.member.mention}, you are going first!")

    def get_player_from_id(self, player_id: int):
        """Returns the player object given a member ID.
        
        Params:
        -------
            player_id : int
                The id to use for searching.
        """
        if self.player_1.member.id == player_id:
            return self.player_1

        if self.player_2.member.id == player_id:
            return self.player_2

    def is_player_turn(self, player: Player):
        """Returns whether or not it is this player's turn.
        
        Params:
        -------
            player : Player
                The player to check.
        """
        return self.current_player == player

    def _is_bot_turn(self):
        """Returns whether or not it is the bot's turn."""
        return self.current_player == self.player_2 and self.bot_player

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
                The id of the person who called the `drop` command.
        """
        player = self.get_player_from_id(player_id)
        if not self._is_player_turn(player):
            return await ctx.send("❌ It is not your turn!", delete_after=10)

        try:
            open_row = self.board.get_next_open(col)
        except IndexError as e:
            return await ctx.send(f"❌ {e}, please select a valid column!")

        ## Add symbols to starting the game....
        symbol = player.symbol
        self.board.drop(col - 1, open_row, symbol)

        await ctx.send(f"{player.member.name} dropped a piece into column {col}.")
        await self.next_turn() 

    async def next_turn(self):
        """Checks the game's state to determine if the game should continue and move to the next turn.
        
        Also updates the board embed message and current turn message.
        """
        embed = self.board.get_embed()
        self.board_message = self.board_message.edit(embed=embed)
        
        state = self._get_game_state()
        if state == "win":
            self.winner = self.current_player
            return await self.bot.get_cog("ConnectFour").end_game(game=self)
        elif state == "draw":
            return await self.bot.get_cog("ConnectFour").end_game(game=self)

        self.current_player = (
            self.player_1 if self.current_player == self.player_2 else self.player_2)

        await self._handle_turn_message()
        if self._is_bot_turn():
            self._bot_turn()

    def _bot_turn(self):
        pass

    def _get_game_state(self):
        """Checks if the current state of the board to determine if the game should end.
        
        If the current player has won, returns `win`. If the board is full, returns `draw`.
        Otherwise, returns `ongoing` and the game continues.
        """
        board_size = self.board.size
        grid = self.board.grid
        symbol = self.current_player.symbol

        for row in range(board_size):
            for col in range(board_size - 3):
                if all(grid[row][col + offset] == symbol for offset in range(4)):
                    return "win"

        for row in range(board_size - 3):
            for col in range(board_size):
                if all(grid[row + offset][col] == symbol for offset in range(4)):
                    return "win"

        for row in range(board_size - 3):
            for col in range(board_size - 3):
                if all(grid[row + offset][col + offset] == symbol for offset in range(4)):
                    return "win"

        for row in range(3, board_size):
            for col in range(board_size - 3):
                if all(grid[row - offset][col + offset] == symbol for offset in range(4)):
                    return "win"

        if self.board.is_full():
            return "draw"

        return "ongoing"

    async def _handle_turn_message(self):
        """Sends a message indicating whose turn it is."""
        if self._is_bot_turn():
            self.turn_message = await self.turn_message.edit(content="It's now my turn!")
            await sleep(3)
        else:
            self.turn_message = await self.turn_message.edit(
                content=f"{self.current_player.member.mention}, it is now your turn!")

    async def cleanup(self):
        """Sends the final game state and cleans up the messages.."""
        try:
            await self.turn_message.delete()
        except discord.errors.NotFound as e:
            print(f"The turn message was not found: {e}")

        embed = self.board.get_embed()
        embed.set_footer(text="This game has ended.")
        
        self.board_message = await self.board_message.edit(embed=embed)
