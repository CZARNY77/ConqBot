import io
import discord
import datetime
from typing import Any
from datetime import datetime
from discord.ext import tasks, commands
from discord import app_commands, ChannelType
from Discord.presence import Pings
from Discord.excel import Excel
from Discord.list import Lists
from Discord.others import Binds, Others
from Discord.Models import MyView, MyReset
from Discord.groups import CreateGroupsBtn
from Discord.planTW import CreatePlanBtn
from Discord.database_connect import Database
import os
from dotenv import load_dotenv
import asyncio

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
        self.createGroupsBtn = None
        self.createPlanBtn = None
        self.db = None
        self.recruView = None
        self.wait_msg = False
        self.editing_user = {}
        
        @self.command()
        async def config(ctx):
            try:
                await self.db.bot_configuration(ctx.author, ctx.guild.id)
                self.wait_msg = True
                self.editing_user[ctx.author.display_name] = ctx.author
                await self.wait_for("message", timeout=60, check=lambda m: m.author == ctx.author)
            except asyncio.TimeoutError:
                await ctx.author.send("Przekroczono czasowy limit!")
                self.wait_msg = False
                self.db.del_editing_user(self.editing_user[ctx.author.display_name])
                del self.editing_user[ctx.author.display_name]

        @self.command()    
        async def createGroup(ctx):
            await ctx.send(view=self.createGroupsBtn)
        
        @self.command()
        async def createPlan(ctx):
            await ctx.send(view=self.createPlanBtn)
        
        @self.command(name="rekru")
        async def rekrutacja(ctx):
            await ctx.send("Rekrutacja!!", view=self.recruView)

    async def on_ready(self):
        try:
            self.db = Database(self)
            self.db.servers_verification(self.guilds)
            self.createGroupsBtn = CreateGroupsBtn(self)
            self.createPlanBtn = CreatePlanBtn(self)
            self.recruView = MyView()
            self.add_view(self.createGroupsBtn)
            self.add_view(self.createPlanBtn)
            self.add_view(self.recruView)
            self.loop_always.start()
            print("Bot is Ready.")
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

    @tasks.loop(seconds=60)
    async def loop_always(self):
        self.db.keep_alive()


bot = MyBot()
load_dotenv()
bot.run(os.getenv('BOT_TOKEN'))


'''@bot.event
async def on_ready():
    global binds
    global myView
    global myReset
    binds = Binds(bot)
    myView = MyView()
    myReset = MyReset()
    loop_always.start()
    try:
        bot.tree.add_command(Lists(bot))
        bot.tree.add_command(binds)
        bot.add_view(myView)
        bot.add_view(myReset)
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands")
    except Exception as e:
        print(f'error: {e}')
    print("Bot is Ready. " + datetime.now().strftime("%H:%M"))


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
            list = Lists(bot)
            await list.initialize()
            del list
        if time == "18:00":
            print("apollo")
            sheet = Excel(bot)
            await sheet.get_apollo_list()
            del sheet


@bot.tree.command(name="warthog")
@app_commands.describe(member="np. @Krang")
async def warthog(ctx: discord.Interaction, member: discord.Member):
    others = Others(bot)
    await others.warthog(ctx, member)
    del others

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

@bot.command(name="ping")
async def ping(ctx):
    ping = Pings()
    await ping.initialize(ctx)
    await ping.del_msg()
    await ping.ping_unchecked()
    del ping

@bot.command(name="ping_to_priv")
async def ping_to_priv(ctx):
    ping = Pings()
    await ping.initialize(ctx)
    await ping.del_msg()
    await ping.ping_to_priv()
    del ping

@bot.command(name="ping_t")
async def ping_t(ctx):
    ping = Pings()
    await ping.initialize(ctx)
    await ping.del_msg()
    await ping.ping_tentative()
    del ping

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

@bot.command() # przenieść do klasy excel
async def ankieta(ctx):
    try:
        excel = Excel(bot)
        players = await excel.get_all_players()
        players = await excel.get_excel_players(players)
        players = await excel.change_to_text(players)
        await excel.del_msg(ctx)
        list = Lists(bot)
        await list.default_embed(ctx.channel, players)
        del list
        del excel
    except:
        await ctx.send("ups... coś poszło nie tak 'error: ankieta")

@bot.command() # przenieść do klasy excel
async def ankieta_ping(ctx):
    try:
        excel = Excel(bot)
        players = await excel.get_all_players()
        players = await excel.get_excel_players(players)
        await excel.del_msg(ctx)
        msg_to_send = ""
        i = 0
        for player in players:
            i += 1
            msg_to_send += player.mention
            if i >= 90:
                i = 0
                await ctx.channel.send(msg_to_send)
                msg_to_send = ""
                await ctx.channel.send(msg_to_send)
        del excel
    except:
        await ctx.send("ups... coś poszło nie tak 'error: ankieta_ping")
    
@bot.command()
async def rekrutacja(ctx):
    global myView
    await ctx.send("Rekrutacja!!", view=myView)

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