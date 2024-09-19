import discord
from discord.ext import commands
from datetime import datetime
from discord.ui import Button, View

class Event(View):
    def __init__(self, bot, event_name):
        super().__init__(timeout=None)
        self.bot = bot
        self.event_name = event_name
        self.events = {}

        @self.bot.tree.command(name='create_event')
        async def create_event(self, ctx, event_name: str, event_time: str):
            try:
                event_datetime = event_time  # Tu możesz sformatować czas według potrzeb
                self.events[event_name] = {
                    "time": event_datetime,
                    "responses": {}  # Słownik na odpowiedzi użytkowników
                }

                # Tworzymy embeda
                embed = discord.Embed(title=event_name, description=f"Wydarzenie o godzinie: {event_datetime}")
                embed.add_field(name="✅ Accepted 0", value="-", inline=True)
                embed.add_field(name="❌ Declined 0", value="-", inline=True)
                embed.add_field(name="❔ Tentative 0", value="-", inline=True)

                # Tworzymy widok (zestaw przycisków)
                view = self(event_name)

                # Wysyłamy wiadomość z embedem i przyciskami
                await ctx.response.send_message(embed=embed, view=view)
            
            except ValueError:
                await ctx.response.send_message("Proszę podać czas w poprawnym formacie")


    @discord.ui.button(label="✅", style=discord.ButtonStyle.green)
    async def yes(self, interaction: discord.Interaction, button: Button):
        await self.handle_response(interaction, "Accepted")

    @discord.ui.button(label="❌", style=discord.ButtonStyle.red)
    async def no(self, interaction: discord.Interaction, button: Button):
        await self.handle_response(interaction, "Declined")

    @discord.ui.button(label="❔", style=discord.ButtonStyle.gray)
    async def maybe(self, interaction: discord.Interaction, button: Button):
        await self.handle_response(interaction, "Tentative")

    async def handle_response(self, interaction: discord.Interaction, response: str):
        event_details = self.events.get(self.event_name)
        if not event_details:
            await interaction.response.send_message("The event does not exist!", ephemeral=True)
            return

        user_name = interaction.user.name

        # Sprawdzenie, czy użytkownik już wybrał odpowiedź
        if user_name in event_details["responses"]:
            await interaction.response.send_message("You've already chosen the answer!", ephemeral=True)
        else:
            event_details["responses"][user_name] = response
            await interaction.response.send_message(f"You have chosen: {response}", ephemeral=True)
            await self.update_event_embed(interaction, self.event_name)

    async def update_event_embed(self, interaction, event_name):
        #Aktualizacja embeda z listą uczestników.
        event_details = self.events.get(event_name)
        if event_details:
            embed = discord.Embed(title=event_name, description=f"Wydarzenie o godzinie: {event_details['time']}")
            embed.add_field(name="✅ Accepted", value="\n".join([user for user, response in event_details["responses"].items() if response == "Accepted"]) or "-", inline=True)
            embed.add_field(name="❌ Declined", value="\n".join([user for user, response in event_details["responses"].items() if response == "Declined"]) or "-", inline=True)
            embed.add_field(name="❔ Tentative", value="\n".join([user for user, response in event_details["responses"].items() if response == "Tentative"]) or "-", inline=True)
            
            await interaction.message.edit(embed=embed)