"""
File in charge of packing a password field
"""

import tkinter as tk


class PasswordEntry(tk.Frame):
    """
    Class in charge of packing a password field
    """

    def __init__(self, window: tk.Tk, text: str = "Password:", width: int = 10, height: int = 1, bkg_window: str = "#FFFFFF", bkg_entry: str = "#000000", fg_window: str = "#000000", fg_entry: str = "#FFFFFF", position_x: int = 0, position_y: int = 0, fill: str = tk.NONE, side: str = tk.LEFT, anchor: str = tk.CENTER, font: tuple = ("Times New Roman", 12), borderwidth: int = 0, relief: str = tk.FLAT, mask_character: str = "*") -> None:
        # ---- General Info ----
        self.error = -1
        self.success = 0

        # ---- GUI elements ----
        # Parent info
        self.window = window
        self.borderwidth = borderwidth
        self.relief = relief
        # Class info
        self.pwd_frame = tk.Frame
        self.pwd_label = tk.Label
        self.pwd_entry = tk.Entry
        self.pwd_button = tk.Button

        # ---- Design ----
        # Colour
        self.bkg_window = bkg_window
        self.bkg_entry = bkg_entry
        self.fg_window = fg_window
        self.fg_entry = fg_entry
        # Label
        self.font = font
        self.text = text
        # Dimensions
        self.width = width
        self.height = height
        # Position
        self.fill = fill
        self.side = side
        self.anchor = anchor
        self.position_y = position_y
        self.position_x = position_x
        # Password mask
        self.mask_character = mask_character
        self.button_placeholder_text = ["Show", "Hide"]
        # Internal padding
        self.iposition_x = 2
        self.iposition_y = 0

        # ---- Tracking Info ----
        self.masked = False

        # ---- Loader ----
        self.main()

    def add_entry(self, window: tk.Tk, text_variable: str = "", width: int = 20, bkg: str = "#FFFFFF", fg: str = "#000000", side: str = tk.LEFT, fill: str = tk.NONE, anchor: str = tk.CENTER, position_x: int = 0, position_y: int = 0, font: tuple = ()) -> tk.Entry:
        """ Add an entry field allowing the user to enter text """
        if isinstance(text_variable, str) == True and text_variable != "":
            tmp = text_variable
            text_variable = tk.StringVar()
            text_variable.set(tmp)

        entree = tk.Entry(
            window,
            textvariable=text_variable,
            width=width,
            bg=bkg,
            fg=fg,
            font=font
        )
        entree.pack(
            side=side,
            fill=fill,
            anchor=anchor,
            padx=position_x,
            pady=position_y
        )
        return entree

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

    def add_label(self, window: tk.Tk, text: str, fg: str, bkg: str, width: int = 50, height: int = 50, position_x: int = 0, position_y: int = 0, side: str = "left", anchor: str = "center", fill: str = tk.NONE, font: tuple = ("Times New Roman", 12)) -> tk.Label:
        """ Add a label to the window """
        Label = tk.Label(
            window,
            text=text,
            fg=fg,
            bg=bkg,
            width=width,
            height=height,
            anchor=anchor,
            font=font
        )
        Label.pack(padx=position_x, pady=position_y, side=side, fill=fill)
        return Label

    def add_button(self, window: tk.Tk, text: str, fg: str, bkg: str, side: str, command: any, width: int = 50, height: int = 50, position_x: int = 0, position_y: int = 0, anchor: str = tk.CENTER, fill: str = tk.NONE, font: tuple = ("Times New Roman", 12)) -> tk.Button:
        """ Add a button to the window """
        button = tk.Button(
            window,
            text=text,
            fg=fg,
            bg=bkg,
            width=width,
            height=height,
            font=font,
            command=command
        )
        button.pack(
            padx=position_x,
            pady=position_y,
            side=side,
            anchor=anchor,
            fill=fill
        )
        return button

    def toggle_view(self) -> None:
        """ Show or Hide the password """
        if self.masked == True:
            self.pwd_entry.config(show="")
            self.pwd_button.config(text=self.button_placeholder_text[-1])
            self.masked = False
        else:
            self.pwd_entry.config(show=self.mask_character)
            self.pwd_button.config(text=self.button_placeholder_text[0])
            self.masked = True

    def get(self) -> str:
        """ Return the content of the entry """
        return self.pwd_entry.get()

    def set(self, text) -> None:
        """ Fill the content of the entry """
        self.pwd_entry.delete(0, tk.END)
        self.pwd_entry.insert(0, text)

    def clear(self) -> None:
        """ Clears the content of the entry """
        self.pwd_entry.delete(0, tk.END)

    def main(self) -> None:
        """ The main function of the program """
        self.pwd_frame = self.add_frame(
            self.window,
            borderwidth=self.borderwidth,
            relief=tk.FLAT,
            bkg=self.bkg_window,
            width=self.width,
            height=self.height,
            position_x=self.position_x,
            position_y=self.position_y,
            side=self.side,
            fill=self.fill,
            anchor=self.anchor
        )
        self.pwd_label = self.add_label(
            self.pwd_frame,
            text=self.text,
            fg=self.fg_window,
            bkg=self.bkg_window,
            width=len(self.text),
            height=self.height,
            position_x=self.iposition_x,
            position_y=self.iposition_y,
            side=tk.LEFT,
            anchor=self.anchor,
            fill=self.fill,
            font=self.font
        )
        self.pwd_entry = self.add_entry(
            self.pwd_frame,
            width=self.width - (
                len(self.text) +
                (self.iposition_x * 2) +
                len(self.button_placeholder_text[0])
            ),
            bkg=self.bkg_entry,
            fg=self.fg_entry,
            side=tk.LEFT,
            fill=self.fill,
            anchor=self.anchor,
            position_x=self.iposition_x,
            position_y=self.iposition_y,
            font=self.font
        )
        self.pwd_button = self.add_button(
            self.pwd_frame,
            text=self.button_placeholder_text[0],
            fg=self.fg_window,
            bkg=self.bkg_window,
            side=tk.RIGHT,
            command=self.toggle_view,
            width=len(self.button_placeholder_text[0]),
            height=self.height,
            position_x=self.iposition_x,
            position_y=self.iposition_y,
            anchor=self.anchor,
            fill=tk.NONE,
            font=self.font
        )
        self.toggle_view()


if __name__ == "__main__":
    TT = tk.Tk()
    password = PasswordEntry(
        TT,
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
    result_label = tk.Label(TT, text="<empty>", bg="white", fg="black")
    result_label.pack()
    but_frame = tk.Frame(TT)
    but_frame.pack(side=tk.TOP, anchor=tk.CENTER)
    tk.Button(but_frame, text="Get", command=get_password).pack(side=tk.LEFT)
    tk.Button(but_frame, text="Set", command=set_password).pack(side=tk.LEFT)
    tk.Button(
        but_frame,
        text="Clear",
        command=clear_password
    ).pack(side=tk.LEFT)
    TT.mainloop()
