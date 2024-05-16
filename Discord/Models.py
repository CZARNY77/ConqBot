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
                      discord.SelectOption(label="Wysłał prośbe/Dodany do rodu bez dc (1 etap)", value=1),
                      discord.SelectOption(label="Przeprowadzona rozmowa rekrutacyjna (2 etap)", value=2),
                      discord.SelectOption(label="Modyfikacja", value=4),
                      discord.SelectOption(label="Powrót do gry", value=5)]
    @discord.ui.select(placeholder = "Sposób Rekcutacji", options=select_options)
    async def select_reset_TW(self, interaction: discord.Interaction, select_item: discord.ui.Select):
        try:
            choice = int(select_item.values[0])
            if choice == 1:
                await interaction.response.send_modal(MyModelAddPlayer_1(interaction, choice))
            elif choice in [2,3,4]:
                await interaction.response.send_modal(MyModelAddPlayer_2(interaction, choice))
            elif choice == 5:
                await interaction.response.send_modal(MyModelAddPlayer_3(interaction, choice))
        except:
            await interaction.response.send_message('Nie masz uprawnień!!', ephemeral=True)


class MyReset(discord.ui.View):
    def __init__(self) -> None:
        super().__init__(timeout = None)

    @discord.ui.button(label="Wyczyść tabele", custom_id="button-3", style=discord.ButtonStyle.primary)
    async def button_reset_TW(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message('wybierz lineup!! (**UWAGA** wybranie odrazu czyści !!!)', ephemeral=True, view=MySelect())

class MySelect(discord.ui.View):
    excel = Excel()
    select_options = excel.get_name_sheet()
    
    @discord.ui.select(placeholder = "Który lineup", options=select_options)
    async def select_reset_TW(self, interaction: discord.Interaction, select_item: discord.ui.Select):
        try:
            await interaction.response.send_message('Czyszczenie...', ephemeral=True)
            excel = Excel(interaction)
            await excel.reset_list_TW(select_item.values[0])
            await interaction.edit_original_response(content='Czyszczenie wykonane!!!')
        except:
            await interaction.response.send_message('coś poszło nie tak!!', ephemeral=True)

class MyModelAddPlayer_1(discord.ui.Modal, title='Formularz'):
    def __init__(self, interaction, choice):
        super().__init__()
        self.interaction = interaction
        self.choice = choice

    name = ui.TextInput(label='Nazwa', placeholder="Rien")
    request = ui.TextInput(label='Czy wysłał zaproszenie do rodu?', placeholder="tak/nie", required=False)
    in_dc = ui.TextInput(label='Czy dołączył na dc?', placeholder="tak/nie", required=False)
    comment = ui.TextInput(label='Komentarz (opcjonalne)', style=discord.TextStyle.long, required=False)
    rekrut = "-"
    in_house = "-"

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message(f'Formularz został wysłany. Na {interaction.guild.get_channel(1100724286139940948).mention} zobacz podsumowanie.', ephemeral=True)
        excel = Excel(self.interaction)
        await excel.add_player_to_excel(self.name, self.choice, self.in_house, self.rekrut, self.comment, self.request, self.in_dc)

class MyModelAddPlayer_2(discord.ui.Modal, title='Formularz'):
    def __init__(self, interaction, choice):
        super().__init__()
        self.interaction = interaction
        self.choice = choice
  
    name = ui.TextInput(label='Nazwa (Pamiętaj najpier zmień nick!)', placeholder="Rien")
    in_house = ui.TextInput(label='Czy w rodzie?', placeholder="1/2/nie", required=False)
    rekrut = ui.TextInput(label='Czy przeszedł rekrutacje?', placeholder="tak/nie", required=False)
    comment = ui.TextInput(label='Komentarz (opcjonalne)', style=discord.TextStyle.long, required=False)
    in_dc = "-"
    request = "-"
  
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message(f'Formularz został wysłany. Na {interaction.guild.get_channel(1100724286139940948).mention} zobacz podsumowanie.', ephemeral=True)
        excel = Excel(self.interaction)
        await excel.add_player_to_excel(self.name, self.choice, self.in_house, self.rekrut, self.comment, self.request, self.in_dc)

class MyModelAddPlayer_3(discord.ui.Modal, title='Formularz'):
    def __init__(self, interaction, choice):
        super().__init__()
        self.interaction = interaction
        self.choice = choice

    name = ui.TextInput(label='Nazwa (Pamiętaj najpier zmień nick!)', placeholder="Rien")
    in_house = ui.TextInput(label='Czy w rodzie?', placeholder="1/2/nie", required=False)
    rekrut = "tak"
    comment = ui.TextInput(label='Komentarz (opcjonalne)', style=discord.TextStyle.long, required=False)
    in_dc = "tak"
    request = "-"

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message(f'Formularz został wysłany. Na {interaction.guild.get_channel(1100724286139940948).mention} zobacz podsumowanie.', ephemeral=True)
        excel = Excel(self.interaction)
        await excel.add_player_to_excel(self.name, self.choice, self.in_house, self.rekrut, self.comment, self.request, self.in_dc)

class MyModelDelPlayer(discord.ui.Modal, title='Formularz'):
    def __init__(self, interaction):
        super().__init__()
        self.interaction = interaction

    name = ui.TextInput(label='Nazwa', placeholder="Rien")
    comment = ui.TextInput(label='Info dlaczego został wywalony (opcjonalne)', style=discord.TextStyle.long, required=False)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message(f'Formularz został wysłany. Na {interaction.guild.get_channel(1100724286139940948).mention} zobacz podsumowanie.', ephemeral=True)
        excel = Excel(self.interaction)
        await excel.del_player_to_excel(self.name, self.comment)