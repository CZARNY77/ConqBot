from discord import app_commands
import discord
from discord.ext import commands
from discord import ChannelType
from datetime import datetime, timezone
from Discord.recruitment import Recruitment
import io
import random
import json
import asyncio

class Others(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.screens_channel = bot.get_channel(1182605597120675850)

        @bot.tree.command(name="warthog")
        @app_commands.describe(member="np. @Krang")
        async def warthog(ctx: discord.Interaction, member: discord.Member):
            await self.warthog(ctx, member)
    
    async def warthog(self, ctx, member):
        if member.id in [373563828513931266, 481981920398540830]:
            await ctx.response.send_message(content=f"Chciałbyś!!!", ephemeral=True)
            await member.send(f"{ctx.user} próbował użyć warthog'a na tobie!")
            member = ctx.user
            await member.send("https://cdn.discordapp.com/attachments/1140638404795695134/114063847723c22a88a969d7d37a330ef10f31645857.gif")
        else:
            await ctx.response.send_message(content="warthog wystarował, wiadomość usunie się utomatycznie po wylądowaniu", ephemeral=True)
        await member.send("✈️✈️✈️ Startujemy ✈️✈️✈️")
        await ctx.delete_original_response()
        for channel in ctx.guild.voice_channels:
            if channel.type == ChannelType.voice:
                temp_channel = self.bot.get_channel(channel.id)
                try:
                    await member.move_to(temp_channel)
                except:
                    await member.send("Nie uciekaj!!!")
                    return
        await member.send("Wylądowaliśmy")

    async def call_to_screen(self, message):
        try:
            if message.content == "<:pepe_telefon:1252356997383327767>":
                screens_list = [msg async for msg in self.screens_channel.history(limit=100)]
                if screens_list:
                    rand = random.randrange(0, len(screens_list))
                    bind = screens_list[rand]
                    if bind.attachments:
                        attachment = bind.attachments[0]
                        file_content = await attachment.read()
                        file = discord.File(io.BytesIO(file_content), filename=attachment.filename)
                        await message.channel.send(file=file)
        except Exception as e:
            print(f"Bindy error:\n{e}")

    async def update_data(self):
        results = self.bot.db.get_results(f"SELECT secretary FROM Others WHERE discord_server_id = %s", (1232957904597024882, ))
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
                        channelList = self.bot.get_channel(1130241398742974546)
                        channelAnime = self.bot.get_channel(950694117711687732)
                        async for msg in channelList.history(limit=100):
                            if msg.content.lower() in str(embed.title).lower():
                                await channelAnime.send(f"{msg.author.mention}")

    async def recruitment_secretary(self, member, after):
        if after.channel and after.channel.id == self.channel_id:
            role = discord.utils.get(member.guild.roles, id=self.role_id)
            if role in member.roles:
                sound_file = "sound/secretary.mp3"
                voice_channel = self.bot.get_channel(self.channel_id)
                if voice_channel and isinstance(voice_channel, discord.VoiceChannel):
                    # Sprawdzenie, czy bot jest już w kanale
                    if not any(member.id == self.bot.user.id for member in voice_channel.members):
                        vc = await voice_channel.connect()
                        print(f"Bot dołączył na kanał rekrutacyjny do: {member.display_name}")

                        # Odtwarzanie dźwięku
                        vc.play(discord.FFmpegPCMAudio(sound_file))

                        # Czekanie na zakończenie odtwarzania
                        while vc.is_playing():
                            await asyncio.sleep(2)
                        
                        # Rozłączanie bota po odtworzeniu dźwięku
                        await vc.disconnect()

    async def sent_on_break(self, before, after):
        # Sprawdzamy, czy użytkownik został wysłany na przerwę
        if before.timed_out_until != after.timed_out_until and after.timed_out_until:
            # Użytkownik został wysłany na przerwę
            time_left = after.timed_out_until - datetime.now(timezone.utc) # obliczaniue ile ma przerwy
            minutes_left = int(time_left.total_seconds() / 60)
            seconds_left = int(time_left.total_seconds() % 60)
            await after.send(f"Masz przerwe na {minutes_left} min {seconds_left} sec.\nhttps://media.discordapp.net/attachments/1105633406764732426/1243121426828099635/BANhammer.gif?ex=6650528c&is=664f010c&hm=c294de1f339a4ca0ad4e73a943e92efe8defaba361330b41c22c8387060f10f5&=")

    async def role_check(self, before, after):
        guild_id = after.guild.id
        basic_roles = self.bot.db.get_specific_value(guild_id, "basic_roles")
        if basic_roles:
            db_role_id = int(basic_roles[0])
            # Sprawdź, czy użytkownik stracił rolę
            if db_role_id and not after.bot:
                db_role_id = int(db_role_id)
                if any(role.id == db_role_id for role in before.roles) and not any(role.id == db_role_id for role in after.roles):
                    print(f"{after.display_name} stracił rolę na serwerze {after.guild.name}")
                    recru_channel_log_id = self.bot.db.get_specific_value(guild_id, "recruiter_logs_id")
                    recruitment = Recruitment(bot=self.bot, log_channel=recru_channel_log_id, member_guild=after.guild)
                    await recruitment.del_player_to_whitelist(before)
                    del recruitment

                # Sprawdź, czy użytkownik dostał rolę
                elif not any(role.id == db_role_id for role in before.roles) and any(role.id == db_role_id for role in after.roles):
                    print(f"{after.display_name} otrzymał rolę na serwerze {after.guild.name}")
                    recru_channel_log_id = self.bot.db.get_specific_value(guild_id, "recruiter_logs_id")
                    recruitment = Recruitment(bot=self.bot, log_channel=recru_channel_log_id, member_guild=after.guild)
                    await recruitment.add_player_to_whitelist(before)
                    del recruitment