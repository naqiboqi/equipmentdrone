import discord


class Player:
    """Base representation of a player in a game.
    
    Attributes:
    -----------
        member : Member
            The Discord member associated with the player.
        is_bot : bool
            If the player is a bot.
    """
    def __init__(self, member: discord.Member, is_bot: bool=False):
        self.member = member
        self.is_bot = is_bot

    def __eq__(self, other: "Player"):
        return self.member.id == other.member.id

    @property
    def avatar_url(self):
        """The player's Discord avatar."""
        return self.member.avatar.url

    @property
    def id(self):
        """The player's Discord ID."""
        return self.member.id

    @property
    def mention(self):
        """Mention the player."""
        return self.member.mention

    @property
    def name(self):
        """The player's Discord name."""
        return self.member.name
