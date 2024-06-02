import discord
import asyncio

class CreateGroupsBtn(discord.ui.View):
    def __init__(self, bot) -> None:
        super().__init__(timeout = None)
        self.edit_group_btn = EditGroupBtn()
        bot.add_view(self.edit_group_btn)
        
        @bot.command()    
        async def createGroup(ctx):
            await bot.del_msg(ctx)
            await ctx.send(view=self)

    #custom emoji w przyciskach
    newEmoji = discord.PartialEmoji(name="ojej", id=887058401132183623)
    @discord.ui.button(label="Stwórz Grupe", custom_id="btn_group-1", style=discord.ButtonStyle.success, emoji=newEmoji)
    async def button_create_group(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            #sprawdzanie numeru grupy
            groups_count = 1
            async for message in interaction.channel.history(limit=100):
                if message.author == interaction.message.author:
                    if message.embeds:
                        groups_count += 1
            #Tworzenie embed grupy
            player_color = interaction.user.color
            self.embed = discord.Embed(title=f"Grupa {groups_count}", color=player_color)
            self.embed.add_field(name=f"Lista graczy: 1/5", value=f"{interaction.user.mention}", inline=True)
            await interaction.channel.send(embed=self.embed, view=self.edit_group_btn)
            await interaction.response.defer()
            #await interaction.response.send_message(f'Grupa została pomyślnie utworzona.', ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f'Coś poszło nie tak, spróbuj jeszcze raz. Jeśli błąd się powtarza zgłoś to do administracji.\n<{e}>', ephemeral=True)

class EditGroupBtn(discord.ui.View):
    def __init__(self) -> None:
        super().__init__(timeout = None)
        self.user_select = discord.ui.MentionableSelect(custom_id="user_select", placeholder="Wybierz użytkownika", min_values=1, max_values=5, row=1)
        self.add_item(self.user_select)
        self.user_select.callback = self.select_invitation

    @discord.ui.button(label="Dopisz się", custom_id="btn_group-2", style=discord.ButtonStyle.success, emoji="🗂")
    async def button_add_player(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            #Pobranie danych i sprawdzenie ilości graczy
            newEmbed = interaction.message.embeds[0]
            embedFields = newEmbed.fields[0]
            embedValue = embedFields.value
            player_count = embedValue.count("<@")
            #dodawanie gracza do listy
            if player_count < 5:
                #sprawdzanie grazca czy nie jest wpisany
                if interaction.user.mention in embedValue:
                    await interaction.response.send_message(f'Już należysz do tej grupy', ephemeral=True)
                    return
                player_count += 1
                textName = f"Lista graczy: {player_count}/5"
                if player_count == 5:
                    textName += " Completed"
                    #button.disabled = False
                embedValue += f"\n{interaction.user.mention}"
                newEmbed.set_field_at(0, name=textName, value=embedValue)
                await interaction.message.edit(embed=newEmbed)
                await interaction.response.defer() #nie zwaraca żadnego komunikatu
            else:
                await interaction.response.send_message(f'Grupa jest pełna', ephemeral=True)
        except Exception as e:
            print(e)
            await interaction.response.send_message(f'Coś poszło nie tak, spróbuj jeszcze raz. Jeśli błąd się powtarza zgłoś to do administracji.\n<{e}>', ephemeral=True)
    
    @discord.ui.button(label="Wyjdz", custom_id="btn_group-3", style=discord.ButtonStyle.danger , emoji="💀")
    async def button_del_player(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            #Pobranie danych i sprawdzenie ilości graczy
            newEmbed = interaction.message.embeds[0]
            embedFields = newEmbed.fields[0]
            embedValue = embedFields.value
            player_count = embedValue.count("<@")
            #usuwanie gracza z listy
            if interaction.user.mention in embedValue:
                player_count -= 1
                textName = f"Lista graczy: {player_count}/5"
                embedValue = embedValue.replace(interaction.user.mention,"") #usuwam gracza
                embedValue = embedValue.rstrip("\n") #usuwam znak z prawej strony
                newEmbed.set_field_at(0, name=textName, value=embedValue)
                await interaction.message.edit(embed=newEmbed)
                await interaction.response.defer() #nie zwaraca żadnego komunikatu
            else:
                await interaction.response.send_message(f'Nie ma cie w tej grupie', ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f'Coś poszło nie tak, spróbuj jeszcze raz. Jeśli błąd się powtarza zgłoś to do administracji.\n<{e}>', ephemeral=True)
        
    @discord.ui.button(label="Usuń grupe", custom_id="btn_group-4", style=discord.ButtonStyle.danger , emoji="💀")
    async def button_del_group(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            #Pobranie danych i sprawdzenie ilości graczy
            newEmbed = interaction.message.embeds[0]
            embedFields = newEmbed.fields[0]
            embedValue = embedFields.value
            lines = embedValue.splitlines() #pocięcie tekstu na linie
            if len(lines) == 0:
                await interaction.response.defer() #nie zwaraca żadnego komunikatu
                return
            id_Captain = lines[0].strip("<>@ ") # wyodrębnienie na id
            captain = await interaction.guild.fetch_member(id_Captain) # pobranie gracza z id
            if interaction.user == captain: #or jakasRola in interaction.user.roles
                await interaction.response.send_message(f'Grupa usunięta', ephemeral=True)
                await interaction.message.delete()
            else:
                await interaction.response.send_message(f'Nie masz uprawnien do usunięcia grupy', ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f'Coś poszło nie tak, spróbuj jeszcze raz. Jeśli błąd się powtarza zgłoś to do administracji.\n<{e}>', ephemeral=True)

    async def select_invitation(self, interaction: discord.Interaction):
        try:
            select_players = interaction.data["values"]  # Pobranie wybranych użytkowników
            
            #Pobranie danych i sprawdzenie ilości graczy
            newEmbed = interaction.message.embeds[0]
            embedFields = newEmbed.fields[0]
            embedValue = embedFields.value
            players_in_group = embedValue.splitlines()
            player_count = embedValue.count("<@")
            ping_msg = ""
            #usuwanie gracza z listy jeżeli już jest w grupie
            for select_player in select_players:
                print(f'<@{select_player}>' , players_in_group)
                if f'<@{select_player}>' in players_in_group:
                    select_players.remove(select_player)
                    continue
                player = await interaction.guild.fetch_member(select_player)
                if player_count < 5: #dodanie gracza
                    player_count += 1
                    textName = f"Lista graczy: {player_count}/5"
                    if player_count == 5:
                        textName += " Completed"
                    embedValue += f"\n{player.mention}"
                    ping_msg += player.mention
                    newEmbed.set_field_at(0, name=textName, value=embedValue)
                else:
                    await interaction.response.send_message(f'{player.mention} brakło miejsca w grupie', ephemeral=True)
            await interaction.message.edit(embed=newEmbed)
            msg = await interaction.channel.send(ping_msg)
            await asyncio.sleep(1)
            await msg.delete()
            await interaction.response.defer()
        except Exception as e:
            await interaction.response.send_message(f'Coś poszło nie tak, spróbuj jeszcze raz. Jeśli błąd się powtarza zgłoś to do administracji.\n<{e}>', ephemeral=True)

