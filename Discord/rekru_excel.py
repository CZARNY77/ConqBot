import os
import json
import discord
from discord.ext import commands
import datetime
from datetime import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials

class Excel(commands.Cog):
    def __init__(self, interaction = None):
        with open('Discord/Keys/credentials_key.json', 'r') as file:
            credentials_info = json.load(file)
        self.credentials = service_account.Credentials.from_service_account_info(credentials_info)
        self.DISCOVERY_SERVICE_URL = 'https://sheets.googleapis.com/$discovery/rest?version=v4'
        self.service = build('sheets', 'v4', credentials=self.credentials, discoveryServiceUrl=self.DISCOVERY_SERVICE_URL)
        with open('Discord/Keys/id_list.json', 'r') as file:
            id_list = json.load(file)
        self.spreadsheet_id = id_list["spreadsheet_id"]
        self.spreadsheet_TW_id = id_list["spreadsheet_TW_id"]
        self.player_sheet = "Gracze"
        self.player_sheet_id = id_list["player_sheet_id"]
        self.archives_sheet = "Archiwum"
        self.archives_sheet_id = id_list["archives_sheet_id"]
        self.recruiter_sheet = "Rekruterzy"
        self.interaction = interaction
        if interaction != None:
            self.members = interaction.guild.members
            self.log_channel = interaction.guild.get_channel(1100724286139940948) # kanał z logami
            self.chat_channel = interaction.guild.get_channel(1100724286509043850) # kanał pogaduchy
            self.Demi = interaction.guild.get_member(462341202600263681)

    async def add_player_to_excel(self, player_name, choice, in_house, recruit, comment, request, in_dc):
        #self.get_roles()
        try:
            values = self.get_values(self.spreadsheet_id, self.player_sheet)
            value_from_archives = self.get_values(self.spreadsheet_id, self.archives_sheet)
            row_num = len(values[0][0]) + 1
            member_mention = self.get_user(player_name)
            current_data = datetime.now().strftime("%Y-%m-%d")
            player_from_archive = False
            row_number_to_delete = 0

            #Sprawdzanie czy taki gracz już istnieje
            for i, v in enumerate(values[0][0]):
              if v.lower() == str(player_name).lower():
                #warunek przy podyfikacji jeśli znajdzie gracza zapisuje jego pozycję
                if choice in [2,4]:
                  current_data = values[0][1][i]
                  row_num = i+1
                  break
                await self.create_embed(4, player_name)
                return
            #sprawdzanie czy gracz jest w archium i kiedy został wyrzucoony
            for i, v in enumerate(value_from_archives[0][1]):
              if v.lower() == str(player_name).lower():
                player_from_archive = True
                #data wyrzucenia > start sezonu -> aktualny dzień
                #data wyrzucenia < start sezonu -> data dodania
                if value_from_archives[0][0][i] < value_from_archives[0][2][0]:
                  current_data = value_from_archives[0][2][i]
                row_number_to_delete = i+1
                break

            # wartości do wpisania
            range_name = f'{self.player_sheet}!{chr(ord("A"))}{row_num}:{chr(ord("E"))}{row_num}'
            body = {
              'values': [[str(player_name),
                          current_data, str(member_mention), str(in_house), str(recruit)]]
            }
            # tworzenie zapytania
            service = build('sheets', 'v4', credentials=self.credentials, discoveryServiceUrl=self.DISCOVERY_SERVICE_URL)
            service.spreadsheets().values().update( spreadsheetId=self.spreadsheet_id, range=range_name, valueInputOption='RAW', body=body).execute()

            await self.points(choice)

            #usunięcie wiersza w archiwum z graczem jeśli taki istnieje
            if player_from_archive == True and choice != 1:
              await self.delete_row(row_number_to_delete, self.archives_sheet_id)
              await self.create_embed(5, player_name, in_house, recruit, comment, member_mention)
            else:
              if choice == 1:
                await self.create_embed(6, player_name, in_house, recruit, comment, member_mention, request, in_dc)
              elif choice in [2,4]:
                await self.update_roles(member_mention, in_house)
                await self.create_embed(7, player_name, in_house, recruit, comment, member_mention)
              else:
                await self.create_embed(1, player_name, in_house, recruit, comment, member_mention)
            if "tak" in str(recruit).lower() and choice in [2, 3, 5]:
              try:
                #update roles
                if choice != 5:
                  await self.add_roles(member_mention, in_house)
                  await self.chat_channel.send(content = f"**Witaj {member_mention.mention} w Zakonie!**\nOd Dzisiaj jesteś jednym z wielu którzy postanowili podążyć z nami na ścieżkach conqueror's blade.\nCzy mógłbyś powiedzieć nam coś o sobie ?")
                try:
                  await member_mention.send('''Witamy w rodzie, teraz kilka linków pomocniczych dla ciebie :saluting_face:
                Ankieta jednostek, pamiętaj zrobić jak tylko będziesz miał chwilkę czasu, to maks 2-3min:
                https://docs.google.com/forms/d/e/1FAIpQLSfGdxPm8R04WYCe9SX2jolHqTTe8sZkpi7YhqxoPMt3s6gGOQ/viewform?usp=sf_link
  
                Rozpiska jednostek na TW (można sobie dodać do zakładki):
                https://docs.google.com/spreadsheets/d/1Yiqd5kfsBGjxsK5QTsb7lx2H2thZinnBog7r1JkzWeI/edit#gid=662960245
  
                Oraz poradniki:
                https://discord.com/channels/1100724285246558208/1100896767463141498/1100896767463141498
                ''')
  
                except:
                  await self.log_channel.send(content = f"{member_mention.mention} Nie dostał wiadomości priv, najprawdopodobniej blokuje")
              except:
                  await self.log_channel.send(content = f"{player_name} nie znaleziono dc")
        except HttpError as error:
            print(f'Coś poszło nie tak przy wpisywaniu do excela gracza {player_name}: {error}')
            await self.create_embed(0, player_name)

    async def del_msg(self, ctx):
        async for message in ctx.channel.history(limit=1):
            await message.delete()

    async def del_player_to_excel(self, player_name, comment):
        try:
            values = self.get_values(self.spreadsheet_id, self.player_sheet)
            row_num = 0
            col_num = 0
            data = [datetime.now().strftime("%Y-%m-%d")]
            player_found = False
            member_mention = self.get_user(player_name)
          
            for v in values[0][0]:
              if v.lower() == str(player_name).lower():
                player_found = True
                break
              row_num += 1
            if player_found:
              for v in values[0]:
                #col_num += 1
                try:
                  data.append(v[row_num])
                except:
                  break
              row_number_to_delete = row_num+1
              values = self.get_values(self.spreadsheet_id, self.archives_sheet)
              row_num = len(values[0][0]) + 1
                
              # wartość do wpisania
              range_name = f'{self.archives_sheet}!{chr(ord("A"))}{row_num}:{chr(ord("S"))}{row_num}'
              body = {'values': [data]}
              # tworzenie zapytania
              service = build('sheets', 'v4', credentials=self.credentials, discoveryServiceUrl=self.DISCOVERY_SERVICE_URL)
              service.spreadsheets().values().update( spreadsheetId=self.spreadsheet_id, range=range_name, valueInputOption='RAW', body=body).execute()
              await self.delete_row(row_number_to_delete, self.player_sheet_id)
              await self.create_embed(2, player_name, comment=comment)

              try:
                await member_mention.send(f'''Cześć z przykrością musimy powiadomoć że zostałeś usunięty z rodu za brak aktywności. Jeśli chciałbyś wrócić do gry napisz do {self.Demi.mention}.
              ''')

              except:
                await self.log_channel.send(content = f"{member_mention.mention} Nie dostał wiadomości priv, najprawdopodobniej blokuje")
            else:
              print("nie znaleziono gracza!!!")
              await self.create_embed(3, player_name)

        except HttpError as error:
            print(f'Coś poszło nie tak przy przenoszeniu do archiwum gracza {player_name}: {error}')
            await self.create_embed(0, player_name)

    def get_values(self, spreadsheet_id, sheet):
      result = self.service.spreadsheets().values().batchGet(spreadsheetId=spreadsheet_id, ranges=sheet, majorDimension='COLUMNS').execute()
      values = []
      for res in result.get('valueRanges'):
          values.append(res.get('values', []))
      return values

    async def delete_row(self, row_num, sheet_id):
      requests = [
          {
              "deleteDimension": {
                  "range": {
                      "sheetId": sheet_id,
                      "dimension": "ROWS",
                      "startIndex": row_num - 1,
                      "endIndex": row_num
                  }
              }
          }
      ]
      body = {"requests": requests}
      #print(body)
      self.service.spreadsheets().batchUpdate(spreadsheetId=self.spreadsheet_id, body=body).execute()

    async def create_embed(self, error, player_name, in_house=None, recruit=None, comment=None, member_mention=None, request=None, in_dc=None):
      ping = ""
      if error == 1:
        embed = discord.Embed(
          title=f'Gracz: {player_name}, DC: {member_mention}',
          color=discord.Color.blue()
        )
        embed.add_field(name="Jest w rodzie?", value=in_house, inline=True)
        embed.add_field(name="Czy przeszedł rekrutacje?", value=recruit, inline=True)
        embed.add_field(name="Komentarz:", value=comment, inline=False)
      elif error == 2:
        embed = discord.Embed(
          title=f'Gracz: {player_name}',
          description='Został pomyślnie usunięty',
          color=discord.Color.blue()
        )
        embed.add_field(name="Komentarz:", value=comment, inline=False)
      elif error == 3:
        ping = self.interaction.user.mention
        embed = discord.Embed(
          title=f'Gracz: {player_name}',
          description='Nie został znaleziony',
          color=discord.Color.blue()
        )
      elif error == 4:
        ping = self.interaction.user.mention
        embed = discord.Embed(
          title=f'Gracz: {player_name}',
          description='Gracz o takim samym nicku już istnieje',
          color=discord.Color.blue()
        )
      elif error == 5:
        embed = discord.Embed(
          title=f'Gracz: {player_name}, DC: {member_mention}, był w archiwum',
          color=discord.Color.blue()
        )
        embed.add_field(name="Jest w rodzie?", value=in_house, inline=True)
        embed.add_field(name="Czy przeszedł rekrutacje?", value=recruit, inline=True)
        embed.add_field(name="Komentarz:", value=comment, inline=False)
      elif error == 6:
        embed = discord.Embed(
          title=f'Gracz: {player_name}, DC: {member_mention}',
          color=discord.Color.blue()
        )
        embed.add_field(name="Wysłał zapro do rodu?", value=request, inline=True)
        embed.add_field(name="Czy jest na dc?", value=in_dc, inline=True)
        embed.add_field(name="Komentarz:", value=comment, inline=False)
      elif error == 7:
        embed = discord.Embed(
          title=f'(Modyfikacja) Gracz: {player_name}, DC: {member_mention}',
          color=discord.Color.blue()
        )
        embed.add_field(name="Jest w rodzie?", value=in_house, inline=True)
        embed.add_field(name="Czy przeszedł rekrutacje?", value=recruit, inline=True)
        embed.add_field(name="Komentarz:", value=comment, inline=False)
      else:
        ping = self.interaction.user.mention
        embed = discord.Embed(
          title=f'Gracz {player_name}',
          description='Error, wyślij jeszcze raz, jeśli nie pomaga zgłoś to do zarządu.',
          color=discord.Color.blue()
        )
      embed.set_author(name=self.interaction.user.global_name, icon_url=self.interaction.user.avatar)

      await self.log_channel.send(content = ping,embed=embed)
  
    async def reset_list_TW(self, lineup_sheet):
      values = self.get_values(self.spreadsheet_TW_id, lineup_sheet)
      col_numbers = [2, 4, 8, 10, 12, 14, 16]
      for col_num in col_numbers:
        value = values[0][col_num]
        row_num = len(value)

        # wartość do wpisania
        range_name = f'{lineup_sheet}!{chr(ord("A")+col_num)}5:{chr(ord("A")+col_num)}'
        body = {
          'values': [["" for _ in range(1)] for _ in range(row_num - 4)]
        }
        # tworzenie zapytania
        service = build('sheets', 'v4', credentials=self.credentials, discoveryServiceUrl=self.DISCOVERY_SERVICE_URL)
        service.spreadsheets().values().update( spreadsheetId=self.spreadsheet_TW_id, range=range_name, valueInputOption='RAW', body=body).execute()

    def get_name_sheet(self):
      spreadsheet = self.service.spreadsheets().get(spreadsheetId=self.spreadsheet_TW_id).execute()
      temp = []
      arkusze = spreadsheet['sheets']
      name_sheets = [arkusz['properties']['title'] for arkusz in arkusze]
      for name_sheet in name_sheets:
        if "Lineup" in name_sheet:
          temp.append(discord.SelectOption(label=name_sheet, value=name_sheet))
      return temp

    async def points(self, choice):
      recruiter = self.interaction.user
      points = 0
      try:
        values = self.get_values(self.spreadsheet_id, self.recruiter_sheet)
        row_num = len(values[0][0]) + 1
        
        for i, v in enumerate(values[0][0]):
          if v.lower() == str(recruiter.global_name).lower():
            points = int(values[0][1][i])
            row_num = i+1
            break
        if choice == 1 or choice == 2:
          points += 1
        elif choice == 3:
          points += 2
        range_name = f'{self.recruiter_sheet}!{chr(ord("A"))}{row_num}:{chr(ord("B"))}{row_num}'
        body = {
          'values': [[str(recruiter.global_name), str(points)]]
        }
        # tworzenie zapytania
        service = build('sheets', 'v4', credentials=self.credentials, discoveryServiceUrl=self.DISCOVERY_SERVICE_URL)
        service.spreadsheets().values().update( spreadsheetId=self.spreadsheet_id, range=range_name, valueInputOption='RAW', body=body).execute()
      except:
        await self.log_channel.send(content = f"{recruiter.global_name}: {int(points)} pkt. ")

    def get_user(self, player_name):
      member_mention = ""
      for member in self.members:
        if str(member.nick).lower() == str(player_name).lower():
          member_mention = member
          break

        elif str(member.global_name).lower() == str(player_name).lower():
          member_mention = member
          break

        elif str(member.name).lower() == str(player_name).lower():
          member_mention = member
          break
        else:
            member_mention = "-"
      return member_mention

    async def add_roles(self, member, in_house):
      # Usuń wszystkie obecne rangi
      await member.edit(roles=[], reason="Usuwanie wszystkich ról")
      
      # Dodaj nowe rangi
      roles_id = [1100724285263331332, 1100724285263331334, 1183456420897771651,]
      if str(in_house) == "2":
        roles_id.append(1106900620960600104)
      roles_to_add = [discord.utils.get(member.guild.roles, id=role_id) for role_id in roles_id]
      await member.add_roles(*roles_to_add, reason="Dodawanie nowych ról")

    async def update_roles(self, member, in_house):
      if member != "-":
        second_house_role = discord.utils.get(member.roles, id=1106900620960600104)
        if str(in_house) == "1" and second_house_role:
          await member.remove_roles(second_house_role)
        elif str(in_house) == "2" and not second_house_role:
          role_add = member.guild.get_role(1106900620960600104)
          await member.add_roles(role_add)