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
- ** `typing`**: For optional type annotations.
- **`asyncio`**: For sleep delays.
"""



import discord

from asyncio import sleep
from discord.ext import commands
from typing import Optional
from .battleship_game import BattleshipPlayer, Game
from .utils import PageView



class BattleShip(commands.Cog):
    """Commands to represent controls for starting and playing a Battleship game.
    
    Attributes:
    ----------
        bot : commands.Bot
            The current bot instance.
        player_games : dict[int, Game]
            Stores the games associated with each player.
    """
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.player_games: dict[int, Game] = {}

    @commands.hybrid_command(name='battleship')
    async def _start(self, ctx: commands.Context, member: Optional[discord.Member]=None):
        """Starts a game of battleship between two players, or against the me!
        
        Player 1 will always go first. If a second player is not specified, then player 1
        will play against the bot. Players may only participate in one game at a time.

        Params:
        -------
            ctx: commands.Context
                The current context associated with a command.
            member : discord.Member
                The other Discord `member` to play against. If `None`, plays agains the bot.
        """
        player_1 = BattleshipPlayer(ctx.author)

        if member and member.bot and member != self.bot.user:
            return await ctx.send("Can't play against that bot, they are not smart enough!")

        is_bot = member is None
        player_2 = BattleshipPlayer(
            member=member if member else self.bot.user,
            is_bot=is_bot)

        if (player_1.id in self.player_games or
            player_2.id in self.player_games):
            return await ctx.send("One of the players is already in a game!")

        if player_1 == player_2:
            return await ctx.send("You can't play against yourself!")

        game = Game(self.bot, player_1, player_2)
        self.player_games[player_1.id] = game
        self.player_games[player_2.id] = game
        await game.setup(ctx)

    @commands.hybrid_command(name='attack')
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def _attack(self, ctx: commands.Context, move: str):
        """Attacks the given position on the board. Valid attacks are `A1`, `b9`, `c10`, `d4`, etc.

        Params:
        -------
            ctx: commands.Context
                The current context associated with a command.
            move : str
                The input move to be validated.
        
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
        await sleep(3)
        
        attack, sunk = game.commence_attack(parsed[0], parsed[1])
        await game.handle_attack_message(attack, sunk)
        await game.next_turn(ctx)
        
    @commands.hybrid_command(name="movelog")
    async def _show_move_log(self, ctx: commands.Context):
        """Sends an embed containing all the moves of the game.
        
        Params:
        -------
            ctx: commands.Context
                The current context associated with a command.
        """
        game = self.player_games.get(ctx.author.id)
        if not game:
            return await ctx.send("You are not in a game!")
        
        view = PageView("Battleship Game Log", game.log_.events)
        game.log_message = await ctx.send(embed=view.pages[0], view=view)
        
    async def end_game_(self, ctx: commands.Context, game: Game):
        """Ends the currently running game.
        
        Params:
        -------
            ctx: commands.Context
                The current context associated with a command.
            game : Game
                The game instance to end.
        """
        player_1 = game.player_1
        player_2 =  game.player_2

        if game.bot_player and game.attacker == game.player_2:
            await ctx.send("I win the game! 🏆")
        else:
            await ctx.send(f"{game.attacker.member.mention}, you win the game! 🏆")

        del self.player_games[player_1.member.id]
        del self.player_games[player_2.member.id]


async def setup(bot: commands.Bot):
    await bot.add_cog(BattleShip(bot))
