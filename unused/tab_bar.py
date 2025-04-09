import math
import os
from pathlib import Path
from kitty.boss import get_boss
from kitty.fast_data_types import Screen, get_options, Color
from kitty.tab_bar import (
    DrawData,
    ExtraData,
    TabBarData,
    as_rgb,
    draw_title
)

class Logger:
    def __init__(self, pipe_path: str = "/tmp/kitty_debug"):
        self.pipe_path = pipe_path
        if not os.path.exists(self.pipe_path):
            os.mkfifo(self.pipe_path)
        self.clear()
        self.log("Logger initialized\n")



    def log(self, msg: str):
        try:
            fd = os.open(self.pipe_path, os.O_WRONLY | os.O_NONBLOCK)
            with os.fdopen(fd, "w") as pipe:
                pipe.write(msg)
                pipe.flush()
        except OSError as e:
            print(f"Could not write to pipe. Error: {e}")

    def inspect(self, obj: object):
        attributes = {}
        for attr in dir(obj):
            if attr.startswith('_'):
                continue
            try:
                value = getattr(obj, attr)
                attributes[attr] = type(value).__name__
            except Exception as e:
                attributes[attr] = f"<error: {e}>"
    
        formatted = "{\n" + "".join(f"    {k}: {v},\n" for k, v in attributes.items()) + "}"
        self.log(formatted)

    def clear(self):
        self.log("\033[2J\033[H") #tput clear
        self.log("\033[3J\033[0;0H") #resets cursor

logger = Logger("/tmp/kitty_debug")

def draw_tab(
    draw_data: DrawData,
    screen: Screen,
    tab: TabBarData,
    before: int,
    max_title_length: int,
    index: int,
    is_last: bool,
    extra_data: ExtraData,
) -> int:

    # logger.inspect(draw_data)
    
    # Open the file in write mode

    try:
        if tab.is_active:
            screen.cursor.bg = as_rgb(draw_data.active_bg.rgb)
            screen.cursor.fg = as_rgb(draw_data.active_bg.rgb)
        else:
            screen.cursor.bg = as_rgb(draw_data.inactive_bg.rgb)
            screen.cursor.fg = as_rgb(draw_data.inactive_bg.rgb)

        screen.draw('')
        logger.inspect(extra_data)
        screen.draw('')
    except Exception as e:
        logger.log(f"{e}\n")
        



    return screen.cursor.x



def draw_tab_with_separator(
    draw_data: DrawData, screen: Screen, tab: TabBarData,
    before: int, max_tab_length: int, index: int, is_last: bool,
    extra_data: ExtraData,
    background: int
) -> int:
    screen.cursor.bg = background
    screen.cursor.fg = as_rgb(draw_data.active_fg.rgb)
    screen.cursor.bold = screen.cursor.italic = False

    if index==1:
        screen.draw(draw_data.sep)


    if tab.is_active:
        screen.cursor.bg = background
        screen.cursor.fg = as_rgb(draw_data.active_bg.rgb)
        screen.draw('')
        screen.cursor.bg = as_rgb(draw_data.active_bg.rgb)
        screen.cursor.fg = as_rgb(draw_data.active_fg.rgb)
    else:
        screen.cursor.bg = as_rgb(draw_data.inactive_bg.rgb)
        screen.cursor.fg = as_rgb(draw_data.inactive_fg.rgb)

    
    draw_title(draw_data, screen, tab, index, max_tab_length)

    if tab.is_active:
        screen.cursor.bg = background
        screen.cursor.fg = as_rgb(draw_data.active_bg.rgb)
        screen.draw('')
        screen.cursor.bg = background
        screen.cursor.fg = as_rgb(draw_data.active_fg.rgb)
    else:
        screen.cursor.bg = background
        screen.cursor.fg = as_rgb(draw_data.inactive_fg.rgb)



    if not is_last:
        screen.draw(draw_data.sep)

    if is_last:
        remaining_size = max(screen.columns - screen.cursor.x, 0)
        cwd = truncate_str(get_cwd() + draw_data.sep , remaining_size) 

        screen.cursor.bg = background
        screen.cursor.fg = as_rgb(draw_data.inactive_fg.rgb)
        screen.cursor.bold = screen.cursor.italic = False
        screen.draw(' ' * (remaining_size - len(cwd)))
        screen.draw(cwd)

    end = screen.cursor.x
    return end

def truncate_str(input_str, max_length):
    if len(input_str) > max_length:
        half = max_length // 2
        return input_str[:half] + "…" + input_str[-half:]
    else:
        return input_str

def get_cwd():
    cwd = ""
    tab_manager = get_boss().active_tab_manager
    if tab_manager is not None:
        window = tab_manager.active_window
        if window is not None:
            cwd = window.cwd_of_child

    cwd_parts = list(Path(cwd).parts)

    if len(cwd_parts) > 1:
        if cwd_parts[1] == "home" or str(Path(*cwd_parts[:3])) == os.getenv("HOME") and len(cwd_parts) > 3:
            # replace /home/{{username}}
            cwd_parts = ["~"] + cwd_parts[3:]
            if len(cwd_parts) > 1:
                cwd_parts[0] = "~/"
        else:
            cwd_parts[0] = "/"
    else:
        cwd_parts[0] = "/"

    max_length = 10
    cwd = cwd_parts[0] + "/".join(
        [
            s if len(s) <= max_length else truncate_str(s, max_length)
            for s in cwd_parts[1:]
        ]
    )
    return cwd

def extract_rgb(hex_color: int):
    r = (hex_color >> 16) & 0xFF  # Extracts the red component
    g = (hex_color >> 8) & 0xFF   # Extracts the green component
    b = hex_color & 0xFF          # Extracts the blue component
    return r, g, b


