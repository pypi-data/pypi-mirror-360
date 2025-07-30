"""
File in charge of containing the class in charge of simplifying the styling of the text input
"""

import tkinter as tk
import webbrowser
from functools import partial
from tkinter.font import Font


class MicroStyler:
    """ The class in charge of containing the code for viewing text styling """

    def __init__(self, frame: tk.Frame or tk.Tk, fg: str = "black", bkg: str = "white", height: int = 10, width: int = 10, padx_text: int = 0, pady_text: int = 0, block_cursor: bool = False, font: tuple = (), cursor: str = "xterm", export_selection: bool = True, highlight_colour: str = "#0077FF",  relief: str = tk.GROOVE, undo: bool = True, wrap: str = "word", fill: str = tk.BOTH, side: str = tk.TOP, padx_pack: int = 0, pady_pack: int = 0, ipadx: int = 1, ipady: int = 1, content: list[dict[str, any]] = [{"text": "sample_text", "style": "B"}], emoji_dict: dict = {}, row:int=-1, column:int=-1) -> None:
        # ---- Constants ----
        self.success = 0
        self.err = 84
        # ---- Text customisations ----
        # dictionnary options
        self.dict_text_input = "text"
        self.dict_font_style = "style"
        self.dict_font_size = "size"
        self.dict_font_family = "family"
        self.dict_font_colour = "colour"
        self.dict_background_colour = "bkg"
        self.dict_foreground_colour = "fg"
        # Special information
        self.dict_special = "special"
        # style options
        self.italic = "I"
        self.bold = "B"
        self.underline = "U"
        self.strike = "S"

        # ---- Action codes ----
        self.dict_type = "type"
        self.dict_type_legend = "type_legend"
        self.dict_function = "function"
        self.dict_hyperlink = "hyperlink"
        self.dict_hyperlink_legend = "hyperlink_legend"
        self.dict_image_url = "image_url"
        self.dict_image_legend = "image_legend"
        self.dict_image_width = "image_width"
        self.dict_image_height = "image_height"

        # ---- GUI customisations ----
        self.text = tk.Text

        # GUI parent
        self.frame = frame
        # GUI element default colours
        self.fg = fg
        self.bkg = bkg
        # GUI element dimensions
        self.height = height
        self.width = width
        # GUI text positioning
        self.padx_text = padx_text
        self.pady_text = pady_text
        # GUI mouse interraction
        self.block_cursor = block_cursor
        self.cursor = cursor
        self.export_selection = export_selection
        self.highlight_colour = highlight_colour
        # GUI borders
        self.relief = relief
        # GUI text management
        self.font = font
        self.font_family = "Times New Roman"
        self.font_size = 12
        if len(self.font) == 1:
            self.font_family = font[0]
        if len(self.font) == 2:
            self.font_size = font[1]
        self.undo = undo
        self.wrap = wrap
        #  GUI positioning
        self.fill = fill
        self.side = side
        self.padx_pack = padx_pack
        self.pady_pack = pady_pack
        self.ipadx = ipadx
        self.ipady = ipady
        # GUI grid management
        self.row = row
        self.column = column

        # ---- Emoji Dictionnary ----
        self.emoji_dictionnary = emoji_dict

        # ---- User data ----
        self.content = content

        # ---- Data Tracking ----
        self.created_tags = dict()
        self.window_elements = {"text": self.text}

        self.alert_window_response = False
        self.alert_function_to_call = print

        # ---- Loader ----
        self.main()

    def get_class_name(self, class_name: object) -> str:
        """ Return the class name """
        try:
            return class_name.__name__
        except AttributeError:
            return class_name.__class__.__name__

    def process_args(self, args: tuple) -> list[str]:
        """ Return a list of the args """
        res = []
        for arg in args:
            if self.get_class_name(arg) == "partial":
                res.extend(self.get_real_function_name_if_partial(arg))
        return res

    def process_keywords(self, args: tuple) -> list[str]:
        """ Return a list of the args """
        res = []
        for arg in args:
            if self.get_class_name(args[arg]) == "partial":
                res.extend(self.get_real_function_name_if_partial(args[arg]))
        return res

    def get_real_function_name_if_partial(self, class_name: partial or object) -> str:
        """ Return the real function name if the function is a partial """
        classes = []
        break_point = 'func'
        ressearched = 'partial'
        child_name = self.get_class_name(class_name)
        if child_name != ressearched:
            classes.append(child_name)
            return classes
        current_content = dir(class_name)
        current_class = class_name
        while break_point in current_content:
            child_name = self.get_class_name(current_class.func)
            if len(current_class.args) > 0:
                classes.extend(self.process_args(current_class.args))
            if len(current_class.keywords) > 0:
                classes.extend(self.process_keywords(current_class.keywords))
            if ressearched != child_name:
                classes.append(child_name)
                current_class = current_class.func
                return classes
        return classes

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

    def add_button(self, window: tk.Tk, text: str, fg: str, bkg: str, side: str, command: any, width: int = 50, height: int = 50, position_x: int = 0, position_y: int = 0, anchor: str = tk.CENTER, fill: str = tk.NONE) -> tk.Button:
        """ Add a button to the window """
        button = tk.Button(
            window,
            text=text,
            fg=fg,
            bg=bkg,
            width=width,
            height=height,
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
        Frame1.pack(padx=position_x, pady=position_y,
                    side=side, fill=fill, anchor=anchor)
        return Frame1

    def add_labelframe(self, window: tk.Tk, title: str, padding_x: int, padding_y: int, fill: str, expand: str, width: int = 50, height: int = 50) -> tk.LabelFrame:
        """ add a labelframe to the window """
        LabelFrame = tk.LabelFrame(
            window,
            text=title,
            padx=padding_x,
            pady=padding_y,
            width=width,
            height=height
        )
        LabelFrame.pack(fill=fill, expand=expand)
        return LabelFrame

    def add_paragraph_field(self, frame: tk.Frame or tk.Tk, fg: str = "black", bkg: str = "white", height: int = 10, width: int = 10, padx_text: int = 0, pady_text: int = 0, block_cursor: bool = False, font: tuple = (), cursor: str = "xterm", export_selection: bool = True, highlight_colour: str = "#0077FF",  relief: str = tk.GROOVE, undo: bool = True, wrap: str = "word", fill: str = tk.BOTH, side: str = tk.TOP, padx_pack: int = 0, pady_pack: int = 0, ipadx: int = 1, ipady: int = 1, row:int=-1, column:int=-1) -> tk.Text:
        """ add a paragraph (a big zone to enter text) """
        paragraph = tk.Text(
            frame,
            background=bkg,
            foreground=fg,
            blockcursor=block_cursor,
            height=height,
            width=width,
            font=font,
            cursor=cursor,
            exportselection=export_selection,
            highlightcolor=highlight_colour,
            padx=padx_text,
            pady=pady_text,
            relief=relief,
            undo=undo,
            wrap=wrap
        )
        if column >= 0 and row >= 0:
            paragraph.grid(
                row=row,
                column=column,
                padx=padx_pack,
                pady=pady_pack,
                ipadx=ipadx,
                ipady=ipady
            )
        else:
            paragraph.pack(
                fill=fill,
                side=side,
                padx=padx_pack,
                pady=pady_pack,
                ipadx=ipadx,
                ipady=ipady
            )
        return paragraph

    def on_enter(self, *args) -> None:
        """ Change the cursor when the mouse is on the button """
        self.text.config(cursor="hand2")

    def on_leave(self, *args) -> None:
        """ Change the cursor when the mouse is not on the button """
        self.text.config(cursor=self.cursor)

    def open_link_in_new_tab(self, link: str) -> None:
        """ Open a link in a new tab on the users browser """
        return webbrowser.open_new_tab(link)

    def create_alert_window(self) -> None:
        """ Create the alert window to be displayed when a link is clicked """
        alert_width = self.width//6 * 5
        alert_height = self.height//6 * 5
        self.window_elements["alert_window"] = self.add_frame(
            window=self.frame,
            borderwidth=0,
            relief=tk.FLAT,
            bkg=self.fg,
            width=alert_width+10,
            height=alert_height+10,
            position_x=0,
            position_y=0,
            side=tk.TOP,
            fill=tk.BOTH,
            anchor=tk.CENTER
        )
        self.window_elements["alert_window"].pack_forget()
        self.window_elements["alert_frame"] = self.add_frame(
            window=self.window_elements["alert_window"],
            borderwidth=0,
            relief=tk.FLAT,
            bkg=self.bkg,
            width=alert_width,
            height=alert_height,
            position_x=1,
            position_y=1,
            side=tk.TOP,
            fill=tk.X,
            anchor=tk.CENTER
        )
        self.window_elements["alert_label_inform"] = self.add_label(
            window=self.window_elements["alert_frame"],
            text="You are about to open : https://hellmart666.com/",
            fg=self.fg,
            bkg=self.bkg,
            width=alert_width,
            height=1,
            position_x=0,
            position_y=0,
            side=tk.TOP,
            anchor=tk.CENTER,
            fill=tk.BOTH
        )
        self.window_elements["alert_label_question"] = self.add_label(
            window=self.window_elements["alert_frame"],
            text="Are you sure you wish to open this link?",
            fg=self.fg,
            bkg=self.bkg,
            width=alert_width,
            height=1,
            position_x=0,
            position_y=0,
            side=tk.TOP,
            anchor=tk.CENTER,
            fill=tk.BOTH
        )
        self.window_elements["alert_button_yes"] = self.add_button(
            window=self.window_elements["alert_frame"],
            text="Yes",
            fg=self.fg,
            bkg=self.bkg,
            width=10,
            height=1,
            position_x=5,
            position_y=2,
            side=tk.LEFT,
            anchor=tk.CENTER,
            fill=tk.BOTH,
            command=partial(self.close_alert, True)
        )
        self.window_elements["alert_button_no"] = self.add_button(
            window=self.window_elements["alert_frame"],
            text="No",
            fg=self.fg,
            bkg=self.bkg,
            width=10,
            height=1,
            position_x=5,
            position_y=2,
            side=tk.RIGHT,
            anchor=tk.CENTER,
            fill=tk.BOTH,
            command=partial(self.close_alert, False)
        )

    def close_alert(self, button_yes: bool, *args) -> None:
        """ Close the alert window """
        # self.window_elements["alert_frame"].pack_forget()
        self.window_elements["alert_window"].place_forget()
        if button_yes == True:
            self.alert_window_response = True
            self.alert_function_to_call()
        else:
            self.alert_window_response = False

    def update_alert_function_to_call(self, function: object, alert_message: str, *args) -> bool:
        """ Update the function to call when the user clicks yes on the alert window """
        self.alert_function_to_call = function
        return self.alert(alert_message)

    def alert(self, text: str) -> bool:
        """ Inform the user of an something """
        self.window_elements["alert_label_inform"].configure(text=text)
        self.window_elements["alert_window"].place(
            in_=self.text,
            relx=0.5,
            rely=0.5,
            anchor=tk.CENTER
        )

    def check_background_colour(self, usr_input: dict) -> str:
        """ Check if the user has specified a background colour """
        if self.dict_background_colour in usr_input:
            return usr_input[self.dict_background_colour]
        return self.bkg

    def check_foreground_colour(self, usr_input: dict) -> str:
        """ Check if the user has specified a foreground colour """
        if self.dict_foreground_colour in usr_input:
            return usr_input[self.dict_foreground_colour]
        return self.fg

    def check_font_family(self, usr_input: dict) -> str:
        """ Check if the user has specified a font family """
        if self.dict_font_family in usr_input:
            return usr_input[self.dict_font_family]
        return self.font_family

    def check_font_size(self, usr_input: dict) -> int:
        """ Check if the user has specified a font size """
        if self.dict_font_size in usr_input:
            return usr_input[self.dict_font_size]
        return self.font_size

    def check_font_slant(self, usr_input: dict) -> str:
        """ Check if the user has specified a font style """
        if self.dict_font_style in usr_input and "i" in usr_input[self.dict_font_style].lower():
            return "italic"
        return "roman"

    def check_font_weight(self, usr_input: dict) -> str:
        """ Check if the user has specified a font style """
        if self.dict_font_style in usr_input and "b" in usr_input[self.dict_font_style].lower():
            return "bold"
        return "normal"

    def check_font_underline(self, usr_input: dict) -> bool:
        """ Check if the user has specified a font style """
        if self.dict_font_style in usr_input and "u" in usr_input[self.dict_font_style].lower():
            return True
        return False

    def check_if_emoji(self, usr_input: dict) -> bool:
        """ Check if the user has specified a font style """
        if self.dict_special in usr_input and "EMOJI" in usr_input[self.dict_special]:
            return True
        return False

    def check_font_strike(self, usr_input: dict) -> bool:
        """ Check if the user has specified a font style """
        if self.dict_font_style in usr_input and "s" in usr_input[self.dict_font_style].lower():
            return True
        return False

    def process_hyperlink(self, usr_input: dict, index: int) -> str:
        """ Check if the user has specified a hyperlink """
        link = ""
        legend = "<your_link>"
        if self.dict_hyperlink in usr_input:
            link = usr_input[self.dict_hyperlink]
            if isinstance(link, str) == True:
                legend = link
                link = partial(self.open_link_in_new_tab, link)
                link = partial(
                    self.update_alert_function_to_call,
                    link,
                    f"Do you wish to open: {str(legend)}"
                )
            elif callable(link) == True:
                legend = self.get_real_function_name_if_partial(link)
                if len(legend) == 1:
                    legend = legend[0]
                link = partial(
                    self.update_alert_function_to_call,
                    link,
                    f"Are you sure you wish to run this function {legend}?"
                )
            else:
                link = partial(
                    self.update_alert_function_to_call,
                    print,
                    f"You are attempting to open '{link}' which is not reccognised as a link or function",
                )
        if self.dict_hyperlink_legend in usr_input:
            legend = usr_input[self.dict_hyperlink_legend]

        legend = str(legend)
        link_tag = f"link{index}"
        if link != "":
            font = Font(
                family=self.check_font_family(usr_input),
                size=self.check_font_size(usr_input),
                slant=self.check_font_slant(usr_input),
                weight=self.check_font_weight(usr_input),
                underline=True,
                overstrike=self.check_font_strike(usr_input)
            )
            self.text.tag_configure(
                link_tag,
                foreground="#0077FF",
                font=font,
                underline=True,
                background=self.check_background_colour(usr_input)
            )
            self.text.tag_bind(
                link_tag,
                "<Enter>",
                self.on_enter
            )
            self.text.tag_bind(
                link_tag,
                "<Leave>",
                self.on_leave
            )
            self.text.tag_bind(link_tag, "<Button-1>", link)
            self.text.insert(tk.END, f"{legend}", link_tag)
        elif link == "" and legend != "<your_link>":
            font = Font(
                family=self.check_font_family(usr_input),
                size=self.check_font_size(usr_input),
                slant=self.check_font_slant(usr_input),
                weight=self.check_font_weight(usr_input),
                underline=True,
                overstrike=True
            )
            self.text.tag_configure(
                link_tag,
                foreground="#F33446",
                font=font,
                underline=True,
                background=self.bkg
            )
            self.text.insert(tk.END, f"{legend} (<error:{index}>)", link_tag)

    def process_user_input(self, usr_input: dict, index: int) -> str:
        """ Take a list of elements that are required in the window and add them with the appropriate style """
        tag = f"P{index}"
        font = Font(
            family=self.check_font_family(usr_input),
            size=self.check_font_size(usr_input),
            slant=self.check_font_slant(usr_input),
            weight=self.check_font_weight(usr_input),
            underline=self.check_font_underline(usr_input),
            overstrike=self.check_font_strike(usr_input)
        )
        self.text.tag_configure(
            tag,
            background=self.check_background_colour(usr_input),
            foreground=self.check_foreground_colour(usr_input),
            font=font
        )
        return tag

    def process_user_input_list(self) -> None:
        """ Take a list of elements that are required in the window and add them with the appropriate style """
        for index, content in enumerate(self.content):
            tag_name = self.process_user_input(content, index)
            if self.check_if_emoji(content) == True:
                if content[self.dict_text_input] in self.emoji_dictionnary:
                    self.text.insert(
                        tk.END,
                        self.emoji_dictionnary[content[self.dict_text_input]],
                        tag_name
                    )
                else:
                    self.text.insert(
                        tk.END,
                        content[self.dict_text_input],
                        tag_name
                    )
            elif self.dict_text_input in content:
                self.text.insert(
                    tk.END,
                    str(content[self.dict_text_input]),
                    tag_name
                )
            self.process_hyperlink(content, index)

    def main(self) -> None:
        """ The main function of the class """
        self.text = self.add_paragraph_field(
            frame=self.frame,
            fg=self.fg,
            bkg=self.bkg,
            height=self.height,
            width=self.width,
            padx_text=self.padx_text,
            pady_text=self.pady_text,
            block_cursor=self.block_cursor,
            font=self.font,
            cursor=self.cursor,
            export_selection=self.export_selection,
            highlight_colour=self.highlight_colour,
            relief=self.relief,
            undo=self.undo,
            wrap=self.wrap,
            fill=self.fill,
            side=self.side,
            padx_pack=self.padx_pack,
            pady_pack=self.pady_pack,
            ipadx=self.ipadx,
            ipady=self.ipady,
            column=self.column,
            row=self.row
        )
        self.create_alert_window()
        self.process_user_input_list()
        self.text.config(state=tk.DISABLED)


if __name__ == "__main__":
    def hello_world(parent_window: tk.Toplevel, *args) -> None:
        TTT = tk.Toplevel(parent_window)
        tk.Label(TTT, text="Hello World !").pack(side=tk.TOP)
        tk.Button(TTT, text="Close", command=TTT.destroy).pack(side=tk.TOP)
        TTT.wait_window()

    TT = tk.Tk()
    data = [
        {"text": "Lorem Ipsum Sit Dolor Amen\n", "style": "BUIS", "size": "12",
            "family": "Times New Roman", "colour": "#FF00FF", "bkg": "#0000FF", "fg": "#FF0000"},
        {"text": "Lorem Ipsum Sit Dolor Amen\n", "style": "B", "size": "12",
            "family": "Times New Roman", "colour": "#FF00FF", "bkg": "#0000FF", "fg": "#FF0000"},
        {"text": "Lorem Ipsum Sit Dolor Amen\n", "style": "U", "size": "12",
            "family": "Times New Roman", "colour": "#FF00FF", "bkg": "#0000FF", "fg": "#FF0000"},
        {"text": "Lorem Ipsum Sit Dolor Amen\n", "style": "I", "size": "12",
            "family": "Times New Roman", "colour": "#FF00FF", "bkg": "#0000FF", "fg": "#FF0000"},
        {"text": "Lorem Ipsum Sit Dolor Amen\n", "style": "S", "size": "12",
            "family": "Times New Roman", "colour": "#FF00FF", "bkg": "#0000FF", "fg": "#FF0000"},
        {"text": "Lorem Ipsum Sit Dolor Amen\n", "style": "BU", "size": "12",
            "family": "Times New Roman", "colour": "#FF00FF", "bkg": "#0000FF", "fg": "#FF0000"},
        {"text": "Lorem Ipsum Sit Dolor Amen\n", "style": "BI", "size": "12",
            "family": "Times New Roman", "colour": "#FF00FF", "bkg": "#0000FF", "fg": "#FF0000"},
        {"text": "Lorem Ipsum Sit Dolor Amen\n", "style": "BS", "size": "12",
            "family": "Times New Roman", "colour": "#FF00FF", "bkg": "#0000FF", "fg": "#FF0000"},
        {"text": "Lorem Ipsum Sit Dolor Amen\n", "style": "US", "size": "12",
            "family": "Times New Roman", "colour": "#FF00FF", "bkg": "#0000FF", "fg": "#FF0000"},
        {"text": "Lorem Ipsum Sit Dolor Amen\n", "style": "UI", "size": "12",
            "family": "Times New Roman", "colour": "#FF00FF", "bkg": "#0000FF", "fg": "#FF0000"},
        {"text": "Lorem Ipsum Sit Dolor Amen\n", "style": "SI", "size": "12",
            "family": "Times New Roman", "colour": "#FF00FF", "bkg": "#0000FF", "fg": "#FF0000"},
        {"text": "Lorem Ipsum Sit Dolor Amen\n", "style": "BUS", "size": "12",
            "family": "Times New Roman", "colour": "#FF00FF", "bkg": "#0000FF", "fg": "#FF0000"},
        {"text": "Lorem Ipsum Sit Dolor Amen\n", "style": "BUI", "size": "12",
            "family": "Times New Roman", "colour": "#FF00FF", "bkg": "#0000FF", "fg": "#FF0000"},
        {"text": "Lorem Ipsum Sit Dolor Amen\n", "style": "BSI", "size": "12",
            "family": "Times New Roman", "colour": "#FF00FF", "bkg": "#0000FF", "fg": "#FF0000"},
        {"text": "Lorem Ipsum Sit Dolor Amen\n", "style": "USI", "size": "12",
            "family": "Times New Roman", "colour": "#FF00FF", "bkg": "#0000FF", "fg": "#FF0000"},
        {"text": "Lorem Ipsum Sit Dolor Amen\n", "style": "BUSI", "size": "12",
            "family": "Times New Roman", "colour": "#FF00FF", "bkg": "#0000FF", "fg": "#FF0000"},
        {"text": "Lorem Ipsum Sit Dolor Amen\n", "style": "B", "size": "14",
            "family": "Arial", "colour": "#00FF00", "bkg": "#FF00FF", "fg": "#0000FF"},
        {"text": "Lorem Ipsum Sit Dolor Amen\n", "style": "I", "size": "16",
            "family": "Courier New", "colour": "#FFFF00", "bkg": "#00FFFF", "fg": "#FF00FF"},
        {"text": "Lorem Ipsum Sit Dolor Amen\n", "style": "U", "size": "18",
            "family": "Verdana", "colour": "#0000FF", "bkg": "#FF0000", "fg": "#00FF00"},
        {"text": "Lorem Ipsum Sit Dolor Amen\n", "style": "S", "size": "20",
            "family": "Georgia", "colour": "#00FFFF", "bkg": "#FFFF00", "fg": "#FF00FF"},
        {"text": "Lorem Ipsum Sit Dolor Amen\n", "style": "BI", "size": "22",
            "family": "Impact", "colour": "#FF00FF", "bkg": "#00FF00", "fg": "#FFFF00"},
        {"text": "Lorem Ipsum Sit Dolor Amen :", "style": "", "size": "22", "family": "Verdana", "colour": "#0000EE",
            "bkg": "#CD5D5D", "fg": "#45A945", "hyperlink": partial(hello_world, TT), "hyperlink_legend": "Hello World !"},
        {"text": "\nLorem Ipsum Sit Dolor Amen :", "style": "", "size": "22", "family": "Verdana", "colour": "#0000CC",
            "bkg": "#CD5D5D", "fg": "#45A945", "hyperlink": partial(hello_world, TT)},
        {"text": "\nLorem Ipsum Sit Dolor Amen :", "style": "", "size": "22", "family": "Verdana", "colour": "#0000AA",
            "bkg": "#CD5D5D", "fg": "#45A945", "hyperlink_legend": "Hello World !"}
    ]
    MSI = MicroStyler(
        TT,
        fg='black',
        bkg='white',
        height=10,
        width=50,
        padx_text=5,
        pady_text=5,
        block_cursor=False,
        font=('Arial', 12),
        cursor='xterm',
        export_selection=True,
        highlight_colour='blue',
        relief=tk.SUNKEN,
        undo=True,
        wrap=tk.WORD,
        fill=tk.BOTH,
        side=tk.TOP,
        padx_pack=0,
        pady_pack=0,
        ipadx=0,
        ipady=0,
        content=data
    )
    TT.wait_window()
