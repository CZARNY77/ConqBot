import discord

class CreatePlanBtn(discord.ui.View):
    def __init__(self, bot) -> None:
        super().__init__(timeout = None)
        self.bot = bot
        self.plan_view = PlanView()
        bot.add_view(self.plan_view)
        
    #custom emoji w przyciskach
    newEmoji = discord.PartialEmoji(name="ojej", id=887058401132183623)
    @discord.ui.button(label="Stwórz Plan", custom_id="btn_plan-1", style=discord.ButtonStyle.success, emoji=newEmoji)
    async def button_create_plan(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            for i in range(1,4):
                await interaction.channel.send(view=PlanView(i*5))
            await interaction.response.defer()
            #await interaction.response.send_message(f'Grupa została pomyślnie utworzona.', ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f'Coś poszło nie tak, spróbuj jeszcze raz. Jeśli błąd się powtarza zgłoś to do administracji.\n<{e}>', ephemeral=True)

class PlanView(discord.ui.View):
    def __init__(self, id = None) -> None:
        super().__init__(timeout = None)
        if id is not None:
            new_row = 0
            for i in range(id-4, id+1):
                text_input = discord.ui.Button(custom_id=f"name_text_{i}", label=f"{i}. Nick", disabled=False, style=discord.ButtonStyle.success, row=new_row)
                first_unit = discord.ui.Button(custom_id=f"first_unit_{i}", label="1. Jednostka", disabled=True, style=discord.ButtonStyle.gray, row=new_row)
                second_unit = discord.ui.Button(custom_id=f"second_unit_{i}", label="2. Jednostka", disabled=True, style=discord.ButtonStyle.gray, row=new_row)
                third_unit = discord.ui.Button(custom_id=f"third_unit_{i}", label="3. Jednostka", disabled=True, style=discord.ButtonStyle.gray, row=new_row)
                self.add_item(text_input)
                self.add_item(first_unit)
                self.add_item(second_unit)
                self.add_item(third_unit)
                new_row += 1