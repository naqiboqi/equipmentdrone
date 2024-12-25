import asyncio
import datetime
import discord

from discord.ext import commands
from random import SystemRandom

BLUE_CIRCLE = "🔵"
OPEN = "⏺️"
RED_CIRCLE = "🔴"

class Board:
    def __init__(self, p1, p2):
        self.size = 2
        self.board = [[OPEN for _ in range(self.size)] for _ in range(self.size)]
        self.players = {BLUE_CIRCLE : p1, RED_CIRCLE : p2} if SystemRandom.randint(0, 1) == 1 else {BLUE_CIRCLE : p2, RED_CIRCLE : p1}

    def is_full(self):
        for row in self.board:
            if OPEN in row:
                return False
            
        return True
    
    def is_over(self):
        pass
    
    def is_spot_open(self, x: int, y: int):
        return self.board[y][x] == OPEN
    
    def place_piece(self, x: int, y: int, player):
        self.board[y][x]
    
    def __str__(self):
        display = ""
        for row in self.board:
            for space in row:
                display += space
                
            display += "\n"
            
        return display

class TTT(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.boards = {}

    async def start(self, ctx, p2: discord.Member):
        p1 = ctx.message.author
        if p1 == p2:
            return await ctx.send("You can't play against yourself")
        
        if p2 == None:
            p2 = ctx.message.guild.me

        if self.boards.get(ctx.message.guild.id) is not None:
            return await ctx.send("You can only play one game at a time.")

        self.boards[ctx.guild.id] = Board(p2)


async def setup(bot):
    bot.add_cog(TTT(bot))