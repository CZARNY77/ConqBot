import discord
import json
import asyncio
from discord import ui
from Discord.recruitment import Recruitment

class ViewMenuEng(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot
        with open('Discord/Keys/config.json', 'r') as file:
            self.url = json.load(file)["kop_singup"]

        @bot.tree.command(name="menu_eng")
        async def menu(ctx: discord.Interaction):
            if self.bot.db.check_role_permissions(ctx.user, ctx.guild_id):
                await ctx.response.send_message(view=self)
            else:
                await ctx.response.send_message(content=f"You don't have the authority!", ephemeral=True)

    presenceAllEmoji = discord.PartialEmoji(name="przeslij_obecnosc", id=1252368947186110525)
    @discord.ui.button(label="Send the presence", custom_id="btn-presence-eng-1", style=discord.ButtonStyle.gray, row=1, emoji=presenceAllEmoji)
    async def button_presence_all(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.bot.db.check_role_permissions(interaction.user, interaction.guild_id) or self.bot.db.check_TW_role_permissions(interaction.user, interaction.guild_id):
            await self.singup(interaction)
        else:
            await interaction.response.send_message(content=f"You don't have the authority!", ephemeral=True)
            
    @discord.ui.button(label="Quick add", custom_id="button-eng-1", style=discord.ButtonStyle.success, row=2, emoji="🏍")
    async def button_add_quickly(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(FormAddQuickly(interaction))

    @discord.ui.button(label="Delete Player", custom_id="button-eng-2", style=discord.ButtonStyle.danger , row=2, emoji="💀")
    async def button_del_player(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.client.db.check_role_permissions(interaction.user, interaction.guild_id):# or interaction.user.id == 373563828513931266:
            await interaction.response.send_modal(FormDelPlayer(interaction))
            return
        else:
            await interaction.response.send_message('Nie masz uprawnień!!', ephemeral=True)
            return 
           
    settingsEmoji = discord.PartialEmoji(name="opcje", id=1252369978137772274)
    @discord.ui.button(custom_id="btn-config-eng-1", style=discord.ButtonStyle.red, row=3, emoji=settingsEmoji)
    async def button_config(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.bot.db.check_role_permissions(interaction.user, interaction.guild_id):
            try:
                await self.bot.db.bot_configuration(interaction.user, interaction.guild_id)
                self.bot.wait_msg = True
                self.bot.editing_user[interaction.user.display_name] = interaction.user
                await interaction.response.defer()
                await self.bot.wait_for("message", timeout=60, check=lambda m: m.author == interaction.user)
            except asyncio.TimeoutError:
                await interaction.user.send("The time limit has been exceeded!")
                self.bot.wait_msg = False
                self.bot.db.del_editing_user(self.bot.editing_user[interaction.user.display_name])
                del self.bot.editing_user[interaction.user.display_name]
        else:
            await interaction.response.send_message(content=f"You don't have the authority!", ephemeral=True)
           
    async def singup(self, interaction):
        try:
            await interaction.response.send_message(content=f"Wysyłanie...", ephemeral=True)
            await self.bot.presenceTW.get_list()
            response = await interaction.original_response()
            await response.edit(content="Sending completed.")
        except Exception as e:
            await interaction.response.send_message(content=f"Something has gone wrong!\nerror: {e}", ephemeral=True)

            
class FormAddPlayer(ui.Modal):
    def __init__(self, title, interaction, choice=None):
        super().__init__(title=title)
        self.name = ui.TextInput(label='Name', placeholder="Rien")
        self.comment = ui.TextInput(label='commentary (optional)', style=discord.TextStyle.long, required=False)
        self.add_item(self.name)
        self.interaction = interaction
        self.choice = choice
        self.bot = interaction.client
        self.recru_channel_log_id = self.bot.db.get_specific_value(interaction.guild_id, "recruiter_logs_id")

    async def on_submit(self, interaction: discord.Interaction):
        pass

class FormDelPlayer(FormAddPlayer):
    def __init__(self, interaction):
        super().__init__(title='Player removal', interaction=interaction)
        self.add_item(self.comment)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message(f'The form has been sent. On {interaction.guild.get_channel_or_thread(self.recru_channel_log_id).mention} see progress.', ephemeral=True)
        recruitment = Recruitment(self.interaction, self.recru_channel_log_id)
        await recruitment.del_player_to_whitelist(self.name, self.comment)
        del recruitment

class FormAddQuickly(FormAddPlayer):
    def __init__(self, interaction):
        super().__init__(title='Adding a player', interaction=interaction)
        self.add_item(self.comment)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message(f'The form has been sent. On {interaction.guild.get_channel_or_thread(self.recru_channel_log_id).mention} see progress.', ephemeral=True)
        recruitment = Recruitment(self.interaction, self.recru_channel_log_id)
        await recruitment.add_quickly(self.name, comment=self.comment)
        del recruitment
      