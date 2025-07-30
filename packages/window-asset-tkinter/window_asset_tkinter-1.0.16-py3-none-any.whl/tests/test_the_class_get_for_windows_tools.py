"""
Test the class Get for Windows tools library.
"""

import tkinter as tk

import unittest
from unittest.mock import MagicMock, patch

# assuming your file is named gui_get.py
from window_asset_tkinter.window_tools.get import Get


class TestGet(unittest.TestCase):
    """
    Test the Get class from the window_tools module.
    """

    def setUp(self):
        """
        Set up the test case with a tkinter root window and an entry widget.
        """
        self.root = tk.Tk()
        self.root.geometry("800x600+100+100")
        self.entry_var = tk.StringVar()
        self.entry = tk.Entry(self.root, textvariable=self.entry_var)
        self.entry_var.set("Test Value")

    def tearDown(self):
        """
        Tear down the test case by destroying the tkinter root window.
        """
        self.root.destroy()

    def test_get_entry_content(self):
        """
        Test the get_entry_content method.
        """
        self.assertEqual(Get.get_entry_content(self.entry), "Test Value")

    def test_get_screen_width(self):
        """
        Test the get_screen_width method.
        """
        width = Get.get_screen_width(self.root)
        self.assertEqual(width, self.root.winfo_screenwidth())

    def test_get_screen_height(self):
        """
        Test the get_screen_height method.
        """
        height = Get.get_screen_height(self.root)
        self.assertEqual(height, self.root.winfo_screenheight())

    def test_get_window_width(self):
        """
        Test the get_window_width method.
        """
        self.assertEqual(Get.get_window_width(
            self.root), self.root.winfo_width())

    def test_get_window_height(self):
        """
        Test the get_window_height method.
        """
        self.assertEqual(Get.get_window_height(
            self.root), self.root.winfo_height())

    def test_get_window_position(self):
        """
        Test the get_window_position method.
        """
        pos = Get.get_window_position(self.root)
        self.assertEqual(pos[0], self.root.winfo_x())
        self.assertEqual(pos[1], self.root.winfo_y())

    def test_get_window_geometry(self):
        """
        Test the get_window_geometry method.
        """
        self.assertEqual(Get.get_window_geometry(
            self.root), self.root.winfo_geometry())

    def test_get_window_size(self):
        """
        Test the get_window_size method.
        """
        size = Get.get_window_size(self.root)
        self.assertEqual(
            size, (self.root.winfo_width(), self.root.winfo_height()))

    def test_get_window_title(self):
        """
        Test the get_window_title method.
        """
        self.root.title("Test Title")
        self.assertEqual(Get.get_window_title(self.root), "Test Title")

    def test_get_window_visual(self):
        """
        Test the get_window_visual method.
        """
        self.assertEqual(Get.get_window_visual(self.root),
                         self.root.winfo_screenvisual())

    def test_get_window_colour_model(self):
        """
        Test the get_window_colour_model method.
        """
        # This uses the same method as get_window_visual
        self.assertEqual(Get.get_window_colour_model(
            self.root), self.root.winfo_screenvisual())

    def test_get_window_position_x_y(self):
        """
        Test the get_window_position_x and get_window_position_y methods.
        """
        x = Get.get_window_position_x(self.root)
        y = Get.get_window_position_y(self.root)
        self.assertEqual(x, self.root.winfo_x())
        self.assertEqual(y, self.root.winfo_y())

    def test_get_image_dimensions(self):
        """
        Test the get_image_dimensions method.
        """
        img = tk.PhotoImage(master=self.root, width=100, height=50)
        dims = Get.get_image_dimensions(img)
        self.assertEqual(dims["width"], 100)
        self.assertEqual(dims["height"], 50)

    @patch('tkinter.filedialog.askopenfilename', return_value='/path/to/file.txt')
    def test_get_filepath(self, mock_dialog):
        """
        Test the get_filepath method.
        """
        result = Get.get_filepath("Pick a file")
        self.assertEqual(result, '/path/to/file.txt')

    @patch('tkinter.filedialog.askdirectory', return_value='/path/to/folder')
    def test_get_folderpath(self, mock_dialog):
        """
        Test the get_folderpath method.
        """
        result = Get.get_folderpath("Pick a folder", "/")
        self.assertEqual(result, '/path/to/folder')

    def test_get_current_host_screen_dimensions(self):
        """
        Test the get_current_host_screen_dimensions method.
        """
        dimensions = Get.get_current_host_screen_dimensions(self.root)
        self.assertIn("width", dimensions)
        self.assertIn("height", dimensions)
        self.assertIn("left", dimensions)
        self.assertIn("top", dimensions)

    def test_get_current_host_screen_dimensions_with_geometry(self):
        """
        Test the get_current_host_screen_dimensions method with geometry.
        """
        dimensions = Get.get_current_host_screen_dimensions(
            self.root, include_raw_geometry=True)
        self.assertIn("geometry", dimensions)


if __name__ == '__main__':
    unittest.main()
