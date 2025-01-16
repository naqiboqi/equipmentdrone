"""This module loads the emojis required for the video player."""

import os

from ..utils import JsonLoader



EMOJIS_FILE = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../data/emojis.json"))

emojis = JsonLoader.load_json(EMOJIS_FILE)
"""Stores the emojis."""