"""
Test cases for the Add class in window_tools module.
"""

import unittest
import tkinter as tk

from window_asset_tkinter.window_tools.add import Add


class TestAddWidgets(unittest.TestCase):

    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()  # Hide main window
        self.add = Add()

    def tearDown(self):
        self.root.destroy()

    def test_add_label(self):
        label = self.add.add_label(
            self.root, text="Test Label", fg="black", bkg="white")
        self.assertIsInstance(label, tk.Label)
        self.assertEqual(label.cget("text"), "Test Label")

    def test_add_button(self):
        btn = self.add.add_button(
            self.root, text="Click Me", fg="white", bkg="black", command=lambda: None, side=tk.LEFT
        )
        self.assertIsInstance(btn, tk.Button)
        self.assertEqual(btn.cget("text"), "Click Me")

    def test_add_entry_with_string(self):
        entry = self.add.add_entry(self.root, text_variable="Hello")
        entry.insert(0, "Hello")
        self.assertIsInstance(entry, tk.Entry)
        self.assertEqual(entry.get(), "Hello")

    def test_add_frame(self):
        frame = self.add.add_frame(
            self.root, borderwidth=1, relief=tk.GROOVE, bkg="gray")
        self.assertIsInstance(frame, tk.Frame)

    def test_add_labelframe(self):
        labelframe = self.add.add_labelframe(
            self.root, title="Group", padding_x=10, padding_y=10, fill=tk.X, expand=False)
        self.assertIsInstance(labelframe, tk.LabelFrame)
        self.assertEqual(labelframe.cget("text"), "Group")

    def test_add_spinbox(self):
        spinbox = self.add.add_spinbox(
            self.root, minimum=0, maximum=10, bkg="white", fg="black")
        self.assertIsInstance(spinbox, tk.Spinbox)

    def test_add_paragraph_field(self):
        text_widget = self.add.add_paragraph_field(
            self.root, fg="black", bkg="white")
        self.assertIsInstance(text_widget, tk.Text)

    def test_add_text_field(self):
        text_widget = self.add.add_text_field(self.root)
        self.assertIsInstance(text_widget, tk.Text)

    def test_add_dropdown(self):
        dropdown = self.add.add_dropdown(
            self.root, elements=["One", "Two", "Three"])
        self.assertIsInstance(dropdown, tk.Widget)
        self.assertEqual(dropdown.get(), "One")

    def test_add_watermark(self):
        watermark = self.add.add_watermark(self.root)
        self.assertIsInstance(watermark, tk.Label)
        self.assertIn("Created by", watermark.cget("text"))

    def test_add_emoji(self):
        emoji_label = self.add.add_emoji(
            self.root, text="😊", fg="black", bkg="white")
        self.assertIsInstance(emoji_label, tk.Label)
        self.assertEqual(emoji_label.cget("text"), "😊")

    def test_add_grid_returns_frame(self):
        frame = self.add.add_grid(
            self.root, borderwidth=2, relief=tk.RAISED, bkg="blue")
        self.assertIsInstance(frame, tk.Frame)

    def test_add_scrollbar_to_text(self):
        text_widget = self.add.add_paragraph_field(self.root)
        scrollbar = self.add.add_scroll_bar(self.root, text_widget)
        self.assertIsInstance(scrollbar, tk.Scrollbar)


if __name__ == '__main__':
    unittest.main()
