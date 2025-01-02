import discord

from .board import Board
from .ship import Ship


class BoardView(discord.ui.View):
    def __init__(self, board: Board, current_ship: Ship, *, timeout=180):
        super().__init__(timeout=timeout)
        self.board = board
        self.current_ship = current_ship

    @discord.ui.button(label="⬅️", style=discord.ButtonStyle.blurple)
    async def move_ship_left_(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button):

        ship = self.current_ship
        dx = -1

        if self.board.is_valid_move_loc(ship, dx=dx):
            self.board.move_ship(ship, dx=dx)
            embed = await self.board.create_embed(ship)
            await interaction.response.edit_message(embed=embed)
        else:
            await interaction.response.defer()

    @discord.ui.button(label="⬆️", style=discord.ButtonStyle.blurple)
    async def move_ship_up_(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button):

        ship = self.current_ship
        dy = -1

        if self.board.is_valid_move_loc(ship, dy=dy):
            self.board.move_ship(ship, dy=dy)
            embed = await self.board.create_embed(ship)
            await interaction.response.edit_message(embed=embed)
        else:
            await interaction.response.defer()
            
    @discord.ui.button(label="➡️", style=discord.ButtonStyle.blurple)
    async def move_ship_right_(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button):

        ship = self.current_ship
        dx = 1

        if self.board.is_valid_move_loc(ship, dx=dx):
            self.board.move_ship(ship, dx=dx)
            embed = await self.board.create_embed(ship)
            await interaction.response.edit_message(embed=embed)
        else:
            await interaction.response.defer()

    @discord.ui.button(label="⬇️", style=discord.ButtonStyle.blurple)
    async def move_ship_down_(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button):

        ship = self.current_ship
        dy = 1
        
        if self.board.is_valid_move_loc(ship, dy=dy):
            self.board.move_ship(ship, dy=dy)
            embed = await self.board.create_embed(ship)
            await interaction.response.edit_message(embed=embed)
        else:
            await interaction.response.defer()

    @discord.ui.button(label="↕️", style=discord.ButtonStyle.blurple)
    async def rotate_ship_vertical_(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button):

        ship = self.current_ship
        direction = "V"

        if self.board.is_valid_rotation(ship, direction=direction):
            self.board.rotate_ship(ship, direction=direction)
            embed = await self.board.create_embed(ship)
            await interaction.response.edit_message(embed=embed)
        else:
            await interaction.response.defer()

    @discord.ui.button(label="↔", style=discord.ButtonStyle.blurple)
    async def rotate_ship_horizontal_(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button):

        ship = self.current_ship
        direction="H"

        if self.board.is_valid_rotation(ship, direction=direction):
            self.board.rotate_ship(ship, direction=direction)
            embed = await self.board.create_embed(ship)
            await interaction.response.edit_message(embed=embed)
        else:
            await interaction.response.defer()
