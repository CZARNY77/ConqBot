import discord
from discord import ui
import json
import asyncio
from functools import partial

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

    pingAllEmoji = discord.PartialEmoji(name="pingnij_nieoznaczonych", id=1252369003771334739)
    @discord.ui.button(label="Pingnij nie oznaczonych", custom_id="btn-ping-1", style=discord.ButtonStyle.success, row=0, emoji=pingAllEmoji)
    async def button_ping_all(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.bot.db.check_role_permissions(interaction.user, interaction.guild_id):
            presence_channels_id = self.bot.db.get_specific_value(interaction.guild_id, "presence_channels_id")
            await self.ping(interaction, presence_channels_id, "unchecked")
        else:
            await interaction.response.send_message(content=f"Nie masz uprawnień!", ephemeral=True)

    pingLineupEmoji = discord.PartialEmoji(name="ping_wybrany_lineup", id=1252369036529106956)
    @discord.ui.button(label="Pingnij wybrany lineup", custom_id="btn-ping-2", style=discord.ButtonStyle.success, row=0, emoji=pingLineupEmoji)
    async def button_ping_lineup(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.bot.db.check_role_permissions(interaction.user, interaction.guild_id) or self.bot.db.check_TW_role_permissions(interaction.user, interaction.guild_id):
            await interaction.response.send_message(view=LineupSelectPing(self.bot, interaction, self, "unchecked"), ephemeral=True)
        else:
            await interaction.response.send_message(content=f"Nie masz uprawnień!", ephemeral=True)

    pingTentativeAllEmoji = discord.PartialEmoji(name="pingnij_nwm", id=1252369306046435348)
    @discord.ui.button(label="Pingnij z nwm wszystkich", custom_id="btn-ten-ping-1", style=discord.ButtonStyle.primary, row=1, emoji=pingTentativeAllEmoji)
    async def button_ping_t_all(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.bot.db.check_role_permissions(interaction.user, interaction.guild_id):
            presence_channels_id = self.bot.db.get_specific_value(interaction.guild_id, "presence_channels_id")
            await self.ping(interaction, presence_channels_id, "tentative")
        else:
            await interaction.response.send_message(content=f"Nie masz uprawnień!", ephemeral=True)

    pingTentativeLineupEmoji = discord.PartialEmoji(name="trabka_lin", id=1252369329316692129)
    @discord.ui.button(label="Pingnij z nwm wybrany lineup", custom_id="btn-ten-ping-2", style=discord.ButtonStyle.primary, row=1, emoji=pingTentativeLineupEmoji)
    async def button_ping_t_lineup(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.bot.db.check_role_permissions(interaction.user, interaction.guild_id) or self.bot.db.check_TW_role_permissions(interaction.user, interaction.guild_id):
            await interaction.response.send_message(view=LineupSelectPing(self.bot, interaction, self, "tentative"), ephemeral=True)
        else:
            await interaction.response.send_message(content=f"Nie masz uprawnień!", ephemeral=True)

    pingPrivAllEmoji = discord.PartialEmoji(name="ping_lineup_prv", id=1252369112949198868)
    @discord.ui.button(label="Pingnij na priv wszytskich", custom_id="btn-priv-ping-1", style=discord.ButtonStyle.primary, row=2, emoji=pingPrivAllEmoji)
    async def button_ping_priv_all(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.bot.db.check_role_permissions(interaction.user, interaction.guild_id):
            presence_channels_id = self.bot.db.get_specific_value(interaction.guild_id, "presence_channels_id")
            await self.ping(interaction, presence_channels_id, "priv")
        else:
            await interaction.response.send_message(content=f"Nie masz uprawnień!", ephemeral=True)

    pingPrivLineupEmoji = discord.PartialEmoji(name="pingnij_na_priv_wybrany_lineup", id=1252369124416295025)
    @discord.ui.button(label="Pingnij na priv z lineup", custom_id="btn-priv-ping-2", style=discord.ButtonStyle.primary, row=2, emoji=pingPrivLineupEmoji)
    async def button_ping_priv_lineup(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.bot.db.check_role_permissions(interaction.user, interaction.guild_id) or self.bot.db.check_TW_role_permissions(interaction.user, interaction.guild_id):
            await interaction.response.send_message(view=LineupSelectPing(self.bot, interaction, self, "priv"), ephemeral=True)
        else:
            await interaction.response.send_message(content=f"Nie masz uprawnień!", ephemeral=True)

    presenceAllEmoji = discord.PartialEmoji(name="przeslij_obecnosc", id=1252368947186110525)
    @discord.ui.button(label="Prześlij obecność wszystkich", custom_id="btn-presence-1", style=discord.ButtonStyle.gray, row=3, emoji=presenceAllEmoji)
    async def button_presence_all(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.bot.db.check_role_permissions(interaction.user, interaction.guild_id) or self.bot.db.check_TW_role_permissions(interaction.user, interaction.guild_id):
            await self.singup(interaction)
        else:
            await interaction.response.send_message(content=f"Nie masz uprawnień!", ephemeral=True)

    checkingSurveysEmoji = discord.PartialEmoji(name="przypomnij_o_ankietach", id=1252368968208089158)
    @discord.ui.button(label="Przypomnij o ankietach", custom_id="btn-presence-2", style=discord.ButtonStyle.gray, row=3, emoji=checkingSurveysEmoji)
    async def button_checking_surveys(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.bot.db.check_role_permissions(interaction.user, interaction.guild_id):
            await self.survey(interaction)
        else:
            await interaction.response.send_message(content=f"Nie masz uprawnień!", ephemeral=True)
            
    settingsEmoji = discord.PartialEmoji(name="opcje", id=1252369978137772274)
    @discord.ui.button(custom_id="btn-config-1", style=discord.ButtonStyle.red, row=4, emoji=settingsEmoji)
    async def button_config(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.bot.db.check_role_permissions(interaction.user, interaction.guild_id):
            try:
                self.bot.db.conf_field = self.bot.db.conf_field_pl
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
            
    addPointsEmoji = discord.PartialEmoji(name="dodaj_punkt", id=1252368923526172724)
    @discord.ui.button(label="Dodaj punkt", custom_id="btn-points-1", style=discord.ButtonStyle.success, row=4, emoji=addPointsEmoji)
    async def button_add_points(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.bot.db.check_role_permissions(interaction.user, interaction.guild_id):
            await interaction.response.send_modal(FormAddPoints(self.bot))
        else:
            await interaction.response.send_message(content=f"Nie masz uprawnień!", ephemeral=True)

    async def ping(self, interaction, presence_channels_id, type_ping):
        try:
            await interaction.response.send_message(content=f"Wysyłanie...", ephemeral=True)
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
            response = await interaction.original_response()
            await response.edit(content=f"Pingowanie zakończone.")
        except Exception as e:
            await interaction.response.send_message(content=f"Coś poszło nie tak!\nerror: {e}", ephemeral=True)

    async def singup(self, interaction):
        try:
            await interaction.response.send_message(content=f"Wysyłanie...", ephemeral=True)
            await self.bot.presenceTW.get_list()
            response = await interaction.original_response()
            await response.edit(content="Wysyłanie zakończone.")
        except Exception as e:
            await interaction.response.send_message(content=f"Coś poszło nie tak!\nerror: {e}", ephemeral=True)

    async def survey(self, interaction):
        try:
            results = self.bot.db.get_specific_value(interaction.guild_id, "basic_roles")
            await interaction.response.send_message(content=f"Sprawdzanie rozpoczęte.", ephemeral=True)
            await self.bot.presenceTW.checking_surveys(interaction.guild, results[0], interaction.user)
        except Exception as e:
            await interaction.response.send_message(content=f"Coś poszło nie tak!\nerror: {e}", ephemeral=True)

            
class LineupSelect(discord.ui.View):
    def __init__(self, bot, interaction, button):
        super().__init__(timeout=None)
        self.button = button
        presence_channels_id = bot.db.get_specific_value(interaction.guild_id, "presence_channels_id")
        select_option = []
        if presence_channels_id:
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
        super().__init__(bot, interaction, button)
        self.type_ping = type_ping

    async def select_callback(self, interaction: discord.Interaction):
        selected_channel_id = self.select_menu.values[0]
        channel = [selected_channel_id]
        await self.button.ping(interaction, channel, self.type_ping)

class LineupSelectAbsent(LineupSelect):
    def __init__(self, bot, interaction, button):
        super().__init__(bot, interaction, button)

    async def select_callback(self, interaction: discord.Interaction):
        selected_channel_id = self.select_menu.values[0]
        channel = interaction.guild.get_channel(int(selected_channel_id))
        await self.button.check_absentees(interaction, channel) 
        
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
        

class ViewMenu2(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

        @bot.tree.command(name="menu_2")
        async def menu(ctx: discord.Interaction):
            if self.bot.db.check_role_permissions(ctx.user, ctx.guild_id):
                await ctx.response.send_message(view=self)
            else:
                await ctx.response.send_message(content=f"Nie masz uprawnień!", ephemeral=True)

    @discord.ui.button(label="Sprawdz nieobecnych", custom_id="btn-absentees-1", style=discord.ButtonStyle.success, row=0)
    async def button_check_absentees(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.bot.db.check_role_permissions(interaction.user, interaction.guild_id) or self.bot.db.check_TW_role_permissions(interaction.user, interaction.guild_id):
            try:
                await interaction.response.send_message(view=LineupSelectAbsent(self.bot, interaction, self), ephemeral=True)
            except:
                print("Error: Sprawdz nieobecnych, pewnie nie ustawiono lineup'ów")
        else:
            await interaction.response.send_message(content=f"Nie masz uprawnień!", ephemeral=True)

    async def check_absentees(self, interaction: discord.Interaction, channel):
        if self.bot.db.check_role_permissions(interaction.user, interaction.guild_id) or self.bot.db.check_TW_role_permissions(interaction.user, interaction.guild_id):
            if channel == None:
                await interaction.response.send_message(content="Nie ma takiego kanału", ephemeral=True)
                return
            await interaction.response.send_message(content="Pracuje...", ephemeral=True)
            player_list = await self.get_apollo_list(channel)
            response = await interaction.original_response()
            await response.edit(content=f"{player_list}")
        else:
            await interaction.response.send_message(content=f"Nie masz uprawnień!", ephemeral=True)        
            
    async def get_apollo_list(self, channel):
        all_players = self.get_players(channel)
        new_players = []
        async for msg in channel.history(limit=30):
            if msg.author.name == 'Apollo' and msg.embeds:
                fields = msg.embeds[0].fields
                for field in fields:
                    if "Accepted" in field.name:
                        players = field.value[4:].splitlines()
                        for player in players:
                            player = player.replace('\\', '')
                            if player not in all_players:
                                new_players.append(player)
                        break
                break
        content = f"{channel.name}: {len(new_players)}\n"
        for player in new_players:
            content += player + "\n"
        return content
    
    def get_players(self, channel):
        roleTW_id = self.bot.db.get_specific_value(channel.guild.id, "roles")
        if not roleTW_id:
            return
        roleTW_id = int(roleTW_id[0])
        guild = channel.guild
        players_list = []
        for channel in guild.voice_channels:
            if channel.members != []:
                for member in channel.members:
                    for role in member.roles:
                        if role.id == roleTW_id:
                            players_list.append(member.display_name)
        return players_list    
        