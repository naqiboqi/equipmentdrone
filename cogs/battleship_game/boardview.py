"""
This module defines the `BoardView` class, a Discord UI View for managing ship placement on a board in a Battleship-style game. 
It allows players to interact with the board, move ships, rotate them, and confirm their placement via Discord's UI components 
like buttons and select menus.

### Dependencies:
- **`discord`**: Used for creating UI components and handling interactions.
- **`Board`**: Represents the game board and manages ship placements.
- **`Ship`**: Represents a ship with properties like size, position, and orientation.

Usage:
    This class is designed to be used as part of a Discord bot for a Battleship-style game. 
    It creates a visual and interactive ship placement interface for players, allowing them to select, move, 
    and rotate ships before starting the game.
"""


import discord

from .board import Board
from .ship import Ship



class BoardView(discord.ui.View):
    def __init__(self, board: Board, fleet: list[Ship], *, timeout=180):
        super().__init__(timeout=timeout)
        self.board = board
        self.current = 0
        self.fleet = fleet
        
    @discord.ui.select(
        placeholder="Select a ship to place",
        options=[
            discord.SelectOption(label=f"Ship {i}", value=str(i)) for i in range(1, 6)])
    async def select_option_(
        self,
        interaction: discord.Interaction,
        select: discord.ui.Select):
        """Allows the user to select a `ship` to place from a dropdown menu."""
        
        ship = self.fleet[self.current]
        if not ship.placed:
            self.board.confirm_ship(ship)

        self.current = int(select.values[0]) - 1
        ship = self.fleet[self.current]
        self.board.select_ship(ship)

        embed = self.board.get_ship_placement_embed(ship)
        await interaction.response.edit_message(embed=embed)

    @discord.ui.button(label="⬅️", style=discord.ButtonStyle.blurple)
    async def move_ship_left_(  
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button):
        """Moves the currently selected `ship` one step to the left if the move is valid."""

        ship = self.fleet[self.current]
        dx = -1

        if self.board.is_valid_move_loc(ship, dx=dx):
            self.board.move_ship(ship, dx=dx)
            embed = self.board.get_ship_placement_embed(ship)
            await interaction.response.edit_message(embed=embed)
        else:
            await interaction.response.defer()

    @discord.ui.button(label="⬆️", style=discord.ButtonStyle.blurple)
    async def move_ship_up_(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button):
        """Moves the currently selected `ship` one step up if the move is valid."""

        ship = self.fleet[self.current]
        dy = -1

        if self.board.is_valid_move_loc(ship, dy=dy):
            self.board.move_ship(ship, dy=dy)
            embed = self.board.get_ship_placement_embed(ship)
            await interaction.response.edit_message(embed=embed)
        else:
            await interaction.response.defer()
            
    @discord.ui.button(label="➡️", style=discord.ButtonStyle.blurple)
    async def move_ship_right_(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button):
        """Moves the currently selected `ship` one step to the right if the move is valid."""

        ship = self.fleet[self.current]
        dx = 1

        if self.board.is_valid_move_loc(ship, dx=dx):
            self.board.move_ship(ship, dx=dx)
            embed = self.board.get_ship_placement_embed(ship)
            await interaction.response.edit_message(embed=embed)
        else:
            await interaction.response.defer()

    @discord.ui.button(label="⬇️", style=discord.ButtonStyle.blurple)
    async def move_ship_down_(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button):
        """Moves the currently selected `ship` one step down if the move is valid."""

        ship = self.fleet[self.current]
        dy = 1
        
        if self.board.is_valid_move_loc(ship, dy=dy):
            self.board.move_ship(ship, dy=dy)
            embed = self.board.get_ship_placement_embed(ship)
            await interaction.response.edit_message(embed=embed)
        else:
            await interaction.response.defer()

    @discord.ui.button(label="✅", style=discord.ButtonStyle.blurple)
    async def confirm_ship_placement_(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button):
        """Confirms the placement of the currently selected `ship` on the board."""

        ship = self.fleet[self.current]
        self.board.confirm_ship(ship)

        embed = self.board.get_ship_placement_embed()
        await interaction.response.edit_message(embed=embed)

    @discord.ui.button(label="Vertical 🔄️", style=discord.ButtonStyle.blurple)
    async def rotate_ship_vertical_(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button):
        """Rotates the currently selected `ship` to a vertical orientation if valid."""

        ship = self.fleet[self.current]
        direction = "V"

        if self.board.is_valid_rotation(ship, direction=direction):
            self.board.rotate_ship(ship, direction=direction)
            embed = self.board.get_ship_placement_embed(ship)
            await interaction.response.edit_message(embed=embed)
        else:
            await interaction.response.defer()

    @discord.ui.button(label="🔄️ Horizontal", style=discord.ButtonStyle.blurple)
    async def rotate_ship_horizontal_(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button):
        """Rotates the currently selected `ship` to a horizontal orientation if valid."""

        ship = self.fleet[self.current]
        direction="H"

        if self.board.is_valid_rotation(ship, direction=direction):
            self.board.rotate_ship(ship, direction=direction)
            embed = self.board.get_ship_placement_embed(ship)
            await interaction.response.edit_message(embed=embed)
        else:
            await interaction.response.defer()
