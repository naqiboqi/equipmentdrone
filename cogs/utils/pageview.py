"""
This module implements a page for a Discord bot, designed to display a series of items 
as interactive embed pages within a Discord channel. It utilizes the `discord.py` library to 
interact with Discord APIs, providing functionality for user navigation

### Key Features:
- **Embed-Based Navigation**:
    - Display items in paginated embed pages for better readability.
    - Navigate between pages using "Previous" and "Next" buttons.

- **Interactive Buttons**:
    - Intuitive UI with buttons for seamless navigation.

### Classes:
- **`PageView`**:
    Represents a Discord UI View that allows users to navigate through items.

### Dependencies:
- **`discord`**: For interacting with Discord APIs and sending embeds.
"""



import discord



class PageView(discord.ui.View):
    """Represents a View for displaying pages of items in Discord.

    Provides interactive buttons for navigating through multiple embed pages in a
    Discord message.
    
    Attributes:
    -----------
        `pages` (list[discord.Embed]): The embed pages containing the stored items.
        `page_num` (int): The current page index.
    """
    def __init__(self, title: str, items: list[str], max_items_per_page: int=20, *, timeout=180):
        super().__init__(timeout=timeout)
        self.title = title
        self.items = items
        self.max_items_per_page = max_items_per_page
        
        self.page_num = 0
        self.pages = self._generate_pages()
        
    def _generate_pages(self):
        pages_content = [
            self.items[i:i + self.max_items_per_page]
            for i in range(0, len(self.items), self.max_items_per_page)]
        
        if not pages_content:
            return [discord.Embed(
                title=self.title, 
                description="No items to display",
                color=discord.Color.red())]

        pages: list[discord.Embed] = []
        for page_content in pages_content:
            description = "\n".join(str(item) for item in page_content)
            page = discord.Embed(
                title=self.title, 
                description=description, 
                color=discord.Color.red())

            page.set_footer(text=f"Page {len(pages) + 1} out of {len(pages_content)}")
            pages.append(page)

        return pages
    
    def _update_buttons(self):
        disable_prev = self.page_num == 0
        self._previous_button.disabled = disable_prev
        
        disable_next = self.page_num == (len(self.pages) - 1)
        self._next_button.disabled = disable_next
        
    @discord.ui.button(label="Previous", style=discord.ButtonStyle.blurple)
    async def _previous_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button):
        """
        Transitions to the previous embed page, if there is one.

        Params:
        -------
            `interaction` (Interaction): The interaction that triggered the `button`.
            `button` (Button): The button object.
        """
        if self.page_num > 0:
            self.page_num -= 1
            await interaction.response.edit_message(embed=self.pages[self.page_num])
        else:
            await interaction.response.defer()

        self._update_buttons()

    @discord.ui.button(label="Next", style=discord.ButtonStyle.blurple)
    async def _next_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button):
        """
        Transitions to the next embed page, if there is one.

        Params:
        -------
            `interaction` (Interaction): The interaction that triggered the `button`.
            `button` (Button): The button object.
        """
        if self.page_num < len(self.pages) - 1:
            self.page_num += 1
            await interaction.response.edit_message(embed=self.pages[self.page_num])
        else:
            await interaction.response.defer()

        self._update_buttons()
