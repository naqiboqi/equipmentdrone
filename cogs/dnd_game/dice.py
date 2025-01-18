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

    def get_embed(self, num_rolls: int, rolls: list[int]=[], roll_type: str="normal"):
        embed = discord.Embed(
            title="Let's go gampling!",
            description=f"**Rolling** `{num_rolls}d{self.num_sides}`",
            color=discord.Color.fuchsia(),
        )
        
        embed.add_field(
            name="Roll Type: ",
            value=f"`{roll_type.capitalize()}`",
        )
        embed.add_field(
            name="All Rolls:",
            value=f"`{', '.join(map(str, rolls))}`" if rolls else "....."
        )

        if roll_type == "advantage":
            value = str(max(rolls))
        elif roll_type == "disadvantage":
            value = str(min(rolls))
        elif roll_type == "normal" and rolls:
            value = str(sum(rolls))
        else:
            value = "Waiting for roll..."

        embed.add_field(
            name="**You rolled: **",
            value=f"`{value}`",
            inline=False)
        
        embed.set_image(url="https://i.imgur.com/kmJYja0.png")
        return embed
