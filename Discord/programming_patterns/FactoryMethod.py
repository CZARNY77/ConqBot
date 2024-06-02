from abc import ABC, abstractmethod
import discord
from discord.ext import commands
from discord.ui import Button, View


class Factory(): # po przyciśnięciu będzie pojawiał nam się embed
    def __init__(self, bot):
        @bot.command()
        async def show_primary_button(ctx):
            factory = PrimaryButtonFactory()
            view = ButtonView(factory)
            await ctx.send("Oto przycisk primary:", view=view)

        @bot.command()
        async def show_success_button(ctx):
            factory = SuccessButtonFactory()
            view = ButtonView(factory)
            await ctx.send("Oto przycisk success:", view=view)


class ButtonFactory(ABC):
    @abstractmethod
    def create_button(self) -> Button:
        pass

class PrimaryButton(Button):
    def __init__(self):
        super().__init__(label="Primary Button", style=discord.ButtonStyle.primary)

class SuccessButton(Button):
    def __init__(self):
        super().__init__(label="Success Button", style=discord.ButtonStyle.success)

class PrimaryButtonFactory(ButtonFactory):
    def create_button(self) -> Button:
        return PrimaryButton()

class SuccessButtonFactory(ButtonFactory):
    def create_button(self) -> Button:
        return SuccessButton()

class ButtonView(View):
    def __init__(self, button_factory: ButtonFactory):
        super().__init__()
        self.add_item(button_factory.create_button())