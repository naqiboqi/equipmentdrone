import discord

from asyncio import sleep
from discord.ext import commands
from random import choice
from .board import Board
from .player import Player



OPEN = "⏹️"



class Game:
    def __init__(self, player_1: Player, player_2: Player, bot_player: bool=False):
        self.player_1 = player_1
        self.player_2 = player_2
        self.bot_player = bot_player
        self.current_player: Player = None
        self.board = Board()
        self.log_ = None

        self.board_message: discord.Message = None
        self.turn_message: discord.Message = None
    
    def is_player_turn(self, member: discord.Member):
        return self.current_player == member
    
    def _is_valid_loc(self, y: int, x: int):
        return self.board.grid[y][x] == OPEN
    
    def mark(self, y: int, x: int, symbol: str):
        if self._is_valid_loc(y, x):
            print("marking")
            self.board.mark(y, x, symbol)
            return True
            
        return False
    
    def _is_bot_turn(self):
        return self.bot_player and self.current_player == self.player_2
        
    async def next_turn(self):
        print("next turn")
        #if self._is_game_over():
        #    return await self._game_over(ctx)
        #    
        #if self.board.is_full():
        #    return await self._game_over_draw(ctx)
        
        if self.current_player == self.player_1.member:
            self.current_player = self.player_2
        else:
            self.current_player = self.player_1

        await self._handle_turn_message()
        if self._is_bot_turn():
            await self._bot_turn()
        
    async def _handle_turn_message(self):
        if self._is_bot_turn():
            self.turn_message = await self.turn_message.edit("It's now my turn!")
            await sleep(3)
        else:
            self.turn_message = await self.turn_message.edit(
                content=f"{self.current_player.member.mention}, it is now your turn!")
        
    async def _bot_turn(self):
        board_size = self.board.size
        
        valid_locs = [
            (y, x) for y in range(board_size) for x in range(board_size) if self._is_valid_loc(y, x)
        ]
        
        y, x = choice(valid_locs)
        self.board.mark(y, x, self.current_player.symbol)
        await self.next_turn()
    
    def _is_game_over(self):
        symbol = self.current_player.symbol
        board_size = self.board.size

        for y in range(board_size):
            if all(self.board.grid[y][x] == symbol for x in range(board_size)):
                return True

        for x in range(board_size):
            if all(self.board.grid[y][x] == symbol for y in range(board_size)):
                return True

        if all(self.board.grid[i][i] == symbol for i in range(board_size)):
            return True

        if all(self.board.grid[i][board_size - i - 1] == symbol for i in range(board_size)):
            return True

        return False
    
    def get_embed(self):
        return self.board.get_embed(self.current_player)

    async def _game_over(self, ctx: commands.Context):
        await ctx.send(f"{self.current_player} has won the game!")