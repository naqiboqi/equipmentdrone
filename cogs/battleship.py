import discord
import random
import re
import typing

from asyncio import sleep
from discord.ext import commands



SHIP = "⏹️"
OPEN = "🟦"
HIT = "🟥"
MISS = "⬜"


class Ship():
    """Representation of a ship in a player's fleet.
    
    The ship's health is represented by an array of bools,
    where undamaged spots are `True` and damaged are `False`.
    An array of `False` indicates that that ship has sunk.
    
    The ship's location is represented by an array of `tuples (y, x)` coordinates
    taken up by the ship's "spots". This array's length is the same as the health array.
    
    This is used to determine which "spot" in the health array needs to be damaged.
    
    Attributes:
    ----------
        `health` (list[bool]): Stores the health of the ship's components.
        For example, a `Ship` of size `4` could look like `self.health = [True, True, True, True]`
        
        `locs` (list[tuple[int, int]]): Stores the `(y, x)` locations of the ship's components.
        For example, a `Ship` of size `4` could look like `self.locs = [(1, 0), (2, 0), (3, 0), (4, 0)]`
        
        `size` (int): The size and starting health of the ship.
    """
    def __init__(self, size: int):
        self.health = [True] * size
        self.locs: list[tuple[int, int]] = []
        self.size = size

    def take_damage(self, y: int, x: int):
        """Damages the targeted section of the ship."""
        section = self.locs.index((y, x))
        self.health[section] = False
        
    def is_sunk(self):
        """Checks if the ship has lost all of its health."""
        return all(hp is False for hp in self.health)

    def __str__(self):
        return f"A ship of size {self.size}. Currently at {self.health.count(True)} hit points."


class Player():
    """Represantation of a player in a Battleship game.
    
    Each player has a board of their own ships and an associated fleet array,
    and a board to track the hits or misses on their opponent's ships.
    
    Attributes:
    ----------
        `board` (Board): Used to store the player's ships
        `tracking_board` (Board): Used to store the player's hits and misses
        `fleet` (list[Ship]): The player's ships
        `member` (discord.Member): The Discord member object associated with the player
        `fleet_msg` (discord.Message): The Discord message used to send and edit the player's fleet
        `track_msg` (discord.Message): The Discord message used to send and edit the player's hits and misses
    """
    def __init__(self, member: discord.Member):
        self.board = Board()
        self.tracking_board = Board()
        self.fleet = [Ship(size) for size in [2, 3, 3, 4, 5]]
        self.member = member
        
        self.fleet_msg: discord.Message = None
        self.track_msg: discord.Message = None
        
    def __eq__(self, other: "Player"):
        return self.member == other.member
        
    def get_ship_at(self, y: int, x: int):
        """Returns the player's ship that is at the given `(y, x)` location."""
        loc = (y, x)
        for ship in self.fleet:
            if loc in ship.locs:
                return ship

    def place_ships(self):
        """Randomly place ships on the player's board."""
        self.board.random_place_ships(self.fleet)

    def is_defeated(self):
        """Returns whether all of the player's ships are sunk."""
        return all(ship.is_sunk() for ship in self.fleet)


