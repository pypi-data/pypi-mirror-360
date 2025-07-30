"""
File in charge of containing the functions that update info on GUI elements
"""

from typing import Union

import os
import platform
import tkinter as tk


class Set:
    """ The class containing the actions for editing GUI aspects on the fly """

    @staticmethod
    def set_transparency(window: tk.Tk, alpha: Union[int, float]) -> None:
        """ Set the transparency of the window """
        if alpha < 0:
            alpha *= (-1)

        if alpha > 1:
            numerator = alpha - 1
            denominator = 1
            fraction = numerator / denominator
            alpha = float(fraction)
        window.attributes('-alpha', alpha)

    @staticmethod
    def set_colour_transparency(window: tk.Tk, colour: str = "grey", transparent: bool = True) -> None:
        """ Make the background of the window transparent"""
        if platform.system() == "Windows":
            if transparent is True:
                window.wm_attributes("-transparentcolor", colour)
            else:
                window.wm_attributes("-transparentcolor", "")
        elif platform.system() == "Java":
            window.wm_attributes("-transparent", transparent)
            if transparent is True:
                window.config(bg='systemTransparent')
            else:
                window.config(bg=colour)
        elif platform.system() == "Darwin":
            window.wm_attributes("-transparentcolor", colour)
            if transparent is True:
                window.config(bg='systemTransparent')
            else:
                window.config(bg=colour)
        elif platform.system() == "Linux":
            window.wm_attributes("-transparentcolor", colour)
            if transparent is True:
                window.config(bg='systemTransparent')
            else:
                window.config(bg=colour)
        else:
            print(f"Unsupported platform: {platform.system()}")
            print("Setting transparency is not supported on this platform.")

    @staticmethod
    def set_window_title_bar_visibility(window: tk.Tk, visible: bool = False) -> None:
        """ Make the title bar (draggable section of a window) visible or not """
        window.overrideredirect(visible)

    @staticmethod
    def set_title(window: tk.Tk, title: str) -> None:
        """ Set the title of the window """
        window.title(title)

    @staticmethod
    def set_window_size(window: tk.Tk, width: int, height: int, posx: int = -666, posy: int = -666) -> None:
        """ Set the size of the window """
        position = ""
        if posx > -666:
            position += f"+{posx}"
        if posy > -666:
            if posx > -666:
                position += f"+{posy}"
            else:
                position += f"+{window.winfo_x()}+{posy}"

        window.geometry(f"{width}x{height}{position}")

    @staticmethod
    def set_min_window_size(window: tk.Tk, width: int, height: int) -> None:
        """ Set the minimum size for a window """
        window.minsize(width, height)

    @staticmethod
    def set_max_window_size(window: tk.Tk, width: int, height: int) -> None:
        """ Set the maximum size for a window """
        window.maxsize(width, height)

    @staticmethod
    def set_window_position(window: tk.Tk, posx: int, posy: int) -> None:
        """ Set the position of the window """
        window.geometry(f"+{posx}+{posy}")

    @staticmethod
    def set_window_position_x(window: tk.Tk, posx: int) -> None:
        """ Set the x position of the window """
        window.geometry(f"+{posx}+{window.winfo_y()}")

    @staticmethod
    def set_window_position_y(window: tk.Tk, posy: int) -> None:
        """ Set the y position of the window """
        window.geometry(f"+{window.winfo_x()}+{posy}")

    @staticmethod
    def set_offset_window_position_x(window: tk.Tk, posx: int) -> None:
        """ Set the x position of the window """
        window.geometry(f"+{posx+window.winfo_x()}+{window.winfo_y()}")

    @staticmethod
    def set_offset_window_position_y(window: tk.Tk, posy: int) -> None:
        """ Set the y position of the window """
        window.geometry(f"+{window.winfo_x()}+{posy+window.winfo_y()}")

    @staticmethod
    def set_offset_window_position(window: tk.Tk, posx: int, posy: int) -> None:
        """ Set the y position of the window """
        window.geometry(f"+{posx+window.winfo_x()}+{posy+window.winfo_y()}")

    @staticmethod
    def set_window_width(window: tk.Tk, width: int) -> None:
        """ Set the width of the window """
        window.geometry(
            f"{width}x{window.winfo_height()}+{window.winfo_x()}+{window.winfo_y()}")

    @staticmethod
    def set_window_height(window: tk.Tk, height: int) -> None:
        """ Set the width of the window """
        window.geometry(
            f"{window.winfo_width()}x{height}+{window.winfo_x()}+{window.winfo_y()}")

    @staticmethod
    def set_offset_window_width(window: tk.Tk, width: int) -> None:
        """ Set the width of the window """
        window.geometry(
            f"{width+window.winfo_width()}x{window.winfo_height()}+{window.winfo_x()}+{window.winfo_y()}"
        )

    @staticmethod
    def set_offset_window_height(window: tk.Tk, height: int) -> None:
        """ Set the width of the window """
        window.geometry(
            f"{window.winfo_width()}x{height+window.winfo_height()}+{window.winfo_x()}+{window.winfo_y()}"
        )

    @staticmethod
    def set_offset_window_dims(window: tk.Tk, width: int, height: int) -> None:
        """ Set the width of the window """
        window.geometry(
            f"{width+window.winfo_width()}x{height+window.winfo_height()}+{window.winfo_x()}+{window.winfo_y()}"
        )

    @staticmethod
    def set_window_background_colour(window: tk.Tk, colour: str) -> None:
        """ Set the background colour of the window """
        window["bg"] = colour

    @staticmethod
    def set_icon(window: tk.Tk, icon_path: str) -> None:
        """ Set an ico image as the window icon to the window """
        if os.path.exists(icon_path) and os.path.isfile(icon_path):
            if platform.system() == 'nt' or platform.system().lower() == "windows" or platform.system().lower() == "darwin":
                window.iconbitmap(icon_path)
            else:
                print(
                    "This is not a bug, this is in order to prevent the program from crashing on some linux systems"
                )
                print(f"system = {platform.system()}")
                print(f"icon_path = {icon_path}")
        else:
            print(f"The icon path '{icon_path}' is not valid")

    @staticmethod
    def set_window_always_on_top(window: tk.Tk, always_on_top: bool = True) -> None:
        """ Set the window to always be on top """
        window.wm_attributes("-topmost", always_on_top)

    def set_total_transparency(self, window: tk.Tk, colour: str = "grey", transparent: bool = True) -> None:
        """ Make the full conversion of the window so that it is transparent """
        if transparent is True:
            self.set_window_background_colour(window=window, colour=colour)
        else:
            self.set_window_background_colour(window=window, colour=colour)
        self.set_colour_transparency(
            window=window,
            colour=colour,
            transparent=transparent
        )
        self.set_window_title_bar_visibility(
            window=window,
            visible=transparent
        )

    @staticmethod
    def set_window_visible(window: tk.Tk, visible: bool = True) -> None:
        """ Set the window to be visible or not """
        if visible is True:
            window.deiconify()
        else:
            window.withdraw()

    @staticmethod
    def set_interaction_possible(window: tk.Tk, window_interaction_disabled: bool = False) -> None:
        """ If set to False, the elements in the window will be interactible """
        if platform.system() == "Windows":
            if window_interaction_disabled is True:
                window.wm_attributes("-disabled", True)
            else:
                window.wm_attributes("-disabled", False)
