#!/bin/python
# -*- coding: utf-8 -*-
"""
input_field.py
Function to display an input field within a curses window.

Author: GrimAndGreedy
License: MIT
"""

import curses
from typing import Tuple, Optional, Callable

def input_field(
        stdscr: curses.window,
        usrtxt:str="",
        field_name:str="Input",
        x:Callable=lambda:0,
        y:Callable=lambda:0,
        colours_start:int=0,
        literal:bool=False,
        max_length:Callable = lambda: 1000,
        registers={},
        refresh_screen_function:Optional[Callable]=None,
        cursor: int = 0,
) -> Tuple[str, bool]:
    """
    Display input field at x,y for the user to enter text.

    ---Arguments
        stdscr: curses screen
        usrtxt (str): text to be edited by the user
        field_name (str): The text to be displayed at the start of the text input
        x (int): prompt begins at (x,y) in the screen given
        y (Callable): prompt begins at (x,y) in the screen given
        colours_start (int): where to start when initialising the colour pairs with curses.
        literal: whether to display the repr() of the string; e.g., if we want to display escape sequences literally
        max_length (callable): function that returns the length of input field


    ---Returns
        usrtxt, return_code
        usrtxt: the text inputted by the user
        return_code: 
                        0: user hit escape
                        1: user hit return
    """
    while True:

        h, w = stdscr.getmaxyx()

        if refresh_screen_function != None:
            refresh_screen_function()
        field_end = min(w-3, max_length())
        field_y = min(h-1, y())
        field_x = min(h-1, x())

        # Clear background to end of row
        stdscr.addstr(field_y, x(), " "*(field_end-x()), curses.color_pair(colours_start+20))
        stdscr.refresh()
        # Display the field name and current text
        field_length = 0

        if literal:
            stdscr.addstr(field_y, x(), f"{field_name}: {repr(usrtxt)}   "[:field_end], curses.color_pair(colours_start+13) | curses.A_BOLD)
            field_length=len(f"{field_name}: {repr(usrtxt)}   ")
        else:
            stdscr.addstr(field_y, x(), f" {field_name}: {usrtxt}   "[:field_end], curses.color_pair(colours_start+13) | curses.A_BOLD)
            field_length=len(f" {field_name}: {usrtxt}   ")

        visible_cursor_x = x()+len(usrtxt)-cursor+len(f" {field_name}: ")
        if literal:
            visible_cursor_x = x()+len(repr(usrtxt))-cursor+len(f" {field_name}: ")-2

        # if key == curses.KEY_RESIZE:  # Terminal resize signal

        # Display cursor if the field fits onto the screen
        if field_length + 1 < field_end:
            if not literal:
                if usrtxt and cursor != 0:
                    stdscr.addstr(field_y, visible_cursor_x, f"{usrtxt[-(cursor)]}", curses.color_pair(colours_start+13) | curses.A_REVERSE | curses.A_BOLD)
                else:
                    stdscr.addstr(field_y, visible_cursor_x, f" ", curses.color_pair(colours_start+13) | curses.A_REVERSE | curses.A_BOLD)
            elif literal:
                stdscr.addstr(field_y, visible_cursor_x, f"{repr(usrtxt)[-(cursor+1)]}", curses.color_pair(colours_start+13) | curses.A_REVERSE | curses.A_BOLD)

        key = stdscr.getch()

        if key == 27:                                                           # ESC key
            return "", False
        elif key == 3:                                                           # ESC key
            stdscr.keypad(False)
            curses.nocbreak()
            curses.noraw()
            curses.echo()
            curses.endwin()
            exit()
        elif key == 10:                                                         # Enter/return key
            return usrtxt, True
            # selected_indices = print_selected_indices()
            # if not selected_indices:
            #     selected_indices = [indexed_items[cursor_pos][0]]
            # full_values = [format_row_full(items[i], hidden_columns) for i in selected_indices]  # Use format_row_full for full data
            # # selected_data = [format_full_row(items[i]).strip() for i, selected in enumerate(selections) if selected and i not in hidden_columns]
            # if full_values:
            #     process = subprocess.Popen(usrtxt, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            #     process.communicate(input='\n'.join(full_values).encode('utf-8'))
            # break
        elif key in [curses.KEY_BACKSPACE, "KEY_BACKSPACE", 263, 127]:

            if cursor == 0:
                usrtxt = usrtxt[:-1]
            else:
                usrtxt = usrtxt[:-(cursor+1)] + usrtxt[-cursor:]

        elif key in [curses.KEY_LEFT, 2]:                                       # CTRL+B
            cursor = min(len(usrtxt), cursor + 1)

        elif key in [curses.KEY_RIGHT, 6]:                                      # CTRL-F
            cursor = max(0, cursor - 1)

        elif key == curses.KEY_UP:
            cursor = max(0, cursor - 1)

        elif key in [4, 330]:                                                   # Ctrl+D, Delete
            if cursor != 0 and usrtxt != "":
                if cursor == 1:
                    usrtxt = usrtxt[:-(cursor)]
                else:
                    usrtxt = usrtxt[:-(cursor)] + usrtxt[-(cursor-1):]
                cursor = max(0, cursor - 1)
                
        elif key == 21 or key == "^U":                                          # CTRL+U
            if cursor == 0:
                usrtxt = ""
            else:
                usrtxt = usrtxt[-(cursor+1):]
            cursor = len(usrtxt)
        elif key == 11 or key == "^K":                                          # CTRL+K
            if cursor: usrtxt = usrtxt[:-cursor]
            cursor = 0

        elif key in [1, 262]:                                                          # CTRL+A (beginning)
            cursor = len(usrtxt)
            
        elif key in [5, 360]:                                                          # CTRL+E (end)
            cursor = 0
        elif key in [18]:                                                          # CTRL+E (end)
            if "*" in registers:
                if cursor == 0:
                    addtxt = registers["*"]
                    usrtxt = usrtxt[-cursor:] + registers["*"]
                else:
                    usrtxt = usrtxt[:-cursor] + registers["*"] + usrtxt[-cursor:]

        # elif key in [23,8]:                                                     # Ctrl+BACKSPACE, CTRL+W
        #     if cursor == 0: tmp = usrtxt[::-1]
        #     else: tmp = usrtxt[:-cursor][::-1]
        #     index = tmp.find(" ")
        #     if index == -1: index = len(usrtxt)-1-cursor
        #
        #     cursor = len(usrtxt)
        elif key == curses.KEY_RESIZE: pass

        else:
            if isinstance(key, int):
                try:
                    val = chr(key) if chr(key).isprintable() else ''
                except:
                    val = ''
            else: val = key
            if cursor == 0:
                usrtxt += val
            else:
                usrtxt = usrtxt[:-cursor] + val + usrtxt[-cursor:]
