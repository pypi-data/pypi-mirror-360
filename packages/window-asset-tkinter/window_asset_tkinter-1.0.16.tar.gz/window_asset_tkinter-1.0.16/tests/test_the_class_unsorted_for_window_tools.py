"""
File in charge of containing the tests for the Unsorted class
"""

import tkinter as tk

import unittest
from unittest.mock import MagicMock, patch

from PIL import ImageTk

# Import the file where Unsorted is defined
from window_asset_tkinter.window_tools.unsorted import Unsorted, static_load_image, static_create_text_variable


class TestUnsortedUtils(unittest.TestCase):
    """_summary_
    Test the Unsorted class for window manipulation functions.
    Args:
        unittest (_type_): _description_
    """

    def test_static_create_text_variable(self):
        """Test creating a text variable."""
        root = tk.Tk()
        root.withdraw()  # Hide the root window
        text_var = static_create_text_variable("Hello")
        self.assertIsInstance(text_var, tk.StringVar)
        self.assertEqual(text_var.get(), "Hello")
        root.destroy()

    @patch("os.path.exists", return_value=False)
    def test_static_load_image_invalid_path(self, mock_exists):
        """Test loading an image with an invalid path."""
        result = static_load_image("invalid.png")
        self.assertIn("err_message", result)
        self.assertEqual(result["err_message"],
                         "Image path is not valid or not provided")

    @patch("os.path.exists", return_value=True)
    @patch("os.path.isfile", return_value=True)
    def test_static_load_image_zero_dimensions(self, mock_exists, mock_isfile):
        """Test loading an image with zero dimensions."""
        result = static_load_image("test.png", 0, 0)
        self.assertIn("err_message", result)
        self.assertEqual(result["err_message"],
                         "Image width and heigh must be greater than 0")

    @patch("PIL.Image.open")
    @patch("os.path.exists", return_value=True)
    @patch("os.path.isfile", return_value=True)
    def test_static_load_image_success(self, mock_exists, mock_isfile, mock_open):
        """Test loading an image successfully."""
        mock_img = MagicMock()
        mock_open.return_value = mock_img
        mock_img.resize.return_value = mock_img

        with patch("PIL.ImageTk.PhotoImage", return_value="mocked_image"):
            result = static_load_image("image.png", 100, 100)
            self.assertIn("img", result)
            self.assertEqual(result["img"], "mocked_image")

    def test_gen_random_name_length(self):
        """Test generating a random name of specified length."""
        name = Unsorted.gen_random_name(8)
        self.assertEqual(len(name), 8)
        self.assertTrue(all(c.isalpha() for c in name))

    def test_create_text_variable(self):
        """Test creating a text variable."""
        root = tk.Tk()
        root.withdraw()
        var = Unsorted.create_text_variable("default")
        self.assertIsInstance(var, tk.StringVar)
        self.assertEqual(var.get(), "default")
        root.destroy()

    def test_clear_entry_content(self):
        """Test clearing the content of an entry."""
        entry = MagicMock(spec=tk.Entry)
        Unsorted.clear_entry_content(entry)
        entry.delete.assert_called_once_with(0, tk.END)

    def test_update_entry_content(self):
        """Test updating the content of an entry."""
        entry = MagicMock(spec=tk.Entry)
        Unsorted.update_entry_content(entry, 2, "Hi")
        entry.insert.assert_called_once_with(2, "Hi")

    def test_enter_fullscreen(self):
        """Test entering fullscreen mode."""
        window = MagicMock()
        Unsorted.enter_fullscreen(window, True)
        window.attributes.assert_called_with('-fullscreen', True)

    def test_allow_resizing(self):
        """Test allowing resizing of the window."""
        window = MagicMock()
        Unsorted.allow_resizing(window, False)
        window.resizable.assert_called_with(False, False)

        Unsorted.allow_resizing(window, True)
        window.resizable.assert_called_with(True, True)

    def test_maintain_on_top(self):
        """Test maintaining the window on top."""
        window = MagicMock()
        Unsorted.maintain_on_top(window, True)
        window.attributes.assert_called_with('-topmost', True)

        Unsorted.maintain_on_top(window, False)
        window.attributes.assert_called_with('-topmost', False)

    def test_free_loaded_image_safe_delete(self):
        """Test freeing a loaded image safely."""
        image = MagicMock(spec=ImageTk.PhotoImage)
        Unsorted.free_loaded_image(image)
        image.__del__.assert_called_once()

    def test_free_loaded_image_fallback_delete(self):
        """Test freeing a loaded image with fallback delete."""
        # Simulate image not having __del__, fallback to del
        class DummyImage:
            """This is an example class"""
            pass
        img = DummyImage()
        try:
            Unsorted.free_loaded_image(img)
        except Exception as e:
            self.fail(f"Exception raised in fallback delete: {e}")

    def test_init_plain_window(self):
        """Test initializing a plain window."""
        root = tk.Tk()
        root.withdraw()

        # Case: root is None
        result = Unsorted.init_plain_window(None)
        self.assertIsInstance(result, tk.Toplevel)

        # Case: root is a Tk instance
        result2 = Unsorted.init_plain_window(root)
        self.assertIsInstance(result2, tk.Toplevel)

        result.destroy()
        result2.destroy()

    def test_init_window_attributes(self):
        """Test initializing a window with attributes."""
        window = MagicMock(spec=tk.Tk)
        Unsorted.init_window(
            window,
            title="Main Window",
            bkg="white",
            width=400,
            height=300,
            position_x=50,
            position_y=60,
            fullscreen=False,
            resizable=True
        )
        window.geometry.assert_called_with("400x300+50+60")
        window.minsize.assert_called_with(width=400, height=300)
        window.maxsize.assert_called_with(width=600, height=500)
        window.title.assert_called_with("Main Window")
        window.__setitem__.assert_called_with("bg", "white")
        window.attributes.assert_any_call("-fullscreen", False)
        window.resizable.assert_called_with(True, True)


if __name__ == "__main__":
    unittest.main()
