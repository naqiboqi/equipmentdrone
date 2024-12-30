import discord

class LogView(discord.ui.View):
    def __init__(self, pages: list, *, timeout=180):
        super().__init__(timeout=timeout)
        self.pages = pages
        self.page_num = 0
        
    @discord.ui.button(label="Previous", style=discord.ButtonStyle.blurple)
    async def previous_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button):

        if self.page_num > 0:
            self.page_num -= 1
            await interaction.response.edit_message(embed=self.pages[self.page_num])
        else:
            interaction.response.defer()

    @discord.ui.button(label="Next", style=discord.ButtonStyle.blurple)
    async def next_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button):

        if self.page_num < len(self.pages) - 1:
            self.page_num += 1
            await interaction.response.edit_message(embed=self.pages[self.page_num])
        else:
            interaction.response.defer()