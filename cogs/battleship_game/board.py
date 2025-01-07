"""
This module implements the classes and functionality for managing the game boards in a 
Battleship game. It includes classes for handling defensive and offensive boards, ship placement, 
attack processing, and board state validation.

### Key Features:
- **Board Representation**:
    - Separates defensive (ship placement) and offensive (attack tracking) boards for a 
      clear distinction of roles during gameplay.
    - Provides a structured grid-based representation for tracking game states.

- **Ship Placement**:
    - Ensures valid ship placement with checks for overlaps, boundaries, and adherence to game rules.
    - Offers a robust mechanism for placing ships strategically or programmatically.

- **Attack Handling**:
    - Processes attacks, updating offensive and defensive boards based on hits, misses, or sunk ships.
    - Tracks ongoing game progress and facilitates feedback on attack results.

- **State Validation**:
    - Validates board configurations for correctness.
    - Tracks remaining ships to determine game status and win conditions.

### Classes:
- **`Board`**:
    A base class providing shared functionality for managing a grid and validating actions.
- **`DefenseBoard`**:
    Represents a player's defensive board, managing ship placements and responding to attacks.
- **`AttackBoard`**:
    Represents a player's offensive board, tracking the results of attacks on the opponent's grid.

### Dependencies:
- **`discord`**: For creating and sending embeds and messages
- **`random`**: For generating randomized ship placements.
- **`typing`**: For type hints and annotations.
- **`ship`**: For placing and moving player ships.
"""


import discord
import random

from typing import Optional
from .ship import Ship



OPEN = "🟦"
CURRENT_SHIP = "🟩"
CONFIRMED_SHIP = "⏹️"
SHIP_NOT_CONFIRMED = "🟥"


class Board():
    """Representation of a player's board in a game, serves as a base for the board's state.
    
    Attributes:
    ----------
        `size` : int
            The size of the board (both width and height).
        `grid` : list[list[str]]
            A 2D grid representing the board. Each cell contains a symbol to indicate 
            its state (e.g., open water, a ship, or a hit/miss).
    """
    def __init__(self):
        self.size = 10
        self.grid = [[OPEN for _ in range(self.size)] for _ in range(self.size)]

    def is_valid_loc_(self, ship: Ship, y: int, x: int, direction: str):
        """Returns whether or not the given location is a valid placement for a ship.
        
        A location is valid if all locations occupied by the ship are only open water.
        
        Params:
        -------
            ship : Ship
                The current ship to check
            y : int
                The y coordinate to test the ship
            x : int
                The x coordinate to test the ship
            direction : 
                str The ships's direction, either vertical or horizontal.
        """
        dy, dx = (0, 1) if direction == "H" else (1, 0)

        for i in range(ship.size):
            ny, nx = y + dy * i, x + dx * i
            if (not 0 <= ny < self.size) or (not 0 <= nx < self.size):
                return False
            if self.grid[ny][nx] != OPEN:
                return False

        return True

    def is_valid_move_loc(self, ship: Ship, dy: int=0, dx: int=0):
        """Returns whether or not the given movement will result in a valid location for a ship.
        
        A location is valid if all locations occupied by the `ship` are only open water.
        
        Params:
        -------
            ship : Ship
                The current ship to check.
            dy : int
                The change in y coordinate to test for the ship.
            dx : int
                The change x coordinate to test for the ship.
        """
        for loc in ship.locs:
            y, x = loc
            ny, nx = y + dy, x + dx
            if (not 0 <= ny < self.size) or (not 0 <= nx < self.size):
                return False
            if (self.grid[ny][nx] != OPEN and (ny, nx) not in ship.locs):
                return False

        return True

    def is_valid_rotation(self, ship: Ship, direction: str):
        """Returns whether or not rotating the ship will result in valid placement.
        
        A location is valid if all locations occupied by the ship are open water.
        
        Params:
        -------
            ship : Ship
                The current ship to check.
            direction : str
                The direction for the ship to face.
        """
        rotate_point = ship.locs[0]
        y, x = rotate_point
        
        dy, dx = (0, 1) if direction == "H" else (1, 0)
        for i in range(ship.size): 
            ny, nx = y + dy * i, x + dx * i
            if not (0 <= ny < self.size) or not (0 <= nx < self.size):
                return False
            if self.grid[ny][nx] != OPEN and (ny, nx) not in ship.locs:
                return False

        return True

    def __str__(self):
        """Returns a string representation of the board."""
        board = ""
        for row in self.grid:
            board += "|".join(spot for spot in row) + "\n"
        return board



