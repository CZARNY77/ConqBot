import discord
from discord import ui
import json
import asyncio

class ViewMenu(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot
        with open('Discord/Keys/config.json', 'r') as file:
            self.url = json.load(file)["kop_singup"]

        @bot.tree.command(name="menu")
        async def menu(ctx: discord.Interaction):
            if self.bot.db.check_role_permissions(ctx.user, ctx.guild_id):
                await ctx.response.send_message(view=self)
            else:
                await ctx.response.send_message(content=f"Nie masz uprawnień!", ephemeral=True)

    @discord.ui.button(label="Pingnij wszyskich", custom_id="btn-ping-1", style=discord.ButtonStyle.primary, row=0)
    async def button_ping_all(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.bot.db.check_role_permissions(interaction.user, interaction.guild_id):
            presence_channels_id = self.bot.db.get_specific_value(interaction.guild_id, "presence_channels_id")
            await self.ping(interaction, presence_channels_id)
        else:
            await interaction.response.send_message(content=f"Nie masz uprawnień!", ephemeral=True)

    @discord.ui.button(label="Pingnij wybrany lineup", custom_id="btn-ping-2", style=discord.ButtonStyle.primary, row=0)
    async def button_ping_lineup(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.bot.db.check_role_permissions(interaction.user, interaction.guild_id):
            await interaction.response.send_message(view=LineupSelectPing(self.bot, interaction, self), ephemeral=True)
        else:
            await interaction.response.send_message(content=f"Nie masz uprawnień!", ephemeral=True)

    @discord.ui.button(label="Prześlij obecność wszystkich", custom_id="btn-presence-1", style=discord.ButtonStyle.primary, row=1)
    async def button_presence_all(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.bot.db.check_role_permissions(interaction.user, interaction.guild_id):
            await self.singup(interaction)
        else:
            await interaction.response.send_message(content=f"Nie masz uprawnień!", ephemeral=True)

    @discord.ui.button(label="Prześlij obecność wybranego lineup", custom_id="btn-presence-2", style=discord.ButtonStyle.primary, row=1)
    async def button_presence_lineup(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.bot.db.check_role_permissions(interaction.user, interaction.guild_id):
            await interaction.response.send_message(view=LineupSelectPresence(self.bot, interaction, self), ephemeral=True)
        else:
            await interaction.response.send_message(content=f"Nie masz uprawnień!", ephemeral=True)

    @discord.ui.button(label="Konfiguruj serwer", custom_id="btn-config-1", style=discord.ButtonStyle.success, row=2)
    async def button_config(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.bot.db.check_role_permissions(interaction.user, interaction.guild_id):
            try:
                await self.bot.db.bot_configuration(interaction.user, interaction.guild_id)
                self.bot.wait_msg = True
                self.bot.editing_user[interaction.user.display_name] = interaction.user
                await self.bot.wait_for("message", timeout=60, check=lambda m: m.author == interaction.user)
            except asyncio.TimeoutError:
                await interaction.user.send("Przekroczono czasowy limit!")
                self.bot.wait_msg = False
                self.del_editing_user(self.bot.editing_user[self.ctx.author.display_name])
                del self.bot.editing_user[interaction.user.display_name]
        else:
            await interaction.response.send_message(content=f"Nie masz uprawnień!", ephemeral=True)

    async def ping(self, interaction, presence_channels_id):
        try:
            for channel in presence_channels_id:
                self.bot.pings.channel = interaction.guild.get_channel(int(channel))
                self.bot.pings.msg_author = interaction.user
                await self.bot.pings.get_parameters()
                await self.bot.pings.ping_unchecked()
            await interaction.response.send_message(content=f"Pingowanie zakończone.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(content=f"Coś poszło nie tak!\nerror: {e}", ephemeral=True)

    async def singup(self, interaction):
        try:
            await self.bot.presenceTW.get_apollo_list(interaction.guild_id)
            await interaction.response.send_message(content=f"Wysyłanie zakończone.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(content=f"Coś poszło nie tak!\nerror: {e}", ephemeral=True)

class LineupSelect(discord.ui.View):
    def __init__(self, bot, interaction, button):
        super().__init__(timeout=None)
        self.button = button
        presence_channels_id = bot.db.get_specific_value(interaction.guild_id, "presence_channels_id")
        select_option = []
        for channel_id in presence_channels_id:
            channel = interaction.guild.get_channel(int(channel_id))
            select_option.append(discord.SelectOption(label=channel.name, value=channel.id))
        self.select_menu = ui.Select(placeholder="wybierz lineup", options=select_option)
        self.select_menu.callback = self.select_callback
        self.add_item(self.select_menu)

    async def select_callback(self, interaction: discord.Interaction):
        pass

class LineupSelectPing(LineupSelect):
    def __init__(self, bot, interaction, button):
        super().__init__(bot, interaction, button)

    async def select_callback(self, interaction: discord.Interaction):
        selected_channel_id = self.select_menu.values[0]
        channel = [selected_channel_id]
        await self.button.ping(interaction, channel)

class LineupSelectPresence(LineupSelect):
    def __init__(self, bot, interaction, button):
        super().__init__(bot, interaction)

    async def select_callback(self, interaction: discord.Interaction):
        selected_channel_id = self.select_menu.values[0]
        channel = interaction.guild.get_channel(int(selected_channel_id))
        if channel:
            await interaction.response.send_message(f"Wybrano kanał: {channel.name}", ephemeral=True)
        else:
            await interaction.response.send_message("Nie można znaleźć wybranego kanału.", ephemeral=True)