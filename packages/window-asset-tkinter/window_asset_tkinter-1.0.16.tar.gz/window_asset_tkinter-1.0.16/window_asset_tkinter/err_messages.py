"""
File in charge of displaying message boxes
"""
import os
import tkinter as tk
from typing import Dict, Any, Union, List
from tkinter import messagebox as msg

if __name__ == "__main__":
    from window_tools import WindowTools as wt
else:
    from .window_tools import WindowTools as wt


class ErrMessages(wt):
    """ Basic error messages for the program """

    images = []

    def __init__(self, base_window: Union[tk.Tk, tk.Toplevel], window_config: dict, print_debug: bool = False, cwd: str = os.getcwd()) -> None:
        """
        The constructor for the ErrMessages class.
        It initializes the base window and the window configuration.
        It also sets the default values for the window properties.
        It loads the window configuration from the provided dictionary.
        It also sets the default values for the window properties.
        It also sets the default values for the button properties.
        It also sets the default values for the image properties.
        It also sets the default values for the execution result.
        It also sets the default values for the message result.

        Args:
            base_window (Union[tk.Tk, tk.Toplevel]): _description_
            window_config (dict): _description_
            print_debug (bool, optional): _description_. Defaults to False.
            cwd (str, optional): _description_. Defaults to os.getcwd().
        """
        self.cwd = cwd.replace("\\", "/")
        self.base_window = base_window
        self.window_config: Dict[str, Any] = {
            "debug_mode_enabled": print_debug
        }
        self.err_messages_load_window_config(window_config)
        self.bkg = self.window_config["background"]
        self.foreground = self.window_config["foreground"]
        self.window_width = self.window_config["width"]
        self.window_height = self.window_config["height"]
        self.button_width = self.window_config["button_width"]
        self.button_height = self.window_config["button_height"]
        self.iheight = self.window_config["image_height"]
        self.iwidth = self.window_config["image_width"]
        self.execution_result = 0
        self.message_result = []
        self.window: tk.Tk = tk.Tk
        self.img_storer = None
        self.button_options = {
            "ok": 0, "o/c": 1,
            "a/r/i": 2, "y/n/c": 3,
            "y/n": 4, "r/c": 5,
            "c/a": 6, "y/n/m": 7,
            "s/d/c": 8, "a/r/c": 9,
            "r/s/a": 10, 11: "c/d/c"
        }

    def advanced_path_analysis(self, path_src: str, append_path: str, search_term: str = "./") -> str:
        """ Analyze the path and append the append_path to it """
        path_src = path_src.replace("\\", "/")
        append_path = append_path.replace("\\", "/")
        if "../" in path_src:
            path_src_list: List[str] = path_src.split("/")
            append_path_list: List[str] = append_path.split("/")
            tracker = []
            for i in path_src_list:
                if i == "..":
                    tracker.append(i)
            for i in range(len(tracker)-1, 0, -1):
                path_src_list.pop(tracker[i])
                append_path_list.pop(len(append_path_list)-1)
            path_src = "/".join(path_src_list)
            append_path = "/".join(append_path_list)
            result = f"{append_path}/{path_src}"
        else:
            result = path_src.replace(search_term, f"{append_path}/")
        return result

    def err_messages_update_paths(self, window_config) -> Dict[str, Dict[str, Any]]:
        """ Update the path for the images of the error messages """
        search_term = "./"
        self.err_message_print_debug(f"new_position = {self.cwd}")
        if "err_message" in window_config:
            self.err_message_print_debug(
                f"icon_path = {window_config['err_message']['icon_path']}"
            )
            icon_path = self.advanced_path_analysis(
                window_config['err_message']['icon_path'],
                self.cwd,
                search_term
            )
            error_icon_path = self.advanced_path_analysis(
                window_config['err_message']['error_icon_path'],
                self.cwd,
                search_term
            )
            warning_icon_path = self.advanced_path_analysis(
                window_config['err_message']['warning_icon_path'],
                self.cwd,
                search_term
            )
            information_icon_path = self.advanced_path_analysis(
                window_config['err_message']['information_icon_path'],
                self.cwd,
                search_term
            )
            self.err_message_print_debug(
                f"icon_path = {icon_path}, error_icon_path = {error_icon_path}, warning_icon_path = {warning_icon_path}, information_icon_path = {information_icon_path}"
            )
            window_config["err_message"]["icon_path"] = icon_path
            window_config["err_message"]["error_icon_path"] = error_icon_path
            window_config["err_message"]["warning_icon_path"] = warning_icon_path
            window_config["err_message"]["information_icon_path"] = information_icon_path
        else:
            icon_path = self.advanced_path_analysis(
                window_config['default_config']['icon_path'],
                self.cwd,
                search_term
            )
            window_config["default_config"]["icon_path"] = icon_path
        return window_config

    def err_opt1(self) -> int:
        """ The first option of the program """
        self.err_message_print_debug("Option 1")
        self.window.destroy()
        self.execution_result = 1
        return 1

    def err_opt2(self) -> int:
        """ The second option of the program """
        self.err_message_print_debug("Option 2")
        self.window.destroy()
        self.execution_result = 2
        return 2

    def err_opt3(self) -> int:
        """ The third option of the program """
        self.err_message_print_debug("Option 3")
        self.window.destroy()
        self.execution_result = 3
        return 3

    def err_message_print_debug(self, string: str) -> None:
        """ Print the string if the debug mode is enabled """
        if self.window_config["debug_mode_enabled"] is True:
            print(f"(em) {string}")

    def err_messages_load_window_config(self, window_config: Dict[str, Dict[str, Any]]) -> None:
        """ Update the settings of the display depending on the configuration """
        window_config = self.err_messages_update_paths(window_config)
        self.err_message_print_debug("Loading window configuration")
        config_name = "err_message"
        if config_name in window_config:
            self.err_message_print_debug(
                f"'{config_name}' configuration found in json, loading '{config_name}'"
            )
            self.window_config = window_config[config_name]
        else:
            self.err_message_print_debug(
                f"'{config_name}' configuration not found in json, loading 'default' configuration"
            )
            self.window_config = window_config["default_config"]
            self.window_config["error_icon_path"] = ""
            self.window_config["warning_icon_path"] = ""
            self.window_config["image_width"] = 0
            self.window_config["image_height"] = 0
        if self.window_config["dark_mode_enabled"] is True:
            self.err_message_print_debug(
                "Dark mode enabled, loading dark_mode colours"
            )
            self.window_config["background"] = self.window_config["dark_mode"]["background"]
            self.window_config["foreground"] = self.window_config["dark_mode"]["foreground"]
        else:
            self.err_message_print_debug(
                "Dark mode not enabled, loading light_mode configuration"
            )
            self.window_config["background"] = self.window_config["light_mode"]["background"]
            self.window_config["foreground"] = self.window_config["light_mode"]["foreground"]
        self.err_message_print_debug("Window configuration loaded")

    def pack_correct_button(self, my_window: Union[tk.Tk, tk.Toplevel], frame: tk.Frame, button: int = 0, command: list = []) -> None:
        """
        Pack the correct button
            * 0  : OK
            * 1  : OK, Annuler
            * 2  : Abandonner, Recommencer, Ignorer
            * 3  : Oui, Non, Annuler
            * 4  : Oui, Non
            * 5  : Recommencer, Annuler
            * 6  : Continuer, Abandonner
            * 7  : Oui, Non, Peut-être
            * 8  : Enregistrer, Ne pas enregistrer, Annuler
            * 9  : Appliquer, Réinitialiser, Annuler
            * 10 : Ré-essayer, Ignorer, Annuler
            * 11 : Confirmer, Supprimer, Annuler
        """
        button_dict = {
            0: ["OK"],
            1: ["OK", "Cancel"],
            2: ["Abandon", "Retry", "Ignore"],
            3: ["Yes", "No", "Cancel"],
            4: ["Yes", "No"],
            5: ["Retry", "Cancel"],
            6: ["Continue", "Abandon"],
            7: ["Yes", "No", "Maybe"],
            8: ["Save", "Don't Save", "Cancel"],
            9: ["Apply", "Reset", "Cancel"],
            10: ["Retry", "Skip", "Abort"],
            11: ["Confirm", "Delete", "Cancel"]
        }
        if button not in button_dict:
            button = 0
        if len(command) == 0:
            for i in button_dict[button]:
                command.append(my_window.destroy)
        elif len(command) < len(button_dict[button]):
            for i in range(len(button_dict[button]) - len(command)):
                command.append(my_window.destroy)
        else:
            command = command[:len(button_dict[button])]
        button_list = button_dict[button]
        command.reverse()
        button_list.reverse()
        self.err_message_print_debug(f"Button list = {button_list}")
        self.err_message_print_debug(
            f"Button list = {button_dict}, button = {button}")
        tracker = 0
        for i in button_dict[button]:
            self.err_message_print_debug(f"i = {i}, tracker = {tracker}")
            self.add_button(
                window=frame,
                text=i,
                fg=self.foreground,
                bkg=self.bkg,
                side=tk.RIGHT,
                command=command[tracker],
                width=self.window_config["button_width"],
                height=self.window_config["button_height"],
                position_x=5,
                position_y=5
            )
            tracker += 1

    def find_longest_string_in_paragraph(self, string: str, sep: str) -> int:
        """ Find the longest string in a given paragraph """
        longest = 0
        for i in string.split(sep):
            length = len(i)
            if length > longest:
                longest = length
        return longest

    def basic_message(self, my_window: Union[tk.Tk, tk.Toplevel], title: str = "", message: str = "", button: int = 0, always_on_top: bool = True, icon_path: str = "", command: list = []) -> None:
        """ Display an error Message for the program """
        message_separator = "\n"
        message_result = {}
        err_screen = my_window
        if self.window_config["debug_mode_enabled"] is True:
            bkg1 = "#00FFFF"
            bkg2 = "#FF00FF"
            bkg3 = "#FFFF00"
        else:
            bkg1 = self.bkg
            bkg2 = self.bkg
            bkg3 = self.bkg
        self.init_window(
            err_screen,
            title,
            bkg1,
            self.window_width,
            self.window_height,
            self.window_config["window_position_x"],
            self.window_config["window_position_y"],
            fullscreen=self.window_config["full_screen"],
            resizable=self.window_config["resizable"]
        )
        self.set_icon(err_screen, self.window_config["icon_path"])
        self.set_min_window_size(
            err_screen,
            self.window_config["min_width"],
            self.window_config["min_height"]
        )
        self.set_max_window_size(
            err_screen,
            self.window_config["max_width"],
            self.window_config["max_height"]
        )
        self.maintain_on_top(err_screen, always_on_top)

        msg_frame = self.add_frame(
            window=err_screen,
            borderwidth=2,
            relief=tk.FLAT,
            bkg=bkg2,
            width=self.window_config["max_width"],
            height=self.window_config["max_height"],
            position_x=0,
            position_y=0,
            side=tk.TOP,
            fill=tk.BOTH
        )
        msg_frame.place(relwidth=1.0, relheight=0.7)
        message_result["msg_frame"] = msg_frame
        button_frame = self.add_frame(
            window=err_screen,
            borderwidth=0,
            relief=tk.FLAT,
            bkg=bkg3,
            width=self.window_width,
            height=self.window_config["button_height"],
            position_x=10,
            position_y=0,
            side=tk.BOTTOM,
            fill=tk.BOTH,
            anchor=tk.CENTER
        )
        message_result["button_frame"] = button_frame
        if os.path.exists(icon_path) and os.path.isfile(icon_path):
            if self.iheight > 0 and self.iwidth > 0:
                self.err_message_print_debug(
                    f"self.iheight = {self.iheight}, self.iwidth = {self.iwidth}"
                )
                self.err_message_print_debug(f"icon path = {icon_path}")
                image = self.add_image(
                    window=msg_frame,
                    image_path=icon_path,
                    bkg=self.bkg,
                    width=self.iwidth,
                    height=self.iheight,
                    fill=tk.BOTH,
                    side=tk.LEFT,
                    padx=0,
                    pady=0,
                    anchor=tk.NW
                )
                if "err_message" in image:
                    self.err_message_print_debug(image["err_message"])
                else:
                    self.img_storer = image["img"]
                    message_result["img"] = image["img"]
                    message_result["panel"] = image["panel"]
        msg_label = self.add_paragraph_field(
            frame=msg_frame,
            fg=self.foreground,
            bkg=self.bkg,
            height=len(message.split(message_separator)),
            width=self.window_width - self.iwidth,
            padx_text=0,
            pady_text=0,
            block_cursor=False,
            font=(
                self.window_config["font_family"],
                self.window_config["font_size"],
            ),
            cursor="left_ptr",
            export_selection=True,
            highlight_colour=self.bkg,
            relief=tk.FLAT,
            undo=False,
            wrap=tk.WORD,
            fill=tk.BOTH,
            side=tk.LEFT,
            padx_pack=10,
            pady_pack=0,
            ipadx=0,
            ipady=0
        )
        msg_label.insert(tk.END, message)
        msg_label.config(state=tk.DISABLED)
        message_result["msg_label"] = msg_label

        self.pack_correct_button(button_frame, button_frame, button, command)

        err_screen.wait_window()

    def simple_information_message(self, my_window: Union[tk.Tk, tk.Toplevel], title: str = "", message: str = "", button: int = 0, always_on_top: bool = True, command: list = []) -> None:
        """ Display a simple warning message """
        self.basic_message(
            my_window,
            title,
            message,
            button,
            always_on_top,
            self.window_config["information_icon_path"],
            command=command
        )

    def simple_warning_message(self, my_window: Union[tk.Tk, tk.Toplevel], title: str = "", message: str = "", button: int = 0, always_on_top: bool = True, command: list = []) -> None:
        """ Display a simple warning message """
        self.basic_message(
            my_window,
            title,
            message,
            button,
            always_on_top,
            self.window_config["warning_icon_path"],
            command=command
        )

    def simple_err_message(self, my_window: Union[tk.Tk, tk.Toplevel], title: str = "", message: str = "", button: int = 0, always_on_top: bool = True, command: list = []) -> None:
        """ Display a simple error message """
        self.basic_message(
            my_window,
            title,
            message,
            button,
            always_on_top,
            self.window_config["error_icon_path"],
            command=command
        )

    def advanced_err_message(self, parent_window: Union[tk.Tk, tk.Toplevel], title: str = "", message: str = "", button: int = 0, always_on_top: bool = True) -> int:
        """ Display a simple error message """
        self.err_message_print_debug(f"""
title = {title}
message = {message}
button = {button}
always_on_top = {always_on_top}
""")
        self.window = self.init_plain_window(parent_window)
        self.execution_result = 0
        self.simple_err_message(
            my_window=self.window,
            title=title,
            message=message,
            button=button,
            always_on_top=always_on_top,
            command=[self.err_opt1, self.err_opt2, self.err_opt3]
        )
        return self.execution_result

    def advanced_warning_message(self, parent_window: Union[tk.Tk, tk.Toplevel], title: str = "", message: str = "", button: int = 0, always_on_top: bool = True) -> int:
        """ Display a simple error message """
        self.window = self.init_plain_window(parent_window)
        self.execution_result = 0
        self.simple_warning_message(
            my_window=self.window,
            title=title,
            message=message,
            button=button,
            always_on_top=always_on_top,
            command=[self.err_opt1, self.err_opt2, self.err_opt3]
        )
        return self.execution_result

    def advanced_information_message(self, parent_window: Union[tk.Tk, tk.Toplevel], title: str = "", message: str = "", button: int = 0, always_on_top: bool = True) -> int:
        """ Display a simple error message """
        self.window = self.init_plain_window(parent_window)
        self.execution_result = 0
        self.simple_information_message(
            my_window=self.window,
            title=title,
            message=message,
            button=button,
            always_on_top=always_on_top,
            command=[self.err_opt1, self.err_opt2, self.err_opt3]
        )
        return self.execution_result

    def goodbye_message(self, parent_window: Union[tk.Tk, tk.Toplevel]) -> None:
        """ Display a goodbye message """
        my_window = self.init_plain_window(parent_window)
        goodbye_msg = "Goodbye, see you next time!"
        goodbye_button = "Goodbye!"
        self.set_icon(my_window, self.window_config["icon_path"])
        self.init_window(
            my_window,
            "Goodbye!",
            self.bkg,
            200,
            50,
            self.window_config["window_position_x"],
            self.window_config["window_position_y"],
            fullscreen=self.window_config["full_screen"],
            resizable=True
        )
        self.add_label(
            my_window,
            goodbye_msg,
            self.foreground,
            self.bkg,
            len(goodbye_msg),
            1,
            0,
            0,
            tk.TOP,
            "center",
            tk.NONE
        )
        self.add_button(
            my_window,
            goodbye_button,
            self.foreground,
            self.bkg,
            tk.TOP,
            my_window.destroy,
            len(goodbye_button),
            1,
            0,
            0
        )
        my_window.wait_window()

    def all_clear(self, entries: Dict) -> bool:
        """ Check if all the entries have content """
        has_had_errors = False
        for i in enumerate(entries):
            if len(i[1]) < 1:
                msg.showerror(
                    f"Error for: {i[0]}",
                    f"The content of {i[0]} cannot be empty!"
                )
                has_had_errors = True
        if has_had_errors is True:
            return False
        return True


