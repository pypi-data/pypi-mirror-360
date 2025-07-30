import json
import pprint
import random
import time

import pyfiglet
from json_repair import json_repair
from rich import box
from rich.color import Color
from rich.console import Console
from rich.console import Group
from rich.json import JSON as RichJSON
from rich.live import Live
from rich.panel import Panel
from rich.rule import Rule
from rich.text import Text
from rich.tree import Tree
from rich.align import Align

from r00logger import log


# def print_vs_text(text1, text2, title=''):
#     console = Console()
#     content = Group(
#         Text(text1, justify="center", style="#b89e60"),
#         Rule(style="bold red"),
#         Text(text2, justify="center", style="#68d61f")
#     )
#     if not title:
#         console.print(Panel(content, expand=False, border_style="#988ba3", padding=(0, 2)))
#     else:
#         console.print(Panel(content, expand=False, border_style="#988ba3", padding=(0, 2), title=title))


def print_vs_text(text1, text2, title=''):
    console = Console()
    content_line = Text.assemble(
        (text1, "#b89e60"),
        (" vs ", "bold red"),  # Стилизуем сам разделитель "vs"
        (text2, "#68d61f")
    )
    content = Align.center(content_line)
    if not title:
        console.print(Panel(content, expand=False, border_style="#988ba3", padding=(0, 2)))
    else:
        console.print(Panel(content, expand=False, border_style="#988ba3", padding=(0, 2), title=title))


def print_tree():
    console = Console()
    tree = Tree(f"[bold red]Корневой элемент: [green]111[/green][/bold red]")
    tree.add("[italic yellow]Первый подпункт[/italic yellow]")
    tree.add("[italic cyan]Второй подпункт[/italic cyan]").add("Вложенный пункт 1").add("Вложенный пункт 2")
    tree.add('xxxxx')
    console.print(tree)


def print_nice(text, variant=1, title='', type='normal'):
    """
    Выводит строку 'text' в консоль, используя различные стили Rich.

    :param text: Строка для вывода.
    :param variant: Вариант оформления [1,2,3,4]
    :param title: title для variant 2, 4
    :param type: Тип сообщения: normal, error
    """
    console = Console()

    if variant == 1:
        if type == 'error':
            color = '#ee65be'
        else:
            color = 'magenta'
        console.print(Rule(style="dim grey"))
        styled_text = Text(text, justify="center", style=f"bold {color}")
        console.print(styled_text)
        console.print(Rule(style="dim grey"))

    elif variant == 2:
        if type == 'error':
            color = '#ee65be'
        else:
            color = '#71d156'
        styled_text = Text(text, justify="center", style=color)
        if title:
            console.print(Panel(styled_text, expand=False, padding=(0, 2), title=title))
        else:
            console.print(Panel(styled_text, expand=False, padding=(0, 2)))

    elif variant == 3:
        styled_text = Text(text, justify="left", style="#f3cb00 on #005979")
        console.print(styled_text)

    elif variant == 4:
        if type == 'error':
            color = '#ee65be'
        else:
            color = '#e7e13a'
        styled_text = Text(text.upper(), justify="center", style=color)
        styled_title_text = f"[bold {color}] {title} [/bold {color}]"
        if not title:
            console.print(Panel(styled_text, expand=False, padding=(1, 4), border_style=color, box=box.DOUBLE_EDGE))
        else:
            console.print(Panel(styled_text, expand=False, padding=(1, 4), border_style=color, box=box.DOUBLE_EDGE, title=styled_title_text))



