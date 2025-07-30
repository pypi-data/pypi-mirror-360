"""
File in charge of containing the class that ad GUI elements ot other GUI elements
"""

import os
from typing import Union, Any, Tuple, Dict, List

import tkinter as tk
from tkinter import ttk
from tkcalendar import DateEntry

if __name__ == "__main__":
    import internal_typing as it
    from unsorted import static_create_text_variable, static_load_image
else:
    from . import internal_typing as it
    from .unsorted import static_create_text_variable, static_load_image


class Add:
    """ The class in charge of adding a GUI element to other GUI elements """

    @staticmethod
    def add_label(window: Union[tk.Misc, tk.PanedWindow, tk.Frame, tk.LabelFrame, tk.Toplevel, tk.Tk], text: str, fg: str, bkg: str, width: int = 50, height: int = 50, position_x: int = 0, position_y: int = 0, side: it.TK_SIDE_TYPE = tk.LEFT, anchor: it.TK_ANCHOR_TYPE = "center", fill: str = tk.NONE, font: Union[Tuple, str] = ("Times New Roman", 12), grid_row: int = -1, grid_column: int = -1, grid_column_span: int = -1) -> tk.Label:
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
        if grid_row > -1 and grid_column > -1:
            grid_column_span = max(grid_column_span, 1)
            Label.grid(
                row=grid_row,
                column=grid_column,
                columnspan=grid_column_span
            )
        else:
            Label.pack(padx=position_x, pady=position_y, side=side, fill=fill)
        return Label

    @staticmethod
    def add_button(window: Union[tk.Misc, tk.PanedWindow, tk.Frame, tk.LabelFrame, tk.Toplevel, tk.Tk], text: str, fg: str, bkg: str, side: it.TK_SIDE_TYPE, command: Any, width: int = 50, height: int = 50, position_x: int = 0, position_y: int = 0, anchor: it.TK_ANCHOR_TYPE = tk.CENTER, fill: str = tk.NONE, column: int = -1, row: int = -1, column_span: int = 1) -> tk.Button:
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
        if column > (-1) and row > (-1):
            if column_span < 1:
                column_span = 1
            button.grid_configure(
                column=column,
                row=row,
                columnspan=column_span
            )
        else:
            button.pack(
                padx=position_x,
                pady=position_y,
                side=side,
                anchor=anchor,
                fill=fill
            )
        return button

    @staticmethod
    def add_frame(window: Union[tk.Misc, tk.PanedWindow, tk.Frame, tk.LabelFrame, tk.Toplevel, tk.Tk], borderwidth: int, relief: str, bkg: str, width: int = 50, height: int = 50, position_x: int = 0, position_y: int = 0, side: it.TK_SIDE_TYPE = tk.TOP, fill: str = tk.BOTH, anchor:  it.TK_ANCHOR_TYPE = tk.CENTER, grid_row: int = -1, grid_column: int = -1, grid_column_span: int = -1) -> tk.Frame:
        """ Add a frame to the window """
        Frame1 = tk.Frame(
            window,
            borderwidth=borderwidth,
            relief=relief,
            bg=bkg,
            width=width,
            height=height
        )
        if grid_row > -1 and grid_column > -1:
            grid_column_span = max(grid_column_span, 1)
            Frame1.grid(
                row=grid_row,
                column=grid_column,
                columnspan=grid_column_span
            )
        else:
            Frame1.pack(
                padx=position_x,
                pady=position_y,
                side=side,
                fill=fill,
                anchor=anchor
            )
        return Frame1

    @staticmethod
    def add_labelframe(window: Union[tk.Misc, tk.PanedWindow, tk.Frame, tk.LabelFrame, tk.Toplevel, tk.Tk], title: str, padding_x: int, padding_y: int, fill: str, expand: bool, width: int = 50, height: int = 50, bkg: str = "#FFFFFF", fg: str = "#000000", font: Union[Tuple, str] = ("Times New Roman", 12), side: it.TK_SIDE_TYPE = tk.TOP, anchor: it.TK_ANCHOR_TYPE = tk.CENTER, grid_row: int = -1, grid_column: int = -1, grid_column_span: int = -1) -> tk.LabelFrame:
        """ add a labelframe to the window """
        LabelFrame = tk.LabelFrame(
            window,
            text=title,
            padx=padding_x,
            pady=padding_y,
            width=width,
            height=height,
            bg=bkg,
            fg=fg,
            font=font
        )

        if grid_row > -1 and grid_column > -1:
            grid_column_span = max(grid_column_span, 1)
            LabelFrame.grid(
                row=grid_row,
                column=grid_column,
                columnspan=grid_column_span
            )
        else:
            LabelFrame.pack(fill=fill, expand=expand, side=side, anchor=anchor)
        return LabelFrame

    @staticmethod
    def add_spinbox(window: Union[tk.Misc, tk.PanedWindow, tk.Frame, tk.LabelFrame, tk.Toplevel, tk.Tk], minimum: int, maximum: int, bkg: str, fg: str, width: int = 50, height: int = 50, position_x: int = 0, position_y: int = 0, grid_row: int = -1, grid_column: int = -1, grid_column_span: int = -1) -> tk.Spinbox:
        """ Add a spinbox to the window """
        spin = tk.Spinbox(
            window,
            from_=minimum,
            to=maximum,
            fg=fg,
            bg=bkg,
            width=width
        )

        if grid_row > -1 and grid_column > -1:
            grid_column_span = max(grid_column_span, 1)
            spin.grid(
                row=grid_row,
                column=grid_column,
                columnspan=grid_column_span
            )
        else:
            spin.pack(padx=position_x, pady=position_y)
        return spin

    @staticmethod
    def add_entry(window: Union[tk.Misc, tk.PanedWindow, tk.Frame, tk.LabelFrame, tk.Toplevel, tk.Tk], text_variable: Union[tk.StringVar, str] = "", width: int = 20, bkg: str = "#FFFFFF", fg: str = "#000000", side: it.TK_SIDE_TYPE = tk.LEFT, fill: str = tk.NONE, anchor:  it.TK_ANCHOR_TYPE = tk.CENTER, position_x: int = 0, position_y: int = 0, font: Union[Tuple, str] = ("Times New Roman", 12), grid_row: int = -1, grid_column: int = -1, grid_column_span: int = -1) -> tk.Entry:
        """ Add an entry field allowing the user to enter text """
        if isinstance(text_variable, str) is True:
            text_variable_internal: tk.StringVar = tk.StringVar()
            text_variable_internal.set(text_variable)
        else:
            text_variable_internal: tk.StringVar = text_variable

        entree = tk.Entry(
            window,
            textvariable=text_variable,
            width=width,
            bg=bkg,
            fg=fg,
            font=font
        )

        if grid_row > -1 and grid_column > -1:
            grid_column_span = max(grid_column_span, 1)
            entree.grid(
                row=grid_row,
                column=grid_column,
                columnspan=grid_column_span
            )
        else:
            entree.pack(
                side=side,
                fill=fill,
                anchor=anchor,
                padx=position_x,
                pady=position_y
            )
        return entree

    @staticmethod
    def add_paned_window(window: Union[tk.Misc, tk.PanedWindow, tk.Frame, tk.LabelFrame, tk.Toplevel, tk.Tk], orientation: str, side: it.TK_SIDE_TYPE, expand: bool, fill: str, vertical_padding: int, horizontal_padding: int, width: int = 50, height: int = 50, relief: str = tk.GROOVE, borderwidth: int = 0, name: str = "", cursor: str = "", grid_row: int = -1, grid_column: int = -1, grid_column_span: int = -1) -> tk.PanedWindow:
        """ Add a paned window to the parent window, and configure orientation """
        panned_window = tk.PanedWindow(
            window,
            orient=orientation,
            borderwidth=borderwidth,
            relief=relief,
            width=width,
            height=height,
            name=name,
            cursor=cursor
            # master: Misc | None=None,
            # cnf: dict[str, Any] | None={},
            # *,
            # background: str=...,
            # bd: _ScreenUnits=1,
            # bg: str=...,
            # border: _ScreenUnits=1,
            # borderwidth: _ScreenUnits=1,
            # cursor: _Cursor="",
            # handlepad: _ScreenUnits=8,
            # handlesize: _ScreenUnits=8,
            # height: _ScreenUnits="",
            # name: str=...,
            # opaqueresize: bool=True,
            # orient: Literal['horizontal', 'vertical']="horizontal",
            # proxybackground: str="",
            # proxyborderwidth: _ScreenUnits=2,
            # proxyrelief: _Relief="flat",
            # relief: _Relief="flat",
            # sashcursor: _Cursor="",
            # sashpad: _ScreenUnits=0,
            # sashrelief: _Relief="flat",
            # sashwidth: _ScreenUnits=3,
            # showhandle: bool=False,
            # width: _ScreenUnits=""
        )
        if grid_row > -1 and grid_column > -1:
            grid_column_span = max(grid_column_span, 1)
            panned_window.grid(
                row=grid_row,
                column=grid_column,
                columnspan=grid_column_span
            )
        else:
            panned_window.pack(
                side=side,
                expand=expand,
                fill=fill,
                pady=vertical_padding,
                padx=horizontal_padding
            )
        return panned_window

    @staticmethod
    def add_panned_window_node(panned_window: tk.PanedWindow, frame_window: Union[tk.Widget, tk.Frame, tk.LabelFrame]) -> None:
        """ Add a node to the Paned window """
        panned_window.add(frame_window)
        panned_window.pack()
        panned_window.update()

    @staticmethod
    def add_date_field(window: Union[tk.Misc, tk.PanedWindow, tk.Frame, tk.LabelFrame, tk.Toplevel, tk.Tk], width: int = 16, date_pattern: str = "dd/MM/yyyy", selectmode: str = "day", pady: int = 0, padx: int = 0, bkg: str = "black", fg: str = "white", borderwidth: int = 2, side: it.TK_SIDE_TYPE = tk.LEFT, fill: str = tk.NONE, grid_row: int = -1, grid_column: int = -1, grid_column_span: int = -1) -> DateEntry:
        """ Add a date field allowing date selection """
        cal = DateEntry(
            window,
            width=width,
            background=bkg,
            foreground=fg,
            bd=borderwidth,
            selectmode=selectmode,
            date_pattern=date_pattern
        )

        if grid_row > -1 and grid_column > -1:
            grid_column_span = max(grid_column_span, 1)
            cal.grid(
                row=grid_row,
                column=grid_column,
                columnspan=grid_column_span
            )
        else:
            cal.pack(
                pady=pady,
                padx=padx,
                side=side,
                fill=fill
            )
        return cal

    @staticmethod
    def add_dropdown(window: Union[tk.Misc, tk.PanedWindow, tk.Frame, tk.LabelFrame, tk.Toplevel, tk.Tk], elements: List[str], state: str = "readonly", padx: int = 0, pady: int = 0, anchor:  it.TK_ANCHOR_TYPE = "e", side: it.TK_SIDE_TYPE = tk.TOP, default_choice: int = 0, fill: str = tk.NONE, bkg: str = "#FFFFFF", fg: str = "#000000", font: Union[Tuple, str] = ("Times New Roman", 12), height: int = 1, width: int = 4, grid_row: int = -1, grid_column: int = -1, grid_column_span: int = -1) -> ttk.Combobox:
        """ generate a drop down menu for a window """
        combo = ttk.Combobox(
            window,
            state=state,
            values=elements,
            background=bkg,
            foreground=fg,
            font=font,
            height=height,
            width=width
        )
        combo.current(default_choice)
        if grid_row > -1 and grid_column > -1:
            grid_column_span = max(grid_column_span, 1)
            combo.grid(
                row=grid_row,
                column=grid_column,
                columnspan=grid_column_span
            )
        else:
            combo.pack(
                padx=padx,
                pady=pady,
                anchor=anchor,
                fill=fill,
                side=side
            )
        return combo

    def add_get_data(self, parent_frame: Union[tk.Frame, tk.LabelFrame], window_width: int, window_height: int, bkg: str, fg: str, label_description: str, button_command: object, grid_row: int = -1, grid_column: int = -1, grid_column_span: int = -1) -> Dict[str, Any]:
        """ generate a filepath gathering section """
        result = {}
        button_description = "..."
        description_entry_width = int(
            window_width - (
                len(label_description) + len(button_description) + 4
            )
        )
        data_frame_height = (window_height - 2)
        result['data_frame'] = self.add_frame(
            window=parent_frame,
            borderwidth=0,
            relief=tk.FLAT,
            bkg=bkg,
            width=window_width,
            height=window_height,
            position_x=0,
            position_y=0,
            grid_row=grid_row,
            grid_column=grid_column,
            grid_column_span=grid_column_span
        )
        result['description_label'] = self.add_label(
            result['data_frame'],
            label_description,
            fg,
            bkg,
            len(label_description) + 2,
            data_frame_height,
            0,
            0,
            tk.LEFT
        )
        result['description_button'] = self.add_button(
            result['data_frame'],
            button_description,
            fg,
            bkg,
            tk.RIGHT,
            button_command,
            len(button_description) + 2,
            1,
            4,
            0
        )
        result['text_var'] = static_create_text_variable("")
        result['description_entry'] = self.add_paragraph_field(
            frame=result['data_frame'],
            fg=fg,
            bkg=bkg,
            height=10,
            width=description_entry_width,
            side=tk.LEFT
        )
        # result['text_var'],
        return result

    @staticmethod
    def add_paragraph_field(frame: Union[tk.Misc, tk.PanedWindow, tk.Frame, tk.LabelFrame, tk.Toplevel, tk.Tk], fg: str = "black", bkg: str = "white", height: int = 10, width: int = 10, padx_text: int = 0, pady_text: int = 0, block_cursor: bool = False, font: Union[Tuple, str] = ("Times New Roman", 12), cursor: str = "xterm", export_selection: bool = True, highlight_colour: str = "#0077FF",  relief: str = tk.GROOVE, undo: bool = True, wrap: str = "word", fill: str = tk.BOTH, side: it.TK_SIDE_TYPE = tk.TOP, padx_pack: int = 0, pady_pack: int = 0, ipadx: int = 1, ipady: int = 1, grid_row: int = -1, grid_column: int = -1, grid_column_span: int = -1) -> tk.Text:
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
        if grid_row > -1 and grid_column > -1:
            grid_column_span = max(grid_column_span, 1)
            paragraph.grid(
                row=grid_row,
                column=grid_column,
                columnspan=grid_column_span
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

    def add_text_field(self, frame: Union[tk.Misc, tk.PanedWindow, tk.Frame, tk.LabelFrame, tk.Toplevel, tk.Tk], fg: str = "black", bkg: str = "white", height: int = 10, width: int = 10, padx_text: int = 0, pady_text: int = 0, block_cursor: bool = False, font: Union[Tuple, str] = ("Times New Roman", 12), cursor: str = "xterm", export_selection: bool = True, highlight_colour: str = "#0077FF",  relief: str = tk.GROOVE, undo: bool = True, wrap: str = "word", fill: str = tk.BOTH, side: it.TK_SIDE_TYPE = tk.TOP, padx_pack: int = 0, pady_pack: int = 0, ipadx: int = 1, ipady: int = 1, grid_row: int = -1, grid_column: int = -1, grid_column_span: int = -1) -> tk.Text:
        """ add a paragraph (a big zone to enter text) """
        return self.add_paragraph_field(
            frame,
            fg,
            bkg,
            height,
            width,
            padx_text,
            pady_text,
            block_cursor,
            font,
            cursor,
            export_selection,
            highlight_colour,
            relief,
            undo,
            wrap,
            fill,
            side,
            padx_pack,
            pady_pack,
            ipadx,
            ipady,
            grid_row,
            grid_column,
            grid_column_span
        )

    def add_grid(self, window: Union[tk.Misc, tk.PanedWindow, tk.Frame, tk.LabelFrame, tk.Toplevel, tk.Tk], borderwidth: int, relief: str, bkg: str, width: int = 50, height: int = 50, position_x: int = 0, position_y: int = 0, side: it.TK_SIDE_TYPE = tk.TOP, grid_row: int = -1, grid_column: int = -1, grid_column_span: int = -1) -> tk.Frame:
        """ add a grid to a frame """
        frame = self.add_frame(
            window,
            borderwidth,
            relief,
            bkg,
            width,
            height,
            position_x,
            position_y,
            side,
            grid_column=grid_column,
            grid_row=grid_row,
            grid_column_span=grid_column_span
        )
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(0, weight=1)
        return frame

    def add_scrollbox(self, window: Union[tk.Misc, tk.PanedWindow, tk.Frame, tk.LabelFrame, tk.Toplevel, tk.Tk], grid_borderwidth: int, grid_relief: str, grid_bkg: str, grid_width: int = 50, grid_height: int = 50, grid_position_x: int = 0, grid_position_y: int = 0, grid_side: it.TK_SIDE_TYPE = tk.TOP, paragraph_fg: str = "black", paragraph_bkg: str = "white", paragraph_height: int = 10, paragraph_width: int = 10, paragraph_padx_text: int = 0, paragraph_pady_text: int = 0, paragraph_block_cursor: bool = False, paragraph_font: Union[Tuple, str] = ("Times New Roman", 12), paragraph_cursor: str = "xterm", paragraph_export_selection: bool = True, paragraph_highlight_colour: str = "#0077FF",  paragraph_relief: str = tk.GROOVE, paragraph_undo: bool = True, paragraph_wrap: str = "word", paragraph_fill: str = tk.BOTH, paragraph_side: it.TK_SIDE_TYPE = tk.TOP, paragraph_padx_pack: int = 0, paragraph_pady_pack: int = 0, paragraph_ipadx: int = 1, paragraph_ipady: int = 1, scroll_orientation: str = tk.VERTICAL, grid_row: int = -1, grid_column: int = -1, grid_column_span: int = -1) -> Dict[str, Any]:
        """ Add a scrollbar to a text entity """
        result = {}
        result["grid"] = self.add_grid(
            window,
            grid_borderwidth,
            grid_relief,
            grid_bkg,
            grid_width,
            grid_height,
            grid_position_x,
            grid_position_y,
            grid_side,
            grid_row=grid_row,
            grid_column=grid_column,
            grid_column_span=grid_column_span
        )
        result["paragraph"] = self.add_paragraph_field(
            frame=result["grid"],
            fg=paragraph_fg,
            bkg=paragraph_bkg,
            height=paragraph_height,
            width=paragraph_width,
            padx_text=paragraph_padx_text,
            pady_text=paragraph_pady_text,
            block_cursor=paragraph_block_cursor,
            font=paragraph_font,
            cursor=paragraph_cursor,
            export_selection=paragraph_export_selection,
            highlight_colour=paragraph_highlight_colour,
            relief=paragraph_relief,
            undo=paragraph_undo,
            wrap=paragraph_wrap,
            fill=paragraph_fill,
            side=paragraph_side,
            padx_pack=paragraph_padx_pack,
            pady_pack=paragraph_pady_pack,
            ipadx=paragraph_ipadx,
            ipady=paragraph_ipady
        )
        result["paragraph"].grid(row=0, column=0, sticky=tk.NS)
        result["scrollbar"] = ttk.Scrollbar(
            result["grid"],
            orient=scroll_orientation,
            command=result["paragraph"].yview
        )
        result["scrollbar"].grid(row=0, column=1, sticky=tk.NS)
        result["paragraph"]['yscrollcommand'] = result["scrollbar"].set
        return result

    @staticmethod
    def add_scroll_bar(frame: Union[tk.Misc, tk.PanedWindow, tk.Frame, tk.LabelFrame, tk.Toplevel, tk.Tk], tk_field: tk.Text, scroll_orientation: it.TK_SCROLL_ORIENTATION_TYPE = tk.VERTICAL, fill: str = tk.BOTH, side: it.TK_SIDE_TYPE = tk.TOP, padx: int = 0, pady: int = 0, anchor:  it.TK_ANCHOR_TYPE = tk.CENTER, row: int = -1, column: int = -1, sticky: str = tk.NS, grid_column_span: int = -1) -> ttk.Scrollbar:
        """ Add a scroll bar to a tkinter asset """
        scroll_bar = ttk.Scrollbar(
            master=frame,
            orient=scroll_orientation,
            command=tk_field.yview
        )
        if row > -1 and column > -1:
            grid_column_span = max(grid_column_span, 1)
            scroll_bar.grid(
                row=row,
                column=column,
                sticky=sticky,
                columnspan=grid_column_span
            )
        else:
            scroll_bar.pack(
                fill=fill,
                side=side,
                padx=padx,
                pady=pady,
                anchor=anchor
            )
        return scroll_bar

    def add_preloaded_image(self, window: Union[tk.Misc, tk.PanedWindow, tk.Frame, tk.LabelFrame, tk.Toplevel, tk.Tk], image_data: Dict, bkg: str = "#FFFFFF", fg: str = "#000000", width: int = 10, height: int = 10, fill: str = tk.BOTH, side: it.TK_SIDE_TYPE = tk.TOP, padx: int = 0, pady: int = 0, anchor:  it.TK_ANCHOR_TYPE = tk.NW, font: Union[Tuple, str] = ("Times New Roman", 12), grid_row: int = -1, grid_column: int = -1, grid_column_span: int = -1) -> Dict[str, Any]:
        """ Add an image to a window """
        result = {}
        ratio = 10
        if "err_message" in image_data:
            err_msg = image_data["err_message"]
            result["Label"] = self.add_label(
                window=window,
                text=err_msg,
                fg=fg,
                bkg=bkg,
                width=int(width/ratio),
                height=height,
                position_x=0,
                position_y=0,
                side=side,
                anchor=anchor,
                fill=fill,
                grid_row=grid_row,
                grid_column=grid_column,
                grid_column_span=grid_column_span
            )
            result["err_message"] = err_msg
            return result
        try:
            result["panel"] = tk.Label(
                window,
                image=image_data["img"],
                width=width,
                height=height
            )
            result["panel"].image = image_data["img"]
            if grid_row > -1 and grid_column > -1:
                grid_column_span = max(grid_column_span, 1)
                result["panel"].grid(
                    row=grid_row,
                    column=grid_column,
                    columnspan=grid_column_span
                )
            else:
                result["panel"].pack(
                    fill=fill,
                    side=side,
                    padx=padx,
                    pady=pady,
                    anchor=anchor
                )
            result["panel"].config(bg=bkg)
            result["img"] = image_data["img"]
        except Exception as error:
            result = {}
            result["err_message"] = f"""
            Error adding image to message box.
            Think to check if the window wasn't initialised twice.
            error = {error}
            """
            result["placeholder"] = self.add_paragraph_field(
                frame=window,
                fg=fg,
                bkg=bkg,
                height=len(result["err_message"].split("\n")),
                width=int(width/ratio),
                padx_text=0,
                pady_text=0,
                block_cursor=False,
                font=font,
                cursor="left_ptr",
                export_selection=True,
                highlight_colour=fg,
                relief=tk.FLAT,
                undo=False,
                wrap=tk.WORD,
                fill=tk.BOTH,
                side=tk.LEFT,
                padx_pack=0,
                pady_pack=0,
                ipadx=0,
                ipady=0,
                grid_row=grid_row,
                grid_column=grid_column,
                grid_column_span=grid_column_span
            )
            result["placeholder"].insert(tk.END, result["err_message"])
            result["placeholder"].config(state=tk.DISABLED)
        return result

    def add_watermark(self, window: Union[tk.Misc, tk.PanedWindow, tk.Frame, tk.LabelFrame, tk.Toplevel, tk.Tk], side: it.TK_SIDE_TYPE = tk.BOTTOM, anchor:  it.TK_ANCHOR_TYPE = tk.E, bkg: str = "white", fg: str = "black", font: Union[Tuple, str] = ("Times New Roman", 12), grid_row: int = -1, grid_column: int = -1, grid_column_span: int = -1) -> tk.Label:
        """ Add the watermark to the window """
        text = f"{chr(169)} Created by Henry Letellier"
        watermark = self.add_label(
            window=window,
            text=text,
            bkg=bkg,
            fg=fg,
            width=len(text),
            height=1,
            position_x=0,
            position_y=0,
            side=side,
            anchor=anchor,
            fill=tk.X,
            font=font,
            grid_row=grid_row,
            grid_column=grid_column,
            grid_column_span=grid_column_span
        )
        return watermark

    @staticmethod
    def add_emoji(window: Union[tk.Misc, tk.PanedWindow, tk.Frame, tk.LabelFrame, tk.Toplevel, tk.Tk], text: str, fg: str, bkg: str, width: int = 50, height: int = 50, position_x: int = 0, position_y: int = 0, side: it.TK_SIDE_TYPE = tk.LEFT, anchor:  it.TK_ANCHOR_TYPE = "center", fill: str = tk.NONE, font: Tuple = ("noto-color", 12), grid_row: int = -1, grid_column: int = -1, grid_column_span: int = -1) -> tk.Label:
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
        if grid_row > -1 and grid_column > -1:
            grid_column_span = max(grid_column_span, 1)
            Label.grid(
                row=grid_row,
                column=grid_column,
                columnspan=grid_column_span
            )
        else:
            Label.pack(padx=position_x, pady=position_y, side=side, fill=fill)
        return Label

    def add_image(self, window: Union[tk.Misc, tk.PanedWindow, tk.Frame, tk.LabelFrame, tk.Toplevel, tk.Tk], image_path: str, bkg: str = "#FFFFFF", fg: str = "#000000", width: int = 10, height: int = 10, fill: str = tk.BOTH, side: it.TK_SIDE_TYPE = tk.TOP, padx: int = 0, pady: int = 0, anchor:  it.TK_ANCHOR_TYPE = tk.NW, font: Union[Tuple, str] = ("Times New Roman", 12), grid_row: int = -1, grid_column: int = -1, grid_column_span: int = -1) -> Dict[str, Any]:
        """ Add an image to a window """
        loaded_image = static_load_image(
            image_path=image_path,
            width=width,
            height=height
        )
        result = self.add_preloaded_image(
            window=window,
            image_data=loaded_image,
            bkg=bkg,
            fg=fg,
            width=width,
            height=height,
            fill=fill,
            side=side,
            padx=padx,
            pady=pady,
            anchor=anchor,
            font=font,
            grid_row=grid_row,
            grid_column=grid_column,
            grid_column_span=grid_column_span
        )
        return result


if __name__ == "__main__":
    def test_assets() -> None:
        """ Test the assets """
        window = tk.Tk()
        ai = Add()
        # basic elements
        sample_frame = ai.add_frame(
            window, 0, tk.GROOVE, "orange",
            width=50,
            height=1,
            fill=tk.NONE,
            anchor=tk.N,
            side=tk.TOP
        )
        ai.add_label(
            sample_frame, "Sample label", "black",
            "white", width=10, height=1,
            side=tk.TOP
        )
        ai.add_spinbox(
            window=sample_frame,
            minimum=0,
            maximum=100,
            bkg="white",
            fg="black",
            width=10,
            height=1
        )
        ai.add_entry(
            window=sample_frame,
            text_variable="Sample entry",
            width=20,
            bkg="white",
            fg="black",
            side=tk.TOP,
            position_x=10,
            position_y=2
        )
        sample_labelframe = ai.add_labelframe(
            sample_frame, "Sample labelframe", 10, 10,
            fill=tk.NONE, expand=tk.NO, side=tk.LEFT
        )
        ai.add_button(
            sample_labelframe, "Sample button", "black", "white", tk.LEFT,
            width=10,
            height=1,
            command=lambda: print("Button pressed")
        )
        sample_paned_window = ai.add_paned_window(
            window=window,
            orientation=tk.HORIZONTAL,
            side=tk.TOP,
            expand=tk.YES,
            fill=tk.BOTH,
            vertical_padding=10,
            horizontal_padding=10,
            width=10,
            height=100,
        )
        sample_label_frame_node = ai.add_labelframe(
            window=sample_paned_window,
            title="Paned window",
            padding_x=10,
            padding_y=10,
            fill=tk.NONE,
            expand=tk.YES,
            bkg="white",
            side=tk.TOP
        )
        ai.add_panned_window_node(
            sample_paned_window, sample_label_frame_node
        )
        ai.add_date_field(sample_label_frame_node)
        ai.add_dropdown(
            sample_label_frame_node, ["Option 1", "Option 2", "Option 3"],
            width=10, bkg="white", fg="black"
        )
        sample_text_field = ai.add_text_field(sample_label_frame_node)
        sample_text_field.insert(tk.END, "Sample text for the text field")
        sample_grid_labelframe = ai.add_labelframe(
            window=window,
            title="Sample grid",
            padding_x=10,
            padding_y=10,
            fill=tk.NONE,
            width=10,
            height=10,
            expand=tk.NO,
            side=tk.TOP
        )
        sample_grid = ai.add_grid(
            window=sample_grid_labelframe,
            borderwidth=2,
            relief=tk.GROOVE,
            bkg="white"
        )
        counter = 0
        for i in range(10):
            ai.add_label(
                sample_grid, f"Label {i+1}", "black",
                "white", width=10, height=1,
                position_x=0,
                position_y=0,
                side=tk.TOP,
                grid_column=i - i % 2,
                grid_row=counter
            )
            if i % 2 == 0:
                counter = 1
            else:
                counter = 0
        sample_scrolling = ai.add_labelframe(
            window=window,
            title="Sample scrolling",
            padding_x=10,
            padding_y=10,
            fill=tk.NONE,
            expand=tk.YES,
            bkg="white",
            side=tk.TOP
        )
        sample_scrollbox = ai.add_scrollbox(
            sample_scrolling, 0, tk.FLAT, "white",
            paragraph_height=5, paragraph_width=40,
        )
        sample_scrollbox["paragraph"].insert(
            tk.END, "Sample text for the scroll box.\n\n\n\n\n\nSample text for the scroll box."
        )
        sample_media_title_frame = ai.add_labelframe(
            window=window,
            title="Sample media",
            padding_x=10,
            padding_y=0,
            fill=tk.NONE,
            expand=tk.YES,
            bkg="white",
            side=tk.TOP
        )
        final_path = f"{os.path.dirname(os.path.abspath(__file__))}/../assets/information_64x64.png"
        ai.add_image(
            sample_media_title_frame, final_path,
            width=64, height=64,
            padx=0, pady=0,
            side=tk.LEFT,
        )
        ai.add_emoji(
            sample_media_title_frame, "😀", "black", "white", width=2, height=2,
            position_x=0, position_y=0, side=tk.LEFT
        )
        ai.add_watermark(window)
        window.mainloop()
    test_assets()
