import json
import discord
from discord.ext import commands
import requests

class Recruitment(commands.Cog):
    def __init__(self, interaction = None, log_channel = None):
        self.interaction = interaction
        with open('Discord/Keys/config.json', 'r') as file:
          self.url = json.load(file)["kop_whitelist"]
        self.recruitment_stage_1_points = 0.5
        self.recruitment_stage_2_points = 0.5
        if interaction != None:
          self.bot = interaction.client
          self.basic_roles = self.bot.db.get_specific_value(interaction.guild_id, "basic_roles")
          self.lineup_roles = self.bot.db.get_specific_value(interaction.guild_id, "lineup_roles")
          main_channel = self.bot.db.get_specific_value(interaction.guild_id, "main_id")
          self.members = interaction.guild.members
          self.log_channel = interaction.guild.get_channel(log_channel) # kanał z logami
          self.chat_channel = interaction.guild.get_channel(main_channel) # kanał pogaduchy
          self.embed_color = interaction.user.color

    async def add_player_to_whitelist(self, player_name, choice, in_house = None, recru_process = None, comment = None, request = None):
        try:
          member_mention = self.get_user(player_name)
          if member_mention == "-":
            await self.create_embed(4, player_name, member_mention, comment)
            return
          self.add_to_database(member_mention.id, self.interaction.guild_id)#dodaje gracza do bazy
          #Sprawdzanie czy taki gracz już istnieje
          response = requests.get(self.url)
          response.raise_for_status() 
          data = response.json()
          found_player = False
          for row in data["whitelist"]: #przeszukuje całą listę
            if str(member_mention.id) == row["idDiscord"]:
              found_player = True
              break
          
          if found_player and choice != 2: #jeżeli gracz znaleziony i drugi etap rekrutacyjny 
            await self.create_embed(3, player_name, member_mention, comment)
            return
          elif not found_player: 
            data = {
                "idDiscord": str(member_mention.id)
            }
            response = requests.post(self.url, json=data)
            response.raise_for_status()  # Raises an HTTPError if the HTTP request returned an unsuccessful status code

          if choice == 1:
            #dodanie rekruterowi punktów
            self.bot.db.points(self.recruitment_stage_1_points, self.interaction.user.id, "recruitment_points")
            await self.create_embed(1, player_name, member_mention, comment, request=request)
            return
          try:
            if "tak" in str(recru_process).lower() and choice in [2, 3]:
              #dodanie rekruterowi punktów
              points = self.recruitment_stage_1_points
              if choice == 3:
                points = self.recruitment_stage_1_points + self.recruitment_stage_2_points
              self.bot.db.points(points, self.interaction.user.id, "recruitment_points")

              #dodanie ról graczowi i wysłanie mu wiadomości
              await self.add_roles(member_mention, in_house)
              await self.chat_channel.send(content = f"**Cześć {member_mention.mention}!**\nPrzywitaj się ze wszystkimi.")
              content = ""
              try:
                pass
                await member_mention.send('''Witamy w rodzie, teraz kilka linków pomocniczych dla ciebie :saluting_face:
              Ankieta jednostek, pamiętaj zrobić jak tylko będziesz miał chwilkę czasu:
              https://cb-social.vercel.app/

              Rozpiska jednostek na TW (można sobie dodać do zakładki):
              https://

              Oraz poradniki:
              https://discord.com/channels/1232957904597024882/1235004633974313123
              ''')

              except Exception as e:
                content = f"{self.interaction.user.mention}, {member_mention.mention} nie dostał wiadomości priv, najprawdopodobniej blokuje\nerror: {e}"
              await self.create_embed(2, player_name, member_mention, comment, in_house=in_house, recru_process=recru_process, content=content)
            elif "nie" in str(recru_process).lower() and choice in [2, 3]:
              content = f"{self.interaction.user.mention} Jakim cudem przeprowadzasz 2 etap albo całą rekrutacje bez rekrutacji głosowej, miałeś tylko jedno zadnie!!!\n-5 punktów dla Slytherin'u"
              await self.create_embed(2, player_name, member_mention, comment, in_house=in_house, recru_process=recru_process, content=content)
          except  Exception as e:
              await self.create_embed(0, player_name, member_mention, error=e)
        except requests.exceptions.HTTPError as e:
          await self.log_channel.send(content = f"Wystąpił błąd HTTP: {e} \n {response.text}")
        except requests.exceptions.RequestException as e:
            await self.log_channel.send(content = f"Wystąpił błąd żądania: {e}")

    async def del_msg(self, ctx):
        async for message in ctx.channel.history(limit=1):
            await message.delete()

    async def del_player_to_whitelist(self, player_name, comment):
        try:
            member_mention = self.get_user(player_name)
            if member_mention:
              self.bot.db.del_with_whitelist(member_mention.id)
              content = ""
              try:
                await member_mention.send(f'''Cześć z przykrością musimy powiadomoć że zostałeś usunięty z rodu za brak aktywności.''')
              except:
                content = f"{self.interaction.user.mention}, {member_mention.mention} nie dostał wiadomości priv, najprawdopodobniej blokuje"
              await self.create_embed(5, player_name, member_mention, comment, content=content)
            else:
              await self.create_embed(4, player_name, member_mention)
        except Exception as error:
            await self.create_embed(0, player_name, member_mention, error=error)

    async def create_embed(self, selection, player_name, member_mention, comment=None, in_house=None, recru_process=None, request=None, error=None, content=None):
      ping = content

      embed = discord.Embed(
          title=f'Gracz: {player_name}',
          description=f"DC: {member_mention.mention}",
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

    def points(self, choice, recruiter):
      points = 0
      if choice in [1,2]:
        points = 1
      elif choice == 3:
        points = 2
      try:
        self.bot.db.send_data(f"UPDATE Players SET points = points + %s WHERE id_player = %s", (points, recruiter.id))
      except Exception as e:
        print(f"błąd przy dodawaniu punktów, pewnie nie ma rekrutera error:\n{e}")
      
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

    def add_to_database(self, player_id, guild_id):
      try:
        self.bot.db.send_data(f"INSERT INTO Players (id_player, discord_server_id, TW_points, signup_points, extra_points, recruitment_points, activity_points) VALUES (%s, %s, %s, %s, %s, %s, %s)""", (player_id, guild_id, 0, 0, 0, 0, 0))
      except Exception as e:
        print(f"add_to_database, error:\n{e}")