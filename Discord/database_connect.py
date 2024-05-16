import mysql.connector
import discord
import json


class Database():
  def __init__(self) -> None:
    self.mydb = self.connect_with_db()
    self.cursor = self.mydb.cursor()
    self.edited_field = {}
    self.editing_users = {}
    self.edited_guild = {}
    #przenieś do innej funkcji
    self.conf_field = {
      1:"Link do excela TW",
      2:"Link do ogólnego Excela",
      3:"ID podstawowych ról (podajemy po przecinku)",
      4:"ID roli rekrutera",
      5:"ID ról lineup'ów (podajemy po przecinku)",
      6:"ID roli oficerów (od tej roli w góre)",
      7:"ID głównego kanału",
      8:"ID głównego kanału na logi",
      9:"ID kanału na logi rekruterów",
      10:"ID sojuszowego serwera",
      11:"ID ról na sojuszowym (jako pierwszą role podaj swoją)",
      }

  def connect_with_db(self):#łączy się z bazą danych
    try:
      mydb = mysql.connector.connect(
        host="mysql.host2play.com",
        user="u732_02scVzBLhf",
        password="cWsmFuy=h=AmVW8lYSTcf6f.",
        database="s732_Discord_Servers"
      )
      return mydb
    except Exception as e:
      print(e)

  def get_tables(self): # pobiera wszystkie tabele
    self.cursor.execute("SHOW TABLES")
    tables = self.cursor.fetchall()
    table_names = [table[0] for table in tables]  # Pobieram nazwy tabel
    return table_names
  
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
    #sprawdzenie czy dane id istnieje
    data_to_display = {}
    #pobranie wartości z tabeli Excel_links
    results = self.get_results("SELECT TW_excel, General_excel FROM Excel_Links WHERE discord_server_id = %s", (id, ))
    for i in range(2):
      if results and results[0][i]:
        data_to_display[i+1] = "Podano"
    #pobranie wartości z tabeli Roles
    results = self.get_results("SELECT basic_roles, recruiter_id, lineup_roles, officer_id FROM Roles WHERE discord_server_id = %s", (id, ))
    #print(results)
    for i in range(4):
      if results and results[0][i]:
        data_to_display[i+3] = results[0][i]
        print(results[0][i])
    #pobranie wartości z tabeli channels
    results = self.get_results("SELECT main_id, general_logs_id, recruiter_logs_id FROM Channels WHERE discord_server_id = %s", (id, ))
    #print(results)
    for i in range(3):
      if results and results[0][i]:
        data_to_display[i+7] = results[0][i]
    #pobranie wartości z tabeli Alliance_Server
    results = self.get_results("SELECT alliance_server_id, roles FROM Alliance_Server WHERE discord_server_id = %s", (id, ))
    #print(results)
    for i in range(2):
      if results and results[0][i]:
        data_to_display[i+10] = results[0][i]
    #tworzenie pól 
    for i in range(1, len(self.conf_field)+1):
      embed.add_field(name=f"{i}. {self.conf_field[i]}", value=f"```python\n{data_to_display.get(i, 'Brak')}\n```", inline=False)
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
          await msg.channel.send(f"Podaj **{self.conf_field[i]}**, albo wpisz **cancel** jak chcesz wrócić")
          self.edited_field[player_name] = i
          break

  def Insert_data(self, edited_field, edited_guild, data):
    #spisanie wszytstkich tabel i kolumn do których mają zostać wpisane dane !!!do porpawy!!!
    tables = ["Excel_Links", "Roles", "Channels", "Alliance_Server"]
    columns = [("TW_excel", "General_excel"),
               ("basic_roles", "recruiter_id", "lineup_roles"),
               ("main_id", "general_logs_id", "recruiter_logs_id"),
               ("alliance_server_id", "roles")]

    if edited_field == 1:
      self.send_data(f"INSERT INTO Excel_Links (discord_server_id, TW_excel) VALUES (%s, %s) ON DUPLICATE KEY UPDATE TW_excel = VALUES(TW_excel);""", (edited_guild, data))
    elif edited_field == 2:
      self.send_data(f"INSERT INTO Excel_Links (discord_server_id, General_excel) VALUES (%s, %s) ON DUPLICATE KEY UPDATE General_excel = VALUES(General_excel);", (edited_guild, data))
    elif edited_field == 3:
      data = json.dumps(data.split(","))
      self.send_data(f"INSERT INTO Roles (discord_server_id, basic_roles) VALUES (%s, %s) ON DUPLICATE KEY UPDATE basic_roles = VALUES(basic_roles);", (edited_guild, data))
    elif edited_field == 4:
      self.send_data(f"INSERT INTO Roles (discord_server_id, recruiter_id) VALUES (%s, %s) ON DUPLICATE KEY UPDATE recruiter_id = VALUES(recruiter_id);", (edited_guild, data))
    elif edited_field == 5:
      data = json.dumps(data.split(","))
      self.send_data(f"INSERT INTO Roles (discord_server_id, lineup_roles) VALUES (%s, %s) ON DUPLICATE KEY UPDATE lineup_roles = VALUES(lineup_roles);", (edited_guild, data))
    elif edited_field == 6:
      self.send_data(f"INSERT INTO Roles (discord_server_id, officer_id) VALUES (%s, %s) ON DUPLICATE KEY UPDATE officer_id = VALUES(officer_id);", (edited_guild, data))
    #main_id 	general_logs_id 	recruiter_logs_id
    elif edited_field == 7:
      self.send_data(f"INSERT INTO Channels (discord_server_id, main_id) VALUES (%s, %s) ON DUPLICATE KEY UPDATE main_id = VALUES(main_id);", (edited_guild, data))
    elif edited_field == 8:
      self.send_data(f"INSERT INTO Channels (discord_server_id, general_logs_id) VALUES (%s, %s) ON DUPLICATE KEY UPDATE general_logs_id = VALUES(general_logs_id);", (edited_guild, data))
    elif edited_field == 9:
      self.send_data(f"INSERT INTO Channels (discord_server_id, recruiter_logs_id) VALUES (%s, %s) ON DUPLICATE KEY UPDATE recruiter_logs_id = VALUES(recruiter_logs_id);", (edited_guild, data))
    #roles 	alliance_server_id 
    elif edited_field == 10:
      self.send_data(f"INSERT INTO Alliance_Server (discord_server_id, alliance_server_id) VALUES (%s, %s) ON DUPLICATE KEY UPDATE alliance_server_id = VALUES(alliance_server_id);", (edited_guild, data))
    elif edited_field ==11:
      data = json.dumps(data.split(","))
      self.send_data(f"INSERT INTO Alliance_Server (discord_server_id, roles) VALUES (%s, %s) ON DUPLICATE KEY UPDATE roles = VALUES(roles);", (edited_guild, data))
