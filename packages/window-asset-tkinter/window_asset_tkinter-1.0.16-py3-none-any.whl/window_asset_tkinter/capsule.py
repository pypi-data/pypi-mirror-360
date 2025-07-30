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

# library dedicated to displaying input windows

# files of the lib
if __name__ == "__main__":
    from window_tools import WindowTools
    from err_messages import ErrMessages
    from action_assets import ActionAssets
    from calculate_window_position import CalculateWindowPosition
else:
    from .window_tools import WindowTools
    from .err_messages import ErrMessages
    from .action_assets import ActionAssets
    from .calculate_window_position import CalculateWindowPosition


class WindowAsset:
    """ A group of classes meant to ease window management """

    def __init__(self) -> None:
        super(WindowAsset, self).__init__()
        self.__version__ = "1.0.0"
        self.window_tools = WindowTools
        self.err_messages = ErrMessages
        self.action_assets = ActionAssets
        self.calculate_window_position = CalculateWindowPosition


if __name__ == "__main__":
    print("Please launch the main program")
    print(f"WindowAsset = {dir(WindowAsset())}")
