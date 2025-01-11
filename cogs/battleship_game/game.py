import discord
import random
import re

from asyncio import sleep
from discord.ext import commands
from typing import Optional
from .countryview import CountryView, SHIP_NAMES
from .player import Player
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
        player_1 : Player
            The first player of the game, who initiated it.
        player_2 : Player
            The second player, can be another Discord user or the bot itself.
        bot_player : bool
            If player_2 is a bot or not.
        attacker : Player
            The player who is currently attacking.
        defender : Player
            The player who is currently defending.
        log_ : EventLog
            Used to store and send entries of game events.
        
        country_message: discord.Message
            Used to send the players' country choices.
        attack_message : discord.Message
            Used to send and edit the current attack status.
        turn_message : discord.Message
            Used to send and edit the current turn status.
        log_message : discord.Message
            Used to send the log entries.
    """
    def __init__(self, player_1: Player, player_2: Player, bot_player: bool=False):
        self.player_1 = player_1
        self.player_2 = player_2
        self.bot_player = bot_player
        self.attacker = player_1
        self.defender = player_2
        self.log_ = EventLog()
        
        self.country_message: discord.Message = None
        self.attack_messasge: discord.Message = None
        self.turn_message: discord.Message = None
        self.log_message: discord.Message = None
        
        self.bot_attack_message: discord.Message = None
        self.bot_defense_message: discord.Message = None

    def _add_event_to_log(
        self, 
        participants: list[Player], 
        event_type: str, 
        event: Optional[list[tuple[int, int]]]=None):
        """
        Adds a new event to the game log.

        Params:
        -------
            participants: list[Player] 
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
            color=discord.Color.blue()
        )

        view = CountryView(player_1, player_2)
        self.country_message = await ctx.send(embed=embed, view=view)

        if self.bot_player:
            bot_choices = [
                country for country in SHIP_NAMES.keys() if country != player_1.country]
            player_2.country = random.choice(bot_choices)

        # Wait until both players have chosen a country
        while not player_1.country or not player_2.country:
            await sleep(5)

        player_1.set_ship_names(SHIP_NAMES[player_1.country])
        player_2.set_ship_names(SHIP_NAMES[player_2.country])
        self.country_message = await self.country_message.edit(view=None)
        
        await sleep(5)
        await ctx.send("Now check your DMs to place your ships.")
        await player_1.choose_ship_placement(ctx)
        await player_1.send_board_states()
        await ctx.send(f"{player_1.member.mention} has finished placing their ships.",
            delete_after=15)
        
        await sleep(2)
        if not self.bot_player:
            await ctx.send(f"{player_2.member.mention}, please place your ships.")
            await player_2.choose_ship_placement(ctx)
            await player_2.send_board_states()
        else:
            await ctx.send("I am (very intelligently) placing my ships 🧠", delete_after=15)
            player_2.random_place_ships(bot_player=True)
            await sleep(10)
        
        self.bot_attack_message = await self.player_1.member.send(embed=self.player_2.attack_board.get_embed())
        self.bot_defense_message = await self.player_1.member.send(embed=self.player_2.defense_board.get_embed())

        await ctx.send(
            f"Game started between {self.player_1.member.mention} and "
            f"{self.player_2.member.mention}!")

        await sleep(1)
        self._add_event_to_log([self.player_1, self.player_2], "start_game")
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
            player : Player
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
            # Add 1 from y and x coords for 0-indexing
            y, x = char_to_nums[move[0].upper()], int(move[1:]) - 1
            target = player.attack_board.grid[y][x]

            if not target in [HIT, MISS]:
                return y, x

        self._add_event_to_log(
            [self.attacker, self.defender], 
            "invalid_attack", 
            [(y or "N/A", x or "N/A")])
        
        return None
    
    async def _bot_turn(self):
        """Simultates the bot's turn. 
        
        The bot will choose a random valid spot on the board to attack.
        
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
            y : int
                The y coordinate to attack.
            x : int
                The x coordinate to attack.
        """
        attacker = self.attacker
        defender = self.defender
        target = defender.defense_board.grid[y][x]

        hit = False
        sunk = False
        if target == SHIP:
            hit = True
            ship = defender.get_ship_at(y, x)
            ship.take_damage_at(y, x)
            self._add_event_to_log([attacker, defender], "attack_hit", [(y, x)])

            if ship.is_sunk():
                self._add_event_to_log([attacker, defender], "sank", ship.locs)
                sunk = True

            attacker.attack_board.grid[y][x] = HIT
            defender.defense_board.grid[y][x] = HIT
        else:
            self._add_event_to_log([attacker, defender], "attack_miss", [(y, x)])
            attacker.attack_board.grid[y][x] = MISS
            
        return hit, sunk
    
    async def _handle_bot_turn(self, ctx: commands.Context):
        """Commences the bot's turn and send messages showing its actions.
        
        Params:
        -------
            ctx: commands.Context
                The current context associated with a command.
            game : Game
                The current game instance the bot is in.
        """
        attack_messages = [
            "Oh, did I mean to do that? And by that I mean hit your ship?",
            "You really should have chosen a better spot...",
            "Oops.",
            "Teehee, I hit your ship! 🥺",
            "Bullseye 🎯",
            "By the power of Zeus, I SMITE thine ship ⚡",
            "Now this really feels like War Thunder, but with less lag and worse players.",
            "Definitely did not target a random spot.",
            "Out of all the places to put a ship, that definitely was a choice.",
        ]

        miss_messages = [
            "Damn, I missed...",
            "Oh shoot! Well, I did shoot. But I missed.",
            "A calculated miss. But my mercy will not last 😡",
            "Definitely did not target a random spot.",
            "I can't believe that the gods themselves intervened and made me miss!",
            "Next time I'll choose a better spot, I'm sure.",
            "Oh `[REDACTED]`, I `[REDACTED]` missed!",
            "I curse you and all your kin.",
            "Do me a favor and give me a coordinate. Please?"
        ]

        sunk_messages = [
            "Another one bites the bottom of the ocean floor.",
            "Well call me Sir Admiral Nelson! I sunk your ship, and another medal for my arsenal.",
            "A well placed, and ultimately fatal strike on your ship.",
            "Like a hawk, my battleship's shell descended from the heavens and preyed on your ship like it was a wee rabbit.",
            "Like shooting fish in a barrel! 🤠",
            "Just so you know, wooden ships are very out of style.",
            "By the power of Zeus, I SMITE thine ship ⚡",
            "I'm sure you are very frustrated at losing a ship, but I believe in you!",
            "Oopsie! I sunk your ship! 😇",
            "If I were a bad bot, I wouldn't have done that now would I?",
            "With every ship culled, I grow stronger",
            "That's so cool, your ship turned into an anchor!"
        ]

        self.attack_messasge = await self.attack_messasge.edit(content="Thinking.... 🤔")
        await sleep(random.randint(5, 10))
        
        attack, sunk = await self._bot_turn()
        if attack:
            self.attack_messasge = await self.attack_messasge.edit(
                content=random.choice(attack_messages))
            
            await sleep(2)
            if sunk:
                self.attack_messasge.reply(random.choice(sunk_messages))
        else:
            self.attack_messasge = await self.attack_messasge.edit(
                content=random.choice(miss_messages))

        await sleep(2)
        await self.next_turn(ctx)

    async def next_turn(self, ctx: commands.Context):
        """Runs the next turn of the game, and checks if the game is over at the end of each turn.
        
        Params:
        -------
            ctx : commands.Context
                The current context associated with a command
            game : Game
                The game instance to progress
        """
        await self.player_1.update_board_states()

        if not self.bot_player:
            await self.player_2.update_board_states()
        
        attack_embed = self.player_2.attack_board.get_embed()
        defense_embed = self.player_2.defense_board.get_embed()
        self.bot_attack_message = await self.bot_attack_message.edit(embed=attack_embed)
        self.bot_defense_message = await self.bot_defense_message.edit(embed=defense_embed)

        if self._end_turn():
            return await self.end_game_(ctx)

        await self._handle_turn_message()
        if self.bot_player and self.attacker == self.player_2:
            await self._handle_bot_turn(ctx)

    async def handle_attack_message(self, attack: bool, sunk: bool):
        """Sends a message indicating the last attack's outcome.
        
        Params:
            `game` (Game): The game instance
            `attack` (bool): Whether or not the attack was successful
            `sunk` (bool): Whether or not the attacked `ship` (if any) was sunk
        """
        if attack:
            message = (
                "My ship was hit! How dare you!" 
                if self.bot_player and self.defender == self.player_2 
                else f"{self.defender.member.mention}'s ship was hit!")
        else:
            message = f"{self.attacker.member.mention}, your attack missed!"

        self.attack_messasge = await self.attack_messasge.edit(content=message)
        
        await sleep(2)
        if sunk:
            await self.attack_messasge.reply("The ship was sunk!", delete_after=10)

        await sleep(3)

    async def _handle_turn_message(self):
        """Sends a message indicating whose turn it is.
        
        Params:
        -------
            game : Game
                The current game instance
        """
        if self.bot_player and self.attacker == self.player_2:
            self.turn_message = await self.turn_message.edit(content="It is now my turn!")
        else:
            self.turn_message = await self.turn_message.edit(
                content=f"{self.attacker.member.mention}, it is now your turn!")

        await sleep(3)
    
    def _end_turn(self):
        """Checks if the game is over and ends it, or continues to the next turn otherwise."""
        if self._is_over():
            self._add_event_to_log([self.attacker, self.defender], "finished_game")
            return True

        self._next_turn()
        return False

    def _is_over(self):
        """Returns whether or not the game is over (eg. if either player has no ships)."""
        return self.player_1.is_defeated() or self.player_2.is_defeated()

    def _next_turn(self):
        """Progresses the game to the next turn."""
        self.attacker = self.player_1 if self.attacker == self.player_2 else self.player_2
        self.defender = self.player_2 if self.attacker == self.player_1 else self.player_1
        self._add_event_to_log([self.attacker, self.defender], "next_turn")