class Board():
    """Representation of a player's board in a game. 
    
    Handles location validation for player hits and misses on ships.
    
    Attributes:
    ----------
        `size` (int): The x and y sizes of the board
        `grid` (list[list[str]]): Keeps track of the player's ships if it is the fleet board,
        or their hits and misses if it is a tracking board.
    """
    def __init__(self):
        self.size = 10
        self.grid = [[OPEN for _ in range(self.size)] for _ in range(self.size)]

    def is_valid_loc(self, ship: Ship, y: int, x: int, direction: str):
        dy, dx = (0, 1) if direction == "H" else (1, 0)

        for i in range(ship.size):
            ny, nx = y + dy * i, x + dx * i
            if ny >= self.size or nx >= self.size or self.grid[ny][nx] != OPEN:
                return False

        return True

    def place_ship(self, ship: Ship, y: int, x: int, direction: str):
        """Places a ship at a given location on the board.
        
        Since all ships take up multiple portions, spaces on the board occupied by a ship
        are labeled by `S`.
        
        A ship present at those locations will also have its
        `self.locs` array appended to store the locations that it occupies.
        """
        dy, dx = (0, 1) if direction == "H" else (1, 0)
        for i in range(ship.size):
            ny, nx = y + dy * i, x + dx * i
            ship.locs.append((ny, nx))
            self.grid[ny][nx] = SHIP

    def random_place_ships(self, fleet: list[Ship]):
        """Attemps to randomly place each ship from a player's fleets onto the board.
        
        Makes sure that no ships intersect and are within the bounds of the board.
        """
        for ship in fleet:
            placed = False
            while not placed:
                x, y = random.randint(0, self.size - 1), random.randint(0, self.size - 1)
                direction = random.choice(["H", "V"])
                if self.is_valid_loc(ship, y, x, direction):
                    self.place_ship(ship, y, x, direction)
                    placed = True

    def __str__(self):
        board = ""
        for row in self.grid:
            board += " ".join(spot for spot in row) + "\n"
        return board


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
        
        `attack_msg` (discord.Message): The Discord message used to send and edit the current attack status
        `turn_msg` (discord.Message): The Discord message used to send and edit the current turn status
    """
    def __init__(self, player_1: Player, player_2: Player, bot_player: bool=False):
        self.player_1 = player_1
        self.player_2 = player_2
        self.bot_player = bot_player
        self.attacker = player_1
        self.defender = player_2
        
        self.attack_msg: discord.Message = None
        self.turn_msg: discord.Message = None

    async def setup(self, ctx):
        """Sets the initial game state, placing player's ships
        and sends the initial boards to the players.
        """
        player_1 = self.player_1
        player_2 = self.player_2

        player_1.place_ships()
        player_2.place_ships()

        await ctx.send(
            f"Game started between {self.player_1.member.mention} and"
            f"{self.player_2.member.mention}!")

        try:
            player_1.fleet_msg = await self.player_1.member.send(
                f"Player 1 ships:\n```{player_1.board.__str__()}```")
            
            player_1.track_msg = await self.player_1.member.send(
                f"Player 1 hits/misses:\n```{player_1.tracking_board.__str__()}```")
            
            if not self.bot_player:
                player_2.fleet_msg = await player_2.member.send(
                    f"Player 2 ships:\n```{player_2.board.__str__()}```")
                
                player_2.fleet_msg = await self.player_2.member.send(
                    f"Player 2 hits/misses:\n```{player_2.tracking_board.__str__()}```")
            else:
                player_2.fleet_msg = await ctx.send(
                    f"Player 2 ships:\n```{player_2.board.__str__()}```")
                
                player_2.track_msg = await ctx.send(
                    f"Player 2 hits/misses:\n```{player_2.tracking_board.__str__()}```")

        except discord.errors.Forbidden:
            await ctx.send(f"Could not send the game boards to {player_1.member.mention}"
                f"or {player_2.member.mention}. Please check your DM settings.")

        self.turn_msg = await ctx.send(
            f"{self.player_1.member.mention}, you are going first!")
        
    def next_turn(self):
        """Progresses the game to the next turn."""
        self.attacker = self.player_1 if self.attacker == self.player_2 else self.player_2
        self.defender = self.player_2 if self.attacker == self.player_1 else self.player_1

    def is_move_valid(self, player: Player, move: str=""):
        """Returns whether or not a player's move is valid.
        
        Letters range from A-J and numbers from 1-10.
        Valid examples:
            `/attack A10`
            
            `!attack B5`

        Note that a player may only attack a given position once.
        """
        char_nums = {
            "A" : 1, "B" : 2, "C" : 3, "D" : 4, "E" : 5,
            "F" : 6, "G" : 7, "H" : 8, "I" : 9, "J" : 10,
        }

        pattern = r'^[a-jA-J](1[0-9]|[1-9])$'
        if re.match(pattern, move):
            y, x = char_nums[move[0].upper()] - 1, int(move[1:]) - 1
            target = player.tracking_board.grid[y][x]

            if not target in [HIT, MISS]:
                return y, x

        return None
    
    async def bot_turn(self):
        """Commences the bot's turn.
        
        The bot will choose a random valid spot on the board to attack,
        and utilizes the `commence_attack(y, x)` method.
        
        Returns whether or not the attack missed.
        """      
        bot_player = self.player_2

        valid_move = None
        while not valid_move:
            y, x = random.randint(0, 9), random.randint(0, 9)
            valid_move = self.is_move_valid(bot_player, f"{chr(65 + y)}{x + 1}")

        attack = self.commence_attack(valid_move[0], valid_move[1])
        return attack

    def commence_attack(self, y: int, x: int):
        """Perform an attack at the targeted position on the board."""
        attacker = self.attacker
        defender = self.defender
        target = defender.board.grid[y][x]

        if target == SHIP:
            ship = defender.get_ship_at(y, x)
            ship.take_damage(y, x)
            print(f"Attack attempt: {attacker.member.mention} -> {y}, {x}, Result: Hit ship at: {ship.locs}")

            attacker.tracking_board.grid[y][x] = HIT
            defender.board.grid[y][x] = HIT
            return True

        print(f"Attack attempt: {attacker.member.mention} -> {y}, {x}, Result: Miss")
        attacker.tracking_board.grid[y][x] = MISS
        return False
    
    def end_turn(self):
        """Checks if the game is over and ends it,
        or continues to the next turn otherwise.
        """
        if self.is_over():
            return True

        self.next_turn()
        return False

    def is_over(self):
        """Returns whether or not the game is over (if either player has no ships)."""
        return self.player_1.is_defeated() or self.player_2.is_defeated()


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
        
        Examples:
            `/attack A10`
            
            `!attack B5`
        
        Valid attacks are determined by the method `game.is_move_valid` method.
        A player may only attack a given position once.
        
        If the attack command is valid, performs an attack on the board and
        then proceeds to the next turn if both players have at least one ship.
        Otherwise declares a winner and ends the game.
        """
        game = self.player_games.get(ctx.author.id)
        if not game:
            return await ctx.send("You are not in a game!")

        if game.attacker.member.id != ctx.author.id:
            return await ctx.send("It is not your turn!", delete_after=10)

        parsed = game.is_move_valid(player=game.attacker, move=move)
        if not parsed:
            return await ctx.send(f"The move {move} is not valid, try again.", delete_after=10)
        
        attack = game.commence_attack(parsed[0], parsed[1])
        await self.handle_attack_message_(ctx, game, attack)
        await self.next_turn(ctx, game)
                
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
        
    # @commands.hybrid_command(name="score")
    # async def show_scores_(self, ctx):
    #     """Displays the hit points of your fleet, and total hits and misses."""
    #     game = self.player_games.get(ctx.author.id)
    #     if not game:
    #         return await ctx.send("No game is currently running.")
        
    #     player_1 = game.player_1
    #     player_2 = game.player_2
        
    @commands.command(name="movelog")
    async def show_move_log_(self, ctx):
        game = self.player_games.get(ctx.author.id)
        if not game:
            return await ctx.send("You are not in a game!")
        
        
    async def next_turn(self, ctx, game: Game):
        """Runs the next turn of the game."""
        player_1 = game.player_1
        player_2 = game.player_2
        
        player_1.fleet_msg = await player_1.fleet_msg.edit(
            content=f"Player 1 ships: \n{player_1.board.__str__()}")
        
        player_1.track_msg = await player_1.track_msg.edit(
            content=f"Player 1 hits/misses: \n{player_1.tracking_board.__str__()}")
        
        player_2.fleet_msg = await player_2.track_msg.edit(
            content=f"Player 2 ships: \n{player_2.board.__str__()}")
        
        player_2.track_msg = await player_2.track_msg.edit(
            content=f"Player 2 hits/misses: \n{player_2.tracking_board.__str__()}")
        
        if game.end_turn():
            return await self.end_game_(ctx, game)
        
        await self.handle_turn_message_(ctx, game)
        if game.bot_player and game.attacker == game.player_2:
            await self.handle_bot_turn_(ctx, game)
            
    async def handle_attack_message_(self, ctx, game: Game, attack: bool):
        """Sends an appropriate message based on attack outcome."""
        if attack:
            message = (
                "My ship was hit! How dare you!" 
                if game.bot_player and game.defender == game.player_2 
                else f"{game.defender.member.mention}'s ship was hit!")
        else:
            message = f"{game.attacker.member.mention}, your attack missed!"
        
        game.attack_msg = await ctx.send(message)
    
    async def handle_turn_message_(self, ctx, game: Game):
        """Sends a message indicating whose turn it is."""
        if game.bot_player and game.attacker == game.player_2:
            game.turn_msg = await game.turn_msg.edit(content="It is now my turn!")
        else:
            game.turn_msg = await game.turn_msg.edit(
                content=f"{game.attacker.member.mention}, it is now your turn!")
        
    async def handle_bot_turn_(self, ctx, game: Game):
        """Performs the bot's turn and send appropriate messages."""
        game.attack_msg = await game.attack_msg.edit(content="Thinking.... 🤔")
        await sleep(random.randint(5, 10))
        attack = await game.bot_turn()
        
        if attack:
            game.attack_msg = await game.attack_msg.edit(
                content=f"{game.defender.member.mention}'s ship was hit!")
        else:
            game.attack_msg = await game.attack_msg.edit(content="Oh, shoot, I missed!")
            
        if game.end_turn():
            return await self.end_game_(ctx, game)
        
        await self.handle_turn_message_(ctx, game)


async def setup(bot):
    await bot.add_cog(BattleShip(bot))
