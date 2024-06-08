import json
from discord.ext import commands
from datetime import datetime
import requests
import re
import time

class Presence(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.points_from_TW = 1
        self.points_accepted = 0.5
        self.points_signup = 0.25
        self.points_extra = 0.25
        with open('Discord/Keys/config.json', 'r') as file:
          self.url = json.load(file)["kop_singup"]

    async def get_apollo_list(self, guild_id): #pobieranie graczy z listy obecności tych tylko zaznaczonych na tak
        guild = self.bot.get_guild(int(guild_id))
        presence_channels = self.get_presence_channels(guild)
        data = {}
        if not presence_channels:
            return
        for i, channel in enumerate(presence_channels):
            all_players = guild.members
            players_list = []
            async for msg in channel.history(limit=30):
                if msg.author.name == 'Apollo' and msg.embeds:
                    fields = msg.embeds[0].fields
                    data["date"] = self.extract_timestamps(fields[0].value)
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
            delete_response  = requests.delete(f"{self.url}/{data['date']}")
            delete_response.raise_for_status()
            response  = requests.post(self.url, json=data)
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
        if presence_channel_id:
            for channel in guild.text_channels:
                if str(channel.id) in presence_channel_id:
                    presence_channels.append(channel)
        return presence_channels

    def extract_timestamps(self, text):
        timestamps = re.findall(r'<t:(\d+):[a-zA-Z]>', text)
        timestamps = [int(ts) for ts in timestamps]
        dates = [datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d') for ts in timestamps]
        return dates[0]

    async def get_attendance(self, guild_id, guildTW_id): #pobranie listy obecnych na TW i dodawanie punktów
        roleTW_id = self.bot.db.get_specific_value(guild_id, "roles")
        if not roleTW_id:
            return
        date = datetime.now().strftime("%Y-%m-%d")
        roleTW_id = int(roleTW_id[0])
        guildTW = self.bot.get_guild(guildTW_id)
        presence_players_list = await self.get_players(guildTW, roleTW_id)
        if presence_players_list:
            record = self.bot.db.get_results("SELECT player_list FROM TW WHERE discord_server_id = %s AND date = %s", (guild_id, date))
            if record:
                existing_player_list = json.loads(record[0][0])
                combined_player_list = list(set(existing_player_list + presence_players_list))
                presence_players_list = list(set(presence_players_list) - set(existing_player_list))
                self.bot.db.send_data(f"UPDATE TW SET player_list = %s WHERE discord_server_id = %s AND date = %s", (json.dumps(combined_player_list), guild_id, date))
            else:
                self.bot.db.send_data(f"INSERT INTO TW (discord_server_id, date, player_list) VALUES (%s, %s, %s)", (guild_id, date, json.dumps(presence_players_list)))
            
            for player_id in presence_players_list:
                player = self.bot.get_guild(guild_id).get_member(int(player_id))
                extra_role = self.bot.db.get_specific_value(guild_id, "extra_role_id")[0]
                if extra_role:
                    role_names = [role.name for role in player.roles if str(role.id) == extra_role]
                points = self.points_from_TW
                if role_names: 
                    points = self.points_from_TW + self.points_extra
                self.bot.db.points(points, int(player_id), "TW_points")

    async def get_players(self, guild, role_id):
        players_list = []
        for channel in guild.voice_channels:
            if channel.members != []:
                for member in channel.members:
                    for role in member.roles:
                        if role.id == role_id:
                            players_list.append(member.id)
        return players_list

    async def get_signup(self, guild_id): # Punktowanie graczy za signup
        guild = self.bot.get_guild(int(guild_id))   #pobieram serwer
        presence_channels = self.get_presence_channels(guild) #pobieram kanały
        if not presence_channels:
            return
        all_players = guild.members #cała lista graczy z serwera
        for channel in presence_channels: #sprawdzamy każdy kanał z botem do oznaczania się
            async for msg in channel.history(limit=30):
                if msg.author.name == 'Apollo' and msg.embeds:
                    fields = msg.embeds[0].fields 
                    for i in range(2, len(fields)): #pobranie fields i puszczenie w pętle, aby pobrać z każdego graczy
                        players = fields[i].value[4:].splitlines()
                        if len(players) > 0 and players is not None:
                            for player in players:  #pobranie każdego gracza z field
                                player = player.replace('\\', '')
                                for p_list in all_players: 
                                    if player == p_list.display_name: #porównanie gracza z field do graczy na serwerze po nazwie
                                        if "Accepted" in fields[i].name: #jeśli jest to dodanie punktów w zależnośći od zaznaczenia
                                            self.bot.db.points(self.points_accepted, p_list.id, "signup_points")
                                        else:
                                            self.bot.db.points(self.points_signup, p_list.id, "signup_points")
                                        break

    def get_server_players(self, guild, role_id):
        players_list = []
        for member in guild.members:
            for role in member.roles:
                if role.id == role_id:
                    players_list.append(member.id)
        return players_list

    async def checking_surveys(self, guild, role_id, msg_author):
        #pobrać role membera z bazy
        players_id = self.get_server_players(guild, int(role_id))
        with open('Discord/Keys/config.json', 'r') as file:
          survey_url = json.load(file)["kop_survey"]
        response = requests.get(survey_url)
        response.raise_for_status() 
        data = response.json()
        for row in data["surveys"]: #przeszukuje całą listę
            discord_id = int(row["discordId"])
            if discord_id in players_id:
                players_id.remove(discord_id)

        await msg_author.send(f"Ilość wiadomości do wysłania {len(players_id)}, przywidywany czas {len(players_id)*10} sec")
        error_player_list = ""
        error_count = 0

        for player_id in players_id:
            player = guild.get_member(player_id)
            try:
                await player.send(f"**Proszę o nie blokowanie tego bota, bo jak za duzo osób zablokuje może chycić BANA**\nSiemanko, przypominam o wypełnieniu ankiety https://cb-social.vercel.app/ \nW razie porblemów proszę pisać do Strijder albo CZARNEGO")
            except:
                error_count += 1
                error_player_list += f"{player.mention} "
            time.sleep(10)
        await msg_author.send(f"Wysyłanie zakończone, wiadomośc nie dotarła do {error_count}: {error_player_list}")


    async def del_msg(self, ctx):
        async for message in ctx.channel.history(limit=1):
            await message.delete()