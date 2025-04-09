import re
import os
from kitty.fast_data_types import Screen, Color
from kitty.tab_bar import (
    DrawData,
    ExtraData,
    TabBarData,
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

def as_hex(color: Color):
    return "{:02X}{:02X}{:02X}".format(color.red, color.green, color.blue)

def replace_custom_tags(draw_data, title_template): 
    pattern1 = r"\{fmt\.(fg|bg)\.(active_bg|inactive_bg|active_fg|inactive_fg|default_bg)\}"
    def replacement1(match):
        fg_or_bg = match.group(1)
        color = as_hex(getattr(draw_data, match.group(2)))
        return f"{{fmt.{fg_or_bg}._{color}}}"
    return re.sub(pattern1, replacement1, title_template)

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


    try:
        new_title_template = replace_custom_tags(draw_data, draw_data.title_template)
        new_active_title_template = replace_custom_tags(draw_data, draw_data.active_title_template)

        new_draw_data = draw_data._replace(title_template = new_title_template, active_title_template = new_active_title_template)
        
        draw_title(new_draw_data, screen, tab, index, max_title_length)
    except Exception as e:
        logger.log(f"{e}\n")
        



    return screen.cursor.x
