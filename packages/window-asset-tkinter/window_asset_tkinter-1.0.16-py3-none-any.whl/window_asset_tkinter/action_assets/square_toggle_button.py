"""
File in charge of containing the multi-toggle button asset
"""

import tkinter as tk
from functools import partial


class SquareToggleButton:
    """ A multi option toggle switch """

    def __init__(self, window: tk.Tk, width: int = 20, height: int = 1, button_options: list = ["text1", "text2"], posx: int = 0, posy: int = 0, borderwidth: int = 0, relief_frame: str = tk.FLAT, relief_button_inactive: str = tk.RAISED, relief_button_disabled: str = tk.FLAT, relief_button_active: str = tk.FLAT, system_bkg_col: str = "white", bkg_active: str = "#1B73BA", bkg_inactive: str = "#666666", system_fg_col_inactive: str = "#FFFFFF", system_fg_col_active: str = "#FFFFFF", command: partial = None, default_option:int = 0) -> None:
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
        self.relief_frame = relief_frame

        # ---- Button elements ----
        self.relief_button_active = relief_button_active
        self.relief_button_inactive = relief_button_inactive
        self.relief_button_disabled = relief_button_disabled
        self.button_options = button_options
        self.buttons = []
        self.frame = tk.Frame

        # ---- Design ----
        self.system_bkg_col = system_bkg_col
        self.bkg_active = bkg_active
        self.bkg_inactive = bkg_inactive
        self.system_fg_col_inactive = system_fg_col_inactive
        self.system_fg_col_active = system_fg_col_active

        # ---- Tracking Info ----
        self.selected_id = 0
        if default_option <= len(button_options)-1:
            self.selected_id = default_option
        self.enabled = True

        # ---- Automation ----
        self.command = command

        # ---- Loader ----
        self.main()

    def add_button(self, window: tk.Tk, text: str, fg: str, bkg: str, side: any, command: any, width: int = 50, height: int = 50, position_x: int = 0, position_y: int = 0, disabled_foreground: str = "grey", relief: str = [tk.RAISED, tk.GROOVE, tk.FLAT, tk.RIDGE, tk.SOLID]) -> tk.Button:
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
            command=command
        )
        button.pack(padx=position_x, pady=position_y, side=side)
        return button

    def add_frame(self, window: tk.Tk, borderwidth: int, relief: str, bkg: str, width: int = 50, height: int = 50, position_x: int = 0, position_y: int = 0, side: str = "top", fill: str = tk.BOTH, anchor: str = tk.CENTER) -> tk.Frame:
        """ Add a frame to the window """
        Frame1 = tk.Frame(
            window,
            borderwidth=borderwidth,
            relief=relief,
            bg=bkg,
            width=width,
            height=height
        )
        Frame1.pack(
            padx=position_x,
            pady=position_y,
            side=side,
            fill=fill,
            anchor=anchor
        )
        return Frame1

    def enable(self, enabled: bool = True) -> None:
        """ Set the state of the items """
        self.enabled = enabled
        if enabled == False:
            bg = self.bkg_inactive
            fg = self.system_fg_col_inactive
            relief = self.relief_button_disabled
        else:
            bg = self.bkg_active
            fg = self.system_fg_col_active
            relief = self.relief_button_active
        for i in self.buttons:
            self.enable_item(i, enabled)
            i.config(
                fg=fg,
                bg=bg,
                relief=relief
            )
        if enabled == True:
            self.toggle(self.selected_id)

    def is_enabled(self) -> bool:
        """ Return True if the Toggle Buttons are enabled, False if the Toggle Buttons are disabled """
        return self.enabled

    def set_active(self, button_id: int = 0) -> int:
        """ Set the active button """
        if len(self.buttons) <= button_id or button_id < 0:
            return self.error
        self.toggle(button_id)

    def enable_item(self, button: tk.Button, enable: bool = True) -> None:
        """ Enable or disable a button """
        if enable == True:
            button.config(state=tk.NORMAL)
        else:
            button.config(state=tk.DISABLED)

    def get_selected_option(self) -> int:
        """ Get the active button id """
        return self.selected_id

    def toggle(self, index: int = 0) -> None:
        """ Change the state of """
        if self.enabled == True:
            for button_id, button in enumerate(self.buttons):
                if button_id == index:
                    button.config(
                        bg=self.bkg_active,
                        fg=self.system_fg_col_active,
                        relief=self.relief_button_active
                    )
                    self.enable_item(button, False)
                    self.selected_id = button_id
                else:
                    button.config(
                        bg=self.bkg_inactive,
                        fg=self.system_fg_col_inactive,
                        relief=self.relief_button_inactive
                    )
                    self.enable_item(button, True)
            if self.command != None:
                self.command()

    def main(self) -> None:
        """ The main function of the program """
        self.frame = self.add_frame(
            self.window,
            borderwidth=self.borderwidth,
            relief=self.relief_frame,
            bkg=self.system_bkg_col,
            width=self.width,
            height=self.height,
            position_x=self.posx,
            position_y=self.posy,
            side=tk.TOP,
            fill=tk.NONE,
            anchor=tk.CENTER
        )
        final_width = int(self.width/len(self.button_options))
        for index, content in enumerate(self.button_options):
            command = partial(self.toggle, index)
            button = self.add_button(
                self.frame,
                text=content,
                fg=self.system_fg_col_inactive,
                bkg=self.bkg_inactive,
                side=tk.LEFT,
                command=command,
                width=final_width,
                height=self.height,
                position_x=0,
                position_y=0,
                disabled_foreground=self.system_fg_col_active,
                relief=self.relief_button_inactive
            )
            if index == 0:
                button.config(
                    fg=self.system_fg_col_active,
                    bg=self.bkg_active,
                    relief=self.relief_button_active
                )
                self.enable_item(button, False)
            self.buttons.append(button)


if __name__ == "__main__":
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
    square_toggle_button = SquareToggleButton(
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
    root.mainloop()
