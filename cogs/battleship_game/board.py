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
from .constants import emojis
from .ship import Ship



OPEN = "🟦"
"""Represents open water."""
CURRENT_SHIP = "🟩"
"""Represents the currently selected ship."""
CONFIRMED_SHIP = "⏹️"
"""Represents a ship with finalized placement."""
SHIP_NOT_CONFIRMED = "🟥"
"""Represents a ship that was placed, but not finalized."""


class Board():
    """Representation of a player's board in a game, serves as a base for the board's state.
    
    Attributes:
    ----------
        `size` : int
            The size of the board (in both width and height).
        `grid` : list[list[str]]
            A 2D grid representing the board. Each cell contains a symbol to indicate 
            its state (e.g., open water, a ship, or a hit/miss).
    """
    def __init__(self, size: int=10):
        self.size = size
        self.grid = [[OPEN for _ in range(self.size)] for _ in range(self.size)]

    def __getitem__(self, index: int):
        return self.grid[index]

    def __setitem__(self, index: int, val: str):
        self.grid[index] = val

    def __str__(self):
        """Returns a string representation of the board with labeled positions."""
        numbers = [
            emojis.get("one_border"),
            emojis.get("two_border"),
            emojis.get("three_border"),
            emojis.get("four_border"),
            emojis.get("five_border"),
            emojis.get("six_border"),
            emojis.get("seven_border"),
            emojis.get("eight_border"),
            emojis.get("nine_border"),
            emojis.get("ten_border"),
        ]

        letters = [
            emojis.get("board_a"),
            emojis.get("board_b"),
            emojis.get("board_c"),
            emojis.get("board_d"),
            emojis.get("board_e"),
            emojis.get("board_f"),
            emojis.get("board_g"),
            emojis.get("board_h"),
            emojis.get("board_i"),
            emojis.get("board_j"),
        ]

        board = f"{emojis.get('board_tl')}{''.join(numbers)}{emojis.get('board_tr')}\n"
        for i in range(self.size):
            row = self.grid[i]
            board += f"{letters[i]}{''.join(spot for spot in row)}{letters[i]}\n"

        board += f"{emojis.get('board_bl')}{''.join(numbers)}{emojis.get('board_br')}\n"
        return board

    def clear_board(self):
        """Clears the board of all ships."""
        self.grid = [[OPEN for _ in range(self.size)] for _ in range(self.size)]

    def _is_valid_loc(self, ship: Ship, y: int, x: int, direction: str):
        """Returns whether or not the given location is a valid placement for a ship.
        
        Is used for the initial random placement. 
        A location is valid if all locations occupied by the ship are only open water.
        
        Params:
        -------
            ship : Ship
                The current ship to check.
            y : int
                The y coordinate to test the ship.
            x : int
                The x coordinate to test the ship.
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
        """Returns whether or not the given movement will result be a location for a ship.
        
        A location is valid if the ship is within bounds of the board.
        
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

        return True

    def is_valid_rotation(self, ship: Ship, direction: str):
        """Returns whether or not rotating the ship will result in valid placement.
        
        A location is valid if the ship is within bounds of the board.
        
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

        return True

    def is_valid_confirm_loc(self, ship: Ship, fleet: list[Ship]):
        """Checks to make sure that the confirming ship does not intersect another ship.
        
        If there is an intersection, returns that ship, or `None` otherwise.
        
        Params:
        -------
            ship : Ship
                The current ship to check.
            fleet: list[Ship]
                The ships to check against.
        """
        for other_ship in fleet:
            if ship == other_ship:
                continue
            if set(ship.locs) & set(other_ship.locs):
                return other_ship

        return None



class DefenseBoard(Board):
    """A specialized version of the `Board` class that represents a player's fleet board.

    This class manages the placement, movement, and rotation of ships during the setup phase
    of the game. It also provides methods to confirm ship placements and to generate visual 
    representations of the fleet for the player while the game is in progress.
    """
    def __init__(self):
        super().__init__(size=10)

    @property
    def embed(self):
        """An embed that shows the player's finalized ship placements on the board."""
        embed = discord.Embed(
            title="These are your ships. Be sure to guard them with your life!",
            description=f"{self}",
            color=discord.Color.dark_magenta())

        embed.add_field(
            name="For you to keep track....",
            value="""
            ⏹️: Healthy ship sections
            
            🟥: Damaged ship sections""")

        return embed

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

    def random_place_ships(self, fleet: list[Ship], bot_player: bool=False):
        """Attemps to randomly place each ship from a player's fleets onto the board.
        
        Ensures that no ships intersect and are within the bounds of the board.

        Params:
        -------
            fleet : list[Ship]
                The player's ships.
            bot_player : bool
                If the placing player is a bot or not.
        """
        self.clear_board()

        for ship in fleet:
            ship.locs = []
            ship.confirmed = False
            ship.placed_before = False

            while not ship.placed_before and not ship.confirmed:
                y, x = random.randint(0, self.size - 1), random.randint(0, self.size - 1)
                direction = random.choice(["H", "V"])
                if self._is_valid_loc(ship, y, x, direction):
                    self._place_ship(ship, y, x, direction, bot_player)
                    ship.placed_before = True

    def _place_ship(self, ship: Ship, y: int, x: int, direction: str, bot_player):
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
                The direction for the ship to face.
            bot_player : bool
                If the placing player is a bot or not.
        """
        dy, dx = (0, 1) if direction == "H" else (1, 0)
        for i in range(ship.size):
            ny, nx = y + dy * i, x + dx * i
            ship.locs.append((ny, nx))
            self.grid[ny][nx] = CONFIRMED_SHIP if bot_player else SHIP_NOT_CONFIRMED

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
        for i in range(len(ship.locs)):
            y, x = ship.locs[i]
            ny, nx = y + dy, x + dx
            ship.locs[i] = (ny, nx)

    def rotate_ship(self, ship: Ship, direction: str):
        """Rotates the ship in the given direction.
        
        Params:
        -------
            ship : Ship
                The current ship to rotate.
            direction : str
                The direction for the ship to face.
        """
        rotate_point = ship.locs[0]
        y, x = rotate_point

        dy, dx = (0, 1) if direction == "H" else (1, 0)
        for i in range(ship.size): 
            ny, nx = y + dy * i, x + dx * i
            ship.locs[i] = (ny, nx)

    def redraw(self, fleet: list[Ship]):
        """Redraws the board with updated ship positions.
        
        Params:
        -------
            fleet : list[Ship]
                The player's fleet.
        """
        self.clear_board()

        for ship in fleet:
            for y, x in ship.locs:
                if ship.current_ship:
                    self.grid[y][x] = CURRENT_SHIP
                elif ship.confirmed:
                    self.grid[y][x] = CONFIRMED_SHIP
                elif ship.placed_before:
                    self.grid[y][x] = SHIP_NOT_CONFIRMED

    def confirm_ship(self, ship: Ship):
        """Confirms the placement of the given ship.
        
        Params:
        -------
            ship : Ship
                The ship to confirm.
        """
        for y, x in ship.locs:
            self.grid[y][x] = CONFIRMED_SHIP

        ship.current_ship = False
        ship.confirmed = True

    def select_ship(self, ship: Ship):
        """Selects and highlights the given ship so the player can choose its location.
        
        Params:
        -------
            ship : Ship
                The ship to select.
        """
        for y, x in ship.locs:
            self.grid[y][x] = CURRENT_SHIP

        ship.current_ship = True
        ship.confirmed = False

    def deselect_ship(self, ship: Ship):
        """Deselects the current ship for placement.
        
        Params:
        -------
            ship : Ship
                The ship to deselect
        """
        for y, x in ship.locs:
            self.grid[y][x] = SHIP_NOT_CONFIRMED

        ship.current_ship = False

    def reset_ship(self, ship: Ship):
        """Resets the positions of the ship."""
        ship.placed_before = False
        ship.confirmed = False
        ship.current_ship = False
        ship.locs = []

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
            description=f"{self}",
            color=discord.Color.fuchsia())

        embed.add_field(
            name=f"{'Currently placing: ' if current_ship else 'Select a ship!'}",
            value=f"{current_ship if current_ship else '....'}")

        embed.set_footer(
            text="Use the buttons to move the current ship, then click ✅ when you are done!")

        return embed



class AttackBoard(Board):
    """
    A specialized version of the `Board` class that represents a player's attack board.

    This class tracks hits and misses on the opponent's fleet, updating the board 
    state based on the results of each attack. It is used during the gameplay phase 
    to visualize the progress of the game.
    """
    def __init__(self):
        super().__init__(size=10)

    @property
    def embed(self):
        """An embed that shows the player's attacking board that keeps track of their
        hits and misses on enemy ships.
        """
        embed = discord.Embed(
            title="These are your hits and misses. Try not to miss too much!",
            description=f"{self}",
            color=discord.Color.red())

        embed.add_field(
            name="For you to keep track....",
            value="""
            🟥: Hits on enemy ships
            
            ⬜: Misses on enemy ships""")

        return embed
