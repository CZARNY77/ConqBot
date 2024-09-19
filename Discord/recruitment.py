import json
import discord
from discord.ext import commands
import requests
from datetime import datetime, timezone
import os
from Discord.conqAppsRequests import conqSite

class Recruitment(commands.Cog):
  def __init__(self, interaction = None, log_channel = None, bot = None, member_guild = None):
      self.interaction = interaction
      with open('Discord/Keys/config.json', 'r') as file:
        self.url = json.load(file)["kop_whitelist"]
      with open('Discord/Keys/config.json', 'r') as file:
        self.survey_url = json.load(file)["kop_survey"]
      self.headers = {'discord-key': f"{os.getenv('SITE_KEY')}"}
      self.recruitment_stage_1_points = 0.5
      if interaction != None or bot != None:
        if bot != None:
          self.bot = bot
          self.guild = member_guild
          self.embed_color = discord.Color.red()
        else:
          self.bot = interaction.client
          self.guild = interaction.guild
          self.embed_color = interaction.user.color

        conq_site = conqSite()
        data_config = conq_site.config(self.guild.id)
        self.house_name = data_config["house"]["name"] or "None" # do wywalenia
        main_channel = self.bot.db.get_specific_value(self.guild.id, "main_id")
        self.members = self.guild.members
        self.log_channel = self.guild.get_channel_or_thread(int(data_config["logs"]["logs"])) # kanał z logami
        self.chat_channel = self.guild.get_channel_or_thread(main_channel) # kanał pogaduchy
  
  async def add_player_to_whitelist(self, member):

    recruiter = self.bot.user #pobieranie rekrutera z logów serwera
    if member.guild.me.guild_permissions.view_audit_log:
      async for entry in self.guild.audit_logs(limit=5, action=discord.AuditLogAction.member_role_update):
        if entry.target.id == member.id:
            recruiter = entry.user
            break
    else:
      print(f"bot nie ma uprawnień do logów na serwerze {member.guild.name}")  
    try:

      response = requests.get(self.url, headers=self.headers)
      response.raise_for_status() 
      data = response.json()
      found_player = False

      for row in data["whitelist"]: #sprawdzamy czy taka osoba jest na whitelist
        if "idDiscord" in row:
          if str(member.id) == row["idDiscord"]:
            found_player = True
            break
      if not found_player: #jeśli nie to dodajemy i tworzymy/przyywracamy ankiete
        data = {
            "idDiscord": str(member.id),
            "house": str(self.house_name)
        }
        response = requests.post(self.url, json=data, headers=self.headers)
        response.raise_for_status()
        await self.add_player_to_survey(member)

      if recruiter: #dodanie punktów rekruterowixcfgvr
        self.bot.db.points(self.recruitment_stage_1_points, recruiter, "recruitment_points")
        self.embed_color = recruiter.color
      if self.chat_channel: # wysłanie na kanał główny wiadomości jeśli została podana
        await self.chat_channel.send(content = f"**Cześć {member.mention}!**\nPrzywitaj się ze wszystkimi.")
        #await member.send('Witamy w rodzie, teraz kilka linków pomocniczych dla ciebie :saluting_face:\nAnkieta jednostek, pamiętaj zrobić jak tylko będziesz miał chwilkę czasu:\nhttps://cb-social.vercel.app/\n\nOraz poradniki:\nhttps://discord.com/channels/1232957904597024882/1235004633974313123')
      await self.create_embed(1, member, recruiter)

    except requests.exceptions.HTTPError as e:
      await self.log_channel.send(content = f"HTTP error occurred: {e} \n {response.text}")
    except requests.exceptions.RequestException as e:
      await self.log_channel.send(content = f"A request error occurred: {e}")

  async def del_player_to_whitelist(self, member = None, player_name = None, recruiter = None):
      if member != None:
        member_mention = member
        recruiter = self.bot.user #przypisuje bota jako rekrutera na start, później jeśli jest to normalnego rekrutera
        if member.guild.me.guild_permissions.view_audit_log:
          async for entry in self.guild.audit_logs(limit=5, action=discord.AuditLogAction.member_role_update):
            if entry.target.id == member.id:
                recruiter = entry.user
                break
        else:
           print(f"bot nie ma uprawnień do logów na serwerze {member.guild.name}")
      else:
        member_mention = self.get_user(player_name)
      try:
          if member_mention != "-":
            or_removed_text = ""
            survey_url = self.survey_url + f"?house={self.house_name}"
            response = requests.get(survey_url, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            for row in data["surveys"]: #przeszukuje całą listę
              discord_id = int(row["discordId"])
              if discord_id == member_mention.id:
                  if row["house"] != self.house_name:
                    return
                  row["house"] = "none"
                  response = requests.post(survey_url, json=row, headers=self.headers)
                  # Sprawdzenie odpowiedzi
                  if response.status_code == 200 or response.status_code == 201: #zamienić aby tylko else było
                      print(f"{member_mention.display_name} został usunięty!")
                      or_removed_text = "It has been successfully removed!!"
                  else:
                      await self.create_embed(0, member_mention, recruiter, error=f"Error when changing form: {response.status_code}, {response.text}")
                      return
                  break

            self.bot.db.del_with_whitelist(member_mention.id)
            await self.create_embed(2, member_mention, recruiter, or_removed=or_removed_text)
          else:
            await self.create_embed(0, member_mention, recruiter, error="No player with that nickname found!")
      except Exception as error:
          await self.create_embed(0, member_mention, recruiter, error=error)

  async def create_embed(self, selection, member, recruiter, error=None, content=None, comment = None, or_removed=None):
    content = content or ""
    embed = discord.Embed(
        description=f"**Player: **{member.mention} ({member.display_name})\n",
        color=self.embed_color
      )
    if selection == 1 or selection == 3: #została dodana ranga 1 to normalne dodanie 3 to szybkie
      creation_date = member.created_at.strftime('%d.%m.%Y %H:%M')
      account_age = self.get_account_age(member.created_at)
      embed.description += "**Add Member**"
      embed.add_field(name="Info",value=f"⏲ Age of account\n```css\n{creation_date}```\n**{account_age}**", inline=True)
      if selection == 3:
         embed.add_field(name="Comment", value=comment, inline=True)
    elif selection == 2: # gracz zostaje usunięty
      bonus_info = "" # dodaje info gdy gracz sam wychodzi z serwera
      if recruiter.id == self.bot.user.id:
         bonus_info = "**Left the server!\n**"
      embed.description += bonus_info + or_removed
      member_roles = member.roles
      member_roles.pop(0)
      embed.add_field(name="Roles (TEST)",value=f"{''.join(role.mention for role in member_roles)}", inline=True)
      embed.color = discord.Color.red()
    elif selection == 0: # wywala error
      content += recruiter.mention
      embed.add_field(name="ERROR", value=error, inline=True)
      embed.color = discord.Color.red()

    image_url = "https://i.imgur.com/AKJKP8a.png"
    if type(member) != str:
        image_url = member.avatar
    embed.set_thumbnail(url=image_url)
    embed.set_author(name=recruiter.display_name, icon_url=recruiter.avatar)
    embed.set_footer(text=f"{self.guild.name} • {datetime.now(self.bot.polish_timezone).strftime('%d.%m.%Y %H:%M')}")

    await self.log_channel.send(content = content,embed=embed)

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

  async def add_quickly(self, player_name, recruiter, comment):
    member_mention = self.get_user(player_name)
    if member_mention == "-":
      await self.create_embed(0, member_mention, recruiter, error="Nie znaleziono gracza o takim nicku!")
      return
    response = requests.get(self.url, headers=self.headers)
    response.raise_for_status() 
    data = response.json()
    found_player = False
    for row in data["whitelist"]: #przeszukuje całą listę
      if "idDiscord" in row:
        if str(member_mention.id) == row["idDiscord"]:
          found_player = True
          await self.create_embed(0, member_mention, recruiter, error="Gracz o takim nicku już jest w bazie!")
          break
    if not found_player:
      data = {
          "idDiscord": str(member_mention.id)
      }
      response = requests.post(self.url, json=data, headers=self.headers)
      response.raise_for_status()
      #dodać sprawdzanie aby nie wywalało mu straej 
      await self.add_player_to_survey(member_mention)
      content = f"Quick recruitment"
      await self.create_embed(3, member_mention, recruiter, content=content, comment=comment)
      
  async def add_player_to_survey(self, player):
      
      survey_url = self.survey_url + f"?house=none"
      response = requests.get(survey_url, headers=self.headers)
      response.raise_for_status()
      data = response.json()

      for row in data["surveys"]: #przeszukuje całą listę
          discord_id = int(row["discordId"])
          if discord_id == player.id:
              row["house"] = self.house_name
              response = requests.post(survey_url, json=row, headers=self.headers)
              if response.status_code == 200 or response.status_code == 201:
                  print(f"{player.display_name} został dodany do rodu {self.house_name}!")
              else:
                  print(f"Błąd podczas wysyłania formularza: {response.status_code}, {response.text}")
              return


      print(f"dodaje {player.display_name}")
      # Definiowanie ilości elementów w tablicach
      num_weapons = 13
      num_low_units = 62
      num_heroic_units = 38
      num_golden_units = 27

      # Tworzenie tablic z odpowiednią ilością elementów
      weapons = [{"value": False, "leadership": 0} for _ in range(num_weapons)]
      low_units = [{"id": index + 1, "value": "0"} for index in range(num_low_units)]
      heroic_units = [{"id": index + 1, "value": "0"} for index in range(num_heroic_units)]
      golden_units = [{"id": index + 1, "value": "0"} for index in range(num_golden_units)]

      form_data = {
          "discordNick": f"{player.display_name}",
          "inGameNick": f"{player.display_name}",
          "discordId": f"{player.id}",
          "characterLevel": "1",
          "artyAmount": "none",
          "house": f"{self.house_name}",
          "weapons": weapons,
          "units": {
              "low": low_units,
              "heroic": heroic_units,
              "golden": golden_units,
          },
      }
      # Wysłanie zapytania POST
      response = requests.post(self.survey_url, json=form_data, headers=self.headers)
      # Sprawdzenie odpowiedzi
      if response.status_code == 200 or response.status_code == 201:
          print(f"{player.display_name} został zapisany pomyślnie!")
      else:
          print(f"Błąd podczas wysyłania formularza: {response.status_code}, {response.text}")

  def get_account_age(self, creation_date):
    now = datetime.now(timezone.utc)
    diff = now - creation_date
    
    years = diff.days // 365
    months = (diff.days % 365) // 30
    days = (diff.days % 365) % 30
    
    if years > 0:
        return f"{years} years, {months} months"
    elif months > 0:
        return f"{months} months, {days} days"
    else:
        return f"{days} days"