import json
from discord.ext import commands
from datetime import datetime
import requests

class Presence(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        with open('Discord/Keys/config.json', 'r') as file:
          self.url = json.load(file)["kop_singup"]

    async def get_apollo_list(self, guild_id): #pobieranie graczy z listy obecności tych tylko zaznaczonych na tak
        guild = self.bot.get_guild(int(guild_id))
        presence_channels = self.get_presence_channels(guild)
        current_data = datetime.now().strftime("%Y-%m-%d")
        data = {"date": current_data}
        if not presence_channels:
            return
        for i, channel in enumerate(presence_channels):
            all_players = guild.members
            players_list = []
            async for msg in channel.history(limit=30):
                if msg.author.name == 'Apollo' and msg.embeds:
                    fields = msg.embeds[0].fields
                    for field in fields:
                        if "Accepted" in field.name:
                            players = field.value[4:].splitlines()
                            if len(players) > 0 and players is not None:
                                # Tworzymy listę wspólnych członków
                                common_members = [member for member in all_players if member.display_name in players]

                                players_list = [str(member.id) for member in common_members]
                                break
                            break
                    break
            data[f"lineup_{i+1}"] = players_list

        try:
            print(data)
            response = requests.post(self.url, json=data)
            response.raise_for_status()
            players_list.clear()
        except requests.exceptions.HTTPError as e:
            log_channel = self.bot.get_channel(int(self.bot.db.get_specific_value(guild.id, "general_logs_id")))
            await log_channel.send(content = f"Wystąpił błąd HTTP: {e} \n {response.text}")
        except requests.exceptions.RequestException as e:
            log_channel = self.bot.get_channel(int(self.bot.db.get_specific_value(guild.id, "general_logs_id")))
            await log_channel.send(content = f"Wystąpił błąd żądania: {e}")

    def get_presence_channels(self, guild):
        presence_channels = []
        presence_channel_id = self.bot.db.get_specific_value(guild.id, "presence_channels_id")
        for channel in guild.text_channels:
            if str(channel.id) in presence_channel_id:
                presence_channels.append(channel)
        return presence_channels

    async def get_attendance(self, guild_id, guildTW_id): #popranie listy obecnych na TW
        roleTW_id = self.bot.db.get_specific_value(guild_id, "roles")
        basic_role_id = self.bot.db.get_specific_value(guild_id, "basic_roles")
        if not roleTW_id or not basic_role_id:
            return
        roleTW_id = int(roleTW_id[0])
        basic_role_id = int(basic_role_id[0])
        guild = self.bot.get_guild(guild_id)
        guildTW = self.bot.get_guild(guildTW_id)
        current_players = await self.get_name_from_server(guild, guildTW, basic_role_id, roleTW_id)

        data = {
            "date": current_players,
        }
        try:
            print(data)
            response = requests.post(self.url, json=data)
            response.raise_for_status()
            current_players.clear()
        except requests.exceptions.HTTPError as e:
            log_channel = self.bot.get_channel(int(self.bot.db.get_specific_value(guild.id, "general_logs_id")))
            await log_channel.send(content = f"Wystąpił błąd HTTP: {e} \n {response.text}")
        except requests.exceptions.RequestException as e:
            log_channel = self.bot.get_channel(int(self.bot.db.get_specific_value(guild.id, "general_logs_id")))
            await log_channel.send(content = f"Wystąpił błąd żądania: {e}")

    async def get_name_from_server(self, guild, guildTW, role_id, roleTW_id):
        server_player_list = await self.get_all_players(guild, role_id)
        presence_players_list = await self.get_players(guildTW, roleTW_id)
        players_list = []
        for presence_player in presence_players_list:
            for server_player in server_player_list:
                if server_player.id == presence_player.id:
                    players_list.append(server_player.display_name)
                    break
        return players_list

    async def get_players(self, guild, role_id):
        players_list = []
        for channel in guild.voice_channels:
            if channel.members != []:
                for member in channel.members:
                    for role in member.roles:
                        if role.id == role_id:
                            players_list.append(member)
        return players_list

    async def get_all_players(self, guild, role_id):
        players_list = []
        for player in guild.members:
            for role in player.roles:
                if role.id == role_id:
                    players_list.append(player)
        return players_list

    async def del_msg(self, ctx):
        async for message in ctx.channel.history(limit=1):
            await message.delete()