"""
This module implements the core Battleship game logic, handling gameplay mechanics 
and game state management for the Discord bot. It provides functionality for ship 
placement, attacking, turn-based play, and game state tracking.

### Key Features:
- **Game Logic**:
    - Manages the core Battleship gameplay, including ship placement, attack validation, 
        and turn progression.
    - Supports multiplayer games, allowing human players or bots to compete.
    - Tracks game state to ensure smooth play and manage turn order.

- **Ship Placement**:
    - Validates player ship placements, ensuring no overlap or invalid positions.
    - Allows players to strategically position their ships before the game starts.

- **Turn-based Play**:
    - Handles turn-based gameplay, allowing players to attack opponents' boards.
    - Tracks each attack and updates the game state accordingly, including hits, misses, 
        and sunk ships.

- **Game State Management**:
    - Keeps track of the ongoing game state and updates the board configurations.
    - Provides methods to check the winner and update the game status.

### Classes:
- **`Game`**:
    Manages the logic of the Battleship game, including player turns, ship placements, 
    attack validation, and game state tracking.

### Dependencies:
- **`discord`**: For interacting with Discord APIs and handling bot commands.
- **`random`**: For randomizing ship placements and attack targeting.
- **`re`**: For regular expression matching and validation (e.g., coordinates).
- **`asyncio`**: For managing sleep delays and asynchronous operations (if required).
- **`discord.ext`**: For Discord command usage
- **`typing`**: For optional type annotations.
"""



import discord
import random
import re

from asyncio import sleep
from discord.ext import commands
from typing import Optional
from .battleship_player import BattleshipPlayer
from .constants import bot_messages, ship_names
from .country_view import CountryView
from ..utils import EventLog



HIT = "🟥"
"""Represents a successful attack."""
MISS = "⬜"
"""Represents a missed attack."""
SHIP = "⏹️"
"""Represents a ship segment."""



