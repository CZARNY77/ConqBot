import discord
import datetime
import pytz
from datetime import datetime, timezone
from discord.ext import tasks, commands
from Discord.presencePing import Pings
from Discord.presenceTW import Presence
from Discord.list import Lists
from Discord.others import Binds, Others
from Discord.Models import MyView
from Discord.groups import CreateGroupsBtn
from Discord.planTW import CreatePlanBtn
from Discord.viewMenu import ViewMenu
from Discord.database_connect import Database
from Discord.recruitment import Recruitment
import os
from dotenv import load_dotenv
import asyncio
import requests
import json
from Discord.programming_patterns.Bridge import Bridge
from Discord.programming_patterns.Decorator import DecoratedView


intents = discord.Intents.all()
intents.message_content = True
intents.messages = True
intents.members = True

permissions = discord.Permissions.all()
permissions.read_message_history = True
permissions.manage_messages = True
permissions.manage_roles = True

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(intents=intents, command_prefix='>')
        self.polish_timezone = pytz.timezone('Europe/Warsaw')
        self.wait_msg = False
        self.editing_user = {}
        with open('Discord/Keys/config.json', 'r') as file:
            self.url = json.load(file)["kop_whitelist"]

    async def on_ready(self):
        try:
            '''for member in self.get_guild(1232957904597024882).members:
                role_name = [role.name for role in member.roles if role.id == 1236647699831586838]
                if not member.bot and role_name:
                    print(member.display_name)'''
            #self.bridge = Bridge(self)
            #self.decorator = DecoratedView(self)
            #self.add_view(self.decorator)
            self.class_initialize()
            await self.tree.sync()
            self.loop_always.start()
            #self.db.del_with_whitelist(887377834920788028)
            #await self.presenceTW.get_attendance(1232957904597024882,1232957904597024882)
            #self.db.update_players_on_website(1232957904597024882)
            #self.add_all_players()

            print(f"Bot is Ready. {datetime.now(self.polish_timezone).strftime('%H:%M')}")
        except Exception as e:
            print(f"error {e}")

    async def on_message(self, message):
        await self.process_commands(message)
        await self.time_to_config(message)
        if message.author.id != self.user.id:
            await self.anime_ping(message)
            await self.binds.verification_msg(message)
    
    async def on_guild_join(self, guild):
        self.db.one_server_verification(guild)

    async def on_member_ban(self, guild, user):
        await user.send(f'**Zostałeś zbanowany.**\nhttps://media.discordapp.net/attachments/1105633406764732426/1243121426828099635/BANhammer.gif?ex=6650528c&is=664f010c&hm=c294de1f339a4ca0ad4e73a943e92efe8defaba361330b41c22c8387060f10f5&=')

    async def on_member_unban(self, guild, user):
        await user.send(f'**Dostałeś unbana.**\nhttps://images-ext-1.discordapp.net/external/sVt4pSwpFwOuzSsYsNdn-v1mW4Vpp7gbYpgGydZdUFw/https/media.tenor.com/7QHbdGI_bZEAAAPo/genie-free-me.mp4')

    async def on_member_update(self, before, after):
        # Sprawdzamy, czy użytkownik został wysłany na przerwę
        if before.timed_out_until != after.timed_out_until and after.timed_out_until:
            # Użytkownik został wysłany na przerwę
            time_left = after.timed_out_until - datetime.now(timezone.utc) # obliczaniue ile ma przerwy
            minutes_left = int(time_left.total_seconds() / 60)
            seconds_left = int(time_left.total_seconds() % 60)
            await after.send(f"Masz przerwe na {minutes_left} min {seconds_left} sec.\nhttps://media.discordapp.net/attachments/1105633406764732426/1243121426828099635/BANhammer.gif?ex=6650528c&is=664f010c&hm=c294de1f339a4ca0ad4e73a943e92efe8defaba361330b41c22c8387060f10f5&=")

    async def on_member_remove(self, member):
        if member.guild.id == 1232957904597024882: # do poprawy
            self.db.del_with_whitelist(member.id)

    @tasks.loop(seconds=60)
    async def loop_always(self):
        await self.db.keep_alive()
        await self.TW_day()

    async def TW_day(self):
        day = datetime.now().strftime("%A")
        if day in ["Tuesday", "Saturday"]:
            time = datetime.now(self.polish_timezone).strftime("%H:%M")
            if time in ["20:10", "20:50", "19:50"]: #wysyłą listy obecności
                results = self.db.get_results(f"SELECT discord_server_id, alliance_server_id FROM Alliance_Server", ( ))
                for result in results:
                    print(result, result[0], result[1])
                    if result and result[0] and result[1]:
                        await self.presenceTW.get_attendance(result[0], result[1])
                        if time in ["20:50"]:
                            self.db.update_players_on_website(result[0])
            if time == "20:30": # wysłanie listy na jakiś kanał
                results = self.db.get_results(f"SELECT alliance_server_id FROM Alliance_Server", ( ))
                for result in results:
                    if result and result[0]:
                        await self.list.initialize(result[0])
            if time == "18:00":
                results = self.db.get_results(f"SELECT discord_server_id FROM Alliance_Server", ( ))
                for result in results:
                    if result and result[0]:
                        await self.presenceTW.get_apollo_list(result[0])
                        await self.presenceTW.get_signup(result[0])

    async def del_msg(self, ctx):
        async for message in ctx.channel.history(limit=1):
            await message.delete()

    def add_all_players(self):
        serwer = self.get_guild(1232957904597024882)
        for member in serwer.members:
            role_name = [role.name for role in member.roles if role.id == 1236647699831586838]

            if not member.bot and role_name:
                #Sprawdzanie czy taki gracz już istnieje
                '''try:
                    rekru = Recruitment()
                    rekru.bot = self
                    rekru.add_to_database(member.id, serwer.id)
                    print(f"dodałem: {member.name}")
                except:
                    print(f"{member.name} już jest")'''
                response = requests.get(self.url)
                response.raise_for_status() 
                data = response.json()
                found_player = False
                for row in data["whitelist"]: #przeszukuje całą listę
                    if str(member.id) == row["idDiscord"]:
                        found_player = True
                        break
                if not found_player:
                    print(member.display_name)
                    data = {
                        "idDiscord": str(member.id)
                    }
                    response = requests.post(self.url, json=data)
                    response.raise_for_status()

    def class_initialize(self):
        self.db = Database(self)
        self.db.servers_verification(self.guilds)
        self.createGroupsBtn = CreateGroupsBtn(self)
        self.createPlanBtn = CreatePlanBtn(self)
        self.recruView = MyView(self)
        self.binds = Binds(self)
        self.others = Others(self)
        self.pings = Pings(self)
        self.presenceTW = Presence(self)
        self.list = Lists(self)
        self.viewMenu = ViewMenu(self)
        self.tree.add_command(self.list)
        self.tree.add_command(self.binds)
        self.add_view(self.createGroupsBtn)
        self.add_view(self.createPlanBtn)
        self.add_view(self.recruView)
        self.add_view(self.viewMenu)

    async def time_to_config(self, message):
        if message.author.id != self.user.id and self.wait_msg:
            if isinstance(message.channel, discord.DMChannel):
                try: 
                    await self.db.user_configuration(message)
                    self.wait_msg = True
                    await self.wait_for("message", timeout=60, check=lambda m: m.author == message.author and m.channel == message.channel)
                except asyncio.TimeoutError:
                    await message.channel.send("Przekroczono czasowy limit.")
                    self.wait_msg = False
                    self.db.del_editing_user(self.editing_user[message.author.display_name])
                    del self.editing_user[message.author.display_name]

    async def anime_ping(self, message):
        if message.channel.id == 950694117711687732:
            async for msg in message.channel.history(limit=1):
                if msg.content == "@epizodyPL":
                    for embed in msg.embeds:
                        channelList = bot.get_channel(1130241398742974546)
                        channelAnime = bot.get_channel(950694117711687732)
                        async for msg in channelList.history(limit=100):
                            if msg.content.lower() in str(embed.title).lower():
                                await channelAnime.send(f"{msg.author.mention}")

bot = MyBot()
load_dotenv()
bot.run(os.getenv('BOT_TOKEN'))