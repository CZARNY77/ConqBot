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

    @discord.ui.button(label="Pingnij nie oznaczonych", custom_id="btn-ping-1", style=discord.ButtonStyle.success, row=0)
    async def button_ping_all(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.bot.db.check_role_permissions(interaction.user, interaction.guild_id):
            presence_channels_id = self.bot.db.get_specific_value(interaction.guild_id, "presence_channels_id")
            await self.ping(interaction, presence_channels_id, "unchecked")
        else:
            await interaction.response.send_message(content=f"Nie masz uprawnień!", ephemeral=True)

    @discord.ui.button(label="Pingnij wybrany lineup", custom_id="btn-ping-2", style=discord.ButtonStyle.success, row=0)
    async def button_ping_lineup(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.bot.db.check_role_permissions(interaction.user, interaction.guild_id):
            await interaction.response.send_message(view=LineupSelectPing(self.bot, interaction, self, "unchecked"), ephemeral=True)
        else:
            await interaction.response.send_message(content=f"Nie masz uprawnień!", ephemeral=True)

    @discord.ui.button(label="Pingnij z nwm wszystkich", custom_id="btn-ten-ping-1", style=discord.ButtonStyle.primary, row=1)
    async def button_ping_t_all(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.bot.db.check_role_permissions(interaction.user, interaction.guild_id):
            presence_channels_id = self.bot.db.get_specific_value(interaction.guild_id, "presence_channels_id")
            await self.ping(interaction, presence_channels_id, "tentative")
        else:
            await interaction.response.send_message(content=f"Nie masz uprawnień!", ephemeral=True)

    @discord.ui.button(label="Pingnij z nwm wybrany lineup", custom_id="btn-ten-ping-2", style=discord.ButtonStyle.primary, row=1)
    async def button_ping_t_lineup(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.bot.db.check_role_permissions(interaction.user, interaction.guild_id):
            await interaction.response.send_message(view=LineupSelectPing(self.bot, interaction, self, "tentative"), ephemeral=True)
        else:
            await interaction.response.send_message(content=f"Nie masz uprawnień!", ephemeral=True)

    @discord.ui.button(label="Pingnij na priv wszytskich", custom_id="btn-priv-ping-1", style=discord.ButtonStyle.primary, row=2)
    async def button_ping_priv_all(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.bot.db.check_role_permissions(interaction.user, interaction.guild_id):
            presence_channels_id = self.bot.db.get_specific_value(interaction.guild_id, "presence_channels_id")
            await self.ping(interaction, presence_channels_id, "priv")
        else:
            await interaction.response.send_message(content=f"Nie masz uprawnień!", ephemeral=True)

    @discord.ui.button(label="Pingnij na priv z lineup", custom_id="btn-priv-ping-2", style=discord.ButtonStyle.primary, row=2)
    async def button_ping_priv_lineup(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.bot.db.check_role_permissions(interaction.user, interaction.guild_id):
            await interaction.response.send_message(view=LineupSelectPing(self.bot, interaction, self, "priv"), ephemeral=True)
        else:
            await interaction.response.send_message(content=f"Nie masz uprawnień!", ephemeral=True)

    @discord.ui.button(label="Prześlij obecność wszystkich", custom_id="btn-presence-1", style=discord.ButtonStyle.gray, row=3)
    async def button_presence_all(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.bot.db.check_role_permissions(interaction.user, interaction.guild_id):
            await self.singup(interaction)
        else:
            await interaction.response.send_message(content=f"Nie masz uprawnień!", ephemeral=True)

    settingsEmoji = discord.PartialEmoji(name="Settings", id=1247272714788409354)
    @discord.ui.button(custom_id="btn-config-1", style=discord.ButtonStyle.red, row=4, emoji=settingsEmoji)
    async def button_config(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.bot.db.check_role_permissions(interaction.user, interaction.guild_id):
            try:
                await self.bot.db.bot_configuration(interaction.user, interaction.guild_id)
                self.bot.wait_msg = True
                self.bot.editing_user[interaction.user.display_name] = interaction.user
                await interaction.response.defer()
                await self.bot.wait_for("message", timeout=60, check=lambda m: m.author == interaction.user)
            except asyncio.TimeoutError:
                await interaction.user.send("Przekroczono czasowy limit!")
                self.bot.wait_msg = False
                self.bot.db.del_editing_user(self.bot.editing_user[interaction.user.display_name])
                del self.bot.editing_user[interaction.user.display_name]
        else:
            await interaction.response.send_message(content=f"Nie masz uprawnień!", ephemeral=True)

    @discord.ui.button(label="Dodaj punkt", custom_id="btn-points-1", style=discord.ButtonStyle.success, row=4)
    async def button_add_points(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.bot.db.check_role_permissions(interaction.user, interaction.guild_id):
            await interaction.response.send_modal(FormAddPoints(self.bot))
        else:
            await interaction.response.send_message(content=f"Nie masz uprawnień!", ephemeral=True)

    async def ping(self, interaction, presence_channels_id, type_ping):
        try:
            for channel in presence_channels_id:
                self.bot.pings.channel = interaction.guild.get_channel(int(channel))
                self.bot.pings.msg_author = interaction.user
                await self.bot.pings.get_parameters()
                if type_ping == "unchecked":
                    await self.bot.pings.ping_unchecked()
                elif type_ping == "tentative":
                    await self.bot.pings.ping_tentative()
                elif type_ping == "priv":
                    await self.bot.pings.ping_to_priv()
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
    def __init__(self, bot, interaction, button, type_ping):
        super().__init__(timeout=None)
        self.button = button
        self.type_ping = type_ping
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
    def __init__(self, bot, interaction, button, type_ping):
        super().__init__(bot, interaction, button, type_ping)

    async def select_callback(self, interaction: discord.Interaction):
        selected_channel_id = self.select_menu.values[0]
        channel = [selected_channel_id]
        await self.button.ping(interaction, channel, self.type_ping)

class FormAddPoints(ui.Modal):
    def __init__(self, bot):
        super().__init__(title="Daj punkty")
        self.bot = bot
        self.name = ui.TextInput(label='Nick w grze', placeholder="Rien")
        self.points = ui.TextInput(label='Ilość punktów', placeholder="1")
        self.command = ui.TextInput(label='Komentarz', style=discord.TextStyle.long, required=False)
        self.add_item(self.name)
        self.add_item(self.points)
        self.add_item(self.command)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            self.points = float(str(self.points))
        except:
            await interaction.response.send_message(f'{interaction.user.mention} Podałeś złą wartość punktów!!!', ephemeral=True)
            return
        member = discord.utils.find(lambda m: m.display_name.lower() == str(self.name).lower(), interaction.guild.members)
        if member:
            channel_log_id = self.bot.db.get_specific_value(interaction.guild_id, "general_logs_id")
            channel_log = interaction.guild.get_channel_or_thread(channel_log_id)
            self.bot.db.points(int(self.points), member.id, "activity_points")

            embed = discord.Embed(
            description=f'Gracz: {member.display_name}, DC: {member.mention}', color=discord.Color.green())
            embed.add_field(name="Punkty:", value=self.points, inline=False)
            embed.add_field(name="Komentarz:", value=self.command, inline=False)
            image_url = member.avatar
            embed.set_thumbnail(url=image_url)
            embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.avatar)
            await channel_log.send(embed=embed)
            await interaction.response.send_message(f'Dodano punkty', ephemeral=True)
        else:
            await interaction.response.send_message(f'{interaction.user.mention} Nie znaleziono takiego gracza!!!', ephemeral=True)
        
