import discord
from discord import ui
from Discord.rekru_excel import Excel


class MyView(discord.ui.View):
    def __init__(self) -> None:
        super().__init__(timeout = None)

    @discord.ui.button(label="Dodaj Gracza", custom_id="button-1", style=discord.ButtonStyle.success, emoji="🗂")
    async def button_add_player(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message('Wybierz w jaki sposób przeprowadzasz rekrutacje', ephemeral=True, view=MyRecruSelect())

    @discord.ui.button(label="Usuń Gracza", custom_id="button-2", style=discord.ButtonStyle.danger , emoji="💀")
    async def button_del_player(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id == 373563828513931266:
            await interaction.response.send_modal(MyModelDelPlayer(interaction))
            return
        for role in interaction.user.roles:
            if role.id in [1100724285305274439, 1100724285305274441, 1100724285305274440]:
                await interaction.response.send_modal(MyModelDelPlayer(interaction))
                return
        await interaction.response.send_message('Nie masz uprawnień!!', ephemeral=True)
        return

class MyRecruSelect(discord.ui.View):
    excel = Excel()
    select_options = [discord.SelectOption(label="Cala rekrutacja", value=3), 
                      discord.SelectOption(label="Wbił na discorda (1 etap)", value=1),
                      discord.SelectOption(label="Przeprowadzona rozmowa rekrutacyjna (2 etap)", value=2),
                      discord.SelectOption(label="Modyfikacja", value=4)]
    @discord.ui.select(placeholder = "Sposób Rekcutacji", options=select_options)
    async def select_reset_TW(self, interaction: discord.Interaction, select_item: discord.ui.Select):
        try:
            choice = int(select_item.values[0])
            if choice == 1:
                await interaction.response.send_modal(Form1(interaction, choice))
            elif choice in [2,3,4]:
                await interaction.response.send_modal(Form2(interaction, choice))
        except Exception as e:
            await interaction.response.send_message(f'error: {e}', ephemeral=True)

class FormAddPlayer(ui.Modal):
    def __init__(self, title, interaction, choice):
        super().__init__(title=title)
        self.name = ui.TextInput(label='Nazwa (Pamiętaj najpier zmień nick!)', placeholder="Rien")
        self.comment = ui.TextInput(label='Komentarz (opcjonalne)', style=discord.TextStyle.long, required=False)
        self.add_item(self.name)
        self.add_item(self.comment)
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

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message(f'Formularz został wysłany. Na {interaction.guild.get_channel(self.recru_channel_log_id).mention} zobacz podsumowanie.', ephemeral=True)
        excel = Excel(self.interaction)
        await excel.add_player_to_excel(self.name, self.choice, comment=self.comment, request=self.request)
        del excel

class Form2(FormAddPlayer):
    def __init__(self, interaction, choice):
        super().__init__(title='Formularz', interaction=interaction, choice=choice)
        self.in_house = ui.TextInput(label='Czy w rodzie?', placeholder="1/2/nie", required=False)
        self.recru_process = ui.TextInput(label='Czy przeszedł rekrutacje?', placeholder="tak/nie", required=False)
        self.add_item(self.in_house)
        self.add_item(self.recru_process)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message(f'Formularz został wysłany. Na {interaction.guild.get_channel(self.recru_channel_log_id).mention} zobacz podsumowanie.', ephemeral=True)
        excel = Excel(self.interaction, self.recru_channel_log_id)
        await excel.add_player_to_excel(self.name, self.choice, in_house=self.in_house, recru_process=self.recru_process, comment=self.comment)
        del excel

class MyModelDelPlayer(FormAddPlayer):
    def __init__(self, interaction, choice):
        super().__init__(title='Formularz', interaction=interaction, choice=choice)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message(f'Formularz został wysłany. Na {interaction.guild.get_channel(self.recru_channel_log_id).mention} zobacz podsumowanie.', ephemeral=True)
        excel = Excel(self.interaction)
        await excel.del_player_to_excel(self.name, self.comment)
        del excel

class MyReset(discord.ui.View):
    def __init__(self) -> None:
        super().__init__(timeout = None)

    @discord.ui.button(label="Wyczyść tabele", custom_id="button-3", style=discord.ButtonStyle.primary)
    async def button_reset_TW(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message('wybierz lineup!! (**UWAGA** wybranie odrazu czyści !!!)', ephemeral=True, view=MySelect())

class MySelect(discord.ui.View):
    excel = Excel()
    select_options = None
    
    @discord.ui.select(placeholder = "Który lineup", options=select_options)
    async def select_reset_TW(self, interaction: discord.Interaction, select_item: discord.ui.Select):
        try:
            await interaction.response.send_message('Czyszczenie...', ephemeral=True)
            excel = Excel(interaction)
            await excel.reset_list_TW(select_item.values[0])
            await interaction.edit_original_response(content='Czyszczenie wykonane!!!')
        except:
            await interaction.response.send_message('coś poszło nie tak!!', ephemeral=True)