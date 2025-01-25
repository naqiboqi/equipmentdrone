"""This module implements a Battleship game cog for a Discord bot, designed to manage 
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
"""



import discord

from discord.ext import commands
from typing import Optional
from .tictactoe_game import Game, GameView, Player



class TicTacToe(commands.Cog):
    """Commands to represent controls for starting and playing a Tic-tac-toe game.
    
    Attributes:
    ----------
        bot : commands.Bot
            The current bot instance.
        player_games : dict[int, GameView]
            Stores the games associated with each player.
    """
    def __init__(self, bot):
        self.bot = bot
        self.player_games: dict[int, GameView] = {}

    @commands.hybrid_command(name='tictactoe', aliases=["ttt"])
    async def _start(self, ctx: commands.Context, member: Optional[discord.Member]=None):
        """Starts a game of Tic-tac-toe between two players, or against me!
        
        Player 1 will always go first. If a second player is not specified, then player 1
        will play against the bot. Players may only participate in one game at a time.

        Params:
        -------
            ctx: commands.Context
                The current context associated with a command.
            member : discord.Member
                The other Discord `member` to play against. If `None`, plays agains the bot.
        """
        player_1 = Player(ctx.message.author, "⭕")

        bot_player = member is None
        player_2 = Player(member if member else self.bot.user, "❌")

        if (player_1.member.id in self.player_games or
            player_2.member.id in self.player_games):
            return await ctx.send("One of the players is already in a game!")

        game = Game(self.bot, player_1, player_2, bot_player)
        game.current_player = player_1
        view = GameView(game)
        game.view = view

        self.player_games[player_1.member.id] = game
        self.player_games[player_2.member.id] = game

        embed = game.get_embed()
        game.board_message = await ctx.send(embed=embed, view=view)
        game.turn_message = await ctx.send(f"{player_1.member.mention}, you are going first!")

    async def end_game(self, game: Game):
        """Sends the final state of the game cleans it up."""
        winner = game.winner
        if not winner:
            message = "The game has ended in a draw."
        else:
            message = f"{winner.member.name} has won the game!"

        await game.board_message.reply(message)
        await self.cleanup(game)

    async def cleanup(self, game: Game):
        """Cleans up the game instance and delete it from the stored player games.
        
        Params:
        -------
            game : Game
                The game that ended.
        """
        await game.cleanup()

        player_1 = game.player_1
        player_2 = game.player_2
        del self.player_games[player_1.member.id]
        del self.player_games[player_2.member.id]

async def setup(bot: commands.Bot):
    await bot.add_cog(TicTacToe(bot))
