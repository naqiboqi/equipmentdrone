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
- **`Game`**:
    Manages the core logic of the Battleship game, handling player turns, attack validation, 
    ship placements, and game state tracking.
- **`Battleship`**:
    A Discord cog integrating the game logic with Discord commands, enabling users to 
    start games, make moves, and view game results through bot interactions.

### Dependencies:
- **`discord`**: For interacting with Discord APIs and handling bot commands.
- **`random`**: For randomizing ship placement.
- **`re`**: For matching user input attack strings.
- **`asyncio`**: For sleep delays.
- **`battleship_game`**: Game 
"""


import discord
import random

from asyncio import sleep
from discord.ext import commands
from .battleship_game import Player, Game
from .event_log import LogView



class BattleShip(commands.Cog):
    """Commands to represent controls for starting and playing a Battleship game.
    
    Attributes:
    ----------
        `bot`: The current bot instance
        `player_games` (dict[int, Game]): Stores the games associated with each player
    """
    def __init__(self, bot):
        self.bot = bot
        self.player_games: dict[int, Game] = {}

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
