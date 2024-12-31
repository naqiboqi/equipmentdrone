"""
This module implements a Battleship game cog for a Discord bot, designed to manage 
Battleship gameplay and user interaction within a server (guild). It utilizes the 
`discord.py` library to interact with Discord APIs, providing functionality for 
game setup, turn-based play, and result tracking.

### Key Features:
- **Game Logic**:
    - Handles the core Battleship gameplay, including ship placement, attack validation, 
      and turn progression.
    - Supports multiplayer games between human players or bots.
    - Manages game state tracking to ensure smooth play and turn order.

- **Discord Integration**:
    - Provides Discord commands for initiating games, making moves, and displaying game status.
    - Interactive bot messages to facilitate gameplay, ensuring players know whose turn it is 
      and the results of their actions.

- **Ship Placement**:
    - Validates player ship placements to ensure no overlap or invalid positions.
    - Allows players to strategically position their ships before the game starts.

- **Turn-based Play**:
    - Supports turn-based gameplay, allowing players to attack opponents' boards.
    - Validates and processes each attack to track hits, misses, and sunk ships.

- **Game State Management**:
    - Tracks ongoing game states and board configurations.
    - Provides embed updates and result displays to players via Discord.

### Classes:
- **`BattleshipGame`**:
    Manages the core logic of the Battleship game, handling player turns, attack validation, 
    ship placements, and game state tracking.
- **`BattleshipBot`**:
    A Discord cog integrating the game logic with Discord commands, enabling users to 
    start games, make moves, and view game results through bot interactions.

### Constants:
- **`GRID_SIZE`**: The size of the game grid for Battleship.
- **`MAX_SHIPS`**: Maximum number of ships each player can place.
- **`SHIP_SIZES`**: List defining the size of each ship type.

### Dependencies:
- **`discord.py`**: For interacting with Discord APIs and handling bot commands.
- **`asyncio`**: For asynchronous event handling and turn-based game logic.
- **`random`**: For randomizing attack results and placing ships.
- **`typing`**: For type hinting and function signatures.
- **`collections`**: For managing game state and player data.
- **`itertools`**: For combinations and sequences.
"""


import discord
import random
import re
import typing

from asyncio import sleep
from discord.ext import commands
from .battleship_game import Player
from .battleship_game import HIT, MISS, SHIP
from .event_log import EventLog, LogView



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
        event: list[tuple[int, int]]|None=None):
        """
        Adds a new event to the game log.
        """
        self.log_.add_event(participants, event_type, event)

    async def setup(self, ctx):
        """Sets the initial game state, placing player's ships
        and sends the initial boards to the players.
        """
        player_1 = self.player_1
        player_2 = self.player_2

        player_1.place_ships()
        player_2.place_ships()

        await ctx.send(
            f"Game started between {self.player_1.member.mention} and "
            f"{self.player_2.member.mention}!")

        try:
            player_1.fleet_msg = await self.player_1.member.send(
                f"Player 1 ships:\n```{player_1.board.__str__()}```\n")

            player_1.track_msg = await self.player_1.member.send(
                f"Player 1 hits/misses:\n```{player_1.tracking_board.__str__()}```\n")

            if not self.bot_player:
                player_2.fleet_msg = await player_2.member.send(
                    f"Player 2 ships:\n```{player_2.board.__str__()}```\n")

                player_2.fleet_msg = await self.player_2.member.send(
                    f"Player 2 hits/misses:\n```{player_2.tracking_board.__str__()}```\n")
            else:
                player_2.fleet_msg = await ctx.send(
                    f"Player 2 ships:\n```{player_2.board.__str__()}```\n")

                player_2.track_msg = await ctx.send(
                    f"Player 2 hits/misses:\n```{player_2.tracking_board.__str__()}```\n")

        except discord.errors.Forbidden:
            await ctx.send(f"Could not send the game boards to {player_1.member.mention}"
                f"or {player_2.member.mention}. Please check your DM settings.")

        await sleep(1)
        self.add_event_to_log([self.player_1, self.player_2], "start_game")
        self.turn_message = await ctx.send(
            f"{self.player_1.member.mention}, you are going first!")
        
        await sleep(1)
        self.attack_messasge = await ctx.send("Waiting for your move...")

    def is_move_valid(self, player: Player, move: str=""):
        """Returns whether or not a player's move is valid.
        
        Letters range from A-J and numbers from 1-10.
        Valid examples:
            `/attack A10`
            
            `!attack B5`

        Note that a player may only attack a given position once.
        """
        char_nums = {
            "A" : 0, "B" : 1, "C" : 2, "D" : 3, "E" : 4,
            "F" : 5, "G" : 6, "H" : 7, "I" : 8, "J" : 9,
        }

        pattern = r'^[a-jA-J](1[0-9]|[1-9])$'
        if re.match(pattern, move):
            # Add 1 from y and x coords for 0-indexing
            y, x = char_nums[move[0].upper()], int(move[1:]) - 1
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
        """Perform an attack at the targeted position on the board.
        
        Returns whether the attack hit a ship and if that ship (if any) was sunk.
        """
        attacker = self.attacker
        defender = self.defender
        target = defender.board.grid[y][x]

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
            defender.board.grid[y][x] = HIT
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


