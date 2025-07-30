"""
File in charge of containing the animation buttons (i.e. toggles)
"""

import tkinter as tk
from functools import partial
from .mono_square_toggle_button import MonoSquareToggleButton
from .round_toggle_switch import RoundToggleSwitch
from .square_toggle_button import SquareToggleButton
from .password_entry import PasswordEntry
from .micro_styler import MicroStyler
from .md_to_micro_styler import MdToMicroStyler
from .dict_to_micro_styler import DictToMicroStyler


class ActionAssets:
    """ Class in charge of creating elements with assigned functions to change states """

    def __init__(self) -> None:
        super(ActionAssets, self).__init__()
        self._round_toggle_switch = RoundToggleSwitch
        self._square_toggle_button = SquareToggleButton
        self._mono_square_toggle_button = MonoSquareToggleButton
        self._password_entry = PasswordEntry
        self._micro_styler = MicroStyler
        self._md_to_micro_styler = MdToMicroStyler
        self._dict_to_micro_styler = DictToMicroStyler

    def test(self) -> None:
        """ A function to test the functionalities """
        sys_bkg_col = "#FFFFFF"
        bkg_active = "#1B73BA"
        bkg_inactive = "#666666"
        button_colour = "#FFFFFF"
        width = 65
        height = 35
        radius = 15
        window_width = 200
        window_height = 250
        root = tk.Tk()
        root['bg'] = "black"
        root.geometry(f"{window_width}x{window_height}")
        toggle = self.round_toggle_switch(
            root,
            sys_bkg_col,
            bkg_active,
            bkg_inactive,
            button_colour,
            width,
            height,
            radius
        )
        tk.Button(
            root,
            text="enable toggle switch",
            command=partial(toggle.enabled, True)
        ).pack(side=tk.TOP)
        tk.Button(
            root,
            text="disable toggle switch",
            command=partial(toggle.enabled, False)
        ).pack(side=tk.TOP)
        square_toggle_button = self.square_toggle_button(
            root,
            width=20,
            height=1,
            button_options=[
                "text1", "text2", "text3", "text4"
            ],
            system_bkg_col=sys_bkg_col,
            bkg_active=bkg_active,
            bkg_inactive=bkg_inactive,
            system_fg_col_inactive=button_colour,
            system_fg_col_active=sys_bkg_col
        )
        tk.Button(
            root,
            text="enable toggle button",
            command=partial(square_toggle_button.enable, True)
        ).pack(side=tk.TOP)
        tk.Button(
            root,
            text="disable toggle button",
            command=partial(square_toggle_button.enable, False)
        ).pack(side=tk.TOP)
        mono_square_toggle_button = self.mono_square_toggle_button(
            root,
            width=40,
            height=1,
            button_options=[
                "text1", "text2", "text3", "text4",
                "text5", "text6", "text7", "text8",
                "text9", "text10", "text11", "text12"
            ],
            posx=0,
            posy=0,
            borderwidth=0,
            relief_button_disabled=tk.FLAT,
            relief_button_active=tk.RAISED,
            bkg_disabled=bkg_inactive,
            bkg_enabled=bkg_active,
            system_fg_col_disabled=button_colour,
            system_fg_col_active=button_colour,
            side=tk.TOP,
            fill=tk.X
        )
        tk.Button(
            root,
            text="enable mono toggle button",
            command=partial(mono_square_toggle_button.enable, True)
        ).pack(side=tk.TOP)
        tk.Button(
            root,
            text="disable mono toggle button",
            command=partial(mono_square_toggle_button.enable, False)
        ).pack(side=tk.TOP)
        password = self.password_entry(
            root,
            text="Password:",
            width=50,
            height=1,
            bkg_window="white",
            bkg_entry="white",
            fg_window="black",
            fg_entry="black",
            position_x=0,
            position_y=0,
            fill=tk.NONE,
            side=tk.TOP,
            anchor=tk.CENTER,
            font=("Times New Roman", 12),
            borderwidth=1,
            relief=tk.GROOVE,
            mask_character="*"
        )

        def get_password():
            pswd = password.get()
            print(pswd)
            result_label.config(text=pswd)

        def set_password(): password.set("Sample Text")
        def clear_password(): password.clear()
        result_label = tk.Label(root, text="<empty>", bg="white", fg="black")
        result_label.pack()
        but_frame = tk.Frame(root)
        but_frame.pack(side=tk.TOP, anchor=tk.CENTER)
        tk.Button(
            but_frame,
            text="Get",
            command=get_password
        ).pack(side=tk.LEFT)
        tk.Button(
            but_frame,
            text="Set",
            command=set_password
        ).pack(side=tk.LEFT)
        tk.Button(
            but_frame,
            text="Clear",
            command=clear_password
        ).pack(side=tk.LEFT)
        root.mainloop()
