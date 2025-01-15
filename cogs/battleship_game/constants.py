"""This module loads the emojis and ship names required for battleship."""



import os

from ..utils import JsonLoader



SHIP_NAMES_FILE = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../data/ship_names.json"))

ship_names = JsonLoader.load_json(SHIP_NAMES_FILE)
"""Stores the possible ship names for each country and class of ship."""