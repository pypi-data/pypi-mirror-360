"""
File in charge of inserting a toggle button contained in one button
"""

from functools import partial
import tkinter as tk


class MonoSquareToggleButton:
    """ A multi option toggle switch """

    def __init__(self, window: tk.Tk, width: int = 40, height: int = 1, button_options: list = ["text1", "text2"], posx: int = 0, posy: int = 0, borderwidth: int = 0, relief_button_disabled: str = tk.FLAT, relief_button_active: str = tk.RAISED, bkg_disabled: str = "#666666", bkg_enabled: str = "#FFFFFF", system_fg_col_disabled: str = "#FFFFFF", system_fg_col_active: str = "#FFFFFF", side: str = tk.TOP, fill: str = tk.X, command: partial = None, font: tuple = ("Times New Roman", 12), selected_id: int = 0):
        # ---- General Info ----
        self.error = -1
        self.success = 0

        # ---- GUI elements ----
        self.window = window
        self.width = width
        self.height = height
        self.posy = posy
        self.posx = posx
        self.borderwidth = borderwidth
        self.side = side
        self.font = font
        self.fill = fill

        # ---- Button elements ----
        self.relief_button_active = relief_button_active
        self.relief_button_disabled = relief_button_disabled
        self.options = button_options
        if len(self.options) == 0:
            self.options.append("Placeholder Text")
        self.button = tk.Button
        self.frame = tk.Frame

        # ---- Design ----
        self.bkg_active = bkg_enabled
        self.bkg_disabled = bkg_disabled
        self.system_fg_col_disabled = system_fg_col_disabled
        self.system_fg_col_active = system_fg_col_active

        # ---- Tracking Info ----
        self.selected_id = 0
        if selected_id >= 0 and selected_id < len(button_options):
            self.selected_id = selected_id
        self.enabled = True

        # ---- Automation ----
        self.command = command

        # ---- Loader ----
        self.main()

    def add_button(self, window: tk.Tk, text: str, fg: str, bkg: str, side: any, command: any, width: int = 50, height: int = 50, position_x: int = 0, position_y: int = 0, disabled_foreground: str = "grey", relief: str = [tk.RAISED, tk.GROOVE, tk.FLAT, tk.RIDGE, tk.SOLID], fill: str = tk.X, font:tuple=("Times New Roman", 12)) -> tk.Button:
        """ Add a button to the window """
        if isinstance(relief, list):
            relief = relief[0]
        button = tk.Button(
            window,
            text=text,
            fg=fg,
            bg=bkg,
            width=width,
            height=height,
            disabledforeground=disabled_foreground,
            relief=relief,
            command=command,
            font=font
        )
        button.pack(
            padx=position_x,
            pady=position_y,
            side=side,
            fill=fill
        )
        return button

    def enable(self, enabled: bool = True) -> None:
        """ Set the state of the items """
        self.enabled = enabled
        if enabled == False:
            bg = self.bkg_disabled
            fg = self.system_fg_col_disabled
            relief = self.relief_button_disabled
        else:
            bg = self.bkg_active
            fg = self.system_fg_col_active
            relief = self.relief_button_active
            self.button.config(state=tk.NORMAL)
            self.set_active(self.selected_id)
        self.button.config(
            fg=fg,
            bg=bg,
            relief=relief
        )
        if enabled == False:
            self.button.config(state=tk.DISABLED)

    def is_enabled(self) -> bool:
        """ Return True if the Toggle Buttons are enabled, False if the Toggle Buttons are disabled """
        return self.enabled

    def set_active(self, button_id: int = 0) -> int:
        """ Set the active button """
        if len(self.options) <= button_id or button_id < 0:
            return self.error
        if self.selected_id == len(self.options):
            self.selected_id = 0
        self.button.config(text=self.options[self.selected_id])

    def get_selected_option(self) -> int:
        """ Get the active button id """
        return self.selected_id

    def toggle(self) -> None:
        """ Change the state of """
        if self.enabled == True:
            self.selected_id += 1
            if self.selected_id == len(self.options):
                self.selected_id = 0
            self.button.config(text=self.options[self.selected_id])
            if self.command != None:
                self.command()

    def main(self) -> None:
        """ The main function of the program """
        self.button = self.add_button(
            self.window,
            text=self.options[self.selected_id],
            fg=self.system_fg_col_active,
            bkg=self.bkg_active,
            side=self.side,
            command=self.toggle,
            width=self.width,
            height=self.height,
            position_x=self.posx,
            position_y=self.posy,
            disabled_foreground=self.system_fg_col_active,
            relief=self.relief_button_active,
            fill=self.fill,
            font=self.font
        )


if __name__ == "__main__":
    sys_bkg_col = "#FFFFFF"
    bkg_active = "#1B73BA"
    bkg_inactive = "#666666"
    button_colour = "#FFFFFF"
    width = 65
    height = 35
    radius = 15
    window_width = 200
    window_height = 200
    root = tk.Tk()
    root['bg'] = "black"
    root.geometry(f"{window_width}x{window_height}")
    mono_square_toggle_button = MonoSquareToggleButton(
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
    root.mainloop()
