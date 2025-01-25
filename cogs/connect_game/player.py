import discord



class Player:
    def __init__(self, color: discord.Color, member: discord.Member, symbol: str):
        self.color = color
        self.member = member
        self.symbol = symbol

    def __eq__(self, other: "Player"):
        return self.member.id == other.member.id
