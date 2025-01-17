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
        
        select = discord.ui.Select(
            placeholder="Select a ship",
            options=[discord.SelectOption(label=ship.name, value=str(i)) for i, ship in enumerate(self.fleet)],
            row=0)
        
        select.callback = self._select_ship_option
        self.add_item(select)

    async def _select_ship(self, interaction: discord.Interaction, ship: Ship):
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
    
    async def _select_ship_option(self, interaction: discord.Interaction):
        """Allows the user to select a ship to place from a dropdown menu.
        
        If the ship is being selected for the first time, it will be randomly placed
        on the board to start.

        If a ship was selected and the user is now selecting a new ship, confirms
        the placement of the previous ship. 
        """
        if self.current is not None:        
            ship = self.fleet[self.current]
            self.placement_board.deselect_ship(ship)

        self.current = int(interaction.data["values"][0])
        ship = self.fleet[self.current]
        await self._select_ship(interaction, ship)

    async def _move_ship(self, interaction: discord.Interaction, dy=0, dx=0):
        """Moves the ship in a given direction.
        
        Notifies the user if the resulting position would be invalid.
        
        Params:
        -------
            interaction: discord.Interaction
                    The interaction for this context.
            dy : int
                The change in the y coordinate to move the ship.
            dx : int
                The change in the x coordinate to move the ship.
        """
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

    @discord.ui.button(label="Move ⬅️", style=discord.ButtonStyle.blurple, row=1)
    async def _move_ship_left(  
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button):
        """Moves the currently selected ship one step to the left if the move is valid."""
        await self._move_ship(interaction, dx=-1)

    @discord.ui.button(label="Move ⬆️", style=discord.ButtonStyle.blurple, row=1)
    async def _move_ship_up(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button):
        """Moves the currently selected ship one step up if the move is valid."""
        await self._move_ship(interaction, dy=-1)
            
    @discord.ui.button(label="Move ➡️", style=discord.ButtonStyle.blurple, row=1)
    async def _move_ship_right(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button):
        """Moves the currently selected ship one step to the right if the move is valid."""
        await self._move_ship(interaction, dx=1)

    @discord.ui.button(label="Move ⬇️", style=discord.ButtonStyle.blurple, row=1)
    async def _move_ship_down(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button):
        """Moves the currently selected ship one step down if the move is valid."""
        await self._move_ship(interaction, dy=1)

    async def _rotate_ship(self, interaction: discord.Interaction, direction: str):
        """Rotates the ship in a given direction.
        
        Notifies the user if the resulting position would be invalid.
        
        Params:
        -------
            interaction: discord.Interaction
                The interaction for this context.
            direction : str
                The direction for the ship to face.
        """
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

    @discord.ui.button(label="🔄️ Vertical", style=discord.ButtonStyle.blurple, row=2)
    async def _rotate_ship_vertical(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button):
        """Rotates the currently selected ship to a vertical orientation if valid."""
        await self.rotate_ship_(interaction, direction="V")

    @discord.ui.button(label="🔄️ Horizontal", style=discord.ButtonStyle.blurple, row=2)
    async def _rotate_ship_horizontal(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button):
        """Rotates the currently selected ship to a horizontal orientation if valid."""
        await self.rotate_ship_(interaction, direction="H")

    @discord.ui.button(label="Randomize❓", style=discord.ButtonStyle.blurple, row=2)
    async def _randomize_placements(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button):
        """
        Randomly places all ships on the board, marking them as placed.
        
        Any ships whose placement was confirmed is skipped. The user must manually
        confirm the remaining ships.
        """
        self.placement_board.random_place_ships(self.fleet)
        embed = self.placement_board.get_ship_placement_embed()
        await interaction.response.edit_message(embed=embed)

    async def _check_ship_conflicts(self, interaction: discord.Interaction, ship: Ship):
        """Returns whether or not any ship in the fleet shares a location with another ship."""
        conflicting_ship = self.placement_board.is_valid_confirm_loc(ship, self.fleet)
        if conflicting_ship:
            await interaction.response.send_message(
                f"The ships {ship.name} and {conflicting_ship.name} intersect at these locations: "
                f"`{set(ship.locs) & set(conflicting_ship.locs)}`, please move one of the ships.",
                delete_after=10)

            return True

        return False

    @discord.ui.button(label="Confirm Current ✅", style=discord.ButtonStyle.blurple, row=3)
    async def _confirm_ship_placement(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button):
        """Confirms the placement of the currently selected ship, if it's location is valid.
        
        Selects the next ship in the fleet that is not confirmed.
        """
        if self.current is None:
            return await interaction.response.send_message("Select a ship first!", delete_after=5)
        
        ship = self.fleet[self.current]
        if await self._check_ship_conflicts(interaction, ship):
            return

        self.placement_board.confirm_ship(ship)
        self.current = next((i for i, ship in enumerate(self.fleet) if not ship.confirmed), None)
        if self.current is not None:
            ship = self.fleet[self.current]
            await self._select_ship(interaction, ship)
        else:
            embed = await self.placement_board.get_ship_placement_embed()
            await interaction.response.edit_message(embed=embed)
            await interaction.followup.send("All ships have been placed!")

    @discord.ui.button(label="Confirm All ✅", style=discord.ButtonStyle.blurple, row=3)
    async def _confirm_all(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button):
        """
        Confirms the placement of all ships with a valid placement on the board.
        
        All ships must have been placed on the board prior to confirmation.
        """

        if not all(ship.placed_before for ship in self.fleet):
            return await interaction.response.send_message(
                "Place all of your ships before confirming!", delete_after=10)

        for ship in self.fleet:
            if not await self._check_ship_conflicts(interaction, ship):
                self.placement_board.confirm_ship(ship)

        embed = self.placement_board.get_ship_placement_embed()
        await interaction.response.edit_message(embed=embed)
        
    @discord.ui.button(label="Clear All ❌", style=discord.ButtonStyle.danger, row=3)
    async def _clear_all(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button):
        """Clears the board and all ship positions."""
        self.placement_board.clear_board()
        
        for ship in self.fleet:
            self.placement_board.reset_ship(ship)

        embed = self.placement_board.get_ship_placement_embed()
        await interaction.response.edit_message(embed=embed)
        await interaction.followup.send("Reset the board.")