def print_fullscreen(text: str, timeout: float = 5.0, figlet_font: str = "big"):
    """
    Отображает сообщение в виде ASCII-арта pyfiglet на фоне анимированного салюта,
            занимающего весь экран терминала.

            :param text: Сообщение (строка), которое будет преобразовано в Figlet-арт.
                         Может быть многострочным (использовать '\n').
            :param timeout: Общая продолжительность анимации в секундах.
            :param figlet_font: Название шрифта PyFiglet для генерации ASCII-арта.
                                 Примеры популярных шрифтов:
                                 - "standard" (по умолчанию, если не указано)
                                 - "big" (большой, заметный)
                                 - "slant" (наклонный)
                                 - "chunky" (толстый)
                                 - "banner" (очень большой)
                                 - "univers" (более строгий)
                                 Полный список доступных шрифтов можно получить,
                                 выполнив в терминале `pyfiglet -l`.
    """
    try:
        speed = 25
        message_style = "bold bright_green reverse on_black"
        text = text.upper()
        console = Console()
        firework_colors = [
            Color.parse("red"), Color.parse("yellow"), Color.parse("green"),
            Color.parse("blue"), Color.parse("magenta"), Color.parse("cyan"),
            Color.parse("bright_white"),
            Color.from_rgb(255, 165, 0),  # Orange (RGB)
            Color.from_rgb(255, 192, 203),  # Pink
            Color.from_rgb(128, 0, 128)  # Purple
        ]
        spark_chars = ['*', '.', 'o', '+', '•', '✨']
        width, height = console.width, console.height
        particles = []

        def generate_particle():
            x = random.randint(0, width - 1)
            y = random.randint(0, height // 3)
            dx = random.uniform(-0.8, 0.8)
            dy = random.uniform(0.5, 1.5)
            lifetime = 0
            max_lifetime = random.randint(20, 50)
            color_idx = random.randint(0, len(firework_colors) - 1)
            return [x, y, dx, dy, lifetime, max_lifetime, color_idx]

        for _ in range(50):
            particles.append(generate_particle())

        figlet_text_raw = pyfiglet.figlet_format(text, font=figlet_font)
        figlet_lines_base = figlet_text_raw.splitlines()

        rich_figlet_lines = []
        for line_text in figlet_lines_base:
            rich_line = Text(line_text, style=message_style)
            rich_line.align("center", width=width, character=' ')
            rich_figlet_lines.append(rich_line)

        message_height = len(rich_figlet_lines)
        message_start_y = (height - message_height) // 2

        with Live(console=console, screen=True, auto_refresh=False, transient=True) as live:
            start_time = time.time()

            while time.time() - start_time < timeout:
                screen_buffer = [[" " for _ in range(width)] for _ in range(height)]

                new_particles = []
                for p in particles:
                    p[0] += p[2]
                    p[1] += p[3]
                    p[3] += 0.05
                    p[4] += 1

                    if p[4] < p[5] and 0 <= int(p[0]) < width and 0 <= int(p[1]) < height:
                        new_particles.append(p)
                        px, py = int(p[0]), int(p[1])
                        if 0 <= px < width and 0 <= py < height:
                            color = firework_colors[p[6]]
                            char_index = min(len(spark_chars) - 1, p[4] // 5)
                            screen_buffer[py][px] = Text(spark_chars[char_index], style=f"bold {color.name}")

                particles = new_particles

                if random.random() < 0.2:
                    for _ in range(random.randint(10, 30)):
                        particles.append(generate_particle())

                for i, rich_figlet_line in enumerate(rich_figlet_lines):
                    current_y = message_start_y + i
                    if 0 <= current_y < height:
                        current_x = 0
                        for segment in rich_figlet_line.render(console):
                            for char in segment.text:
                                if current_x < width:
                                    screen_buffer[current_y][current_x] = Text(char, style=segment.style)
                                    current_x += 1
                                else:
                                    break

                rendered_frame = Text()
                for row in screen_buffer:
                    for char_cell in row:
                        if isinstance(char_cell, Text):
                            rendered_frame.append_text(char_cell)
                        else:
                            rendered_frame.append(char_cell)
                    # Важно не добавлять \n здесь, если хотим управлять выводом по одной строке
                    # Но для полноэкранного буфера это нормально
                    rendered_frame.append("\n")

                live.update(rendered_frame)
                live.refresh()
                time.sleep(1 / speed)

        print_animated(text.replace('\n', ' '), frames=25)
    except:
        log.info(text)


def print_animated(message: str, frames: int = 100):
    try:
        message = '  ' + message
        console = Console()
        colors = [
            Color.parse("white"),
            Color.from_rgb(255, 255, 200),  # Light Yellow
            Color.from_rgb(255, 255, 150),
            Color.from_rgb(255, 255, 100),
            Color.parse("yellow"),
            Color.from_rgb(200, 255, 100),  # Yellow-Green
            Color.from_rgb(150, 255, 100),
            Color.parse("green"),
            Color.from_rgb(100, 255, 150),  # Green-Cyan
            Color.from_rgb(100, 255, 200),
            Color.parse("cyan"),
            Color.from_rgb(100, 200, 255),  # Cyan-Blue
            Color.from_rgb(100, 150, 255),
            Color.parse("blue"),
            Color.from_rgb(150, 100, 255),  # Blue-Magenta
            Color.from_rgb(200, 100, 255),
            Color.parse("magenta"),
            Color.from_rgb(255, 100, 200),  # Magenta-Red
            Color.from_rgb(255, 100, 150),
            Color.parse("red"),
            Color.from_rgb(255, 150, 100),  # Red-Orange
            Color.from_rgb(255, 200, 100),
        ]

        for _ in range(frames):
            with console.status("", spinner="dots", spinner_style="green"):
                animated_text = Text("")
                for i, char in enumerate(message):
                    # Циклический выбор цвета из списка
                    color_index = (i + _) % len(colors)
                    current_color = colors[color_index]

                    animated_text.append(char, style=f"bold {current_color.name}")

                console.print(animated_text, end="\r")
                time.sleep(0.05)

        # Финальный вывод сообщения
        console.print(Text(message, style="bold bright_green"))
    except:
        log.info(message)


def is_valid_json_string(data_string: str) -> bool:
    try:
        json.loads(data_string)
    except:
        return False
    return True


def print_json(data) -> None:
    console = Console()
    if not is_valid_json_string(data):
        processed_data1 = pprint.pformat(data)
        processed_data2 = json_repair.repair_json(processed_data1, return_objects=True)
        data = json.dumps(processed_data2)

    rich_json = RichJSON(data)
    output_panel = Panel(rich_json,
                         title='JSON Output',
                         border_style='bold blue',
                         padding=1,
                         expand=False)
    console.print(output_panel)


if __name__ == '__main__':
    print_fullscreen('123\nx444', timeout=1)
