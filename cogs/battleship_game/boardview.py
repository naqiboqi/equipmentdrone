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

from .board import DefenseBoard
from .ship import Ship



class BoardView(discord.ui.View):
    """
    A Discord UI View for managing ship placement in a Battleship-style game.

    This class provides an interactive interface for players to place their ships on a game board 
    using Discord's UI components, including buttons and dropdown menus. Players can move ships, 
    rotate them, and confirm their placement.

    Attributes:
    ----------
        placement_board : DefenseBoard
            The board to interact with.
        current : int
            The current ship value to move.
        fleet : list[Ship] 
            The ships to choose between.
    """
    def __init__(self, board: DefenseBoard, fleet: list[Ship], *, timeout=600):
        super().__init__(timeout=timeout)
        self.placement_board = board
        self.current: int = None
        self.fleet = fleet

    async def select_ship_(self, interaction: discord.Interaction, ship: Ship):
        """Selects a ship to be placed. Occurs when the user selects the ship manually
        or when the previous ship's location is confirmed.
        
        Params:
        -------
            interaction: discord.Interaction
                The interaction for this context.
            ship : Ship
                The ship to place.
        """
        if not ship.placed_before:
            self.placement_board.first_placement(ship)
            
        self.placement_board.select_ship(ship)
        embed = self.placement_board.get_ship_placement_embed(ship)
        await interaction.response.edit_message(embed=embed)
        
    @discord.ui.select(
        placeholder="Select a ship to place",
        options=[discord.SelectOption(label=f"Ship {i}", value=str(i)) for i in range(1, 6)])
    async def select_ship_option_(
        self,
        interaction: discord.Interaction,
        select: discord.ui.Select):
        """Allows the user to select a ship to place from a dropdown menu.
        
        If the ship is being selected for the first time, it will be randomly placed
        on the board to start.

        If a ship was selected and the user is now selecting a new ship, confirms
        the placement of the previous ship. 
        """
        if self.current is not None:        
            ship = self.fleet[self.current]
            self.placement_board.deselect_ship(ship)
            print("deselected")

        self.current = int(select.values[0]) - 1
        ship = self.fleet[self.current]
        await self.select_ship_(interaction, ship)

    async def move_ship_(self, interaction: discord.Interaction, dy=0, dx=0):
        if self.current is None:
            return await interaction.response.send_message("Select a ship first!", delete_after=5)

        ship = self.fleet[self.current]
        if self.placement_board.is_valid_move_loc(ship, dy=dy, dx=dx):
            self.placement_board.move_ship(ship, dy=dy, dx=dx)
            self.placement_board.redraw(self.fleet)
            
            embed = self.placement_board.get_ship_placement_embed(ship)
            await interaction.response.edit_message(embed=embed)
        else:
            await interaction.response.defer()

    @discord.ui.button(label="⬅️", style=discord.ButtonStyle.blurple)
    async def move_ship_left_(  
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button):
        """Moves the currently selected ship one step to the left if the move is valid."""
        await self.move_ship_(interaction, dx=-1)

    @discord.ui.button(label="⬆️", style=discord.ButtonStyle.blurple)
    async def move_ship_up_(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button):
        """Moves the currently selected ship one step up if the move is valid."""
        await self.move_ship_(interaction, dy=-1)
            
    @discord.ui.button(label="➡️", style=discord.ButtonStyle.blurple)
    async def move_ship_right_(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button):
        """Moves the currently selected ship one step to the right if the move is valid."""
        await self.move_ship_(interaction, dx=1)

    @discord.ui.button(label="⬇️", style=discord.ButtonStyle.blurple)
    async def move_ship_down_(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button):
        """Moves the currently selected ship one step down if the move is valid."""
        await self.move_ship_(interaction, dy=1)

    @discord.ui.button(label="✅", style=discord.ButtonStyle.blurple)
    async def confirm_ship_placement_(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button):
        """Confirms the placement of the currently selected ship on the board.
        
        Moves to the next ship in the fleet that is not placed, unless all ships have been placed.
        """
        if self.current is None:
            return await interaction.response.send_message("Select a ship first!", delete_after=5)
        
        ship = self.fleet[self.current]
        
        conflicting_ship = self.placement_board.is_valid_confirm_loc(ship, self.fleet)
        if conflicting_ship:
            return await interaction.response.send_message(
                f"The ships {ship.name} and {conflicting_ship.name} intersect at these locations: "
                f"`{set(ship.locs) & set(conflicting_ship.locs)}`, please move one of the ships.",
                delete_after=10)
        
        self.placement_board.confirm_ship(ship)
        
        ## Get the next unconfirmed ship
        self.current = next((i for i, ship in enumerate(self.fleet) if not ship.confirmed), None)
        if self.current is not None:
            ship = self.fleet[self.current]
            await self.select_ship_(interaction, ship)
        else:
            await interaction.response.send_message("All ships have been placed!")

    async def rotate_ship_(self, interaction: discord.Interaction, direction: str):
        if self.current is None:
            return await interaction.response.send_message("Select a ship first!", delete_after=5)

        ship = self.fleet[self.current]
        if self.placement_board.is_valid_rotation(ship, direction):
            self.placement_board.rotate_ship(ship, direction)
            self.placement_board.redraw(self.fleet)
            
            embed = self.placement_board.get_ship_placement_embed(ship)
            await interaction.response.edit_message(embed=embed)
        else:
            await interaction.response.defer()

    @discord.ui.button(label="Vertical 🔄️", style=discord.ButtonStyle.blurple)
    async def rotate_ship_vertical_(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button):
        """Rotates the currently selected ship to a vertical orientation if valid."""
        await self.rotate_ship_(interaction, direction="V")

    @discord.ui.button(label="🔄️ Horizontal", style=discord.ButtonStyle.blurple)
    async def rotate_ship_horizontal_(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button):
        """Rotates the currently selected ship to a horizontal orientation if valid."""
        await self.rotate_ship_(interaction, direction="H")
