import discord

from .dice import Dice



class DiceView(discord.ui.View):
    """
    A Discord UI View for rolling DnD dice.

    This class provides an interactive interface where players can roll a dice by
    rules of advantage or disadvantage with buttons.

    Attributes:
    -----------
        dice : Dice
            The dice to roll.
        num_rolls : int
            Number of times to roll.
    """
    def __init__(self, dice: Dice, num_rolls: int, *, timeout=None):
        super().__init__(timeout=timeout)
        self.dice = dice
        self.num_rolls = num_rolls

    @discord.ui.button(label="Roll", style=discord.ButtonStyle.blurple)
    async def roll_button_(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button):
        """
        Transitions to the previous embed page, or defers if at the first page.

        Params:
        -------
            interaction : discord.Interaction
                The interaction that triggered the button.
            button : Button
                The button object.
        """

        rolls = self.dice.roll(self.num_rolls)
        embed = self.dice.get_embed(self.num_rolls, rolls)

        await interaction.response.edit_message(embed=embed)

    @discord.ui.button(label="Roll Advantage", style=discord.ButtonStyle.blurple)
    async def roll_advantage_button_(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button):
        """
        Transitions to the previous embed page, or defers if at the first page.

        Params:
        -------
            interaction : discord.Interaction
                The interaction that triggered the button.
            button : Button
                The button object.
        """

        rolls = self.dice.roll(self.num_rolls)
        embed = self.dice.get_embed(self.num_rolls, rolls, "advantage")

        await interaction.response.edit_message(embed=embed)

    @discord.ui.button(label="Roll Disadvantage", style=discord.ButtonStyle.blurple)
    async def roll_disadvantage_button_(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button):
        """
        Transitions to the previous embed page, or defers if at the first page.

        Params:
        -------
            interaction : discord.Interaction
                The interaction that triggered the button.
            button : Button
                The button object.
        """
        rolls = self.dice.roll(self.num_rolls)
        embed = self.dice.get_embed(self.num_rolls, rolls, "disadvantage")

        await interaction.response.edit_message(embed=embed)
