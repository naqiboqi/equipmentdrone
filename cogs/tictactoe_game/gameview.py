import discord

from .game import Game



class Tile(discord.ui.Button):
    def __init__(self, y: int, x: int, label: str, style: discord.ButtonStyle, row: int):
        super().__init__(label=label, style=style, row=row, custom_id=f"{y}:{x}")
        self.y = y
        self.x = x



class GameView(discord.ui.View):
    def __init__(self, game: Game, timeout=None):
        super().__init__(timeout=timeout)
        self.game = game
        self.board = game.board
        self._create_buttons()
        
    async def mark_button_tile(self, y: int, x: int, symbol: str):
        for child in self.children:
            if isinstance(child, Tile) and child.custom_id == f"{y}:{x}":
                child.label = symbol
                child.disabled = True
                return
        
    async def _select_tile(self, interaction: discord.Interaction):
        if not self.game.is_player_turn(interaction.user):
            return await interaction.response.send_message("It is not your turn!", delete_after=10)
        
        current_player = self.game.current_player
        custom_id = interaction.data["custom_id"]
        symbol = current_player.symbol
        
        y, x = map(int, custom_id.split(":"))
        if not self.game.mark(y, x, symbol):
            return await interaction.response.send_message(
                f"{current_player.member.mention}, that space is filled!", delete_after=10)

        await self.mark_button_tile(y, x, symbol)
        await self.game.next_turn(y, x)

    def _create_buttons(self):
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
                
    async def disable_all_tiles(self):
        for child in self.children:
            child.disabled = True