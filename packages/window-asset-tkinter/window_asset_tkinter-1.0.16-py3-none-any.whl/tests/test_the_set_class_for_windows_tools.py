"""
File in charge of containing the tests for the Set class
"""

import tkinter as tk

import unittest
from unittest.mock import MagicMock, patch

# Import your Set class (update this to match your file name)
from window_asset_tkinter.window_tools import Set


class TestSet(unittest.TestCase):
    """_summary_
    Test the Set class for window manipulation functions.

    Args:
        unittest (_type_): _description_
    """

    def setUp(self):
        # Create a mock Tkinter window
        self.window = MagicMock(spec=tk.Tk)

    def test_set_title(self):
        """Test setting the title of the window."""
        Set.set_title(self.window, "Test Window")
        self.window.title.assert_called_with("Test Window")

    def test_set_window_size(self):
        """Test setting the size of the window."""
        Set.set_window_size(self.window, 300, 200, 100, 150)
        self.window.geometry.assert_called_with("300x200+100+150")

    def test_set_window_position_x(self):
        """Test setting the x position of the window."""
        self.window.winfo_y.return_value = 250
        Set.set_window_position_x(self.window, 500)
        self.window.geometry.assert_called_with("+500+250")

    def test_set_window_position_y(self):
        """Test setting the y position of the window."""
        self.window.winfo_x.return_value = 300
        Set.set_window_position_y(self.window, 400)
        self.window.geometry.assert_called_with("+300+400")

    def test_set_window_background_colour(self):
        """Test setting the background color of the window."""
        Set.set_window_background_colour(self.window, "blue")
        self.window.__setitem__.assert_called_with("bg", "blue")

    def test_set_window_always_on_top(self):
        """Test setting the window to always be on top."""
        Set.set_window_always_on_top(self.window, True)
        self.window.wm_attributes.assert_called_with("-topmost", True)

    def test_set_transparency_clamping(self):
        """Test setting the transparency of the window with clamping."""
        Set.set_transparency(self.window, (-0.5))
        self.window.attributes.assert_called_with('-alpha', 0.5)

        Set.set_transparency(self.window, 2)
        self.window.attributes.assert_called_with('-alpha', 1.0)

    def test_set_icon_path_does_not_exist(self):
        """Test setting an icon path that does not exist."""
        with patch("os.path.exists", return_value=False):
            with patch("os.path.isfile", return_value=False):
                with patch("builtins.print") as mock_print:
                    Set.set_icon(self.window, "nonexistent.ico")
                    mock_print.assert_any_call(
                        "The icon path 'nonexistent.ico' is not valid")

    def test_set_window_visible(self):
        """Test setting the window visibility."""
        Set.set_window_visible(self.window, True)
        self.window.deiconify.assert_called_once()

        Set.set_window_visible(self.window, False)
        self.window.withdraw.assert_called_once()

    def test_set_window_title_bar_visibility(self):
        """Test setting the window title bar visibility."""
        Set.set_window_title_bar_visibility(self.window, visible=False)
        self.window.overrideredirect.assert_called_with(False)

    def test_set_offset_window_position(self):
        """Test setting the offset position of the window."""
        self.window.winfo_x.return_value = 50
        self.window.winfo_y.return_value = 75
        Set.set_offset_window_position(self.window, 20, 30)
        self.window.geometry.assert_called_with("+70+105")


if __name__ == "__main__":
    unittest.main()
