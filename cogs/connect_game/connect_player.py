import discord

from ..game_elements import Player



class ConnectFourPlayer(Player):
    def __init__(self, member: discord.Member, symbol: str, is_bot: bool=False):
        super().__init__(member=member, is_bot=is_bot)
        self.symbol = symbol
