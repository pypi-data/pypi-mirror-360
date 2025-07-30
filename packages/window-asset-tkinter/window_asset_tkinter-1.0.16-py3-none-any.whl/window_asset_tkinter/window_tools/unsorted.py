"""
File in charge of containing the rest of the Window Tools class that could not be placed by action type
"""

import os
import string
import random
from typing import Dict, Any, Union

import tkinter as tk
from PIL import ImageTk, Image


def static_create_text_variable(default_text: str) -> tk.StringVar:
    """ create a text variable in order to store inputted and outputted text """
    value = tk.StringVar()
    value.set(default_text)

    return value


def static_load_image(image_path: str, width: int = 10, height: int = 10) -> Dict[str, Any]:
    """
        Add an image to a window
        :param image_path: The path to the image
        :param width: The destination width of the image
        :param height: The destination height of the image
        :return: A dictionnary with the following values:
            * If everything went fine:
                * "img": The image
                * raw_output:
                    * {"img":<object_pointing_to_the_image>}
            * otherwise:
                * "err_message": The error message if the image could not be loaded
                * raw_output:
                    * {"err_message":<error_message>}
    """
    result = {}
    if (os.path.exists(image_path) is False) or (os.path.isfile(image_path) is False):
        err_msg = "Image path is not valid or not provided"
        result["err_message"] = err_msg
        return result
    if height <= 0 and width <= 0:
        err_msg = "Image width and heigh must be greater than 0"
        result["err_message"] = err_msg
        return result
    try:
        result["img"] = Image.open(image_path)
        if not hasattr(Image, 'Resampling'):  # Pillow<9.0
            Image.Resampling = Image
        result["img"] = result["img"].resize(
            (width, height),
            Image.Resampling.LANCZOS
        )
        result["img"] = ImageTk.PhotoImage(result["img"])
    except Exception as error:
        result["err_message"] = error
        return result
    return result


class Unsorted:
    """ Class in the charge of containing the functions that could not be placed by action """
    @staticmethod
    def gen_random_name(length: int = 10) -> str:
        """ Generate a random name """
        result = ""
        while length > 0:
            result += random.choice(string.ascii_letters)
            length -= 1
        return result

    @staticmethod
    def init_plain_window(root_window: Union[tk.Tk, tk.Toplevel, None] = None) -> Union[tk.Tk, tk.Toplevel]:
        """ Returns the basics of a window """
        my_window = root_window
        if isinstance(root_window, (tk.Tk, tk.Toplevel)):
            my_window = tk.Toplevel(root_window)
        elif root_window is None:
            my_window = tk.Toplevel()
        else:
            my_window = tk.Tk()
        return my_window

    @staticmethod
    def init_window(window: tk.Tk, title: str, bkg: str, width: int, height: int, position_x: int, position_y: int, fullscreen: bool, resizable: bool) -> None:
        """ initialise the window for the main_menu """
        maximum = 200
        window.geometry(f"{width}x{height}+{position_x}+{position_y}")
        window.minsize(width=width, height=height)
        if fullscreen is False:
            window.maxsize(width=width+maximum, height=height + maximum)
        window.title(title)
        window['bg'] = bkg
        window.attributes('-fullscreen', fullscreen)
        if resizable is False:
            window.resizable(False, False)
        else:
            window.resizable(True, True)

    @staticmethod
    def load_image(image_path: str, width: int = 10, height: int = 10) -> Dict[str, Any]:
        """
        Add an image to a window 
        :param image_path: The path to the image
        :param width: The destination width of the image
        :param height: The destination height of the image
        :return: A dictionnary with the following values:
            * If everything went fine:
                * "img": The image
                * raw_output:
                    * {"img":<object_pointing_to_the_image>}
            * otherwise:
                * "err_message": The error message if the image could not be loaded
                * raw_output:
                    * {"err_message":<error_message>}
        """
        return static_load_image(image_path, width, height)

    @staticmethod
    def create_text_variable(default_text: str) -> tk.StringVar:
        """ create a text variable in order to store inputted and outputted text """
        return static_create_text_variable(default_text)

    @staticmethod
    def clear_entry_content(entry: tk.Entry) -> None:
        """ Clear all text currently present in the entry field """
        entry.delete(0, tk.END)

    @staticmethod
    def update_entry_content(entry: tk.Entry, position: int, new_text: str) -> None:
        """ update the content of an entry field """
        entry.insert(position, new_text)

    @staticmethod
    def enter_fullscreen(window: tk.Tk, fullscreen: bool) -> None:
        """ enter or exit the fullscreen """
        window.attributes('-fullscreen', fullscreen)

    @staticmethod
    def allow_resizing(window: tk.Tk, allow: bool = True) -> None:
        """ Allow the window to be resized """
        if allow is False:
            window.resizable(False, False)
        else:
            window.resizable(True, True)

    @staticmethod
    def maintain_on_top(window: tk.Tk, always_on_top: bool) -> None:
        """ Maintain the window always on top """
        if always_on_top is True:
            window.attributes('-topmost', True)
        else:
            window.attributes('-topmost', False)

    @staticmethod
    def free_loaded_image(image_pointer: ImageTk.PhotoImage) -> None:
        """ Free an image that was loaded and stored in memory """
        try:
            image_pointer.__del__()
        except Exception as error:
            del image_pointer

    @staticmethod
    def hide_window(window: tk.Tk) -> None:
        """ Hide the window """
        window.withdraw()

    @staticmethod
    def show_window(window: tk.Tk) -> None:
        """ Show the window """
        window.deiconify()

    @staticmethod
    def destroy_window(window: tk.Tk) -> None:
        """ Destroy the window """
        window.destroy()

    @staticmethod
    def close_window(window: tk.Tk) -> None:
        """ Close the window """
        window.quit()
        window.destroy()

# usefull ressource:
# icon: https://www.pythontutorial.net/tkinter/tkinter-window/
