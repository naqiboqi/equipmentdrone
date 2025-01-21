import discord

from asyncio import sleep
from discord.ext import commands
from random import choice
from .board import Board
from .player import Player



OPEN = "⏹️"



class Game:
    def __init__(
        self, 
        bot: commands.Bot, 
        player_1: Player, 
        player_2: Player, 
        bot_player: bool):
        self.bot = bot
        self.player_1 = player_1
        self.player_2 = player_2
        self.bot_player = bot_player
        self.current_player: Player = None
        self.winner: Player = None
        
        self.board = Board()
        self.view = None
        self.board_message: discord.Message = None
        self.turn_message: discord.Message = None
    
    def is_player_turn(self, member: discord.Member):
        return self.current_player == member
    
    def _is_valid_loc(self, y: int, x: int):
        return self.board.grid[y][x] == OPEN
    
    def mark(self, y: int, x: int, symbol: str):
        if self._is_valid_loc(y, x):
            self.board.mark(y, x, symbol)
            return True
            
        return False
    
    def _is_bot_turn(self):
        return self.bot_player and self.current_player == self.player_2.member
        
    async def next_turn(self, y: int, x: int):
        embed = self.get_embed()

        await self.view.mark_button_tile(y, x, self.current_player.symbol)
        self.board_message = await self.board_message.edit(embed=embed, view=self.view)
        
        state = self._check_game_state()
        if state == "win":
            self.winner = self.current_player
            return await self.bot.get_cog("TicTacToe").end_game(game=self)
        elif state == "draw":
            return await self.bot.get_cog("TicTacToe").end_game(game=self)
        
        self.current_player = (
            self.player_2 if self.current_player == self.player_1.member
                else self.player_1)

        await self._handle_turn_message()
        if self._is_bot_turn():
            await self._bot_turn()
            
    async def _bot_turn(self):
        board_size = self.board.size
        valid_locs = [
            (y, x) for y in range(board_size) for x in range(board_size) if self._is_valid_loc(y, x)
        ]
        
        y, x = choice(valid_locs)
        self.board.mark(y, x, self.current_player.symbol)
        await self.next_turn(y, x)
            
    def _check_game_state(self):
        board_size = self.board.size
        grid = self.board.grid
        symbol = self.current_player.symbol

        for y in range(board_size):
            if all(grid[y][x] == symbol for x in range(board_size)):
                return "win"
        for x in range(board_size):
            if all(grid[y][x] == symbol for y in range(board_size)):
                return "win"

        if all(grid[i][i] == symbol for i in range(board_size)):
            return "win"
        if all(grid[i][board_size - i - 1] == symbol for i in range(board_size)):
            return "win"

        if self.board.is_full():
            return "draw"

        return "ongoing"
        
    async def _handle_turn_message(self):
        if self._is_bot_turn():
            self.turn_message = await self.turn_message.edit(content="It's now my turn!")
            await sleep(3)
        else:
            self.turn_message = await self.turn_message.edit(
                content=f"{self.current_player.member.mention}, it is now your turn!")

    def get_embed(self):
        return self.board.get_embed(self.current_player)
    
    async def cleanup(self):
        await self.view.disable_all_tiles()
        
        try:
            await self.turn_message.delete()
        except discord.errors.NotFound as e:
            print(f"The turn message was not found: {e}")

        embed = self.get_embed()
        embed.set_footer(text="This game has ended.")
        
        self.board_message = await self.board_message.edit(embed=embed, view=self.view)
        self.view = None
