"""
    File in charge of testing the window_asset_tkinter module
"""

from typing import Dict, Any

import os

import tkinter as tk

print(f"__name__ = {__name__}")

try:
    from window_tools import WindowTools
    from err_messages import ErrMessages
    from action_assets import ActionAssets
    from calculate_window_position import CalculateWindowPosition
except ModuleNotFoundError:
    from .window_tools import WindowTools
    from .err_messages import ErrMessages
    from .action_assets import ActionAssets
    from .calculate_window_position import CalculateWindowPosition
except ImportError:
    from .window_tools import WindowTools
    from .err_messages import ErrMessages
    from .action_assets import ActionAssets
    from .calculate_window_position import CalculateWindowPosition

__all__ = [
    "WindowTools",
    "ErrMessages",
    "ActionAssets",
    "CalculateWindowPosition"
]

if __name__ == "__main__":
    file_info: Dict[str, Dict[str, Any]] = {
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

    def test_the_error_message_class() -> None:
        """_summary_
        This is a function in charge of testing the error message class
        """
        lore = False
        print("Please launch the main program")

        print_debug = False
        if lore is True:
            file_info["err_message"]["debug_mode_enabled"] = True
            print_debug = True

        base_window = tk.Tk()
        cwd: str = os.getcwd()
        emi = ErrMessages(
            base_window,
            file_info,
            print_debug=print_debug,
            cwd=cwd
        )
        win = emi.init_plain_window(base_window)
        win.update()
        emi.simple_err_message(
            my_window=win,
            title="Test message error",
            message="This is a test message for the error message box",
            button=emi.button_options["ok"],
            always_on_top=True,
            command=[win.destroy]
        )
        win = emi.init_plain_window(base_window)
        emi.simple_warning_message(
            my_window=win,
            title="Test message warning",
            message="This is a test message for the warning message box",
            button=emi.button_options["ok"],
            always_on_top=True,
            command=[win.destroy]
        )
        emi.window = emi.init_plain_window(base_window)
        emi.simple_information_message(
            my_window=emi.window,
            title="Test message information",
            message="This is a test message for the inform message box",
            button=emi.button_options["o/c"],  # button_options["c/a"],
            always_on_top=True,
            command=[emi.window.destroy, emi.window.destroy]
        )
        emi.advanced_warning_message(
            parent_window=base_window,
            title="You have found a corps",
            message="You have found a rotting corps",
            button=emi.button_options["ok"],
            always_on_top=True
        )
        response = emi.advanced_information_message(
            parent_window=base_window,
            title="Save corps?",
            message="Do you wish to save the rotting corpse to your inventory?",
            button=emi.button_options["s/d/c"],
            always_on_top=True
        )
        emi.err_message_print_debug(f"response = {response}")
        response_sentence = {
            0: "undefined",
            1: "save",
            2: "not save",
            3: "ignore"
        }
        if response == 0:
            if lore is True:
                emi.init_plain_window()
            emi.advanced_err_message(
                parent_window=base_window,
                title="Error",
                message="You have not chosen a response!\nThus, the corpse will be added to your inventory.\nTough luck bud!",
                button=emi.button_options["ok"],
                always_on_top=True
            )
        else:
            emi.advanced_information_message(
                parent_window=base_window,
                title="Your corpsy response",
                message=f"You have chosen to {response_sentence[response]} the corpse.",
                button=emi.button_options["ok"],
                always_on_top=True
            )
        emi.goodbye_message(parent_window=base_window)
        base_window.update()
        base_window.destroy()

    def test_window_position() -> None:
        """_summary_
        This is a function in charge of testing the window position
        """
        cwpi = CalculateWindowPosition(10, 10, 1, 1)
        test_input = {
            cwpi.top_left: (0, 0),
            cwpi.top_center: (4, 0),
            cwpi.top_right: (9, 0),
            cwpi.bottom_left: (0, 9),
            cwpi.bottom_center: (4, 9),
            cwpi.bottom_right: (9, 9),
            cwpi.left_center: (0, 4),
            cwpi.center: (4, 4),
            cwpi.right_center: (9, 4),
            "gobbledygook": (0, 0)
        }
        for key, value in test_input.items():
            print(f"Testing: CPI.re_router({key}):", end="")
            response = cwpi.re_router(key)
            if response == value:
                print("[OK]")
            else:
                print(f"[KO]: Got {response} but expected {value}")

    def test_assets() -> None:
        """ Test the assets """
        window = tk.Tk()
        ai = WindowTools()
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
        file_path = file_info["err_message"]["information_icon_path"]
        print(f"file_path = {file_path}")
        ai.add_image(
            sample_media_title_frame, file_path,
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

    def test_get_functions(debug: bool = False) -> None:
        """ Test the get functions """
        def print_debug(msg: str) -> None:
            """ Print the debug message """
            if debug:
                print(msg)
        default_screen_width = 800
        default_screen_height = 600
        default_screen_position_x = 100
        default_screen_position_y = 100
        default_screen_geometry = f"{default_screen_width}x{default_screen_height}+{default_screen_position_x}+{default_screen_position_y}"
        default_window_title = "Get Functions Test"
        default_entry_test_string = "Test Entry"

        default_image_width = 100
        default_image_height = 100

        gi = WindowTools()

        tt = tk.Tk()
        tt.geometry(default_screen_geometry)
        tt.title(default_window_title)
        # Create the sample image
        default_sample_image = tk.PhotoImage(
            master=tt,
            width=default_image_width,
            height=default_image_height
        )
        # Entry field
        string = tk.StringVar()
        entry = tk.Entry(tt, textvariable=string)
        string.set(default_entry_test_string)
        entry_content = gi.get_entry_content(entry)
        # Screen dimensions
        curent_host_screen_dimensions = gi.get_current_host_screen_dimensions(
            tt
        )
        default_host_screen_total_width = tt.winfo_screenwidth()
        default_host_screen_total_height = tt.winfo_screenheight()
        current_host_screen_total_width = gi.get_screen_width(tt)
        current_host_screen_total_height = gi.get_screen_height(tt)
        # Gathering the screen visuals
        default_host_screen_visual = tt.winfo_screenvisual()
        current_host_screen_visual = gi.get_window_visual(tt)
        # Window dimensions
        window_width = gi.get_window_width(tt)
        window_height = gi.get_window_height(tt)
        window_position_x = gi.get_window_position_x(tt)
        window_position_y = gi.get_window_position_y(tt)
        window_position = gi.get_window_position(tt)
        window_geometry = gi.get_window_geometry(tt)
        window_size = gi.get_window_size(tt)
        # Image dimensions
        image_dimensions = gi.get_image_dimensions(default_sample_image)
        # Get the window size manually
        ttt = tk.Toplevel(tt)
        ttt['bg'] = 'black'
        ttt.attributes('-fullscreen', True)
        # update idletasks needs to be run after the fullscreen flag has been set to true.
        ttt.update_idletasks()
        ttt.withdraw()
        gathered_screen_geometry = ttt.winfo_geometry()
        print_debug(
            f"ttt = gathered_screen_geometry: {gathered_screen_geometry}")
        ttt.destroy()
        # Get the window title
        window_title = gi.get_window_title(tt)
        # Destroy the parent window
        tt.destroy()
        # File selection
        filepath = gi.get_filepath(
            "Select a file",
            [("Text files", "*.txt"), ("All files", "*.*")]
        )
        # Folder selection
        folderpath = gi.get_folderpath("Select a folder", "/", True)
        # Testing the results gathered from the GUI
        # Checking the gathered entry content
        assert entry_content == default_entry_test_string
        # Checking the gathered filepath
        print_debug(f"filepath: '{filepath}', type: {type(filepath)}")
        if filepath == ():
            print("filepath: No file selected")
            filepath = " "
        assert len(filepath) > 0
        # Checking the gathered folderpath
        print_debug(f"folderpath: '{folderpath}', type: {type(folderpath)}")
        if folderpath == ():
            print("folderpath: No folder selected")
            folderpath = " "
        assert len(folderpath) > 0
        # Checking the gathered screen dimensions
        chsd = curent_host_screen_dimensions
        print_debug(
            f"curent_host_screen_dimensions: {chsd} == {gathered_screen_geometry}")
        assert f"{chsd['width']}x{chsd['height']}+{chsd['left']}+{chsd['top']}" == gathered_screen_geometry
        # Checking the screen width and height
        print_debug(
            f"current_host_screen_total_width<{current_host_screen_total_width}> == default_host_screen_total_width<{default_host_screen_total_width}>")
        print_debug(
            f"current_host_screen_total_height<{current_host_screen_total_height}> == default_host_screen_total_height<{default_host_screen_total_height}>")
        assert current_host_screen_total_width == default_host_screen_total_width
        assert current_host_screen_total_height == default_host_screen_total_height
        # Checking the screen visual
        print_debug(
            f"current_host_screen_visual<{current_host_screen_visual}> == default_host_screen_visual<{default_host_screen_visual}>"
        )
        assert current_host_screen_visual == default_host_screen_visual
        # Checking gathered window dimensions
        print_debug(
            f"window_width<{window_width}> == default_screen_width<{default_screen_width}>"
        )
        print_debug(
            f"window_height<{window_height}> == default_screen_height<{default_screen_height}>"
        )
        print_debug(
            f"window_position_x<{window_position_x}> == default_screen_position_x<{default_screen_position_x}>"
        )
        print_debug(
            f"window_position_y<{window_position_y}> == default_screen_position_y<{default_screen_position_y}>"
        )
        print_debug(
            f"window_position<{window_position}> == default_screen_position<{default_screen_position_x}, {default_screen_position_y}>"
        )
        print_debug(
            f"window_size<{window_size}> == default_screen_size<{default_screen_width}, {default_screen_height}>"
        )
        print_debug(
            f"window_geometry<{window_geometry}> == default_screen_geometry<{default_screen_geometry}>"
        )
        assert window_width == default_screen_width
        assert window_height == default_screen_height
        assert window_position_x == default_screen_position_x
        # For some reason the y position gets offset by some window position operation making it different from the reference, this is not an error in the library, this is the value returned by tkinter. This only happens if the window is not full screened, this could be due to the border desing.
        assert window_position_y >= default_screen_position_y
        assert window_position[0] == default_screen_position_x
        assert window_position[1] >= default_screen_position_y
        assert window_size == (default_screen_width, default_screen_height)
        separation = window_geometry.split("+")[-1]
        window_geometry = window_geometry.split("+")
        window_geometry.pop(-1)
        window_geometry = "+".join(window_geometry)
        assert window_geometry == f"{default_screen_width}x{default_screen_height}+{default_screen_position_x}"
        assert int(separation) >= int(default_screen_position_y)
        # Checking gathered image dimensions
        print_debug(
            f"image_dimensions['width']<{image_dimensions['width']}> == default_image_width<{default_image_width}>"
        )
        print_debug(
            f"image_dimensions['height']<{image_dimensions['height']}> == default_image_height<{default_image_height}>"
        )
        assert image_dimensions["width"] == default_image_width
        assert image_dimensions["height"] == default_image_height
        # Checking the gathered window title
        print_debug(
            f"window_title<'{window_title}'> == default_window_title<'{default_window_title}'>"
        )
        assert window_title == default_window_title
        print("All tests passed!")

    print("Testing the calculate window position class")
    test_window_position()
    print("Testing the message boxes")
    test_the_error_message_class()
    print("Testing the window tools")
    print("Testing the assets")
    test_assets()
    print("Testing the get functions")
    test_get_functions()
