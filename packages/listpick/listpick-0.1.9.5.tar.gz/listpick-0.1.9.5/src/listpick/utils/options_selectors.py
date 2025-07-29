#!/bin/python
# -*- coding: utf-8 -*-
"""
options_selectors.py
Handle option specification.

Author: GrimAndGreedy
License: MIT
"""

import curses
from typing import Tuple
from listpick.ui.input_field import input_field
from listpick.utils.utils import dir_picker, get_column_widths
from listpick.listpick_app import Picker

def default_option_input(stdscr: curses.window, refresh_screen_function=None, starting_value:str="", field_name:str="Opts", registers={}) -> Tuple[bool, str]:
    # notification(stdscr, message=f"opt required for {index}")
    usrtxt = f"{starting_value} " if starting_value else ""
    h, w = stdscr.getmaxyx()
    # field_end = w-38 if show_footer else w-3
    field_end = w-3
    field_end_f = lambda: stdscr.getmaxyx()[1]-3
    usrtxt, return_val = input_field(
        stdscr,
        usrtxt=usrtxt,
        field_name=field_name,
        x=lambda:2,
        y=lambda: stdscr.getmaxyx()[0]-1,
        max_length=field_end_f,
        registers=registers,
    )
    if return_val: return True, usrtxt
    else: return False, starting_value


def default_option_selector(stdscr: curses.window, option_list:list[str]=[], refresh_screen_function=None, starting_value:str="", field_name:str="Opts", registers={}) -> Tuple[bool, str]:
    if option_list == []: option_list = [str(i) for i in range(32)]


    option_picker_data = {
        "items": option_list,
        # "colours": notification_colours,
        # "colours_start": 50,
        # "title":field_name,
        # "header": [],
        # "hidden_columns":[],
        # "require_option":require_option,
        # "keys_dict": options_keys,
        "show_footer": False,
        "cancel_is_back": True,
    }
    while True:
        h, w = stdscr.getmaxyx()

        choose_opts_widths = get_column_widths(option_list)
        window_width = min(max(sum(choose_opts_widths) + 6, 50) + 6, w)
        window_height = min(h//2, max(6, len(option_list)+2))

        submenu_win = curses.newwin(window_height, window_width, (h-window_height)//2, (w-window_width)//2)
        submenu_win.keypad(True)
        OptionPicker = Picker(submenu_win, **option_picker_data)
        s, o, f = OptionPicker.run()
        if s:
            return True, option_list[s[0]]
        else:
            return False, starting_value

        # if o == "refresh": 
        #     self.draw_screen(self.indexed_items, self.highlights)
        #     continue
        # if s:
        #     return {x: options[x] for x in s}, o, f
        # return {}, "", f
    return False, starting_value


def output_file_option_selector(stdscr:curses.window, refresh_screen_function, registers={}) -> Tuple[bool, str]:
    s = dir_picker()

    stdscr.clear()
    stdscr.refresh()
    refresh_screen_function()
    usrtxt = f"{s}/"
    h, w = stdscr.getmaxyx()
    # field_end = w-38 if show_footer else w-3
    field_end_f = lambda: stdscr.getmaxyx()[1]-3
    usrtxt, return_val = input_field(
        stdscr,
        usrtxt=usrtxt,
        field_name="Save as",
        x=lambda:2,
        y=lambda: stdscr.getmaxyx()[0]-1,
        max_length=field_end_f,
        registers=registers,
    )
    if return_val: return True, usrtxt
    else: return False, ""
