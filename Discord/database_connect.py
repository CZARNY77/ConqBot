import mysql.connector
import discord
import json
import asyncio
import requests
import pytz
from datetime import datetime, timezone

class Database():
  def __init__(self, bot) -> None:
    self.polish_timezone = pytz.timezone('Europe/Warsaw')
    self.bot = bot
    self.cursor = None
    self.mydb = self.connect_with_db()
    self.edited_field = {}
    self.editing_users = {}
    self.edited_guild = {}
    with open('Discord/json/menu.json', 'r') as file:
        menu = json.load(file)
    self.conf_field = menu["conf_field"]
    self.conf_field_pl = menu["conf_field"]
    self.conf_field_eng = menu["conf_field_eng"]
    #inaczej połączyć z powyżej
    self.tables = menu["tables"]

    @bot.command()
    async def config(ctx):
      await bot.del_msg(ctx)
      if self.check_role_permissions(ctx.message.author, ctx.guild.id):
          try:
              await self.bot_configuration(ctx.author, ctx.guild.id)
              bot.wait_msg = True
              bot.editing_user[ctx.author.display_name] = ctx.author
              await bot.wait_for("message", timeout=60, check=lambda m: m.author == ctx.author)
          except asyncio.TimeoutError:
              await ctx.author.send("Przekroczono czasowy limit!")
              bot.wait_msg = False
              self.del_editing_user(bot.editing_user[ctx.author.display_name])
              del bot.editing_user[ctx.author.display_name]
      else:
          await ctx.message.author.send("Nie masz uprawnien!")

  def connect_with_db(self):#łączy się z bazą danych
    try:
      with open('Discord/Keys/config.json', 'r') as file:
        config = json.load(file)
      mydb = mysql.connector.connect(
        host=config["host"],
        user=config["user"],
        password=config["password"],
        database=config["database"],
        autocommit=True
      )
      self.cursor = mydb.cursor()
      return mydb
    except Exception as e:
      print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ❌ Error connecting to the database: {str(e)}")
      return None

  async def keep_alive(self):
    try:
        if self.mydb is None or not self.mydb.is_connected():
            print(f"[{datetime.now(self.polish_timezone).strftime('%Y-%m-%d %H:%M:%S')}] 🔄 Reconnecting to the database...")
            if self.cursor:
                self.cursor.close()
            if self.mydb:
                self.mydb.close()
            self.mydb = self.connect_with_db()
            if self.mydb:
                print(f"[{datetime.now(self.polish_timezone).strftime('%Y-%m-%d %H:%M:%S')}] ✅ Reconnected successfully.")
            else:
                print(f"[{datetime.now(self.polish_timezone).strftime('%Y-%m-%d %H:%M:%S')}] ❌ Reconnection failed.")
        else:
            self.mydb.ping(reconnect=True, attempts=3, delay=5)
    except mysql.connector.Error as err:
        print(f"[{datetime.now(self.polish_timezone).strftime('%Y-%m-%d %H:%M:%S')}] ❌ Database Error: {err}")
        try:
            self.mydb.reconnect(attempts=3, delay=5)
            print(f"[{datetime.now(self.polish_timezone).strftime('%Y-%m-%d %H:%M:%S')}] ✅ Reconnected successfully.")
        except mysql.connector.Error as reconnect_err:
            print(f"[{datetime.now(self.polish_timezone).strftime('%Y-%m-%d %H:%M:%S')}] ❌ Error during reconnect: {reconnect_err}")

  def get_tables(self): # pobiera wszystkie tabele
    self.cursor.execute("SHOW TABLES")
    tables = self.cursor.fetchall()
    table_names = [table[0] for table in tables]  # Pobieram nazwy tabel
    return table_names
  
  def get_columns(self, tables):
    tables_and_columns = {}
    for table_name in tables:
      self.cursor.execute(f"SHOW COLUMNS FROM {table_name}")
      columns = self.cursor.fetchall()
      column_details  = [(column[0], column[1]) for column in columns]
      tables_and_columns[table_name] = column_details 
    return tables_and_columns

  def add_new_guild(self, id, nazwa): #dodanie nowego serwera do bazydanych
    sql = "INSERT INTO Discord_Servers (ID, name) VALUES (%s, %s)"
    val = (id, nazwa)
    self.cursor.execute(sql, val)
    self.mydb.commit()
    print("dodałem")
  
  def servers_verification(self, all_servers): #sprawdzanie czy wszyskie serwery są w bazie danych
    self.cursor.execute("SELECT ID FROM Discord_Servers")
    results = self.cursor.fetchall()
    new_all_servers = []
    for server in all_servers:  # jeśli jakiegoś elementu nie ma w bazie to dodaje do nowej tablicy
        if server.id not in (result[0] for result in results):
            new_all_servers.append(server)
    for server in new_all_servers:  # dodanie serwerów których nie ma w bazie
      self.add_new_guild(server.id, server.name)
    
  def one_server_verification(self, server): #sprawdzanie czy serwer nie jest w bazie danych
    self.cursor.execute("SELECT ID FROM Discord_Servers")
    results = self.cursor.fetchall()
    if server.id not in (result[0] for result in results):
      self.add_new_guild(server.id, server.name)

  def get_results(self, sql, val):
    try:
        self.cursor.execute(sql, val)
        return self.cursor.fetchall()
    except mysql.connector.errors.OperationalError as e:
        if "Lost connection to MySQL server" in str(e):
            print("Lost connection to MySQL server. Attempting to reconnect...")
            try:
                self.mydb.reconnect(attempts=3, delay=5)
                self.cursor.execute(sql, val)  # Spróbuj ponownie wykonać zapytanie
                return self.cursor.fetchall()
            except mysql.connector.Error as reconnect_err:
                print(f"Error during reconnect: {reconnect_err}")
                raise reconnect_err
        else:
            raise e

  async def bot_configuration(self, user, id):
    #zapisanie który użytkownik z jakiego dc edytuje można sprówbować stworzyć nową funkcję
    self.editing_users[user.id] = user
    self.edited_guild[user.id] = id

    embed = discord.Embed(color=user.color, title="Co chcesz zmienić")
    data_to_display = {}
    #pobranie wartości z tabeli Excel_links
    tables_and_columns = self.get_columns(self.get_tables())
    #pobieram wszystkie tabele i kolumny z bazy, sprawwdzam czy w danej tabeli nie ma kolumny "discord_server_id", jeśli tak usuwam ją i robie zapytanie
    for table, columns in tables_and_columns.items():
      column_names = [column_name for column_name, _ in columns]
      if "discord_server_id" in column_names:
        column_names.remove("discord_server_id")
        results = self.get_results(f"SELECT {', '.join(column_names)} FROM {table} WHERE discord_server_id = %s", (id, ))
        for i in range(len(column_names)): # mając wynik zapytania zapisuje to do słownika, nazywając klucze od nazw kolumn
          if results and results[0][i]:
            new_result = self.check_type(results[0][i], id, column_names[i])
            #print(new_result)
            data_to_display[column_names[i]] = new_result

    #tworzenie pola embed
    for i in range(1, len(self.conf_field)+1):
      embed.add_field(name=f"{i}. {self.conf_field[i][0]}", value=f"```python\n{data_to_display.get(self.conf_field[i][1], 'Brak')}\n```", inline=False)
    await user.send(embed=embed)

  def send_data(self, sql, val):  #funckja od wysyłanie danych do bazy danych
    self.cursor.execute(sql, val)
    self.mydb.commit()

  async def user_configuration(self, msg):
    player_name =  msg.author.id
    if msg.author.id == self.editing_users[player_name]: #sprawdzenie czy dany użytkownik edytuje, musi wcześniej wywołać komende na serwerze
      #sprawdzenie czy dany gracz nie cofną się do menu
      if msg.content == "cancel" and player_name in self.edited_field:
        del self.edited_field[player_name]
        await self.bot_configuration(self.editing_users[player_name], self.edited_guild[player_name])
        return
      elif player_name in self.edited_field:
        #przekierowanie do funkcji która dodaje do bazy danych i wywołanie menu konfuguracji jeszcze raz
        self.Insert_data(self.edited_field[player_name], self.edited_guild[player_name], msg.content)
        del self.edited_field[player_name]
        await self.bot_configuration(self.editing_users[player_name], self.edited_guild[player_name])
        return
      for i in range(1, len(self.conf_field)+1):
        if msg.content == str(i) and not player_name in self.edited_field:
          await msg.channel.send(f"Podaj **{self.conf_field[i][0]}**, albo wpisz **cancel** jak chcesz wrócić")
          self.edited_field[player_name] = self.conf_field[i][1]
          break

  def Insert_data(self, edited_field, edited_guild, data):
    #pobieram wszystkie tabele, a następnie ich informacje o kolumnach i za pomocą pętli sprawdzam, jeśli jest kolumna jest taka sama jak edited_field to wpisuje
    tables_and_columns = self.get_columns(self.get_tables())
    for table, columns in tables_and_columns.items():
      for name, type in columns:
        if name == edited_field:
          data = data.replace(' ', '')
          if type == "varchar(255)" and name != "house_name": #gdy podajemy więcej niż jedną role konwertujemy na json
            data = json.dumps(data.split(","))
          self.send_data(f"INSERT INTO {table} (discord_server_id, {edited_field}) VALUES (%s, %s) ON DUPLICATE KEY UPDATE {edited_field} = VALUES({edited_field});""", (edited_guild, data))
          break

  def del_editing_user(self, user):
    del self.editing_users[user.id]
    del self.edited_guild[user.id]

  def get_specific_value(self, id, column_name):
    specific_value = self.get_results(f"SELECT {column_name} FROM {self.tables[column_name]} WHERE discord_server_id = %s", (id, ))
    if specific_value and type(specific_value[0][0]) == str:
      try:
        specific_value = json.loads(specific_value[0][0])
        return specific_value
      except:
        return specific_value[0][0]    
    elif specific_value:
      return specific_value[0][0]
    return None

  def check_role_permissions(self, member, id):
    if member.guild_permissions.administrator:
      return True
    service = self.get_results(f"SELECT officer_id FROM Roles WHERE discord_server_id = %s", (id, ))
    for role in member.roles:
      if role.id == service[0][0]:
        return True
    return False
  
  def check_TW_role_permissions(self, member, id):
    if member.guild_permissions.administrator:
      return True
    service = self.get_specific_value(id, "extra_role_id")
    if service:
      for role in member.roles:
        if role.id == int(service[0]):
          return True
      return False
    
  def check_type(self, results, id, column_name): # 
    guild = self.bot.get_guild(id)
    if type(results) == str and column_name not in ["nick", "house_name"]:
      results = json.loads(results)
      results = list(map(int, results))
    if isinstance(results, int):
        try:
          if self.tables[column_name] in ["Roles"]:
            return guild.get_role(results).name
          elif self.tables[column_name] in ["Channels"]:
            return guild.get_channel_or_thread(results).name
          elif column_name in ["alliance_server_id"]:
            return guild.name
          return results
        except:
          return "Nie znaleziono ID"
    elif isinstance(results, list):
        new_result = []
        for i, result in enumerate(results):
          try:
            if self.tables[column_name] in ["Roles"]:
              new_result.append(guild.get_role(result).name)
            elif self.tables[column_name] in ["Channels"]:
              new_result.append(guild.get_channel_or_thread(result).name)
            elif column_name in ["roles"]:
              new_result.append(guild.get_role(result).name)
            elif column_name in ["secretary"]:
                if i == 0:
                    new_result.append(guild.get_channel_or_thread(result).name)
                elif i == 1:
                    new_result.append(guild.get_role(result).name)
          except:
            new_result.append("Nie znaleziono ID")
        return new_result
    else:
        return results
    
  def points(self, points, player_id, type_points):
    try:
      self.send_data(f"UPDATE Players SET {type_points} = {type_points} + %s WHERE id_player = %s", (points, player_id))
    except Exception as e:
      print(f"błąd przy dodawaniu punktów, pewnie nie ma gracza error:\n{e}")

  def update_players_on_website(self, guild_id):
    try:
      with open('Discord/Keys/config.json', 'r') as file:
          url = json.load(file)["kop_users"]
      guild = self.bot.get_guild(guild_id)
      result = self.get_results("SELECT id_player, TW_points, signup_points, recruitment_points, activity_points FROM Players WHERE discord_server_id = %s", (guild_id,))
      TW_role = self.get_specific_value(guild_id, "extra_role_id")
      for player_id, TW_points, signup_points, recruitment_points, activity_points in result:
        player = guild.get_member(player_id)
        if player:
          avatar = ""
          if player.avatar:
            avatar = str(player.avatar.url)
          role_name = [role.name for role in player.roles if role.name != "@everyone" and str(role.id) in TW_role]
          if role_name:
            role_name = role_name[-1]
            data ={
              "idDiscord": str(player_id),   
              "role": role_name,
              "TW_points": TW_points,
              "signup_points": signup_points,
              "recruitment_points": recruitment_points,
              "activity_points": activity_points,
              "image": avatar
            }
            print(data)
            #delete_response  = requests.delete(f"{url}/{data['date']}")
            #delete_response.raise_for_status()

            #response  = requests.post(url, json=data)
            #response.raise_for_status()
            #print("ok")
    except Exception as e:
      print(e)

  def del_with_whitelist(self, member_id):
    with open('/Discord/Keys/config.json', 'r') as file:
      url = json.load(file)["kop_whitelist"]
    full_url = f"{url}/{member_id}"
    print(full_url)
    response = requests.delete(full_url)
    response.raise_for_status()
    print("usunięto gracza")

  def surveys_backup(self):
    try:
      with open('Discord/Keys/config.json', 'r') as file:
        url = json.load(file)["kop_survey"]
      response = requests.get(url)
      response.raise_for_status() 
      data = response.json()
      with open('jsons/surveys_backup.json', 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)
    except:
      print("coś poszło nie tak przy robieniu surveys backup.")