class Game:
    """Representation of the Battleship game.
    
    Handles turn progression and action validation.
    
    Attributes:
    ----------
        player_1 : BattleshipPlayer
            The first player of the game, who initiated it.
        player_2 : BattleshipPlayer
            The second player, can be another Discord user or the bot itself.
            If player_2 is a bot or not.
        attacker : BattleshipPlayer
            The player who is currently attacking.
        defender : BattleshipPlayer
            The player who is currently defending.
        log_ : EventLog
            Used to store and send entries of game events.
        
        country_message : discord.Message
            Used to send the players' country choices.
        attack_message : discord.Message
            Used to send and edit the current attack status.
        turn_message : discord.Message
            Used to send and edit the current turn status.
        log_message : discord.Message
            Used to send the log entries.
    """
    def __init__(self, bot: commands.Bot, player_1: BattleshipPlayer, player_2: BattleshipPlayer):
        self.bot = bot
        self.player_1 = player_1
        self.player_2 = player_2
        self.attacker = player_1
        self.defender = player_2
        self.log_ = EventLog()

        self.country_message: discord.Message = None
        self.attack_messasge: discord.Message = None
        self.turn_message: discord.Message = None
        self.log_message: discord.Message = None

    @property
    def is_over(self):
        """If the game is over (eg. if either player has no ships)."""
        return self.player_1.is_defeated or self.player_2.is_defeated

    @property
    def is_bot_turn(self):
        """If it is currently the bot's turn, if the bot is in the game."""
        return self.attacker == self.player_2 and self.player_2.is_bot

    def _add_event_to_log(
        self, 
        participants: list[BattleshipPlayer], 
        event_type: str, 
        event: Optional[list[tuple[int, int]]]=None):
        """
        Adds a new event to the game log.

        Params:
        -------
            participants : list[BattleshipPlayer] 
                The players involved in the event.
            event_type : str
                A tag to represent the type of the event.
            event : list[tuple[int, int]] 
                Coordinates of the event, if any.
        """
        self.log_.add_event(participants, event_type, event)

    async def setup(self, ctx: commands.Context):
        """Sets the initial game state.

        Params:
        -------
            ctx : commands.Context
                The current context associated with a command.
        """
        player_1 = self.player_1
        player_2 = self.player_2

        embed = discord.Embed(
            title="Select a country to lead into battle 🌎",
            color=discord.Color.blue())

        view = CountryView(player_1, player_2, timeout=300)
        self.country_message = await ctx.send(embed=embed, view=view)

        if player_2.is_bot:
            bot_choices = [
                country for country in ship_names.keys() if country != player_1.country]
            player_2.country = random.choice(bot_choices)

        while not player_1.country or not player_2.country:
            await sleep(5)

        player_1.set_ship_names(ship_names[player_1.country])
        player_2.set_ship_names(ship_names[player_2.country])
        self.country_message = await self.country_message.edit(view=None)

        await sleep(2)
        await ctx.send("Check your DMs to place your ships.")
        await player_1.choose_ship_placement(ctx)
        await player_1.send_board_states()
        await ctx.send(f"{player_1.mention} has finished placing their ships.",
            delete_after=15)

        await sleep(2)
        if not self.player_2.is_bot:
            await ctx.send(f"{player_2.mention}, please place your ships.")
            await player_2.choose_ship_placement(ctx)
            await player_2.send_board_states()
        else:
            await ctx.send("I am (very intelligently) placing my ships 🧠", delete_after=15)
            player_2.random_place_ships()
            await sleep(10)

        await ctx.send(f"{player_2.mention} has finished placing their ships.",
            delete_after=15)

        await ctx.send(
            f"Game started between {self.player_1.mention} and "
            f"{self.player_2.mention}!")

        await sleep(1)
        self._add_event_to_log([self.player_1, self.player_2], "start_game")
        self.turn_message = await ctx.send(
            f"{self.player_1.mention}, you are going first!")

        await sleep(1)
        self.attack_messasge = await ctx.send("Waiting for your move...")

    def is_move_valid(self, player: BattleshipPlayer, move: str=""):
        """Returns whether or not a player's move is valid.
        
        Letters range from A-J (case-insensitive) and numbers from 1-10.

        Valid examples:
            `/attack A10`
            
            `/attack b5`

        Note that a player may only attack a given position once.

        Params:
        -------
            player : BattleshipPlayer
                The attacking player.
            move : str
                The input move to be validated.
        """
        char_to_nums = {
            "A" : 0, "B" : 1, "C" : 2, "D" : 3, "E" : 4,
            "F" : 5, "G" : 6, "H" : 7, "I" : 8, "J" : 9,
        }

        pattern = r'^[a-jA-J](1[0-9]|[1-9])$'
        if re.match(pattern, move):
            y, x = char_to_nums[move[0].upper()], int(move[1:]) - 1
            target = player.attack_board[y][x]

            if not target in [HIT, MISS]:
                return y, x

        self._add_event_to_log(
            [self.attacker, self.defender], 
            "invalid_attack", 
            [(y or "N/A", x or "N/A")])

        return None

    def _do_bot_turn(self):
        """Simultates the bot's turn. 
        
        The bot will choose a random valid spot on the board to attack.
        
        Returns whether or not the attack missed.
        """      
        valid_move = None
        while not valid_move:
            y, x = random.randint(0, 9), random.randint(0, 9)
            move = f"{chr(65 + y)}{x + 1}"
            valid_move = self.is_move_valid(self.player_2, move)

        attack, sunk = self.commence_attack(valid_move[0], valid_move[1])
        return attack, sunk 

    def commence_attack(self, y: int, x: int):
        """Attacks the targeted `(y, x)` location of the board.
        
        Returns whether the attack hit a ship and if that ship was sunk.

        Params:
        -------
            y : int
                The y coordinate to attack.
            x : int
                The x coordinate to attack.
        """
        attacker = self.attacker
        defender = self.defender
        target = defender.defense_board[y][x]

        hit = False
        sunk = False
        if target == SHIP:
            hit = True
            ship = defender.get_ship_at(y, x)
            ship.take_damage_at(y, x)
            self._add_event_to_log([attacker, defender], "attack_hit", [(y, x)])

            if ship.is_sunk:
                self._add_event_to_log([attacker, defender], "sank", ship.locs)
                sunk = True

            attacker.attack_board[y][x] = HIT
            defender.defense_board[y][x] = HIT
        else:
            self._add_event_to_log([attacker, defender], "attack_miss", [(y, x)])
            attacker.attack_board[y][x] = MISS

        return hit, sunk

    async def _handle_bot_turn(self, ctx: commands.Context):
        """Commences the bot's turn and send messages showing its actions.
        
        Params:
        -------
            ctx : commands.Context
                The current context associated with a command.
        """
        self.attack_messasge = await self.attack_messasge.edit(content="Thinking.... 🤔")
        await sleep(random.randint(1, 5))

        hit, sunk = self._do_bot_turn()
        if hit:
            self.attack_messasge = await self.attack_messasge.edit(
                content=random.choice(bot_messages.get("attack_messages")))

            await sleep(1)
            if sunk:
                self.attack_messasge.reply(
                    random.choice(bot_messages.get("sunk_messages")))
        else:
            self.attack_messasge = await self.attack_messasge.edit(
                content=random.choice(bot_messages.get("miss_messages")))

        await sleep(2)
        await self.next_turn(ctx)

    async def next_turn(self, ctx: commands.Context):
        """Runs the next turn of the game, and checks if the game is over at the end of each turn.
        
        Params:
        -------
            ctx : commands.Context
                The current context associated with a command.
        """
        await self.player_1.update_board_states()

        if not self.player_2.is_bot:
            await self.player_2.update_board_states()

        if self.is_over:
            self._add_event_to_log([self.attacker, self.defender], "finished_game")
            return await self.end_game_(ctx)

        self.attacker = self.player_1 if self.attacker == self.player_2 else self.player_2
        self.defender = self.player_2 if self.attacker == self.player_1 else self.player_1
        self._add_event_to_log([self.attacker, self.defender], "next_turn")

        await self._handle_turn_message()
        if self.is_bot_turn:
            await self._handle_bot_turn(ctx)

    async def handle_attack_message(self, attack: bool, sunk: bool):
        """Sends a message indicating the last attack's outcome.
        
        Params:
        -------
            attack : bool
                Whether or not the attack was successful.
            sunk : bool
                Whether or not the attacked `ship` (if any) was sunk.
        """
        if attack:
            message = (
                "My ship was hit! How dare you!" if self.defender.is_bot 
                else f"{self.defender.mention}'s ship was hit!")
        else:
            message = f"{self.attacker.mention}, your attack missed!"

        self.attack_messasge = await self.attack_messasge.edit(content=message)

        await sleep(2)
        if sunk:
            await self.attack_messasge.reply("The ship was sunk!", delete_after=10)

        await sleep(2)

    async def _handle_turn_message(self):
        """Sends a message indicating whose turn it is."""
        if self.is_bot_turn:
            self.turn_message = await self.turn_message.edit(content="It is now my turn!")
        else:
            self.turn_message = await self.turn_message.edit(
                content=f"{self.attacker.mention}, it is now your turn!")

        await sleep(3)
