import discord
import random
import re

from asyncio import sleep
from discord.ext import commands
from typing import Optional
from ..event_log import EventLog
from .player import Player



HIT = "🟥"
MISS = "⬜"
SHIP = "⏹️"



class Game:
    """Representation of the Battleship game.
    
    Handles turn progression and action validation.
    
    Attributes:
    ----------
        `player_1` (Player): The first player of the game, who initiated it
        `player_2` (Player): The second player, can be another Discord user or the bot itself
        `bot_player` (bool): If player_2 is a bot or not
        `attacker` (Player): The player who is currently attacking
        `defender` (Player): The player who is currently defending
        
        `attack_messasge` (discord.Message): The Discord message used to send and edit the current attack status
        `turn_message` (discord.Message): The Discord message used to send and edit the current turn status
        `log_` (EventLog): Keeps tracks of all the hits, misses, and sunken ships
    """
    def __init__(self, player_1: Player, player_2: Player, bot_player: bool=False):
        self.player_1 = player_1
        self.player_2 = player_2
        self.bot_player = bot_player
        self.attacker = player_1
        self.defender = player_2
        self.log_ = EventLog()
        
        self.attack_messasge: discord.Message = None
        self.turn_message: discord.Message = None
        self.log_message: discord.Message = None

    def add_event_to_log(
        self, 
        participants: list[Player], 
        event_type: str, 
        event: Optional[list[tuple[int, int]]]):
        """
        Adds a new event to the game log.

        Params:
        -------
            `participants` (list[Player]): The players involved in the event
            `event_type` (str): A tag to represent the type of the event
            `event` (list[tuple[int, int]]|None): Coordinates of the event, if any
        """
        self.log_.add_event(participants, event_type, event)

    async def setup(self, ctx: commands.Context):
        """Sets the initial game state, placing player's ships
        and sends the initial boards to the players.

        Params:
        -------
            `ctx` (commands.Context): The current `context` associated with a command
        """
        player_1 = self.player_1
        player_2 = self.player_2

        await ctx.send("Please check your DMs in order to place your ships.")
        await player_1.choose_ship_placement(ctx)
        self.add_event_to_log([self.player_1], "ship_placement")
        
        if not self.bot_player:
            await player_2.choose_ship_placement(ctx)
        else:
            await player_2.random_place_ships()

        await ctx.send(
            f"Game started between {self.player_1.member.mention} and "
            f"{self.player_2.member.mention}!")

        await sleep(1)
        self.add_event_to_log([self.player_1, self.player_2], "start_game")
        self.turn_message = await ctx.send(
            f"{self.player_1.member.mention}, you are going first!")
        
        await sleep(1)
        self.attack_messasge = await ctx.send("Waiting for your move...")

    def is_move_valid(self, player: Player, move: str=""):
        """Returns whether or not a player's move is valid.
        
        Letters range from A-J (case-insensitive) and numbers from 1-10.

        Valid examples:
            `/attack A10`
            
            `/attack b5`

        Note that a player may only attack a given position once.

        Params:
        -------
            `player` (Player): The attacking player
            `move` (str): The input move to be validated
        """
        char_to_nums = {
            "A" : 0, "B" : 1, "C" : 2, "D" : 3, "E" : 4,
            "F" : 5, "G" : 6, "H" : 7, "I" : 8, "J" : 9,
        }

        pattern = r'^[a-jA-J](1[0-9]|[1-9])$'
        if re.match(pattern, move):
            # Add 1 from y and x coords for 0-indexing
            y, x = char_to_nums[move[0].upper()], int(move[1:]) - 1
            target = player.tracking_board.grid[y][x]

            if not target in [HIT, MISS]:
                return y, x

        self.add_event_to_log([self.attacker, self.defender], "invalid_attack", [(y, x)])
        return None
    
    async def bot_turn(self):
        """Simultates the bot's turn. 
        
        The bot will choose a random valid spot on the board to attack,
        and utilizes the `commence_attack(y, x)` method.
        
        Returns whether or not the attack missed.
        """      
        bot_player = self.player_2

        valid_move = None
        while not valid_move:
            y, x = random.randint(0, 9), random.randint(0, 9)
            move = f"{chr(65 + y)}{x + 1}"
            valid_move = self.is_move_valid(bot_player, move)

        attack, sunk = self.commence_attack(valid_move[0], valid_move[1])
        return attack, sunk 

    def commence_attack(self, y: int, x: int):
        """Attacks the targeted `(y, x)` location of the board.
        
        Returns whether the attack hit a ship and if that ship was sunk.

        Params:
        -------
            `y` (int): The y coordinate to attack
            `x` (int): The x coordinate to attack
        """
        attacker = self.attacker
        defender = self.defender
        target = defender.fleet_board.grid[y][x]

        hit = False
        sunk = False
        if target == SHIP:
            hit = True
            ship = defender.get_ship_at(y, x)
            ship.take_damage_at(y, x)
            self.add_event_to_log([attacker, defender], "attack_hit", [(y, x)])

            if ship.is_sunk():
                self.add_event_to_log([attacker, defender], "sank", ship.locs)
                sunk = True

            attacker.tracking_board.grid[y][x] = HIT
            defender.fleet_board.grid[y][x] = HIT
        else:
            self.add_event_to_log([attacker, defender], "attack_miss", [(y, x)])
            attacker.tracking_board.grid[y][x] = MISS
            
        return hit, sunk
    
    def end_turn(self):
        """Checks if the game is over and ends it,
        or continues to the next turn otherwise.
        """
        if self.is_over_():
            self.add_event_to_log([self.attacker, self.defender], "finished_game")
            return True

        self.next_turn_()
        return False

    def is_over_(self):
        """Returns whether or not the game is over (if either player has no ships)."""
        return self.player_1.is_defeated() or self.player_2.is_defeated()

    def next_turn_(self):
        """Progresses the game to the next turn."""
        self.attacker = self.player_1 if self.attacker == self.player_2 else self.player_2
        self.defender = self.player_2 if self.attacker == self.player_1 else self.player_1
        self.add_event_to_log([self.attacker, self.defender], "next_turn")
