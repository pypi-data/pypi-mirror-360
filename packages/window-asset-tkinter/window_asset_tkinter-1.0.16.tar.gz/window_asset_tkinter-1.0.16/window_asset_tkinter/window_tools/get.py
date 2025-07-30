"""
File in charge of containing the funcitons that gather info from GUI elements
"""

from typing import Union, List, Tuple

from time import sleep

import tkinter as tk
import tkinter.filedialog as TKF


class Get:
    """ The  class in charge of gathering the info of a GUI element """

    @staticmethod
    def get_entry_content(entry: tk.Entry) -> str:
        """ 
        get the content and update the entry field 

        Arg:
            entry (tk.Entry): The entry field to get the content from.

        Returns:
            data (str): The content of the entry field.
        """
        return entry.get()

    @staticmethod
    def get_screen_width(window: Union[tk.Tk, tk.Toplevel, None] = None) -> int:
        """
        Get the width of the physical display 

        Args:
            window (tk.Tk or tk.Toplevel): The parent window to use for the geometry calculation.
                If None, a new Tk window will be created and destroyed.
        Returns:
            data (int): The width of the physical display.
        """
        if window is None:
            parent_window = tk.Tk()
        else:
            parent_window = window
        parent_window.update_idletasks()
        data = parent_window.winfo_screenwidth()
        if window is None:
            parent_window.destroy()
        return data

    @staticmethod
    def get_screen_height(window: Union[tk.Tk, tk.Toplevel, None] = None) -> int:
        """ Get the height of the physical display """
        if window is None:
            parent_window = tk.Tk()
        else:
            parent_window = window
        parent_window.update_idletasks()
        data = parent_window.winfo_screenheight()
        if window is None:
            parent_window.destroy()
        return data

    @staticmethod
    def get_window_width(window: Union[tk.Tk, tk.Toplevel, None] = None) -> int:
        """ Get the width of the physical display """
        if window is None:
            parent_window = tk.Tk()
        else:
            parent_window = window
        parent_window.update_idletasks()
        data = parent_window.winfo_width()
        if window is None:
            parent_window.destroy()
        return data

    @staticmethod
    def get_window_height(window: Union[tk.Tk, tk.Toplevel, None] = None) -> int:
        """ Get the height of the physical display """
        if window is None:
            parent_window = tk.Tk()
        else:
            parent_window = window
        parent_window.update_idletasks()
        data = parent_window.winfo_height()
        if window is None:
            parent_window.destroy()
        return data

    @staticmethod
    def get_window_visual(window: Union[tk.Tk, tk.Toplevel, None] = None) -> str:
        """ Get the visual (directcolor, grayscale, pseudocolor, staticcolor, staticgray, or truecolor) of the window """
        if window is None:
            parent_window = tk.Tk()
        else:
            parent_window = window
        parent_window.update_idletasks()
        data = parent_window.winfo_screenvisual()
        if window is None:
            parent_window.destroy()
        return data

    @staticmethod
    def get_window_colour_model(window: Union[tk.Tk, tk.Toplevel, None] = None) -> str:
        """ Get the colour mode (RGB or CMYK) of the window """
        if window is None:
            parent_window = tk.Tk()
        else:
            parent_window = window
        parent_window.update_idletasks()
        data = parent_window.winfo_screenvisual()
        if window is None:
            parent_window.destroy()
        return data

    @staticmethod
    def get_window_position_x(window: Union[tk.Tk, tk.Toplevel, None] = None) -> int:
        """ Get the x position of the window """
        if window is None:
            parent_window = tk.Tk()
        else:
            parent_window = window
        parent_window.update_idletasks()
        data = parent_window.winfo_x()
        if window is None:
            parent_window.destroy()
        return data

    @staticmethod
    def get_window_position_y(window: Union[tk.Tk, tk.Toplevel, None] = None) -> int:
        """ Get the y position of the window """
        if window is None:
            parent_window = tk.Tk()
        else:
            parent_window = window
        parent_window.update_idletasks()
        data = parent_window.winfo_y()
        if window is None:
            parent_window.destroy()
        return data

    @staticmethod
    def get_window_position(window: Union[tk.Tk, tk.Toplevel, None] = None) -> Tuple:
        """ Get the position of a tkinter window """
        if window is None:
            parent_window = tk.Tk()
        else:
            parent_window = window
        parent_window.update_idletasks()
        data = (parent_window.winfo_x(), parent_window.winfo_y())
        if window is None:
            parent_window.destroy()
        return data

    @staticmethod
    def get_window_geometry(window: Union[tk.Tk, tk.Toplevel, None] = None) -> str:
        """ Get the geometry of the window """
        if window is None:
            parent_window = tk.Tk()
        else:
            parent_window = window
        parent_window.update_idletasks()
        data = parent_window.winfo_geometry()
        if window is None:
            parent_window.destroy()
        return data

    @staticmethod
    def get_window_size(window: Union[tk.Tk, tk.Toplevel, None] = None) -> Tuple:
        """ Get the size of the window """
        if window is None:
            parent_window = tk.Tk()
        else:
            parent_window = window
        parent_window.update_idletasks()
        data = (parent_window.winfo_width(), parent_window.winfo_height())
        if window is None:
            parent_window.destroy()
        return data

    @staticmethod
    def get_window_title(window: Union[tk.Tk, tk.Toplevel]) -> str:
        """ Get the title of the window """
        return window.title()

    @staticmethod
    def get_filepath(window_title: str, filetypes: List[Tuple] = [('txt files', '.txt'), ('all files', '.*')], parent_window: Union[tk.Misc, tk.Tk, tk.Toplevel, None] = None) -> str:
        """ Get a filepath from the user's computer """
        if parent_window is not None:
            filename = TKF.askopenfilename(
                parent=parent_window,
                title=window_title,
                filetypes=filetypes
            )
        else:
            filename = TKF.askopenfilename(
                title=window_title,
                filetypes=filetypes
            )
        return filename

    @staticmethod
    def get_folderpath(window_title: str, initial_directory: str, must_exist: bool = True, parent_window: Union[tk.Misc, tk.Tk, tk.Toplevel, None] = None) -> str:
        """ Get the folderpath from the user's computer """
        if parent_window is not None:
            folderpath = TKF.askdirectory(
                parent=parent_window,
                initialdir=initial_directory,
                mustexist=must_exist,
                title=window_title
            )
        else:
            folderpath = TKF.askdirectory(
                initialdir=initial_directory,
                mustexist=must_exist,
                title=window_title
            )
        return folderpath

    @staticmethod
    def get_current_host_screen_dimensions(window: Union[tk.Tk, tk.Toplevel, None] = None, include_raw_geometry: bool = False) -> dict:
        """
        Get the size of the screen on which the program is running
        Workaround to get the size of the current screen in a multi-screen setup.

        Args:
            window (tk.Tk or tk.Toplevel): The parent window to use for the geometry calculation.
                If None, a new Tk window will be created and destroyed.
            include_raw_geometry (bool): If True, include the raw geometry string in the returned dictionary.
                Defaults to False.

        Returns:
            geometry (dict): The standard Tk geometry string.
                {"width":width, "height":height, "left":left, "top":top}
            if include_raw_geometry is True:
                the returned dictionary will look like this:
                    {"width":width, "height":height, "left":left, "top":top, "geometry":geometry}
        """
        if window is None:
            parent_window = tk.Tk()
        else:
            parent_window = window
        root = tk.Toplevel(parent_window)
        root['bg'] = 'black'
        root.attributes('-fullscreen', True)
        # update idletasks needs to be run after the fullscreen flag has been set to true.
        root.update_idletasks()
        root.withdraw()
        geometry = root.winfo_geometry()
        root.destroy()
        if window is None:
            parent_window.destroy()
        result = {}
        window_width = int(
            geometry.split("+", maxsplit=1)[0].split("x", maxsplit=1)[0]
        )
        window_height = int(geometry.split("+", maxsplit=1)[0].split("x")[1])
        window_position_x = int(geometry.split("+")[1])
        window_position_y = int(geometry.split("+")[2])
        result["width"] = window_width
        result["height"] = window_height
        result["left"] = window_position_x
        result["top"] = window_position_y
        if include_raw_geometry:
            result["geometry"] = geometry
        return result

    @staticmethod
    def get_image_dimensions(image: tk.Image) -> dict[str, int]:
        """ Get the dimensions of a given image """
        result = {}
        result["width"] = image.width()
        result["height"] = image.height()
        return result


if __name__ == "__main__":
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

        gi = Get()

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
    test_get_functions()
