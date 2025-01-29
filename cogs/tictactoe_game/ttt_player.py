

import discord

from ..game_elements import Player


class TTTPlayer(Player):
    def __init__(self, member: discord.Member, symbol: str, is_bot: bool=False):
        super().__init__(member=member, is_bot=is_bot)
        self.symbol = symbol

    def __eq__(self, other: discord.Member):
        return self.member == other