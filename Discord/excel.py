import os
import json
from discord.ext import commands
import datetime
from datetime import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials


class Excel(commands.Cog):
    def __init__(self, bot):
        with open('/home/container/DiesMedaBot/Keys/credentials_key.json', 'r') as file:
            credentials_info = json.load(file)
        self.credentials = service_account.Credentials.from_service_account_info(credentials_info)
        self.DISCOVERY_SERVICE_URL = 'https://sheets.googleapis.com/$discovery/rest?version=v4'
        self.service = build('sheets', 'v4', credentials=self.credentials, discoveryServiceUrl=self.DISCOVERY_SERVICE_URL)
        with open('/home/container/DiesMedaBot/Keys/id_list.json', 'r') as file:
            id_list = json.load(file)
        self.spreadsheet_id = id_list["spreadsheet_id"]
        self.spreadsheet_TW_id = id_list["spreadsheet_TW_id"]
        self.guild = bot.get_guild(1100724285246558208)
        self.name_role = "House Member"

    async def connect_with_excel(self, players_online, sheet):
        # Otwiera arkusz kalkulacyjny
        row_num = 0
        column_num = 0

        try:
            result = self.service.spreadsheets().values().batchGet(
                spreadsheetId=self.spreadsheet_id,
                ranges=sheet,
                majorDimension='COLUMNS').execute()
            values = []
            players_list = []
            for res in result.get('valueRanges'):
                values.append(res.get('values', []))
            for v in enumerate(values[0]):
                if v[1][0] == str(datetime.now().date()):
                    players_list = v[1]
                    del players_list[0:2]
                    break
                column_num += 1
            row_num = len(players_list) + 3

            for player_l in players_list:
                for player_o in players_online:
                    if player_o == player_l:
                        players_online.remove(player_o)
                        break
            # wartość do wpisania
            range_name = f'{sheet}!{chr(ord("A")+column_num)}{row_num}:{chr(ord("A")+column_num)}'
            body = {'values': [[player] for player in players_online]}
            # tworzenie zapytania
            service = build('sheets', 'v4', credentials=self.credentials, discoveryServiceUrl=self.DISCOVERY_SERVICE_URL)
            service.spreadsheets().values().update( spreadsheetId=self.spreadsheet_id, range=range_name, valueInputOption='RAW', body=body).execute()

        except HttpError as error:
            print(f'Coś poszło nie tak przy wpisywaniu obecności: {error}')  # dodać wysyłanie wiadomości gdy coś pójdzie nie tak

    async def get_players(self, guild): #przerobić aby pobierało graczy i stworzyć funkcje która będzie porównywała 
        players_list = []
        for channel in guild.voice_channels:
            if channel.members != []:
                for member in channel.members:
                    for role in member.roles:
                        if role.name == self.name_role:
                            players_list.append(member)
        return players_list

    async def get_presence_channels(self):
        self.presence_channels = []
        presence_channel_id = [1153391476789743708, 1153390631192891402, 1163931612011053217]
        for channel in self.guild.text_channels:
            if channel.id in presence_channel_id:
                self.presence_channels.append(channel)

    async def get_apollo_list(self):
        await self.get_presence_channels()
        fields_name = ["Accepted", "Declined", "Tentative"]
        for field_name in fields_name:
            for channel in self.presence_channels:
                players_list = []
                count_msg = 0
                messages = [message async for message in channel.history(limit=30)]
                for msg in messages:
                    if msg.author.name == 'Apollo':
                        count_msg += 1
                        if count_msg == 2:
                            fields = msg.embeds[0].fields
                            for field in fields:
                                if field_name in field.name:
                                    players = field.value[4:].splitlines()
                                    if len(players) > 0 and players is not None:
                                        for player in players:
                                            player = player.replace('\\', '')
                                            players_list.append(player)
                            await self.connect_with_excel(
                                players_list, field_name.upper())
                            break

    async def del_msg(self, ctx):
        async for message in ctx.channel.history(limit=1):
            await message.delete()

    async def get_all_players(self):
        players_list = []
        for player in self.guild.members:
            for role in player.roles:
                if role.id == 1100724285263331332:
                    players_list.append(player)
        return players_list

    async def get_excel_players(self, all_players):
        try:
            result = self.service.spreadsheets().values().batchGet(
                spreadsheetId=self.spreadsheet_TW_id,
                ranges="Liczba odpowiedzi: 3",
                majorDimension='COLUMNS').execute()
            values = []
            players_list = []
            for res in result.get('valueRanges'):
                values.append(res.get('values', []))
            for v in enumerate(values[0][1]):
                players_list.append(v[1])

            for player_list in players_list:
                for player in all_players:
                    if player.nick != None and player_list.lower( ) == player.nick.lower():
                        all_players.remove(player)
                        break
                    elif player.global_name != None and player_list.lower() == player.global_name.lower():
                        all_players.remove(player)
                        break
                    elif player.name != None and player_list.lower() == player.name.lower():
                        all_players.remove(player)
                        break
            return all_players

        except HttpError as error:
            print(f'Coś poszło nie tak przy wpisywaniu obecności: {error}')

    async def change_to_text(self, old_player_list):
        players_list = []
        for player in old_player_list:
            print(player)
            if player.nick != None:
                players_list.append(player.nick)
            elif player.global_name != None:
                players_list.append(player.global_name)
            elif player.name != None:
                players_list.append(player.name)
        return players_list

    async def get_name_from_server(self, server):
        server_player_list = await self.get_all_players()
        presence_players_list = await self.get_players(server)
        players_list = []
        for presence_player in presence_players_list:
            for server_player in server_player_list:
                if server_player.id == presence_player.id:
                    if server_player.nick != None:
                        players_list.append(server_player.nick)
                    elif server_player.global_name != None:
                        players_list.append(server_player.global_name)
                    elif server_player.name != None:
                        players_list.append(server_player.name)
                    break
        return players_list