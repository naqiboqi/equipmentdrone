import discord

from asyncio import sleep
from discord.ext import commands
from typing import Optional
from connect_game import Game, Player



class ConnectFour(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.player_games: dict[int, Game] = {}

    @commands.hybrid_command(name="connectfour", aliases=["c4"])
    async def _start(self, ctx: commands.Context, member: Optional[discord.Member]=None):
        player_1 = Player(discord.Color.blue(), ctx.author)

        bot_player = member is None
        player_2 = Player(discord.Color.red(), member if member else self.bot.user)

        if (player_1.member.id in self.player_games or 
            player_2.member.id in self.player_games):
            return await ctx.send("One of the players is in a game!")

        if player_1 == player_2:
            return await ctx.send("You can't play against yourself!")

        game = Game(player_1, player_2, bot_player)
        self.player_games[player_1.member.id] = game
        self.player_games[player_2.member.id] = game
        await game.setup(ctx)

    @commands.hybrid_command(name="drop")
    async def _drop_piece(self, ctx: commands.Context, column: int):
        player_id = ctx.author.id
        game = self.player_games.get(player_id)

        if not game:
            return await ctx.send("You are not in the game!", delete_after=10)

        await game.player_turn(ctx, column, player_id)
        
    # @commands.hybrid_command(name="endconnectfour")
    # async def _end(self, ctx: commands.Context):
    #     player_id = ctx.author.id
    #     game = self.player_games.get(player_id)
        
    #     if not game:
    #         return await ctx.send("Nice try, but you are not in the game!", delete_after=10)

    #     end_message = await ctx.send("Ending the game in 10 seconds, reply `❌` to cancel.")
        
    #     timer = 10
        
    #     while timer >= 0:
    #         sleep(1)
    #         timer -= 1
            
    #         if end_message.reply()
    #     else:
            

    async def end_game(self, game: Game):
        """Sends the final state of the game and cleans it up."""
        winner = game.winner
        if not winner:
            message = "The game has ended in a draw."
        else:
            message = f"{winner.member.name} has won the game! 🎉"

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