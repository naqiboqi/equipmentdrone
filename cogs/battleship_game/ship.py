"""
This module defines the ship class, representing a ship
in a player's fleet in the `Battleship` game.
"""


class Ship():
    """Representation of a ship in a player's fleet.
    
    Attributes:
    ----------
        size : int
            The size and starting health of the ship.
        name : str
            The name of the ship.
        ship_class : str
            The class (or type) of ship.
        
        health : list[bool] 
            Stores the health of the ship's components.
        
        For example, a ship of size `4` could look like:
        
        `self.health = [True, True, True, True]`
        
        A ship with a health array of all `False` means that it has sunk.
        
        locs : list[tuple[int, int]] 
            Stores the `(y, x)` locations of the ship's components.
        
        For example, a ship of size `4` could look like:

        `self.locs = [(1, 0), (2, 0), (3, 0), (4, 0)]`
        
        final_placed : bool
            Whether or not the ship's position is finalized.
        placed_before : bool
            Whether or not the ship has been placed before.
    """
    def __init__(self, size: int):
        self.size = size
        self.name: str = None
        self.ship_class: str = None
        self.health = [True] * size
        self.locs: list[tuple[int, int]] = []
        self.final_placed = False
        self.placed_before = False

    def take_damage_at(self, y: int, x: int):
        """Damages the targeted section of the ship.
        
        Sets the associated ship section's health at that `(y, x)` coordinate of that board to False by
        getting the index of that coordinate in `self.locs`.

        Params:
        -------
            y : int
                The y coordinate of the location.
            x : int
                The x coordinate of the location.
        """
        section = self.locs.index((y, x))
        self.health[section] = False

    def is_sunk(self):
        """Returns whether the ship has lost all of its health."""
        return all(hp is False for hp in self.health)

    def __str__(self):
        """Returns a string representation of the ship.
        
        For example:
            `The SS Varmland, a Destroyer. Currently at 2 health.`"""
        return f"""
            The **{self.name}**, a {self.ship_class} (size: {self.size})
            Currently at {self.health.count(True)} health."""
