import discord

from .game import Game



class Tile(discord.ui.Button):
    """Represents a button tile for the players to select where to place their symbol.
    
    The `y` and `x` locations are used to construct a `custom id` 
    for the tile for easy retrieval when clicked.
    
    Attributes:
    -----------
        y : int
            The `y` location of the tile.
        x : int
            The `x` location of the tile.
    """
    def __init__(self, y: int, x: int, label: str, style: discord.ButtonStyle, row: int):
        super().__init__(label=label, style=style, row=row, custom_id=f"{y}:{x}")
        self.y = y
        self.x = x



class GameView(discord.ui.View):
    """A Discord UI View for selecting a tile to place on in Tic-tac-toe.

    This class provides an interactive interface where players can choose which tile on the board to play.
    The selected tile is marked on the board and the respective button is disabled.
    
    Attributes:
    -----------
        game : Game
            The game instance to interact with.
        board : Board
            The board associated with the current game.
    """
    def __init__(self, game: Game, timeout=None):
        super().__init__(timeout=timeout)
        self.game = game
        self.board = game.board
        self._create_buttons()
        
    def _create_buttons(self):
        """Creates the tile buttons for the view."""
        for y in range(self.board.size):
            for x in range(self.board.size):
                tile = Tile(
                    y=y,
                    x=x,
                    label=self.board.grid[y][x],
                    style=discord.ButtonStyle.blurple,
                    row=y)

                tile.callback = self._select_tile
                self.add_item(tile)

    async def _select_tile(self, interaction: discord.Interaction):
        """Callback function for when the player clicks a button tile.
        
        Checks if it is that player's turn, and marks the button tile to proceed
        to the next turn.
        """
        if not self.game.is_player_turn(interaction.user):
            return await interaction.response.send_message("It is not your turn!", delete_after=10)

        current_player = self.game.current_player
        custom_id = interaction.data["custom_id"]
        symbol = current_player.symbol

        y, x = map(int, custom_id.split(":"))
        if not self.game.mark(y, x, symbol):
            return await interaction.response.send_message(
                f"{current_player.member.mention}, that space is filled!", delete_after=10)

        await interaction.response.defer()
        await self.mark_button_tile(y, x, symbol)
        await self.game.next_turn(y, x)

    async def mark_button_tile(self, y: int, x: int, symbol: str):
        """Marks the selected button tile with the player's symbol.
        
        Finds the clicked tile by using the `y` and `x` location to get the tile's ID
        and disables it afterwards.
        
        Params:
        ------
            y : int
                The `y` location of the board.
            x : int
                The `x` location of the board.
            symbol : str
                The player's symbol.
        """
        for child in self.children:
            if isinstance(child, Tile) and child.custom_id == f"{y}:{x}":
                child.label = symbol
                child.disabled = True
                return

    async def disable_all_tiles(self):
        """Disables all tile buttons for the game's embed."""
        for child in self.children:
            child.disabled = True
