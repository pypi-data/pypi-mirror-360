"""
File in charge of calculating the x and y coordinates for a given postion based on the window's size and the user's screen size
"""

CENTER = "c"
TOP_LEFT = "tl"
TOP_RIGHT = "tr"
TOP_CENTER = "tc"
LEFT_CENTER = "lc"
BOTTOM_LEFT = "bl"
RIGHT_CENTER = "rc"
BOTTOM_RIGHT = "br"
BOTTOM_CENTER = "bc"


class CalculateWindowPosition:
    """
    Class in charge of calculating the position of a window based of the user's screen dimension
    Input:
        host_width: int -> The width of the user's screen
        host_height: int -> The height of the user's screen
        window_width: int -> The width of the window
        window_height: int -> The height of the window

    Output:
        tuple: (x: int, y: int)

    Example: Entering correct data
        CPI = CalculatePosition(10, 10, 1, 1)
        CPI.re_router(CPI.top_left) -> (0, 0)

    Example 2: Entering gobbledygook data will default in the top left position
        CPI = CalculatePosition(10, 10, 1, 1)
        CPI.re_router("gobbledygook") -> (0, 0)
    """

    def __init__(self, host_width: int, host_height: int, window_width: int, window_height: int, offset_left: int = 0, offset_top: int = 0, offset_right: int = 0, offset_bottom: int = 0) -> None:
        self.host_width = host_width
        self.host_height = host_height
        self.window_width = window_width
        self.window_height = window_height
        # ---- Offset ----
        self.offset_left = offset_left
        self.offset_top = offset_top
        self.offset_right = offset_right
        self.offset_bottom = offset_bottom
        self.offset_x = 0
        self.offset_y = 0
        self.calculate_x_y_offsets()
        # ---- Pre-coded positions ----
        self.top_left = "tl"
        self.top_center = "tc"
        self.top_right = "tr"
        self.bottom_left = "bl"
        self.bottom_center = "bc"
        self.bottom_right = "br"
        self.left_center = "lc"
        self.center = "c"
        self.right_center = "rc"
        # ---- Reference dict ----
        self.reference_dict = {
            self.top_left: self.calculate_top_left,
            self.top_center: self.calculate_top_center,
            self.top_right: self.calculate_top_rigth,
            self.bottom_left: self.calculate_bottom_left,
            self.bottom_center: self.calculate_bottom_center,
            self.bottom_right: self.calculate_bottom_right,
            self.left_center: self.calculate_left_center,
            self.center: self.calculate_center,
            self.right_center: self.calculate_right_center
        }

    def calculate_x_y_offsets(self) -> None:
        """
        This is an inner function meant to update the x and y offsets based on the left, top, right, bottom user inputted offsets
        Input:
            None
        Output:
            None
        """
        self.offset_x = self.offset_left - self.offset_right
        self.offset_y = self.offset_top - self.offset_bottom

    def update_offsets(self, offset_left: int = 0, offset_top: int = 0, offset_right: int = 0, offset_bottom: int = 0) -> None:
        """
        Update the stored values of the offsets that can be used to finetune the position of the window
        Input:
            offset_left: int (default value: 0) -> Set the value of the offset to the left
            offset_top: int (default value: 0) -> Set the value of the offset to the top
            offset_right: int (default value: 0) -> Set the value of the offset to the right
            offset_bottom: int (default value: 0) -> Set the value of the offset to the bottom
        Output:
            Nothing
        """
        self.offset_left = offset_left
        self.offset_top = offset_top
        self.offset_right = offset_right
        self.offset_bottom = offset_bottom
        self.calculate_x_y_offsets()

    def update_offset_left(self, offset_left: int = 0) -> None:
        """
        Update the stored values of the offsets that can be used to finetune the position of the window
        Input:
            offset_left: int (default value: 0) -> Set the value of the offset to the left
        Output:
            Nothing
        """
        self.offset_left = offset_left
        self.calculate_x_y_offsets()

    def update_offset_top(self, offset_top: int = 0) -> None:
        """
        Update the stored values of the offsets that can be used to finetune the position of the window
        Input:
            offset_top: int (default value: 0) -> Set the value of the offset to the top
        Output:
            Nothing
        """
        self.offset_top = offset_top
        self.calculate_x_y_offsets()

    def update_offset_right(self, offset_right: int = 0) -> None:
        """
        Update the stored values of the offsets that can be used to finetune the position of the window
        Input:
            offset_right: int (default value: 0) -> Set the value of the offset to the right
        Output:
            Nothing
        """
        self.offset_right = offset_right
        self.calculate_x_y_offsets()

    def update_offset_bottom(self, offset_bottom: int = 0) -> None:
        """
        Update the stored values of the offsets that can be used to finetune the position of the window
        Input:
            offset_bottom: int (default value: 0) -> Set the value of the offset to the bottom
        Output:
            Nothing
        """
        self.offset_bottom = offset_bottom
        self.calculate_x_y_offsets()

    def update_host_dimensions(self, width: int, height: int) -> None:
        """
        Update the stored size of the host screen
        Input:
            width: int -> The width of the host screen
            height: int -> The height of the host screen
        Output:
            Nothing
        """
        self.host_width = width
        self.host_height = height

    def update_window_dimensions(self, width: int, height: int) -> None:
        """
        Update the stored size of the window
        Input:
            width: int -> The width of the tkinter window
            height: int -> The height of the tkinter window
        Output:
            Nothing
        """
        self.window_width = width
        self.window_height = height

    def re_router(self, position: str) -> tuple:
        """
        Output the correct coordinates based on the provided position
        Input:
            position: str -> The position of the window
        Output:
            tuple: (x: int, y: int)
        """
        if position in self.reference_dict:
            return self.reference_dict[position]()
        return self.calculate_top_left()

    def calculate_top_left(self) -> tuple:
        """
        Place the window on the top left of the screen
        Input:
            Nothing
        Output:
            tuple: (x: int, y: int)
        """
        x = 0 + self.offset_x
        y = 0 + self.offset_y
        return (x, y)

    def calculate_top_center(self) -> tuple:
        """
        Place the window on the top center of the screen
        Input:
            Nothing
        Output:
            tuple: (x: int, y: int)
        """
        x = ((self.host_width - self.window_width) // 2) + self.offset_x
        y = 0 + self.offset_y
        return (x, y)

    def calculate_top_rigth(self) -> tuple:
        """
        Place the window on the top right of the screen
        Input:
            Nothing
        Output:
            tuple: (x: int, y: int)
        """
        x = (self.host_width - self.window_width) + self.offset_x
        y = 0 + self.offset_y
        return (x, y)

    def calculate_bottom_left(self) -> tuple:
        """
        Place the window on the bottom left of the screen
        Input:
            Nothing
        Output:
            tuple: (x: int, y: int)
        """
        x = 0 + self.offset_x
        y = (self.host_height - self.window_height) + self.offset_y
        return (x, y)

    def calculate_bottom_center(self) -> tuple:
        """
        Place the window on the bottom center of the screen
        Input:
            Nothing
        Output:
            tuple: (x: int, y: int)
        """
        x = ((self.host_width - self.window_width) // 2) + self.offset_x
        y = (self.host_height - self.window_height) + self.offset_y
        return (x, y)

    def calculate_bottom_right(self) -> tuple:
        """
        Place the window on the bottom right of the screen
        Input:
            Nothing
        Output:
            tuple: (x: int, y: int)
        """
        x = (self.host_width - self.window_width) + self.offset_x
        y = (self.host_height - self.window_height) + self.offset_y
        return (x, y)

    def calculate_left_center(self) -> tuple:
        """
        Place the window on the left center of the screen
        Input:
            Nothing
        Output:
            tuple: (x: int, y: int)
        """
        x = 0 + self.offset_x
        y = ((self.host_height - self.window_height) // 2) + self.offset_y
        return (x, y)

    def calculate_center(self) -> tuple:
        """
        Place the window on the center of the screen
        Input:
            Nothing
        Output:
            tuple: (x: int, y: int)
        """
        x = ((self.host_width - self.window_width) // 2) + self.offset_x
        y = ((self.host_height - self.window_height) // 2) + self.offset_y
        return (x, y)

    def calculate_right_center(self) -> tuple:
        """
        Place the window on the right center of the screen
        Input:
            Nothing
        Output:
            tuple: (x: int, y: int)
        """
        x = (self.host_width - self.window_width) + self.offset_x
        y = ((self.host_height - self.window_height) // 2) + self.offset_y
        return (x, y)


if __name__ == "__main__":
    CWPI = CalculateWindowPosition(10, 10, 1, 1)
    test_input = {
        CWPI.top_left: (0, 0),
        CWPI.top_center: (4, 0),
        CWPI.top_right: (9, 0),
        CWPI.bottom_left: (0, 9),
        CWPI.bottom_center: (4, 9),
        CWPI.bottom_right: (9, 9),
        CWPI.left_center: (0, 4),
        CWPI.center: (4, 4),
        CWPI.right_center: (9, 4),
        "gobbledygook": (0, 0)
    }
    for key, value in test_input.items():
        print(f"Testing: CPI.re_router({key}):", end="")
        response = CWPI.re_router(key)
        if response == value:
            print("[OK]")
        else:
            print(f"[KO]: Got {response} but expected {value}")
