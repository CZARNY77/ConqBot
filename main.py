import io
import discord
import datetime
from typing import Any
from datetime import datetime, timezone
from discord.ext import tasks, commands
from Discord.presencePing import Pings
from Discord.presenceTW import Presence
from Discord.list import Lists
from Discord.others import Binds, Others
from Discord.Models import MyView, MyReset
from Discord.groups import CreateGroupsBtn
from Discord.planTW import CreatePlanBtn
from Discord.viewMenu import ViewMenu
from Discord.database_connect import Database
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
        self.wait_msg = False
        self.editing_user = {}
        with open('Discord/Keys/config.json', 'r') as file:
            self.url = json.load(file)["kop_whitelist"]

    async def on_ready(self):
        try:
            #self.add_all_players()
            #self.bridge = Bridge(self)
            #self.decorator = DecoratedView(self)
            #self.add_view(self.decorator)
            self.viewMenu = ViewMenu(self)
            self.add_view(self.viewMenu)
            self.class_initialize()
            await self.tree.sync()
            self.loop_always.start()
            
            #results = self.db.get_results(f"SELECT discord_server_id, alliance_server_id FROM Alliance_Server", ( ))
            #print(results[0][0], results[0][1])
            #await self.presenceTW.get_apollo_list(results[1][0])
            #await self.presenceTW.get_attendance(results[1][0], results[1][1])

            print(f"Bot is Ready. {datetime.now().strftime('%H:%M')}")
        except Exception as e:
            print(f"error {e}")

    async def on_message(self, message):
        await self.process_commands(message)
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

    @tasks.loop(seconds=60)
    async def loop_always(self):
        self.db.keep_alive()

    async def del_msg(self, ctx):
        async for message in ctx.channel.history(limit=1):
            await message.delete()

    def add_all_players(self):
        serwer = self.get_guild(1232957904597024882)
        for member in serwer.members:
            #Sprawdzanie czy taki gracz już istnieje
            response = requests.get(self.url)
            response.raise_for_status() 
            data = response.json()
            found_player = False
            for row in data["whitelist"]: #przeszukuje całą listę
                if str(member.id) == row["idDiscord"]:
                    found_player = True
                    break
            if not found_player and not member.bot:
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
        #self.myReset = MyReset()
        self.presenceTW = Presence(self)
        self.tree.add_command(Lists(self))
        self.tree.add_command(self.binds)
        self.add_view(self.createGroupsBtn)
        self.add_view(self.createPlanBtn)
        self.add_view(self.recruView)

bot = MyBot()
load_dotenv()
bot.run(os.getenv('BOT_TOKEN'))


'''
@tasks.loop(seconds=60)
async def loop_always():
    day = datetime.now().strftime("%A")
    if day == "Tuesday" or day == "Saturday":
        time = datetime.now().strftime("%H:%M")
        if time in ["19:10", "19:50", "18:50"]: 
            print("Lista TW")
            server = bot.get_guild(1100724285246558208)
            sheet = Excel(bot)
            players_list = await sheet.get_name_from_server(server)
            await sheet.connect_with_excel(players_list, "TW")
            del sheet
        if time == "19:30": 
            results = self.db.get_results(f"SELECT alliance_server_id FROM Alliance_Server", ( ))
            for result in results:
                if result[0]:
                    print(result[0])
                    await self.list.initialize(result[0])
        if time == "18:00":
            print("apollo")
            sheet = Excel(bot)
            await sheet.get_apollo_list()
            del sheet

@bot.event
async def on_message(message):
    if message.author.id != 1002261855718342759: #id bota aby sam siebie nie pingował
        global binds
        await bot.process_commands(message)
        await binds.verification_msg(message)
        if message.channel.id == 950694117711687732 and message.author.id != bot.user.id:
            async for msg in message.channel.history(limit=1):
                if msg.content == "@epizodyPL":
                    for embed in msg.embeds:
                        await GetList(embed.title)

@bot.command()
async def list_TW(ctx):
    excel = Excel(bot)
    players_list = await excel.get_name_from_server(ctx.guild)
    await excel.del_msg(ctx)
    await excel.connect_with_excel(players_list, "TW")
    del excel

@bot.command()
async def list_adt(ctx):
    try:
        excel = Excel(bot)
        await excel.get_apollo_list()
        await excel.del_msg(ctx)
        del excel
    except:
        await ctx.send("ups... coś poszło nie tak 'error: get_apollo_list")
    
@bot.command()
async def reset_TW(ctx):
    global myReset
    await ctx.send("Przycisk do czyszczenia tabel na TW, używaj go z głową!!", view=myReset)

async def GetList(animeName):
    channelList = bot.get_channel(1130241398742974546)
    channelAnime = bot.get_channel(950694117711687732)
    async for message in channelList.history(limit=100):
        if message.content == animeName:
            await channelAnime.send(f"<@{message.author.id}> ")
            '''