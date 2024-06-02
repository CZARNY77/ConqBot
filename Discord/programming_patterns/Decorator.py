import discord
from discord.ext import commands
from discord.ui import Button, View

class BasicButtonView(View):
    def __init__(self):
        super().__init__()
        self.add_item(Button(label="Kliknij mnie", style=discord.ButtonStyle.primary))

    @discord.ui.button(label="Kliknij mnie", style=discord.ButtonStyle.primary)
    async def basic_button(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_message("Przycisk został kliknięty!", ephemeral=True)

class ViewDecorator(View):
    def __init__(self, view: View):
        super().__init__()
        self.view = view

    def add_item(self, item):
        self.view.add_item(item)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return await self.view.interaction_check(interaction)

class ClickCounterDecorator(ViewDecorator):
    def __init__(self, view: View):
        super().__init__(view)
        self.click_count = 0

    async def on_click(self, interaction: discord.Interaction):
        self.click_count += 1
        await interaction.response.send_message(f"Przycisk został kliknięty {self.click_count} razy.", ephemeral=True)

    @discord.ui.button(label="Kliknij mnie", style=discord.ButtonStyle.primary)
    async def click_counter_button(self, interaction: discord.Interaction, button: Button):
        await self.on_click(interaction)

class StyleChangerDecorator(ViewDecorator):
    def __init__(self, view: View):
        super().__init__(view)

    @discord.ui.button(label="Kliknij mnie", style=discord.ButtonStyle.success)
    async def styled_button(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_message("Przycisk został kliknięty i ma inny styl!", ephemeral=True)

class DecoratedView(ClickCounterDecorator, StyleChangerDecorator):
    def __init__(self, bot):
        basic_view = BasicButtonView()
        ClickCounterDecorator.__init__(self, basic_view)
        StyleChangerDecorator.__init__(self, self.view)

        @bot.command()
        async def show_view(ctx):
            view = self
            await ctx.send("Oto dekorowany przycisk!", view=view)