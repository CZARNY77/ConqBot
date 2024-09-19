import discord
import json
import asyncio
from discord import ui
from Discord.recruitment import Recruitment
from Discord.conqAppsRequests import conqSite

class ViewMenuEng(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot
        with open('/home/container/Discord/Keys/config.json', 'r') as file:
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
            await interaction.response.send_message("You don't have the authority!", ephemeral=True)
            return 
           
    @discord.ui.button(label="Add All", custom_id="button-eng-3", style=discord.ButtonStyle.primary, row=2, emoji="🗃")
    async def button_add_all(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.client.db.check_role_permissions(interaction.user, interaction.guild_id):
            await self.add_all(interaction)
        else:
            await interaction.response.send_message("You don't have the authority!", ephemeral=True)

    @discord.ui.button(label="Verification", custom_id="button-config-eng-2", style=discord.ButtonStyle.primary , row=3, emoji="✅")
    async def button_verification(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.client.db.check_role_permissions(interaction.user, interaction.guild_id):
            await interaction.response.send_message(content=f"Checking...", ephemeral=True)
            await self.server_verification(interaction)
        else:
            await interaction.response.send_message("You don't have the authority!", ephemeral=True)
           
    async def singup(self, interaction):
        try:
            await interaction.response.send_message(content=f"Sending...", ephemeral=True)
            await self.bot.presenceTW.get_list(interaction.guild)
            response = await interaction.original_response()
            await response.edit(content="Sending completed.")
        except Exception as e:
            await interaction.response.send_message(content=f"Something has gone wrong!\nerror: {e}", ephemeral=True)

    async def add_all(self, interaction):
        await interaction.response.send_message(content=f"Adding... 0 Members", ephemeral=True)
        response = await interaction.original_response()
        guild = interaction.guild
        conq_site = conqSite()
        data_config = conq_site.config(interaction.guild_id)
        member_role_id = int(data_config["member"]["id"])
        member_role = guild.get_role(member_role_id)
        if not member_role:
            await response.edit(content=f"Error: wrong member role id!!!")
            return
        data_whitelist = conq_site.whitelist()
        guild_members = guild.members
        count_members = 0
        found_players = ""
        house_name = data_config["house"]["name"]
        for member in guild_members:
            if member_role in member.roles:
                for row in data_whitelist["whitelist"]:
                    if "idDiscord" in row:
                        if str(member.id) == row["idDiscord"]:
                            found_player = True
                            found_players += f"{member.mention} "
                            break 
                if not found_player:
                    conq_site.post_whitelist(member.id, house_name)
                    recru = Recruitment(bot=self.bot, member_guild=guild)
                    await recru.add_player_to_survey(member)
                    count_members += 1
                    if found_players != "":
                        found_players = f"\nThese members have been added before: {found_players}"
                    await response.edit(content=f"Adding... {count_members} Members {found_players}")

        await response.edit(content=f"Addition completed {count_members}")

    async def server_verification(self, interaction):
        response = await interaction.original_response()
        conq_site = conqSite()
        data = conq_site.config(interaction.guild_id)
        guild_id = int(data["house"]["id"])
        member_role_id = int(data["member"]["id"])
        logs_channel_id = int(data["logs"]["logs"])
        attendance_channel_id = int(data["logs"]["attendance"])
        tw_server_id = int(data["tw"]["server"])
        tw_role_id = int(data["tw"]["member"])
        
        guild = self.bot.get_guild(guild_id)
        if guild:
            member_role = guild.get_role(member_role_id)
            error = ""
            if not member_role:
                error += "error: member role with given id not found! \n"
            logs_channel = guild.get_channel_or_thread(logs_channel_id)
            if not logs_channel:
                error += "error: the logs channel with the specified id was not found! \n"
            attendance_channel = guild.get_channel_or_thread(attendance_channel_id)
            if not attendance_channel:
                error += "error: no attendance channel with the specified id found! \n"
            tw_server = self.bot.get_guild(tw_server_id)
            if not tw_server:
                error += "error: no server found on TW! \n"
            if tw_server:
                tw_role = tw_server.get_role(tw_role_id)
                if not tw_role:
                    error += "error: member role TW not found! \n"
            if error != "":
                await response.edit(content=f"{error}")
                return
            summary = f"\n**Summary:**\n**Server:** {guild.name}\n**Member role:** {member_role.name}\n**Logs channel:** {logs_channel.name}\n**Attendance_channel:** {attendance_channel.name}\n**TW server:** {tw_server.name}\n**TW role:** {tw_role.name}"
            await response.edit(content=f"✅ OK {summary}")
        else:
            await response.edit(content=f"error: bad guild id!")

            
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
        await recruitment.del_player_to_whitelist(player_name=self.name, recruiter=interaction.user)
        del recruitment

class FormAddQuickly(FormAddPlayer):
    def __init__(self, interaction):
        super().__init__(title='Adding a player', interaction=interaction)
        self.add_item(self.comment)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message(f'The form has been sent. On {interaction.guild.get_channel_or_thread(self.recru_channel_log_id).mention} see progress.', ephemeral=True)
        recruitment = Recruitment(self.interaction, self.recru_channel_log_id)
        await recruitment.add_quickly(self.name, interaction.user, self.comment)
        del recruitment
      