"""
This module implements a log viewer for a Discord bot, designed to display a series of log events 
as interactive embed pages within a Discord channel. It utilizes the `discord.py` library to 
interact with Discord APIs, providing functionality for user navigation through the log.

### Key Features:
- **Embed-Based Navigation**:
    - Display events in paginated embed pages for better readability.
    - Navigate between pages using "Previous" and "Next" buttons.

- **Interactive Buttons**:
    - Intuitive UI with buttons for seamless navigation.
    - Prevent navigation beyond the first or last page.

- **Asynchronous Operations**:
    - Utilize `asyncio` for non-blocking interaction handling.
    - Efficiently update messages with the selected page.

### Classes:
- **`LogView`**:
    Represents a Discord UI View that allows users to navigate through log events.

### Dependencies:
- **`discord`**: For interacting with Discord APIs and sending embeds.
"""


import discord



class LogView(discord.ui.View):
    """Represents a View for displaying the stored log events in Discord.

    Provides interactive buttons for navigating through multiple embed pages in a
    Discord message.
    
    Attributes:
    -----------
        `pages` (list[discord.Embed]): The embed pages containing the stored events.
        `page_num` (int): The current page index.
    """
    def __init__(self, pages: list, *, timeout=180):
        super().__init__(timeout=timeout)
        self.pages = pages
        self.page_num = 0
        
    @discord.ui.button(label="Previous", style=discord.ButtonStyle.blurple)
    async def previous_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button):
        """
        Transitions to the previous embed page, or defers if at the first page.

        Params:
        -------
            `interaction` (Interaction): The interaction that triggered the `button`.
            `button` (Button): The button object.
        """
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
        """
        Transitions to the previous embed page, or defers if at the first page.

        Params:
        -------
            `interaction` (Interaction): The interaction that triggered the `button`.
            `button` (Button): The button object.
        """
        if self.page_num < len(self.pages) - 1:
            self.page_num += 1
            await interaction.response.edit_message(embed=self.pages[self.page_num])
        else:
            interaction.response.defer()
