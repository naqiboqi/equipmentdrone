import discord

from random import randint



class Dice():
    def __init__(self, num_sides: int):
        self.num_sides = num_sides

    def roll(self, num_rolls: int=1):
        rolls: list[int] = []
        for _ in range(num_rolls):
            roll = randint(1, self.num_sides)
            rolls.append(roll)

        return rolls

    def create_roll_embed(self, num_rolls: int, rolls: list[int]=[], roll_type: str="normal"):
        embed = discord.Embed(
            title="Time to roll!",
            description=f"**Rolling** `{num_rolls}d{self.num_sides}`",
            color=discord.Color.fuchsia(),
        )

        if roll_type == "adv":
            value = str(max(rolls))
        elif roll_type == "disadv":
            value = str(min(rolls))
        elif roll_type == "normal" and rolls:
            value = rolls[0]
        else:
            value = "Waiting for roll..."

        embed.add_field(
            name="Roll Type",
            value=f"`{roll_type.capitalize()}`"
        )
        embed.add_field(
            name="**Dice Roll Result**",
            value=f"`{value}`",
            inline=False
        )

        return embed
