

import discord


class Player:
    def __init__(self, member: discord.Member, symbol: str):
        self.member = member
        self.symbol = symbol
        
    def __eq__(self, other: discord.Member):
        return self.member == other