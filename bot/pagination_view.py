import math

import discord

from bot.embed_creation import create_leaderboard_embed


class PaginationView(discord.ui.View):

    def __init__(
            self,
            leaderboard_list: list[list[str, int, int, int, int]],
            platform: str,
            author: discord.Member,
            sep: int = 10,
            current_page: int = 1,
    ):
        super().__init__(timeout=None)
        self.leaderboard_list: list[list[str, int, int, int, int]] = leaderboard_list
        self.platform: str = platform
        self.author: discord.Member = author
        self.sep: int = sep
        self.current_page: int = current_page
        self.message = None

    async def respond(self, ctx):
        await ctx.defer()
        self.update_buttons()
        self.message = await ctx.respond(
            embed=create_leaderboard_embed(self.get_current_page_data(), self.platform, self.author),
            view=self
        )

    async def update_message(self, leaderboard_list: list[list[str, int, int, int, int]]):
        self.update_buttons()
        await self.message.edit(
            embed=create_leaderboard_embed(leaderboard_list, self.platform, self.author),
            view=self
        )

    def update_buttons(self):
        if self.current_page == 1:
            self.first_page_button.disabled = True
            self.prev_button.disabled = True
            self.first_page_button.style = discord.ButtonStyle.gray
            self.prev_button.style = discord.ButtonStyle.gray
        else:
            self.first_page_button.disabled = False
            self.prev_button.disabled = False
            self.first_page_button.style = discord.ButtonStyle.green
            self.prev_button.style = discord.ButtonStyle.primary

        if self.current_page == int(len(self.leaderboard_list) / self.sep) + 1:
            self.next_button.disabled = True
            self.last_page_button.disabled = True
            self.last_page_button.style = discord.ButtonStyle.gray
            self.next_button.style = discord.ButtonStyle.gray
        else:
            self.next_button.disabled = False
            self.last_page_button.disabled = False
            self.last_page_button.style = discord.ButtonStyle.green
            self.next_button.style = discord.ButtonStyle.primary

    def get_current_page_data(self):
        from_item = (self.current_page - 1) * self.sep
        until_item = from_item + self.sep
        return self.leaderboard_list[from_item:until_item]

    @discord.ui.button(label="|<", style=discord.ButtonStyle.green)
    async def first_page_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.current_page = 1
        await interaction.response.defer(ephemeral=True)
        await self.update_message(self.get_current_page_data())

    @discord.ui.button(label="<", style=discord.ButtonStyle.primary)
    async def prev_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.current_page -= 1
        await interaction.response.defer(ephemeral=True)
        await self.update_message(self.get_current_page_data())

    @discord.ui.button(label=">", style=discord.ButtonStyle.primary)
    async def next_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.current_page += 1
        await interaction.response.defer(ephemeral=True)
        await self.update_message(self.get_current_page_data())

    @discord.ui.button(label=">|", style=discord.ButtonStyle.green)
    async def last_page_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.current_page = math.ceil(len(self.leaderboard_list) / self.sep)
        await interaction.response.defer(ephemeral=True)
        await self.update_message(self.get_current_page_data())