class DefenseBoard(Board):
    """
    A specialized version of the `Board` class that represents a player's fleet board.

    This class manages the placement, movement, and rotation of ships during the setup phase
    of the game. It also provides methods to confirm ship placements and to generate visual 
    representations of the fleet for the player while the game is in progress.
    """
    def __init__(self):
        super().__init__()

    def first_placement(self, ship: Ship):
        """Places the ship on a random valid location on the board.
        
        Only happens for the ship's first placement, when the ship is selected for the first time.
        
        Params:
        -------
            ship : Ship
                The ship to place
        """
        self.random_place_ships([ship])
        ship.placed_before = True

    def random_place_ships(self, fleet: list[Ship]):
        """Attemps to randomly place each ship from a player's fleets onto the board.
        
        Ensures that no ships intersect and are within the bounds of the board.

        Params:
        -------
            fleet : list[Ship]
                The player's ships
        """
        for ship in fleet:
            placed = False
            while not placed:
                x, y = random.randint(0, self.size - 1), random.randint(0, self.size - 1)
                direction = random.choice(["H", "V"])
                if self.is_valid_loc_(ship, y, x, direction):
                    self.place_ship_(ship, y, x, direction)
                    placed = True

    def place_ship_(self, ship: Ship, y: int, x: int, direction: str):
        """Places a ship at a given location on the board.
        
        When placed, the `self.locs` of the ship are updated as well as the symbols
        on the board.

        Params:
        -------
            ship : Ship
                The current ship to place.
            y : int
                The y coordinate to place at.
            x : int
                The x coordinate to place at.
            direction : str
                The direction for the ship to face
        """
        dy, dx = (0, 1) if direction == "H" else (1, 0)
        for i in range(ship.size):
            ny, nx = y + dy * i, x + dx * i
            ship.locs.append((ny, nx))
            self.grid[ny][nx] = SHIP_NOT_CONFIRMED

    def move_ship(self, ship: Ship, dy: int=0, dx: int=0):
        """Moves the ship to a new location given a change in y or x coordinate.
        
        Params:
        -------
            ship : Ship
                The current ship to move.
            dy : int
                The change in y coordinate to move the ship.
            dx : int
                The change x coordinate to move the ship.
        """
        for y, x in ship.locs:
            self.grid[y][x] = OPEN

        for i in range(len(ship.locs)):
            y, x = ship.locs[i]
            ny, nx = y + dy, x + dx

            ship.locs[i] = (ny, nx)
            self.grid[ny][nx] = CURRENT_SHIP

    def rotate_ship(self, ship: Ship, direction: str):
        """Rotates the ship in the given direction.
        
        Params:
        -------
            ship : Ship
                The current ship to rotate.
            direction : str
                The direction for the ship to face.
        """
        for y, x in ship.locs:
            self.grid[y][x] = OPEN

        rotate_point = ship.locs[0]
        y, x = rotate_point

        dy, dx = (0, 1) if direction == "H" else (1, 0)
        for i in range(ship.size): 
            ny, nx = y + dy * i, x + dx * i

            ship.locs[i] = (ny, nx)
            self.grid[ny][nx] = CURRENT_SHIP
            
    def confirm_ship(self, ship: Ship):
        """Confirms the placement of the given ship.
        
        Params:
        -------
            ship : Ship
                The ship to confirm.
        """
        for y, x in ship.locs:
            self.grid[y][x] = CONFIRMED_SHIP
            
        ship.final_placed = True
        
    def select_ship(self, ship: Ship):
        """Selects and highlights the given ship so the player can choose its location.
        
        Params:
        -------
            ship : Ship
                The ship to select.
        """
        for y, x in ship.locs:
            self.grid[y][x] = CURRENT_SHIP
            
        ship.final_placed = False
            
    def deselect_ship(self, ship: Ship):
        """Deselects the current ship for placement.
        
        Params:
        -------
            ship : Ship
                The ship to deselect
        """
        for y, x in ship.locs:
            self.grid[y][x] = SHIP_NOT_CONFIRMED

    def get_ship_placement_embed(self, current_ship: Optional[Ship]=None):
        """Returns an embed showing the currently selected ship and
        the player's fleet on the board.
        
        Params:
        -------
            current_ship : Ship
                The currently selected ship
        """
        embed = discord.Embed(
            title="Place your ships!",
            description=f"```{self.__str__()}```",
            color=discord.Color.fuchsia(),
        )

        embed.add_field(
            name=f"{'Currently placing: ' if current_ship else 'Select a ship!'}",
            value=f"{current_ship if current_ship else '....'}"
        )

        embed.set_footer(
            text="Use the buttons to move the current ship, then click ✅ when you are done!")

        return embed

    def get_embed(self):
        """Returns an embed that shows the player's finalized ship placements on the board."""
        embed = discord.Embed(
            title="Your fleet: ",
            description=f"```{self.__str__()}```",
            color=discord.Color.dark_magenta()
        )

        embed.add_field(
            name="These are your ships, guard them with your life!",
            value=
            """
            Healthy ships have their sections marked as ⏹️
            Damaged ships have their sections marked as 🟥
            """)
        
        return embed



class AttackBoard(Board):
    """
    A specialized version of the `Board` class that represents a player's attack board.

    This class tracks hits and misses on the opponent's fleet, updating the board 
    state based on the results of each attack. It is used during the gameplay phase 
    to visualize the progress of the game.
    """
    def __init__(self):
        super().__init__()

    def get_embed(self):
        """Returns an embed that shows the player's attacking board that keeps track of their
        hits and misses on enemy ships.
        """
        embed = discord.Embed(
            title="These are your hits and misses. Try not to miss too much!",
            description=f"```{self.__str__()}```",
            color=discord.Color.red()
        )

        embed.add_field(
            name="Each attack on your enemy can have one of two results. You may only attack a position once!",
            value="""
            Your hits on enemy ships are marked with 🟥
            Your misses are marked with ⬜
            """)

        return embed
