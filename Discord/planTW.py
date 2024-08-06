import discord
from discord.ext import tasks, commands
import io
import os
from PIL import Image, ImageDraw, ImageFont


class ImageTable():
    def __init__(self, bot) -> None:
        @bot.command()
        async def send_table(ctx):
            data = []
            column_names = ["Nick", "Pierwsza Jednostka", "Druga Jednostka", "Trzecia Jednostka", "Broń", "Opis"]

            images = {}
            for i, row in enumerate(data):
                for cell in range(1, len(row)-2):
                    unit = row[cell]
                    path = f"Discord\image/{unit}.png"
                    if os.path.exists(path):
                        images[(i, cell)] = Image.open(path)
                    else:
                        images[(i, cell)] = Image.open("Discord\image/0.png")

            image = self.generate_table_image(data, column_names, images)
            
            with io.BytesIO() as image_binary:
                image.save(image_binary, 'PNG')
                image_binary.seek(0)
                await ctx.send(content=f"**Pierwsza 15**" ,file=discord.File(fp=image_binary, filename='table.png'))
        
    def generate_table_image(self, data, column_names, images=None):
        font_path = "/path/to/your/font/arial.ttf"
        font_size = 52
        font = ImageFont.truetype(font_path, font_size)

        # Ustalenie rozmiaru komórek
        column_widths = [1024] + [1024] * (len(column_names) - 1)
        cell_height = 128  # Zwiększony rozmiar komórki, aby pomieścić obrazki
        padding = 10

        # Obliczenie rozmiaru obrazu
        width = sum(column_widths) + padding * (len(column_names) + 1)
        height = (cell_height + padding) * (len(data)) + padding

        # Tworzenie obrazu
        image = Image.new('RGB', (width, height), color=(2, 6, 23))  # Przezroczyste tło RGBA
        draw = ImageDraw.Draw(image)

        # Rysowanie danych
        for row_num, row in enumerate(data):
            x = padding
            for col_num, cell in enumerate(row):
                col_width = column_widths[col_num]
                y = (row_num) * (cell_height + padding) + padding
                draw.line([(x, y + cell_height), (x + col_width, y + cell_height)], fill=(20, 31, 47), width=5)

                if col_num == 0:  # Pierwsza komórka pierwszego wiersza
                    # Tworzenie gradientu dla pierwszej komórki
                    color_start = (255, 0, 0)    # Czerwony, pełna przezroczystość
                    color_end = (2, 5, 23)        # Niebieski, pełna przezroczystość
                    
                    for gradient_x in range(col_width):
                        color = (
                            int(color_start[0] * (1 - gradient_x / col_width) + color_end[0] * (gradient_x / col_width)),
                            int(color_start[1] * (1 - gradient_x / col_width) + color_end[1] * (gradient_x / col_width)),
                            int(color_start[2] * (1 - gradient_x / col_width) + color_end[2] * (gradient_x / col_width)),
                        )
                        draw.line([(x + gradient_x, y), (x + gradient_x, y + cell_height)], fill=color, width=1)
                        draw.text((x + padding, y + int((cell_height / 2)) - (padding * 2)), str(cell), fill="white", font=font)

                else:
                    #draw.rectangle([x, y, x + col_width, y + cell_height], outline="black", width=1, fill=(255, 255, 255))  # Domyślne tło, przezroczyste
                    if images and images.get((row_num, col_num)):
                        cell_image = images[(row_num, col_num)].resize((cell_height - padding, cell_height - padding))
                        image.paste(cell_image, (x + padding // 2, y + padding // 2))
                        draw.text(((x + padding) + (cell_height + padding), y + int((cell_height / 2)) - (padding * 2)), str(cell), fill="white", font=font)
                    else:
                        draw.text((x + padding, y + int((cell_height / 2)) - (padding * 2)), str(cell), fill="white", font=font)
                x += col_width + padding

        return image















'''import discord

class CreatePlanBtn(discord.ui.View):
    def __init__(self, bot) -> None:
        super().__init__(timeout = None)
        self.plan_view = PlanView()
        bot.add_view(self.plan_view)
        
        @bot.command()
        async def createPlan(ctx):
            await bot.del_msg(ctx)
            await ctx.send(view=self)

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
                new_row += 1'''