

import discord


class Player:
    def __init__(self, member: discord.Member, symbol: str):
        self.member = member
        self.symbol = symbol
        
    def __eq__(self, other: "Player"):
        return self.member == other.member