if __name__ == "__main__":
    LORE = False
    print("Please launch the main program")

    FILE_INFO: Dict[str, Dict[str, Any]] = {
        "err_message": {
            "width": 300,
            "height": 110,
            "min_width": 300,
            "min_height": 110,
            "max_width": 1000,
            "max_height": 1000,
            "window_position_x": 0,
            "window_position_y": 0,
            "resizable": True,
            "dark_mode_enabled": False,
            "full_screen": False,
            "dark_mode": {
                "background": "#000000",
                "foreground": "#FFFFFF"
            },
            "light_mode": {
                "background": "#FFFFFF",
                "foreground": "#000000"
            },
            "background": "#000000",
            "foreground": "#FFFFFF",
            "font_size": 12,
            "font_family": "Times New Roman",
            "debug_mode_enabled": False,
            "icon_path": f"{os.path.dirname(os.path.abspath(__file__))}/assets/favicon.ico",
            "button_width": 10,
            "button_height": 1,
            "error_icon_path": f"{os.path.dirname(os.path.abspath(__file__))}/assets/error_64x64.png",
            "warning_icon_path": f"{os.path.dirname(os.path.abspath(__file__))}/assets/warning_64x64.png",
            "information_icon_path": f"{os.path.dirname(os.path.abspath(__file__))}/assets/information_64x64.png",
            "image_width": 64,
            "image_height": 64
        }
    }
    PRINT_DEBUG = False
    if LORE is True:
        FILE_INFO["debug_mode_enabled"] = True
        PRINT_DEBUG = True

    BASE_WINDOW = tk.Tk()
    CWD = os.getcwd()
    EMI = ErrMessages(
        BASE_WINDOW,
        FILE_INFO,
        print_debug=PRINT_DEBUG,
        cwd=CWD
    )
    win = EMI.init_plain_window(BASE_WINDOW)
    win.update()
    EMI.simple_err_message(
        my_window=win,
        title="Test message error",
        message="This is a test message for the error message box",
        button=EMI.button_options["ok"],
        always_on_top=True,
        command=[win.destroy]
    )
    win = EMI.init_plain_window(BASE_WINDOW)
    EMI.simple_warning_message(
        my_window=win,
        title="Test message warning",
        message="This is a test message for the warning message box",
        button=EMI.button_options["ok"],
        always_on_top=True,
        command=[win.destroy]
    )
    EMI.window = EMI.init_plain_window(BASE_WINDOW)
    EMI.simple_information_message(
        my_window=EMI.window,
        title="Test message information",
        message="This is a test message for the inform message box",
        button=EMI.button_options["o/c"],  # button_options["c/a"],
        always_on_top=True,
        command=[EMI.window.destroy, EMI.window.destroy]
    )
    EMI.advanced_warning_message(
        parent_window=BASE_WINDOW,
        title="You have found a corps",
        message="You have found a rotting corps",
        button=EMI.button_options["ok"],
        always_on_top=True
    )
    RESPONSE = EMI.advanced_information_message(
        parent_window=BASE_WINDOW,
        title="Save corps?",
        message="Do you wish to save the rotting corpse to your inventory?",
        button=EMI.button_options["s/d/c"],
        always_on_top=True
    )
    EMI.err_message_print_debug(f"RESPONSE = {RESPONSE}")
    response_sentence = {0: "undefined", 1: "save", 2: "not save", 3: "ignore"}
    if RESPONSE == 0:
        if LORE is True:
            window = EMI.init_plain_window()
        EMI.advanced_err_message(
            parent_window=BASE_WINDOW,
            title="Error",
            message="You have not chosen a response!\nThus, the corpse will be added to your inventory.\nTouth luck bud!",
            button=EMI.button_options["ok"],
            always_on_top=True
        )
    else:
        EMI.advanced_information_message(
            parent_window=BASE_WINDOW,
            title="Your corpsy response",
            message=f"You have chosen to {response_sentence[RESPONSE]} the corpse.",
            button=EMI.button_options["ok"],
            always_on_top=True
        )
    EMI.goodbye_message(parent_window=BASE_WINDOW)
