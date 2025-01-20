import discord

from .player import Player


OPEN = "⏹️"



class Board:
    def __init__(self, size: int=3):
        self.size = size
        self.grid = [[OPEN for _ in range(self.size)] for _ in range(self.size)]

    def is_full(self):
        return not any([OPEN in self.grid[i]] for i in range(self.size))
    
    def mark(self, y: int, x: int, symbol: str):
        self.grid[y][x] = symbol
        
    def get_embed(self, current_player: Player):
        embed = discord.Embed(
            title="Tic-Tac-Toe!",
            description=f"{self}",
            color=discord.Color.red()
        )
        
        embed.set_footer(text=f"Currently {current_player.member.name}'s turn.")
        return embed

    def __str__(self):
        board = ""
        for row in self.grid:
            board += f"{''.join(row)}\n"

        return board