class BattleShip(commands.Cog):
    """Commands to represent controls for starting and playing a Battleship game.
    
    Attributes:
    ----------
        `bot`: The current bot instance
        `player_games` (dict[int, Game]): Stores the games associated with each player
    """
    def __init__(self, bot):
        self.bot = bot
        self.player_games: typing.Dict[int, Game] = {}

    @commands.hybrid_command(name='battleship')
    async def start_(self, ctx, member: discord.Member=None):
        """Starts a game of battleship between two players, or against you and me!
        
        Player 1 will always go first.
        """
        player_1 = Player(ctx.message.author)

        bot_player = member is None
        player_2 = Player(member if member else self.bot.user)

        if (player_1.member.id in self.player_games or
            player_2.member.id in self.player_games):
            return await ctx.send("One of the players is already in a game!")

        game = Game(player_1, player_2, bot_player)
        self.player_games[player_1.member.id] = game
        self.player_games[player_2.member.id] = game
        await game.setup(ctx)

    @commands.hybrid_command(name='attack')
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def attack_(self, ctx, move: str):
        """Execute an attack at specified position on the board. Format as `A1`

        Params:
        -------
            `move` (str): The location on the board to attack.
            
            Must be a letter-number combination where the letter must be from A to J and
            the number from 1 to 10
        
        Examples:
        --------
            `/attack A10`
            
            `!attack B5`
        
        Valid attacks are determined by the method `game.is_move_valid` method.
        A player may only attack a given position once.
        
        If the attack command is valid, performs an attack on the board and
        then proceeds to the next turn, or prompts the user again if invalid.
        """
        game = self.player_games.get(ctx.author.id)
        if not game:
            return await ctx.send("You are not in a game!")

        if game.attacker.member.id != ctx.author.id:
            return await ctx.send("It is not your turn!", delete_after=10)

        parsed = game.is_move_valid(player=game.attacker, move=move)
        if not parsed:
            return await ctx.send(f"The move {move} is not valid, try again.", delete_after=10)

        await ctx.send(f"Attacking {move}...", delete_after=5)
        await sleep(5.5)
        
        attack, sunk = game.commence_attack(parsed[0], parsed[1])
        await self.handle_attack_message_(game, attack, sunk)
        await self.next_turn(ctx, game)

    # @commands.hybrid_command(name="score")
    # async def show_scores_(self, ctx):
    #     """Displays the hit points of your fleet, and total hits and misses."""
    #     game = self.player_games.get(ctx.author.id)
    #     if not game:
    #         return await ctx.send("No game is currently running.")
        
    #     player_1 = game.player_1
    #     player_2 = game.player_2
        
    @commands.hybrid_command(name="movelog")
    async def show_move_log_(self, ctx):
        """Sends an embed containing all the moves of the game."""
        game = self.player_games.get(ctx.author.id)
        if not game:
            return await ctx.send("You are not in a game!")
        
        pages = await game.log_.get_embed_pages()
        if not pages:
            return await ctx.send("The log is empty.")
        
        view = LogView(pages)
        game.log_message = await ctx.send(embed=pages[0], view=view)
        
    async def handle_bot_turn_(self, ctx, game: Game):
        """Performs the bot's turn and send appropriate messages."""
        game.attack_messasge = await game.attack_messasge.edit(content="Thinking.... 🤔")
        await sleep(random.randint(5, 10))
        
        attack, sunk = await game.bot_turn()
        if attack:
            game.attack_messasge = await game.attack_messasge.edit(
                content=f"{game.defender.member.mention}'s ship was hit!")
            
            await sleep(3)
            if sunk:
                game.attack_messasge.reply("Oopsie! I sunk your ship! 😇")
        else:
            game.attack_messasge = await game.attack_messasge.edit(content="Oh, shoot, I missed!")

        await self.next_turn(ctx, game)

    async def next_turn(self, ctx, game: Game):
        """Runs the next turn of the game."""
        player_1 = game.player_1
        player_2 = game.player_2

        # Edit all of the board messages
        player_1.fleet_msg = await player_1.fleet_msg.edit(
            content=f"Player 1 ships: \n```{player_1.board.__str__()}```")

        player_1.track_msg = await player_1.track_msg.edit(
            content=f"Player 1 hits/misses: \n```{player_1.tracking_board.__str__()}```")

        player_2.fleet_msg = await player_2.fleet_msg.edit(
            content=f"Player 2 ships: \n```{player_2.board.__str__()}```")

        player_2.track_msg = await player_2.track_msg.edit(
            content=f"Player 2 hits/misses: \n```{player_2.tracking_board.__str__()}```")

        if game.end_turn():
            return await self.end_game_(ctx, game)

        await self.handle_turn_message_(game)
        if game.bot_player and game.attacker == game.player_2:
            await self.handle_bot_turn_(ctx, game)

    async def handle_attack_message_(self, game: Game, attack: bool, sunk: bool):
        """Sends a message indicating the attack's outcome."""
        if attack:
            message = (
                "My ship was hit! How dare you!" 
                if game.bot_player and game.defender == game.player_2 
                else f"{game.defender.member.mention}'s ship was hit!")
        else:
            message = f"{game.attacker.member.mention}, your attack missed!"

        game.attack_messasge = await game.attack_messasge.edit(content=message)
        
        await sleep(3)
        if sunk:
            await game.attack_messasge.reply("The ship was sunk!", delete_after=10)

        await sleep(5)

    async def handle_turn_message_(self, game: Game):
        """Sends a message indicating whose turn it is."""
        if game.bot_player and game.attacker == game.player_2:
            game.turn_message = await game.turn_message.edit(content="It is now my turn!")
        else:
            game.turn_message = await game.turn_message.edit(
                content=f"{game.attacker.member.mention}, it is now your turn!")

        await sleep(5)

    async def end_game_(self, ctx, game: Game):
        """Ends the currently running game."""
        player_1 = game.player_1
        player_2 =  game.player_2

        if game.bot_player and game.attacker == game.player_2:
            await ctx.send("I win the game! 🏆")
        else:
            await ctx.send(f"{game.attacker.member.mention}, you win the game! 🏆")

        del self.player_games[player_1.member.id]
        del self.player_games[player_2.member.id]


async def setup(bot):
    await bot.add_cog(BattleShip(bot))
