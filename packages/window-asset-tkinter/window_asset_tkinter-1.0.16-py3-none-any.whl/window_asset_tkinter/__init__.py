##
# EPITECH PROJECT, 2022
# Desktop_pet (Workspace)
# File description:
# __init__.py
##

"""
The file containing the code to ease the import of python files
contained in the current folder to any other python code that is
not contained in the same directory.
"""

from os.path import dirname, abspath
from typing import Dict, Any

# library dedicated to displaying input windows

# files of the lib
if __name__ == "__main__":
    from capsule import WindowAsset, WindowTools,  ErrMessages, ActionAssets, CalculateWindowPosition
else:
    from .capsule import WindowAsset, WindowTools, ErrMessages, ActionAssets, CalculateWindowPosition

__all__ = [
    "WindowAsset",
    "WindowTools",
    "ErrMessages",
    "ActionAssets",
    "CalculateWindowPosition",
]

window_asset_tkinter_window_default_config: Dict[str, Dict[str, Any]] = {
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
        "icon_path": f"{dirname(abspath(__file__))}/assets/favicon.ico",
        "button_width": 10,
        "button_height": 1,
        "error_icon_path": f"{dirname(abspath(__file__))}/assets/error_64x64.png",
        "warning_icon_path": f"{dirname(abspath(__file__))}/assets/warning_64x64.png",
        "information_icon_path": f"{dirname(abspath(__file__))}/assets/information_64x64.png",
        "image_width": 64,
        "image_height": 64
    }
}
