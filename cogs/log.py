from discord import Embed

class Event():
    event_counter = 1

    def __init__(
        self, 
        participants: list,
        event_type: str,
        event: list[tuple[int, int]]|None):

        self.event_id = Event.event_counter
        self.participants = participants
        self.event_type = event_type
        self.event = event
        
        self.Event.event_counter += 1

    def __repr__(self):
        attacker = self.participants[0]
        defender = self.participants[1]

        event_types = {
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

            "next_turn" : f"It is `{attacker.member.name}'s` turn.",
        }

        return f"{self.event_id}) {event_types[self.event_type]}"


class Log():
    def __init__(self):
        self.events: list[Event] = []
        self.embed: Embed = None

    def add_event(
        self, 
        participants: list,
        event_type: str, 
        event: list[tuple[int, int]]|None):
        """
        Adds a new event to the game log.
        """
        event = Event(participants, event_type, event)
        self.events.append(event)
        print(event)

    async def get_embed_pages(self):
        event_slices = [self.events[i:i + 10]
            for i in range(0, len(self.events), 10)]

        pages: list[Embed] = []
        for event_slice in event_slices:

            events = "\n".join(str(event) for event in event_slice)
            page = Embed(
                title="Game Log", 
                description=events, 
                color=0x206694)

            pages.append(page)

        return pages