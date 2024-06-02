from abc import ABC, abstractmethod
import discord
from discord.ext import commands
from discord.ui import View

class Bridge(): # bęziemy nadawać i usuwać role
    def __init__(self, bot) -> None:
        @bot.command()
        async def btn_add_role(ctx):
            # Tworzymy przycisk typu nadaj z akcją 
            action = ActionAddRole()
            view = ButtonTypeAdd(action)
            await ctx.send("Weź role wskazówki:", view=view)

        @bot.command()
        async def btn_remove_role(ctx):
            # Tworzymy przycisk typu zabierz z akcją 
            action = ActionRemoveRole()
            view = ButtonTypeRemove(action)
            await ctx.send("Zabierz role wskazówki:", view=view)

class ButtonAction(ABC):
    @abstractmethod
    async def execute(self, interaction: discord.Interaction, role):
        pass

class ActionAddRole(ButtonAction):
    async def execute(self, interaction: discord.Interaction, role):
        await interaction.user.add_roles(role)
        await interaction.response.send_message("Dodano role.", ephemeral=True)

class ActionRemoveRole(ButtonAction):
    async def execute(self, interaction: discord.Interaction, role):
        await interaction.user.remove_roles(role)
        await interaction.response.send_message("Usunięto role.", ephemeral=True)

class ButtonAbstraction(View):
    def __init__(self, action: ButtonAction):
        super().__init__()
        self.action = action
    
    @discord.ui.button(label="Kliknij mnie", style=discord.ButtonStyle.primary)
    async def button_clicked(self, interaction: discord.Interaction, button: discord.ui.Button,):
        role_id = 1245509077367390342
        role = interaction.client.get_guild(interaction.guild_id).get_role(role_id)
        await self.action.execute(interaction, role)

class ButtonTypeAdd(ButtonAbstraction):
    def __init__(self, action: ButtonAction):
        super().__init__(action)
        self.children[0].label = "Weź"
        self.children[0].style = discord.ButtonStyle.success

class ButtonTypeRemove(ButtonAbstraction):
    def __init__(self, action: ButtonAction):
        super().__init__(action)
        self.children[0].label = "Zabierz"
        self.children[0].style = discord.ButtonStyle.danger
