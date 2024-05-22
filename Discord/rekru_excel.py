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
    def __init__(self, interaction = None, log_channel = None):
        self.interaction = interaction
        if interaction != None:
            self.bot = interaction.client
            self.basic_roles = self.bot.db.get_specific_value(interaction.guild_id, "basic_roles")
            self.lineup_roles = self.bot.db.get_specific_value(interaction.guild_id, "lineup_roles")
            main_channel = self.bot.db.get_specific_value(interaction.guild_id, "main_id")
            self.members = interaction.guild.members
            self.log_channel = interaction.guild.get_channel(log_channel) # kanał z logami
            self.chat_channel = interaction.guild.get_channel(main_channel) # kanał pogaduchy
            self.Demi = interaction.guild.get_member(462341202600263681)
            self.embed_color = interaction.user.color

    async def add_player_to_excel(self, player_name, choice, in_house = None, recru_process = None, comment = None, request = None):
        try:
          member_mention = self.get_user(player_name)
          current_data = datetime.now().strftime("%Y-%m-%d")
          
          if member_mention == "-":
            await self.create_embed(4, player_name, member_mention, comment)
            return

          #Sprawdzanie czy taki gracz już istnieje
          if False:
              await self.create_embed(3, player_name)
              return
              
          if choice == 1:
            #dodanie rekruterowi punktów
            #await self.points(choice)
            await self.create_embed(1, player_name, member_mention, comment, request=request)
            return
          try:
            if "tak" in str(recru_process).lower() and choice in [2, 3]:
              #dodanie rekruterowi punktów
              #await self.points(choice)

              #dodanie ról graczowi i wysłanie mu wiadomości
              await self.add_roles(member_mention, in_house)
              await self.chat_channel.send(content = f"**Cześć {member_mention.mention}!**\nPrzywitaj się z wszystkimi.")
              content = ""
              try:
                await member_mention.send('''Witamy w rodzie, teraz kilka linków pomocniczych dla ciebie :saluting_face:
              Ankieta jednostek, pamiętaj zrobić jak tylko będziesz miał chwilkę czasu, to maks 2-3min:
              https://

              Rozpiska jednostek na TW (można sobie dodać do zakładki):
              https://

              Oraz poradniki:
              https://
              ''')

              except Exception as e:
                content = f"{self.interaction.user.mention}, {member_mention.mention} nie dostał wiadomości priv, najprawdopodobniej blokuje\nerror: {e}"
              await self.create_embed(2, player_name, member_mention, comment, in_house=in_house, recru_process=recru_process, content=content)
          except  Exception as e:
              await self.create_embed(0, player_name, member_mention, error=e)
        except HttpError as error:
          print(f'Coś poszło nie tak przy wpisywaniu do excela gracza {player_name}: {error}')
          await self.log_channel.send(content = f"Coś poszło nie tak z graczem: {player_name}\nerror: {e}")

    async def del_msg(self, ctx):
        async for message in ctx.channel.history(limit=1):
            await message.delete()

    async def del_player_to_excel(self, player_name, comment):
        try:
            player_found = False
            member_mention = self.get_user(player_name)
          
            #znalezienie gracza w bazie
            if player_found:
              #usunięcie gracza z listy
              
              content = ""
              try:
                await member_mention.send(f'''Cześć z przykrością musimy powiadomoć że zostałeś usunięty z rodu za brak aktywności. Jeśli chciałbyś wrócić do gry napisz do {self.Demi.mention}.''')
              except:
                content = f"{self.interaction.user.mention}, {member_mention.mention} nie dostał wiadomości priv, najprawdopodobniej blokuje"
              await self.create_embed(5, player_name, member_mention, comment, content=content)
            else:
              await self.create_embed(4, player_name, member_mention)
        except HttpError as error:
            await self.create_embed(0, player_name, member_mention, error=error)

    async def create_embed(self, selection, player_name, member_mention, comment=None, in_house=None, recru_process=None, request=None, error=None, content=None):
      ping = content

      embed = discord.Embed(
          title=f'Gracz: {player_name}, DC: {member_mention}',
          color=self.embed_color
        )
      if selection == 1: # rekruter dodaje tylko na dc
        embed.add_field(name="Czy wysłał zapro do rodu?", value=request, inline=True)
      elif selection == 2:
        embed.add_field(name="W jakim jest rodzie?", value=in_house, inline=True)
        embed.add_field(name="Czy przeszedł rekrutacje?", value=recru_process, inline=True)
      elif selection == 3: # ta osoba znajduje się już w bazie
        ping = self.interaction.user.mention
        embed.description = "Gracz o takim samym nicku już istnieje!!"
        embed.color = discord.Color.red()
      elif selection == 4: # Nick gracza nie został znaleziony na serwerze dc
        ping = self.interaction.user.mention
        embed.description = "Nie został znaleziony!!"
        embed.color = discord.Color.red()
      elif selection == 5: # gracz zostaje usunięty
        embed.description = "Został pomyślnie usunięty!"
      elif selection == 0: # gracz zostaje usunięty
        ping = self.interaction.user.mention
        embed.add_field(name="ERROR", value=error, inline=True)
        embed.color = discord.Color.red()

      embed.add_field(name="Komentarz:", value=comment, inline=False)
      image_url = "https://cdn.discordapp.com/attachments/1105633406764732426/1242415582922412112/Unknown_knight_4.PNG?ex=664dc12d&is=664c6fad&hm=3b6deabaa66da5e337508f1b518bdcb97c518de217cca96e88b45f516acd294a&"
      if type(member_mention) != str:
         image_url = member_mention.avatar
      embed.set_thumbnail(url=image_url)
      embed.set_author(name=self.interaction.user.global_name, icon_url=self.interaction.user.avatar)

      await self.log_channel.send(content = ping,embed=embed)

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
      member_mention = "-"
      for member in self.members:
        if str(member.display_name).lower() == str(player_name).lower():
          member_mention = member
          break
      return member_mention

    async def add_roles(self, member, in_house):
      # Usuń wszystkie obecne rangi
      await member.edit(roles=[], reason="Usuwanie wszystkich ról")
      
      # Dodaj nowe rangi
      roles_id = self.basic_roles
      if str(in_house) == "1" and self.lineup_roles:
        roles_id.append(self.lineup_roles[0])
      elif str(in_house) == "2" and self.lineup_roles:
        roles_id.append(self.lineup_roles[1])
      roles_to_add = [discord.utils.get(member.guild.roles, id=int(role_id)) for role_id in roles_id]
      await member.add_roles(*roles_to_add, reason="Dodawanie nowych ról")

    async def update_roles(self, member, in_house):
      if member != "-":
        second_house_role = discord.utils.get(member.roles, id=1106900620960600104)
        if str(in_house) == "1" and second_house_role:
          await member.remove_roles(second_house_role)
        elif str(in_house) == "2" and not second_house_role:
          role_add = member.guild.get_role(1106900620960600104)
          await member.add_roles(role_add)