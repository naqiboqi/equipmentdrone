"""
This module defines the `Ship` class, representing a ship
in a player's fleet in the `Battleship` game.
"""


class Ship():
    """Representation of a ship in a player's fleet.
    
    Attributes:
    ----------
        `health` (list[bool]): Stores the health of the ship's components.
        For example, a `Ship` of size `4` could look like
        `self.health = [True, True, True, True]`.
        A `Ship` with a health array of all `False` means that it has sunk.
        
        `locs` (list[tuple[int, int]]): Stores the `(y, x)` locations of the ship's components.
        For example, a `Ship` of size `4` could look like
        `self.locs = [(1, 0), (2, 0), (3, 0), (4, 0)]`
        
        `size` (int): The size and starting health of the ship.
    """
    def __init__(self, size: int):
        self.health = [True] * size
        self.locs: list[tuple[int, int]] = []
        self.size = size
        self.placed = False

    def take_damage_at(self, y: int, x: int):
        """Damages the targeted section of the ship.
        
        Sets the associated `Ship` section's health at that `(y, x)` coordinate of that board to False by
        getting the index of that coordinate in `self.locs`.

        Params:
        -------
            `y` (int): The y coordinate of the location.
            `x` (int): The x coordinate of the location.
        """
        section = self.locs.index((y, x))
        self.health[section] = False

    def is_sunk(self):
        """Returns whether the `Ship` has lost all of its health.
        
        A sunken `Ship` has all elements = `False` in `self.health`.
        """
        return all(hp is False for hp in self.health)

    def __str__(self):
        return f"A ship of size {self.size}. Currently at {self.health.count(True)} hit points."
