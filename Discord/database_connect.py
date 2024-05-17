import mysql.connector
import discord
import json


class Database():
  def __init__(self, bot) -> None:
    self.mydb = self.connect_with_db()
    self.cursor = self.mydb.cursor()
    self.bot = bot
    self.edited_field = {}
    self.editing_users = {}
    self.edited_guild = {}
    #przenieś do json
    self.conf_field = {
      1:("Link do excela TW", "TW_excel"),
      2:("Link do ogólnego Excela", "General_excel"),
      3:("ID podstawowych ról (podajemy po przecinku)", "basic_roles"),
      4:("ID roli rekrutera", "recruiter_id"),
      5:("ID ról lineup'ów (podajemy po przecinku)", "lineup_roles"),
      6:("ID roli oficerów (od tej roli w góre)", "officer_id"),
      7:("ID głównego kanału", "main_id"),
      8:("ID głównego kanału na logi", "general_logs_id"),
      9:("ID kanału na logi rekruterów", "recruiter_logs_id"),
      10:("ID sojuszowego serwera", "alliance_server_id"),
      11:("ID ról na sojuszowym (jako pierwszą role podaj swoją)", "roles"),
      }

  def connect_with_db(self):#łączy się z bazą danych
    try:
      with open('Discord/Keys/id_list.json', 'r') as file:
        id_list = json.load(file)
      mydb = mysql.connector.connect(
        host=id_list["host"],
        user=id_list["user"],
        password=id_list["password"],
        database=id_list["database"]
      )
      return mydb
    except Exception as e:
      print(e)

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
    if server.id not in results:
      self.add_new_guild(server.id, server.name)

  def get_results(self, sql, val):
    self.cursor.execute(sql, val)
    results = self.cursor.fetchall()
    return results

  async def bot_configuration(self, user, id):
    #zapisanie który użytkownik z jakiego dc edytuje można sprówbować stworzyć nową funkcję
    self.editing_users[user.display_name] = user
    self.edited_guild[user.display_name] = id

    embed = discord.Embed(color=user.color, title="Co chcesz zmienić")
    data_to_display = {}
    #pobranie wartości z tabeli Excel_links
    tables_and_columns = self.get_columns(self.get_tables())
    
    for table, columns in tables_and_columns.items():
      column_names = [column_name for column_name, column_type in columns]
      if "discord_server_id" in column_names:
        column_names.remove("discord_server_id")
        results = self.get_results(f"SELECT {', '.join(column_names)} FROM {table} WHERE discord_server_id = %s", (id, ))
        for i in range(len(column_names)):
          if results and results[0][i]:
            data_to_display[column_names[i]] = results[0][i]

    #tworzenie pól 
    for i in range(1, len(self.conf_field)+1):
      embed.add_field(name=f"{i}. {self.conf_field[i][0]}", value=f"```python\n{data_to_display.get(self.conf_field[i][1], 'Brak')}\n```", inline=False)
    await user.send(embed=embed)

  def send_data(self, sql, val):  #funckja od wysyłanie danych do bazy danych
    self.cursor.execute(sql, val)
    self.mydb.commit()

  async def user_configuration(self, msg):
    player_name =  msg.author.display_name
    if msg.author == self.editing_users[player_name]: #sprawdzenie czy dany użytkownik edytuje, musi wcześniej wywołać komende na serwerze
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
          if type == "varchar(255)": #gdy podajemy więcej niż jedną role konwertujemy na json
            data = json.dumps(data.split(","))
          self.send_data(f"INSERT INTO {table} (discord_server_id, {edited_field}) VALUES (%s, %s) ON DUPLICATE KEY UPDATE {edited_field} = VALUES({edited_field});""", (edited_guild, data))
          break