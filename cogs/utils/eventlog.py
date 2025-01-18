"""
This module implements a log viewer for a Discord bot, designed to display a series of game events 
as interactive embed pages within a Discord channel. It utilizes the `discord.py` library to 
interact with Discord APIs, providing functionality for user navigation through the log.

### Key Features:
- **Embed-Based Navigation**:
    - Display events in paginated embed pages for better readability.
    - Navigate between pages using "Previous" and "Next" buttons.

- **Interactive Buttons**:
    - Intuitive UI with buttons for seamless navigation.

### Classes:
- **`Event`**:
    Represents an individual game event with details of participants, event type, and ID.
- **`Log`**:
    Maintains a collection of game events and provides methods to add new events and generate embed pages for display.

### Dependencies:
- **`discord`**: For interacting with Discord APIs and sending embeds.
"""


from discord import Embed
from typing import Optional



class Event():
    """Represents an event with details of its type, participants, and ID.
    
    Attributes:
    -----------
        event_id : int
            Unique ID for each `event`.
        partipants : list
            Users involved in the `event`.
        event_type : str
            Type of event.
        event : list[tuple[int, int]]
            Details of the `event` (coordinates).
    """
    event_counter = 1

    def __init__(
        self, 
        participants: list,
        event_type: str,
        event: Optional[list[tuple[int, int]]]):

        self.event_id = Event.event_counter
        self.participants = participants
        self.event_type = event_type
        self.event = event
        Event.event_counter += 1

    def __repr__(self):
        """Returns a formatted string representation of the event."""
        attacker = self.participants[0]
        defender = self.participants[1]

        event_descriptions = {
            "attack_hit" : f"`{attacker.member.name}` hit"
                f" `{defender.member.name}'s` ship by attacking `{self.event}`.",

            "attack_miss" : f"`{attacker.member.name}` missed"
                f" by attacking `{self.event}`.",

            "sank" : f"`{attacker.member.name}` sank"
                f" `{defender.member.name}'s` ship at `{self.event}`.",

            "invalid_attack" : f"`{attacker.member.name}` input an"
                f" invalid attack at `{self.event}`.",

            "start_game" : f"A new game started between `{attacker.member.name}`"
                f" and `{defender.member.name}`.",

            "finished_game" : f"`{attacker.member.name}` won the game against"
                f" `{defender.member.name}`.",

            "next_turn" : f"It is `{attacker.member.name}'s` turn."
        }

        return f"{self.event_id}) {event_descriptions.get(self.event_type, 'Unknown event')}"


class EventLog():
    """Represents a log of `events` that can be displayed.
    
    Can create new `events` with specified details in `add_event()`.
    
    Attributes:
    -----------
        events : list[Event]
            The stored events.
    """
    def __init__(self):
        self.events: list[Event] = []

    def add_event(
        self, 
        participants: list,
        event_type: str, 
        event: Optional[list[tuple[int, int]]]):
        """
        Adds a new `event` to the game log with the given details.
        
        Params:
        -------
            participants : list
                Users involved in the `event`.
            event_type : str
                Type of `event`, used for the string representation.
            event : list[tuple[int, int]]
                Details of the `event`.
        """
        event = Event(participants, event_type, event)
        self.events.append(event)