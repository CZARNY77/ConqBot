import time


class Pings():
  def __init__(self, bot):
    self.channel = None
    self.bot = bot

    @bot.command(name="ping")
    async def ping(ctx):
        self.ctx = ctx
        self.channel = None
        await self.get_parameters()
        await self.del_msg()
        await self.ping_unchecked()

    @bot.command(name="ping_to_priv")
    async def ping_to_priv(ctx):
        self.ctx = ctx
        self.channel = None
        await self.get_parameters()
        await self.del_msg()
        await self.ping_to_priv()

    @bot.command(name="ping_t")
    async def ping_t(ctx):
        self.ctx = ctx
        self.channel = None
        await self.get_parameters()
        await self.del_msg()
        await self.ping_tentative()

  async def get_parameters(self):
    self.msg =  await self.get_msg()
    self.role = self.get_role()
    self.players_list = await self.get_players_list()
    self.fields = self.msg.embeds[0].fields

  async def ping_unchecked(self):
    if self.players_list is None:
      return
    max_fields = len(self.fields)
    for i in range(2, max_fields):
      players = self.fields[i].value[4:].splitlines()
      if len(players) > 0 and players is not None:
        await self.get_player_name(players)
    await self.create_msg_to_send(self.players_list)

  async def ping_tentative(self):
    if self.players_list is None:
      return
    ping_players = []

    for field in self.fields:
      if "Tentative" in field.name:
        players = field.value[4:].splitlines()
        if len(players) > 0 and players is not None:
          for player in players:
            player = player.replace('\\', '')

            for p_list in self.players_list:
              if player == p_list.display_name:
                  ping_players.append(p_list)
                  break

    await self.create_msg_to_send(ping_players)

  async def ping_to_priv(self):
    if self.players_list is None:
      return
    if self.channel:
      guild = self.channel.guild
    else:
      guild = self.ctx.guild
    #dodać do tabeli channels id z kanałami do list
    presence_channels_text = ""
    presence_channels = self.bot.db.get_specific_value(guild.id, "presence_channels_id")
    for channel in presence_channels:
      presence_channels_text += self.bot.get_channel(int(channel)).mention + "\n"

    max_fields = len(self.fields)
    for i in range(2, max_fields):
      players = self.fields[i].value[4:].splitlines()
      if len(players) > 0 and players is not None:
        await self.get_player_name(players)
    await self.msg_author.send(f"Ilość wiadomości do wysłania {len(self.players_list)}, przywidywany czas {len(self.players_list)*10} sec")
    error_player_list = ""
    error_count = 0
    for player in self.players_list:
      try:
        await player.send(f"**Proszę o nie blokowanie tego bota, bo jak za duzo osób zablokuje może chycić BANA**\nSiemanko, przypominam o oznaczeniu się na bocie, bo tego jeszcze nie zrobiłeś\n{presence_channels_text}")
      except:
        error_count += 1
        error_player_list += f"{player.mention} "
      time.sleep(10)
    await self.msg_author.send(f"Wysyłanie zakończone, wiadomośc nie dotarła do {error_count}: {error_player_list}")

  def get_role(self):
    if self.msg is None:
      return None
    return self.msg.content

  async def get_msg(self):
    if self.channel:
      messages = [message async for message in self.channel.history(limit=30)]
    else:
      messages = [message async for message in self.ctx.channel.history(limit=30)]
    for msg in messages:
      if msg.author.name == 'Apollo' and msg.embeds:
        return msg
    return None

  async def get_players_list(self):
    if self.channel:
      guild = self.channel.guild
    else:
      guild = self.ctx.guild
    players_list = []
    for member in guild.members:
      for role in member.roles:
        if f"<@&{role.id}>" == self.role:
          players_list.append(member)
    if len(players_list) > 0:
      return players_list
    else:
      await self.msg_author.send("Error, Najpewniej została wybrana zła rola, albo nik jej nie posiada")
    return None

  async def get_player_name(self, players):
    for player in players: # lista graczy z bota do oznacza się
      player = player.replace('\\', '')

      for p_list in self.players_list: # sprawdzam czy gracz znajduje się na dc
        if player == p_list.display_name: #jeśli tak to usuwam go, aby go nie pingować
            self.players_list.remove(p_list)
            break
        
  async def create_msg_to_send(self, list):
    if self.channel:
      send_channel = self.channel
    else:
      send_channel = self.ctx.channel
    msg_to_send = ""
    count = 0
    for player in list:
      count += 1
      msg_to_send += f"{player.mention} "
      if count % 50 == 0:
        await send_channel.send(f'{msg_to_send}')
        msg_to_send = ""
    try:
      await send_channel.send(f'{msg_to_send} ({count})')
    except:
      await self.msg_author.send("Nie ma nikogo do pingowania")

  async def del_msg(self):
    async for message in self.ctx.channel.history(limit=1):
      self.msg_author = message.author
      await message.delete()
