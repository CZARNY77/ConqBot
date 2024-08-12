import discord
import datetime
import pytz
import io
import asyncio
from datetime import datetime, timezone
from discord.ext import tasks, commands
from Discord.presencePing import Pings
from Discord.presenceTW import Presence
from Discord.list import Lists
from Discord.others import Binds, Others
from Discord.Models import MyView
from Discord.groups import CreateGroupsBtn, EditGroupBtn
from Discord.viewMenu import ViewMenu, ViewMenu2
from Discord.viewMenuEng import ViewMenuEng
from Discord.database_connect import Database
import subprocess
from dotenv import load_dotenv
import os
import json


intents = discord.Intents.all()
intents.message_content = True
intents.messages = True
intents.members = True
intents.voice_states = True

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

    async def on_ready(self):
        try:
            self.class_initialize()
            await self.update_data()
            await self.tree.sync()
            self.loop_always.start()
            print(f"Bot is Ready. {datetime.now(self.polish_timezone).strftime('%H:%M')}")
        except Exception as e:
            print(f"error {e}")

    async def on_message(self, message):
        await self.process_commands(message)
        await self.time_to_config(message)
        await self.szpieg(message)
        if message.author.id != self.user.id:
            await self.anime_ping(message)
            #await self.binds.verification_msg(message)
            await self.binds.call_to_screen(message)
    
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
        if member.guild.id in [1232957904597024882, 1105196730414272562]: # do poprawy
            self.db.del_with_whitelist(member.id)
    
    @tasks.loop(seconds=60)
    async def loop_always(self):
        await self.db.keep_alive()
        await self.TW_day()
        await self.training_day()

    async def surveys_backup(self):
        time = datetime.now(self.polish_timezone).strftime("%H:%M")
        if time in ["00:00"]:
            self.db.surveys_backup()

    async def TW_day(self):
        day = datetime.now().strftime("%A")
        if day == "Tuesday" or day == "Saturday":
            time = datetime.now(self.polish_timezone).strftime("%H:%M")
            if time in ["20:10", "20:50", "19:50"]: #wysyła listy obecności
                results = self.db.get_results(f"SELECT discord_server_id, alliance_server_id FROM Alliance_Server", ( ))
                for result in results:
                    if result and result[0] and result[1]:
                        await self.presenceTW.get_attendance(result[0], result[1])
                        if time in ["20:50"]:
                            self.db.update_players_on_website(result[0]) 
            if time == "20:30": # wysłanie listy na jakiś kanał
                print("lista obecności")
                results = self.db.get_results(f"SELECT alliance_server_id FROM Alliance_Server", ( ))
                for result in results:
                    if result and result[0]:
                        await self.list.initialize(result[0])
            if time == "19:00":
                results = self.db.get_results(f"SELECT discord_server_id FROM Alliance_Server", ( ))
                for result in results:
                    if result and result[0]:
                        await self.presenceTW.get_signup(result[0])

    async def training_day(self):
        day = datetime.now().strftime("%A")
        if day in ["Monday"]:
            time = datetime.now(self.polish_timezone).strftime("%H:%M")
            if time in ["20:00"]:
                results = self.db.get_results(f"SELECT discord_server_id, training_channel_id FROM Channels", ( ))
                for result in results:
                    if result and result[0] and result[1]:
                        channel = self.get_guild(result[0]).get_channel(result[1])
                        if channel:
                            await self.createGroupsBtn.clear_history(channel)
                        else:
                            print("Nie znaleziono kanału od treningu")
                        
    async def del_msg(self, ctx):
        async for message in ctx.channel.history(limit=1):
            await message.delete()

    def class_initialize(self):
        self.db = Database(self)
        self.db.servers_verification(self.guilds)
        self.createGroupsBtn = CreateGroupsBtn(self)
        self.recruView = MyView(self)
        self.binds = Binds(self)
        self.others = Others(self)
        self.pings = Pings(self)
        self.list = Lists(self)
        self.viewMenu = ViewMenu(self)
        self.viewMenu2 = ViewMenu2(self)
        self.ViewMenuEnd = ViewMenuEng(self)
        self.presenceTW = Presence(self)
        self.tree.add_command(self.list)
        self.tree.add_command(self.binds)
        self.add_view(self.createGroupsBtn)
        self.add_view(self.recruView)
        self.add_view(self.viewMenu)
        self.add_view(self.viewMenu2)
        self.add_view(self.ViewMenuEnd)
        self.add_view(EditGroupBtn())

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
                    self.db.del_editing_user(self.editing_user[message.author.id])
                    del self.editing_user[message.author.id]

    async def on_voice_state_update(self, member, before, after):
        if after.channel and after.channel.id == self.channel_id:
            role = discord.utils.get(member.guild.roles, id=self.role_id)
            if role in member.roles:
                sound_file = "sound/secretary.mp3"
                voice_channel = self.get_channel(self.channel_id)
                if voice_channel and isinstance(voice_channel, discord.VoiceChannel):
                    # Sprawdzenie, czy bot jest już w kanale
                    if not any(member.id == self.user.id for member in voice_channel.members):
                        vc = await voice_channel.connect()
                        print(f"Bot dołączył na kanał rekrutacyjny do: {member.display_name}")

                        # Odtwarzanie dźwięku
                        vc.play(discord.FFmpegPCMAudio(sound_file))

                        # Czekanie na zakończenie odtwarzania
                        while vc.is_playing():
                            await asyncio.sleep(2)
                        
                        # Rozłączanie bota po odtworzeniu dźwięku
                        await vc.disconnect()
                    
    async def update_data(self):
        results = self.db.get_results(f"SELECT secretary FROM Others WHERE discord_server_id = %s", (1232957904597024882, ))
        results = results[0][0]
        if results and type(results) == str:
            results = json.loads(results)
        if len(results) < 2:
            return
        self.channel_id = int(results[0])
        self.role_id = int(results[1])
                    
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
subprocess.Popen(['./start_gunicorn.sh'])
load_dotenv()
bot.run(os.getenv('BOT_TOKEN'))