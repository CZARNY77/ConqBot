import discord
import datetime
import pytz
import asyncio
from datetime import datetime
from discord.ext import tasks, commands
from Discord.presencePing import Pings
from Discord.presenceTW import Presence
from Discord.list import Lists
from Discord.others import Others
from Discord.groups import CreateGroupsBtn, EditGroupBtn
from Discord.viewMenu import ViewMenu, ViewMenu2
from Discord.viewMenuEng import ViewMenuEng
from Discord.database_connect import Database
from Discord.recruitment import Recruitment
import subprocess
from dotenv import load_dotenv
import os
from aiohttp import web


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
        self.headers = {'discord-key': f"{os.getenv('SITE_KEY')}"}
        self.app = web.Application()
        self.app.router.add_get("/api/attendance/{guild_id:\d+}", self.get_attendance)
        self.app.router.add_get("/api/server_verification", self.server_verification)
        self.app.router.add_post("/api/set_config", self.set_config)

    async def start_server(self):
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, 'localhost', 8080)
        await site.start()

    async def on_ready(self):
        try:
            self.class_initialize()
            await self.others.update_data()
            await self.tree.sync()
            self.loop_always.start()
            await self.start_server()
            print(f"Bot is Ready. {datetime.now(self.polish_timezone).strftime('%H:%M')}")
        except Exception as e:
            print(f"error {e}")

    async def on_message(self, message):
        await self.process_commands(message)
        await self.time_to_config(message)
        if message.author.id != self.user.id:
            await self.others.anime_ping(message)
            await self.others.call_to_screen(message)
    
    async def on_guild_join(self, guild):
        self.db.one_server_verification(guild)

    async def on_member_ban(self, guild, user):
        await user.send(f'**Zostałeś zbanowany.**\nhttps://media.discordapp.net/attachments/1105633406764732426/1243121426828099635/BANhammer.gif?ex=6650528c&is=664f010c&hm=c294de1f339a4ca0ad4e73a943e92efe8defaba361330b41c22c8387060f10f5&=')

    async def on_member_unban(self, guild, user):
        await user.send(f'**Dostałeś unbana.**\nhttps://images-ext-1.discordapp.net/external/sVt4pSwpFwOuzSsYsNdn-v1mW4Vpp7gbYpgGydZdUFw/https/media.tenor.com/7QHbdGI_bZEAAAPo/genie-free-me.mp4')

    async def on_member_update(self, before, after):
        await self.others.sent_on_break(before, after)
        await self.others.role_check(before, after)

    async def on_member_remove(self, member):
        recru_channel_log_id = self.db.get_specific_value(member.guild.id, "recruiter_logs_id")
        recruitment = Recruitment(bot=self, log_channel=recru_channel_log_id, member_guild=member.guild)
        await recruitment.del_player_to_whitelist(member)
        del recruitment
        await recruitment.del_player_to_whitelist(member)
        del recruitment

    async def on_voice_state_update(self, member, before, after):
        await self.others.recruitment_secretary(member, after)

    @tasks.loop(seconds=60)
    async def loop_always(self):
        await self.db.keep_alive()
        await self.TW_day()
        await self.training_day()
        await self.surveys_backup()

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
                        await self.presenceTW.get_attendance(result[0], result[1]) #do poprawy bo daje 3 punkty na jednym TW
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
        self.others = Others(self)
        self.pings = Pings(self)
        self.list = Lists(self)
        self.viewMenu = ViewMenu(self)
        self.viewMenu2 = ViewMenu2(self)
        self.ViewMenuEnd = ViewMenuEng(self)
        self.presenceTW = Presence(self)
        self.tree.add_command(self.list)
        self.add_view(self.createGroupsBtn)
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

    #------------Endpoints----------------

    async def get_attendance(self, request):
        try:
            guild_id = int(request.match_info['guild_id'])
            guild = self.get_guild(guild_id)
            if guild:
                await self.presenceTW.get_list(guild)
                return web.json_response({"status": "complete" })
            else:
                return web.json_response({"status": "error: wrong server id!" })
        except Exception as e:
            return web.json_response({"status": f"failed: {e}"})               
                                
    async def server_verification(self, request):
        #guild_id = int(request.match_info['guild_id'])
        #member_id = int(request.match_info['member_id'])
        guild_id = int(request.query.get('guild_id'))
        member_id = int(request.query.get('member_id'))
        member_role_id = int(request.query.get('member'))
        logs_channel_id = int(request.query.get('logs'))
        attendance_channel_id = int(request.query.get('attendance'))
        tw_server_id = int(request.query.get('tw_server'))
        tw_role_id = int(request.query.get('tw_member'))

        guild = self.get_guild(guild_id)
        if guild:
            member = guild.get_member(member_id)
            if member:
                if member.guild_permissions.administrator:

                    member_role = guild.get_role(member_role_id)
                    if not member_role:
                        return web.json_response({"status": "error: member role with given id not found!" })
                    logs_channel = guild.get_channel_or_thread(logs_channel_id)
                    if not logs_channel:
                        return web.json_response({"status": "error: the logs channel with the specified id was not found!" })
                    attendance_channel = guild.get_channel_or_thread(attendance_channel_id)
                    if not attendance_channel:
                        return web.json_response({"status": "error: no attendance channel with the specified id found!" })
                    tw_server = self.get_guild(tw_server_id)
                    if not tw_server:
                        return web.json_response({"status": "error: no server found on TW!" })
                    if tw_server:
                        tw_role = tw_server.get_role(tw_role_id)
                        if not tw_role:
                            return web.json_response({"status": "error: member role TW not found!" })

                    return web.json_response({"status": "ok" })
                else:
                    return web.json_response({"status": "error: you don't have enough permissions on the server!" })
            else:
                return web.json_response({"status": "error: member not found on server!" })
        else:
            return web.json_response({"status": "error: bad guild id!" })
        
    async def set_config(self, request):
        try:
            print(request)
            print(await request.json())
            return web.json_response({"status": f"jeszcze nic tu nie ma :P"}) 
        except Exception as e:
            return web.json_response({"status": f"failed: {e}"}) 

    async def app_get_roles(self, request):
        try:
            print(request)
            print(await request.json())
            return web.json_response({"status": f"jeszcze nic tu nie ma :P"}) 
        except Exception as e:
            return web.json_response({"status": f"failed: {e}"}) 

bot = MyBot()
subprocess.Popen(['./start_gunicorn.sh'])
load_dotenv()
bot.run(os.getenv('BOT_TOKEN'))