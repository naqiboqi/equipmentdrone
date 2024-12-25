import discord
import random
import re
import typing

from discord.ext import commands

OPEN = ""


class Ship():
    def __init__(self, size: int):
        self.health = [True] * size
        self.size = size
        self.sunk = False

    def take_damage(self, section):
        self.health[section] = False
        self.sunk = all(not hp for hp in self.health)
    
    def __str__(self):
        return f"A ship of size {self.size}. Currently at {self.health} hit points."


class Player():
    def __init__(self, member: discord.Member):
        self.board = Board()
        self.tracking_board = Board()
        self.fleet = [Ship(size) for size in range(2, 6)]
        self.member = member
        
    def place_ships(self):
        self.board.random_place_ships(self.fleet)

    def is_defeated(self):
        return all(ship.sunk for ship in self.fleet)


class Board():
    def __init__(self):
        self.size = 10
        self.grid = [[OPEN for _ in range(self.size)] for _ in range(self.size)]
        
    def is_valid_loc(self, ship: Ship, x: int, y: int, direction: str):
        dx, dy = (1, 0) if direction == "H" else (0, 1)

        for i in range(ship.size):
            nx, ny = x + dx * i, y + dy * i
            if nx >= self.size or ny >= self.size or self.grid[ny][nx] != OPEN:
                return False

        return True

    def place_ship(self, ship: Ship, x: int, y: int, direction: str):
        if not self.is_valid_loc(ship, x, y, direction):
            raise ValueError("Invalid ship placement.")

        dx, dy = (1, 0) if direction == "H" else (0, 1)
        for i in range(ship.size):
            nx, ny = x + dx * i, y + dy * i
            self.grid[ny][nx] = ship

    def random_place_ships(self, fleet: list[Ship]):
        for ship in fleet:
            placed = False
            while not placed:
                x, y = random.randint(0, self.size - 1), random.randint(0, self.size - 1)
                direction = random.choice(["H", "V"])
                if self.is_valid_loc(ship, x, y, direction):
                    self.place_ship(ship, x, y, direction)
                    placed = True
    
    def __str__(self):
        board = ""
        for row in self.grid:
            board += " ".join("X"
                "H" if spot == "H" else
                "M" if spot == "M" else
                "." if spot == OPEN else
                "S"
            for spot in row) + "\n"
        return board
    

class Game:
    def __init__(self, player_1: Player, player_2: Player, bot_player: bool=False):
        self.player_1 = player_1
        self.player_2 = player_2
        self.bot_player = bot_player
        self.turn = player_1
        self.other = player_2
        self.winner = None
        
    def setup(self):
        self.player_1.place_ships()
        self.player_2.place_ships()
        
    def next_turn(self):
        self.turn = self.player_1 if self.turn == self.player_2 else self.player_2
        self.other = self.player_2 if self.turn == self.player_1 else self.player_1
        
    def process_attack(self, x: int, y: int):
        attacker = self.turn
        defender = self.other
        target = defender.board.grid[y][x]
        
        if isinstance(target, Ship):
            ship = target
            ship_section = ship.health.index(True)
            ship.take_damage(ship_section)
                
            attacker.tracking_board.grid[y][x] = "H"
            return True, ship.sunk
        
        attacker.tracking_board.grid[y][x] = "M"
        return False, False
        
    def is_over(self):
        return self.player_1.is_defeated() or self.player_2.is_defeated()


class BattleShip(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.player_games: typing.Dict[Player, Game] = {}

    @commands.hybrid_command(name='battleship')
    async def start(self, ctx, member: discord.Member=None):
        player_1 = Player(ctx.message.author)
        
        bot_player = member is None
        player_2 = Player(member if member else self.bot.user)
        
        if (player_1.member.id in self.player_games or
            player_2.member.id in self.player_games):
            return await ctx.send("One of the players is already in a game!")
        
        game = Game(player_1, player_2, bot_player)
        self.player_games[player_1.member.id] = game
        self.player_games[player_2.member.id] = game
        game.setup()
        
        await ctx.send(f"""
            Game started between {player_1.member.mention} and {player_2.member.mention}!""")

        try:
            await player_1.member.send(f"Your board:\n```{player_1.board.__str__()}```")

            if not bot_player:
                await player_2.member.send(f"Your board:\n```{player_2.board.__str__()}```")
            else:
                await ctx.send("The bot is ready! Let the battle begin!")
                print(player_2.board)

        except discord.errors.Forbidden:
            await ctx.send(f"""Could not send the game boards to {player_1.member.mention} or
                {player_2.member.mention}. Please check your DM settings.""")
        
        # while not game.is_over():
        #     pass
        
    async def is_move_valid(self, move: str):
        if not move:
            return False

        pattern = r'[a-jA-J][1-9]10$'
        return re.match(pattern, move)

    @commands.hybrid_command(name='attack')
    async def attack(self, ctx, move: str):
        game = self.player_games.get(ctx.author.id)
        if not game:
            return await ctx.send("You are not in a game!")
        
        if game.turn.member.id != ctx.author.id:
            return await ctx.send("It is not your turn!")
        
        if not await self.is_move_valid(move):
            return await ctx.send(f"The move {move} is not valid!")
        
        #hit, was_sunk = game.process_attack(x, y)
        #if hit:
        #    await ctx.send(f"{game.other.member.mention}, Your ship was hit!")
        
        
async def setup(bot):
    await bot.add_cog(BattleShip(bot))