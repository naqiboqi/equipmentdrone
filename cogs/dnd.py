"""
This module implements a Dungeons and Dragons (DnD) cog for a Discord bot, designed to handle 
various actions commonly encountered in a Dungeons and Dragons game. It provides functionality 
for rolling dice, managing gameplay interactions, and enhancing user experience through 
interactive embeds.

### Key Features:
- **Dice Rolling**:
    - Roll dice with customizable numbers of rolls and sides.
    - Supports traditional DnD dice formats like `XdY` (e.g., `2d20` for two 20-sided dice).
    - Enforces validation to ensure reasonable roll inputs.

- **Interactive Views**:
    - Provides an interactive `DiceView` for users to re-roll dice dynamically.
    - Displays results in a visually appealing embed format.

- **Validation**:
    - Ensures dice rolls follow the format `XdY` with constraints on the number of rolls (1-100) 
    and the number of sides (1-100).
    - Returns meaningful error messages for invalid inputs.

### Classes:
- **`DnD`**:
    Represents the DnD cog, which includes commands for dice rolling and integrates with 
    `Dice` and `DiceView` objects for gameplay functionality.


### Dependencies:
- **`re`**: For validating and parsing dice roll strings.
- **`discord.ext`**: For Discord bot command usage.
- **`dnd_game`**: Custom module containing `Dice` and `DiceView` for gameplay logic.
- **`dice`**: Handles the logic for rolling dice and generating results.
- **`diceview`**: An interactive Discord view that allows users to re-roll
    dice and interact with the results.
"""


import re

from discord.ext import commands
from .dnd_game import Dice, DiceView



class DnD(commands.Cog):
    """Commands to represent Dungeons and Dragons dice, characters sheets, and more.
    
    Params:
        `bot` (commands.Bot): The bot instance.
    """
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def is_valid_roll(self, roll: str):
        """Returns the number of rolls and sides of the dice if the roll string is valid,
        or `None` if it is not valid."""
        pattern = r"^(\d+)d(\d+)$"
        result = re.match(pattern, roll)
        if not result:
            return None

        num_rolls, num_sides = int(result.group(1)), int(result.group(2))
        if 0 < num_rolls <= 100 and 0 < num_sides <= 100:
            return (num_rolls, num_sides)

        return None

    @commands.hybrid_command(name="roll")
    async def _setup_roll(self, ctx: commands.Context, roll: str="1d6"):
        """Sends an embed to roll dice with the given number of rolls and sides."""
        result = self.is_valid_roll(roll)
        if not result:
            return await ctx.send("Invalid roll, try again.")

        num_rolls, num_sides = result[0], result[1]
        dice = Dice(num_sides)
        view = DiceView(dice, num_rolls)

        embed = dice.get_embed(num_rolls)
        await ctx.send(embed=embed, view=view)


async def setup(bot: commands.Bot):
    await bot.add_cog(DnD(bot))
