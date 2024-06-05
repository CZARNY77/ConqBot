from discord import app_commands
import discord
from discord.ext import commands
from discord import ChannelType
import io

class Binds(app_commands.Group):
    def __init__(self, bot):
        super().__init__(name="bind")
        self.bot = bot
        self.DiesMeda = bot.get_guild(1100724285246558208)
        self.binds_channel = bot.get_channel(1179153163622813747) # database channel

    async def verification_msg(self, message):
        try:
            async for bind in self.binds_channel.history(limit=100):
                parts = bind.content.splitlines()
                if parts[0].lower() in message.content.lower():
                    if len(parts) >= 2:
                        await message.channel.send(parts[1])
                    elif bind.attachments:
                        attachment = bind.attachments[0]
                        file_content = await attachment.read()
                        file = discord.File(io.BytesIO(file_content), filename=attachment.filename)
                        await message.channel.send(file=file)
                    return
        except Exception as e:
            print(f"Bindy error:\n{e}")
  
    def verification_users(self, ctx):
        return self.bot.db.check_role_permissions(ctx.user, ctx.guild_id)
    
    @app_commands.command(name="_")
    @app_commands.describe(tekst="np. Witam!", link = "jakiś link np. do gifa, obrazka albo tekst")
    async def bind(self, ctx: discord.Interaction, tekst: str, link: str):
        try:
            if self.verification_users(ctx):
                async for message in self.binds_channel.history(limit=100):
                    parts = message.content.splitlines()
                    if tekst in parts[0]:
                        await ctx.response.send_message(content=f"Ten bind {tekst} już istnieje!", ephemeral=True)
                        return
                    await self.binds_channel.send(f"{tekst}\n{link}")
                    await ctx.response.send_message(content=f"Bind dodano", ephemeral=True)
            else:
                await ctx.response.send_message(content=f"Nie masz uprawnień!!", ephemeral=True)
        except:
            await ctx.response.send_message(content=f"Ups.. Coś poszło nie tak", ephemeral=True)
    
    @app_commands.command(name="usun")
    @app_commands.describe(tekst="np. Witam!")
    async def del_bind(self, ctx: discord.Interaction, tekst: str):
        try:
            if self.verification_users(ctx):
                async for message in self.binds_channel.history(limit=100):
                    parts = message.content.splitlines()
                    if parts[0].lower() == tekst.lower():
                        await message.delete()
                        await ctx.response.send_message(content=f"Bind usunięto", ephemeral=True)
                        return
                    await ctx.response.send_message(content=f"Nie znaleziono binda!", ephemeral=True)
            else:  
                await ctx.response.send_message(content=f"Nie masz uprawnień!!", ephemeral=True)
        except:
            await ctx.response.send_message(content=f"Ups.. Coś poszło nie tak", ephemeral=True)
    
    @app_commands.command(name="lista")
    async def bind_list(self, ctx: discord.Interaction):
        embed = discord.Embed(title=f"Lista bindów", color=0x9900FF)
        list = ""
        i = 0
        async for message in self.binds_channel.history(limit=100):
            parts = message.content.splitlines()
            i += 1
            if i >= 50:
                embed.add_field(name="Bindy:", value=list, inline=True)
                list = ""
            list += parts[0] +"\n"
        embed.add_field(name="Bindy:", value=list, inline=True)
        await ctx.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="plikowy")
    @app_commands.describe(tekst="np. Witam!")
    async def bind_file(self, ctx: discord.Interaction, tekst: str):
        try:
            if self.verification_users(ctx):
                async for message in self.binds_channel.history(limit=100):
                    parts = message.content.splitlines()
                    if tekst in parts[0]:
                        await ctx.response.send_message(content=f"Ten bind {tekst} już istnieje!", ephemeral=True)
                        return
                    async for message in ctx.channel.history(limit=2):
                        if message.attachments:
                            attachment = message.attachments[0]
                            file_content = await attachment.read()
                            file = discord.File(io.BytesIO(file_content), filename=attachment.filename)
                            await self.binds_channel.send(content=f'{tekst}', file=file)
                            await ctx.response.send_message(content=f"Bind dodano", ephemeral=True)
                            return    
                    await ctx.response.send_message(content='Nie znaleziono załącznika, upewnij się że załącznik jest w wiadomości wyżej!')
                    return
            else:
                await ctx.response.send_message(content=f"Nie masz uprawnień!!", ephemeral=True)
        except:
            await ctx.response.send_message(content=f"Ups.. Coś poszło nie tak", ephemeral=True)



#-------------------------------------------------------------------------------

class Others(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        @bot.tree.command(name="warthog")
        @app_commands.describe(member="np. @Krang")
        async def warthog(ctx: discord.Interaction, member: discord.Member):
            await self.warthog(ctx, member)
    
    async def warthog(self, ctx, member):
        if member.id == 373563828513931266:
            await ctx.response.send_message(content=f"Chciałbyś!!!", ephemeral=True)
            await member.send(f"{ctx.user} próbowam użyć warthog'a na tobie!")
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