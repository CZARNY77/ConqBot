import discord
from discord import ui
from Discord.recruitment import Recruitment


class MyView(discord.ui.View):
    def __init__(self, bot) -> None:
        super().__init__(timeout = None)

        @bot.command(name="rekru")
        async def rekrutacja(ctx):
            await bot.del_msg(ctx)
            await ctx.send("Rekrutacja!!", view=self)

    @discord.ui.button(label="Dodaj Gracza", custom_id="button-1", style=discord.ButtonStyle.success, emoji="🗂")
    async def button_add_player(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message('Wybierz w jaki sposób przeprowadzasz rekrutacje', ephemeral=True, view=MyRecruSelect())

    @discord.ui.button(label="Usuń Gracza", custom_id="button-2", style=discord.ButtonStyle.danger , emoji="💀")
    async def button_del_player(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.client.db.check_role_permissions(interaction.user, interaction.guild_id):# or interaction.user.id == 373563828513931266:
            await interaction.response.send_modal(MyModelDelPlayer(interaction))
            return
        else:
            await interaction.response.send_message('Nie masz uprawnień!!', ephemeral=True)
            return

class MyRecruSelect(discord.ui.View):
    select_options = [discord.SelectOption(label="Cala rekrutacja", value=3), 
                      discord.SelectOption(label="Wbił na discorda (1 etap)", value=1),
                      discord.SelectOption(label="Przeprowadzona rozmowa rekrutacyjna (2 etap)", value=2)]
    @discord.ui.select(placeholder = "Sposób Rekcutacji", options=select_options)
    async def select_reset_TW(self, interaction: discord.Interaction, select_item: discord.ui.Select):
        try:
            choice = int(select_item.values[0])
            if choice == 1:
                await interaction.response.send_modal(Form1(interaction, choice))
            elif choice in [2,3]:
                await interaction.response.send_modal(Form2(interaction, choice))
        except Exception as e:
            await interaction.response.send_message(f'error: {e}', ephemeral=True)

class FormAddPlayer(ui.Modal):
    def __init__(self, title, interaction, choice=None):
        super().__init__(title=title)
        self.name = ui.TextInput(label='Nazwa (Pamiętaj najpier zmień nick!)', placeholder="Rien")
        self.comment = ui.TextInput(label='Komentarz (opcjonalne)', style=discord.TextStyle.long, required=False)
        self.add_item(self.name)
        self.interaction = interaction
        self.choice = choice
        self.bot = interaction.client
        self.recru_channel_log_id = self.bot.db.get_specific_value(interaction.guild_id, "recruiter_logs_id")

    async def on_submit(self, interaction: discord.Interaction):
        pass

class Form1(FormAddPlayer):
    def __init__(self, interaction, choice):
        super().__init__(title='Formularz', interaction=interaction, choice=choice)
        self.request = ui.TextInput(label='Czy wysłał zaproszenie do rodu?', placeholder="tak/nie", required=False)
        self.add_item(self.request)
        self.add_item(self.comment)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message(f'Formularz został wysłany. Na {interaction.guild.get_channel(self.recru_channel_log_id).mention} zobacz podsumowanie.', ephemeral=True)
        recruitment = Recruitment(self.interaction)
        await recruitment.add_player_to_whitelist(self.name, self.choice, comment=self.comment, request=self.request)
        del recruitment

class Form2(FormAddPlayer):
    def __init__(self, interaction, choice):
        super().__init__(title='Formularz', interaction=interaction, choice=choice)
        self.in_house = ui.TextInput(label='Czy w rodzie?', placeholder="1/2/nie", required=False)
        self.recru_process = ui.TextInput(label='Czy przeszedł rekrutacje?', placeholder="tak/nie", required=False)
        self.add_item(self.in_house)
        self.add_item(self.recru_process)
        self.add_item(self.comment)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message(f'Formularz został wysłany. Na {interaction.guild.get_channel(self.recru_channel_log_id).mention} zobacz podsumowanie.', ephemeral=True)
        recruitment = Recruitment(self.interaction, self.recru_channel_log_id)
        await recruitment.add_player_to_whitelist(self.name, self.choice, in_house=self.in_house, recru_process=self.recru_process, comment=self.comment)
        del recruitment

class MyModelDelPlayer(FormAddPlayer):
    def __init__(self, interaction):
        super().__init__(title='Formularz', interaction=interaction)
        self.add_item(self.comment)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message(f'Formularz został wysłany. Na {interaction.guild.get_channel(self.recru_channel_log_id).mention} zobacz podsumowanie.', ephemeral=True)
        recruitment = Recruitment(self.interaction)
        await recruitment.del_player_to_whitelist(self.name, self.comment)
        del recruitment

class MyReset(discord.ui.View):
    def __init__(self) -> None:
        super().__init__(timeout = None)

    @discord.ui.button(label="Wyczyść tabele", custom_id="button-3", style=discord.ButtonStyle.primary)
    async def button_reset_TW(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message('wybierz lineup!! (**UWAGA** wybranie odrazu czyści !!!)', ephemeral=True, view=MySelect())

class MySelect(discord.ui.View):
    select_options = None
    
    @discord.ui.select(placeholder = "Który lineup", options=select_options)
    async def select_reset_TW(self, interaction: discord.Interaction, select_item: discord.ui.Select):
        try:
            await interaction.response.send_message('Czyszczenie...', ephemeral=True)
            await interaction.edit_original_response(content='Czyszczenie wykonane!!!')
        except:
            await interaction.response.send_message('coś poszło nie tak!!', ephemeral=True)