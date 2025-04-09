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

# opts = get_options()

lavender = as_rgb(int("B4BEFE", 16))
surface1 = as_rgb(int("45475A", 16))
base = as_rgb(int("1E1E2E", 16))
window_icon = ""
layout_icon = ""
active_tab_layout_name = ""
active_tab_num_windows = 1
left_status_length = 0


file_path = "/Users/mattia/Desktop/log.txt"
with open(file_path, "a") as file:
    file.write("Script loaded\n")

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

    
    # Open the file in write mode
    global base
    global active_tab_layout_name
    global active_tab_num_windows

    with open(file_path, "a") as file:
        # Write the desired content to the file
        file.write("Draw tab\n")
        try:
            # active_tab_idx = get_boss().active_tab_manager.active_tab_idx
            # curr_tab_id = tab.tab_id
            # file.write(str(get_boss().active_tab_manager.active_tab_idx))
            output = get_boss().call_remote_control(None, ('get-colors', f'--match=recent:0'))



            lines = output.split('\n')
            background_value = None
            
            for line in lines:
                if line.startswith('background'):
                    background_value = line.split()[1]
                    break

            
            base = int(background_value[1:], 16)
            r,g,b = extract_rgb(base)
            base_color = Color(r,g,b)

            # file.write(f'Active tab color: {output}')
            new_draw_data = draw_data._replace(inactive_bg=base_color)
            # file.write(f'Drawing with new color:\t{str(new_draw_data.inactive_bg.rgb)}\n')
            file.write(f'active_fg: {new_draw_data.active_fg}\n')

            # if tab.is_active:
            #     active_tab_layout_name = tab.layout_name
            #     active_tab_num_windows = tab.num_windows
            #
            # if index == 1:
            #     _draw_left_status(screen)

            draw_tab_with_separator(new_draw_data, screen, tab, before, max_title_length, index, is_last, extra_data, as_rgb(base))
            # if is_last:
            #     screen_cursor_x = screen.cursor.x
            #     center_status_length = screen_cursor_x - left_status_length
            #     leading_spaces = math.ceil(
            #         (screen.columns - left_status_length * 2 - center_status_length) / 2
            #     )
            #     screen.cursor.x = left_status_length
            #     screen.insert_characters(leading_spaces)
            #     # TODO: fix tab click handlers
            #     # self.cell_ranges = [(s + leading_spaces, e + leading_spaces) for (s, e) in self.cell_ranges]
            #     screen.cursor.x = screen_cursor_x + leading_spaces
            #
            # if is_last:
            #     _draw_right_status(screen, is_last)


            # draw_data.inactive_bg = base_color

            # file.write(f'Original color:\t{str(draw_data.inactive_bg.rgb)}\n')
            # file.write(f'Current tab window bg:\t{background_value}\n')
            # file.write(str(r))
            # file.write(" ")
            # file.write(str(g))
            # file.write(" ")
            # file.write(str(b))
            # file.write("\n")
            # file.write(str(int(Color(r,g,b))))
            # file.write("\n")
            # file.write(str(base))
            # file.write("\n")
        except Exception as e:
             file.write(f"Error: {e}\n")



    return screen.cursor.x


def _draw_left_status(screen: Screen):
    global left_status_length
    with open(file_path, "a") as file:
        # Write the desired content to the file
        file.write("Draw left status\n")
        file.write("Base in draw_left")

    cwd = get_cwd()
    cells = [
        (surface1, base, cwd),
    ]

    left_status_length = 0
    for _, _, cell in cells:
        left_status_length += len(cell)

    # draw right status
    for fg, bg, cell in cells:
        screen.cursor.fg = fg
        screen.cursor.bg = bg
        screen.draw(cell)
    screen.cursor.fg = 0
    screen.cursor.bg = 0

    # update cursor position
    screen.cursor.x = left_status_length
    return screen.cursor.x


def _draw_right_status(screen: Screen, is_last: bool) -> int:
    with open(file_path, "a") as file:
        # Write the desired content to the file
        file.write("Draw right status\n")
    layout_fg = surface1 if active_tab_layout_name == "fat" else lavender
    cells = [
        # layout name
        (layout_fg, base, " " + layout_icon + " "),
        (layout_fg, base, active_tab_layout_name + " "),
        # num windows
        (surface1, base, " " + window_icon + " "),
        (surface1, base, str(active_tab_num_windows)),
    ]

    # calculate leading spaces to separate tabs from right status
    right_status_length = 0
    for _, _, cell in cells:
        right_status_length += len(cell)
    leading_spaces = 0
    if opts.tab_bar_align == "center":
        leading_spaces = (
            math.ceil((screen.columns - screen.cursor.x) / 2) - right_status_length
        )
    elif opts.tab_bar_align == "left":
        leading_spaces = screen.columns - screen.cursor.x - right_status_length

    # draw leading spaces
    if leading_spaces > 0:
        screen.draw(" " * leading_spaces)

    # draw right status
    for fg, bg, cell in cells:
        screen.cursor.fg = fg
        screen.cursor.bg = bg
        screen.draw(cell)
    screen.cursor.fg = 0
    screen.cursor.bg = 0

    # update cursor position
    screen.cursor.x = max(screen.cursor.x, screen.columns - right_status_length)
    return screen.cursor.x


def truncate_str(input_str, max_length):
    if len(input_str) > max_length:
        half = max_length / 2
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
    with open(file_path, "a") as file:
        file.write(f'First path part: {Path(*cwd_parts[:3])}\n')
        file.write(f'Parts: {cwd_parts}\n')
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

def draw_tab_with_separator(
    draw_data: DrawData, screen: Screen, tab: TabBarData,
    before: int, max_tab_length: int, index: int, is_last: bool,
    extra_data: ExtraData,
    background: int
) -> int:
    screen.cursor.bg = background
    screen.cursor.fg = as_rgb(draw_data.active_fg.rgb)
    # screen.cursor.bold = screen.cursor.italic = False
    # if draw_data.leading_spaces:
    #     screen.draw(' ' * draw_data.leading_spaces)
    
    with open(file_path, "a") as file:
        # Write the desired content to the file
        file.write(f'Background: {background}\n')
        file.write(f'%HOME= : {os.getenv("HOME")}\n')


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


    # trailing_spaces = min(max_tab_length - 1, draw_data.trailing_spaces)
    # max_tab_length -= trailing_spaces
    # extra = screen.cursor.x - before - max_tab_length
    # if extra > 0:
    #     screen.cursor.x -= extra + 1
    #     screen.draw('…')
    # if trailing_spaces:
    #     screen.draw(' ' * trailing_spaces)

    if not is_last:
        # screen.cursor.bg = as_rgb(color_as_int(draw_data.inactive_bg))
        with open(file_path, "a") as file:
            # Write the desired content to the file
            file.write(f'Separator color: {screen.cursor.bg}')
        screen.draw(draw_data.sep)

    if is_last:
        remaining_size = screen.columns - screen.cursor.x
        cwd = truncate_str(get_cwd(), remaining_size)
        
        with open(file_path, "a") as file:
            file.write(f'CWD: {get_cwd()}')

        screen.cursor.bg = background
        screen.cursor.fg = as_rgb(draw_data.inactive_fg.rgb)
        screen.cursor.bold = screen.cursor.italic = False
        screen.draw(' ' * (remaining_size - len(cwd)))
        screen.draw(cwd)

    end = screen.cursor.x
    return end


