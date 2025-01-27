import discord



class Player:
    def __init__(self, color: discord.Color, member: discord.Member, symbol: str):
        self.color = color
        self.member = member
        self.symbol = symbol

    @property
    def mention(self):
        """Mention the player."""
        return self.member.mention

    @property
    def name(self):
        """The player's Discord name."""
        return self.member.name

    def __eq__(self, other: "Player"):
        return self.member.id == other.member.id
