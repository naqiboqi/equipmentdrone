import discord

import asyncio
from discord.ext import commands
from typing import Optional
from .connect_game import ConnectFourPlayer, Game



class ConnectFour(commands.Cog):
    """Commands to represent controls for starting and playing a Connect Four game.
    
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

    @commands.hybrid_command(name="connectfour", aliases=["c4"])
    async def _start(self, ctx: commands.Context, member: Optional[discord.Member]=None):
        """Starts a game of Connect Four between two players, or against me!
        
        Player 1 will always go first. If a second player is not specified, then player 1
        will play against the bot. Players may only participate in one game at a time.

        Params:
        -------
            ctx: commands.Context
                The context for the current command.
            member : discord.Member
                The other Discord `member` to play against. If `None`, plays agains the bot.
        """
        player_1 = ConnectFourPlayer(member=ctx.author, symbol="🟪")

        if member and member.bot and member != self.bot.user:
            return await ctx.send("Can't play against that bot, they are not smart enough!")

        is_bot = member is None
        player_2 = ConnectFourPlayer(
            member=member if not is_bot else self.bot.user, 
            symbol="🟥", 
            is_bot=is_bot)

        if (player_1.id in self.player_games or 
            player_2.id in self.player_games):
            return await ctx.send("One of the players is in a game!")

        if player_1 == player_2:
            return await ctx.send("You can't play against yourself!")

        game = Game(self.bot, player_1, player_2)
        self.player_games[player_1.id] = game
        self.player_games[player_2.id] = game
        await game.setup(ctx)

    @commands.hybrid_command(name="drop")
    async def _drop_piece(self, ctx: commands.Context, column: int):
        """Drops a piece in the chosen column.
        
        Params:
            ctx : commands.Context
                The context for the current command.
            column : int
                The column to drop in.
        """
        player_id = ctx.author.id
        game = self.player_games.get(player_id)
        if not game:
            return await ctx.send("You are not in the game!", delete_after=10)

        await game.player_turn(ctx, column, player_id)

    @commands.hybrid_command(name="endconnectfour")
    async def _end(self, ctx: commands.Context):
        """Ends the current game. Can be cancelled up to 10 seconds afterwards.
        
        Params:
            ctx : commands.Context
                The context for the current command.
        """
        player_id = ctx.author.id
        game = self.player_games.get(player_id)

        if not game:
            return await ctx.send("Nice try, but you are not in the game!", delete_after=10)

        end_message = await ctx.send("Ending the game in 10 seconds, reply `❌` to cancel.")
        def check(reaction: discord.Reaction, user):
            return (reaction.message.id == end_message.id and
                str(reaction.emoji) == "❌" and
                user.id in self.player_games)

        try:
            await self.bot.wait_for("reaction_add", check=check, timeout=10)
            await end_message.delete()
            return await ctx.send("The game shall continue!", delete_after=10)

        except asyncio.TimeoutError:
            await end_message.delete()
            await self.end_game(game)

    async def end_game(self, game: Game):
        """Sends the final state of the game and cleans it up."""
        winner = game.winner
        if not winner:
            message = "The game has ended in a draw."
        else:
            message = f"{winner.name} has won the game! 🎉"

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
    await bot.add_cog(ConnectFour(bot))