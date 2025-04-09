import re
import os
from kitty.fast_data_types import Screen, Color
from kitty.tab_bar import (
    DrawData,
    ExtraData,
    TabBarData,
    draw_title
)


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
