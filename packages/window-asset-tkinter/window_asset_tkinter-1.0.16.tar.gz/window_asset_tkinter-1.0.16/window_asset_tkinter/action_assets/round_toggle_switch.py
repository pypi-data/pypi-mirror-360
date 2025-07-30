"""
File in charge of creating a round toggle switch (mordern version of a toggle switch on browsers)
"""

import math
import tkinter as tk
from functools import partial


class RoundToggleSwitch:
    """ add a modern looking Toggle button """

    # , width: int = 200, height: int = 200) -> None:
    def __init__(self, window: tk.Tk, system_bkg_col: str = "white", bkg_active: str = "#1B73BA", bkg_inactive: str = "#666666", button_colour: str = "#FFFFFF", width: int = 65, height: int = 35, radius: int = 15, command: partial = None) -> None:
        """ The toggle button class in charge of displaying a toggle button """
        # ---- Parent info ----
        self.window = window
        self.width = width
        self.height = height
        # self.width = 65
        # self.height = 35
        self.system_bkg_col = system_bkg_col
        # ---- Status information ----
        self.button_active = False
        self.bkg_active = bkg_active
        self.bkg_inactive = bkg_inactive
        # ---- Basic dimensions ----
        self.radius = radius
        # self.radius = 15  # self.calculate_radius(self.width, self.height, 20)
        # ---- Button coordinates ----
        self.posx = 1
        self.posy = 1
        self.offset_x = 0
        self.offset_y = 0
        # button of the toggle (specific config)
        self.ipadx = 4
        self.ipady = 3
        # ---- Outer shell coordinates ----
        # => 20 for width = 90 and height = 50
        # Outer shell of the toggle (specific config)
        self.shell_padding = 4
        self.shell_radius = self.radius + self.shell_padding
        self.num_points = 500
        self.rect_width = int(self.width/2)+self.offset_x
        self.rect_height = int(self.height) + self.shell_padding
        self.rect_posx = self.posx + self.radius
        self.rect_posy = self.posy
        self.pill_right_posx = int(self.width/2.5)
        self.pill_right_posy = self.posy
        # ---- GUI elements ---
        self.canvas_container = tk.Canvas
        self.pill_left = int
        self.pill_right = int
        self.pill_center = int
        self.pill_button = int
        # ---- Enabled (Variables) ----
        self.button_colour = button_colour
        self.enabled_colour = button_colour
        self.button_enabled = True
        # ---- Automation ----
        self.command = command
        # ---- Loader ----
        self.main()

    def calculate_radius(self, width: int = 90, height: int = 50, desired_radius: int = 20) -> float:
        # Find the largest value between width and height
        # updated_radius = min(width, height)/4
        if desired_radius == 0 or height == 0:
            return 1
        updated_radius = height/width
        print(f"quotient = {updated_radius}")
        updated_radius = updated_radius * desired_radius
        print(f"updated_radius = {updated_radius}")

        return int(updated_radius)
        # return 20

    def create_circle(self, canvas: tk.Canvas, x: int, y: int, radius: int, num_points: int = 100, **kwargs) -> int:
        points = []
        for i in range(num_points):
            angle = 2 * math.pi * i / num_points
            px = x + radius + radius * math.cos(angle)
            py = y + radius + radius * math.sin(angle)
            points.append(px)
            points.append(py)
        circle_id = canvas.create_polygon(*points, **kwargs)
        return circle_id

    def create_rectangle(self, canvas: tk.Canvas, width: int, height: int, posx: int = 0, posy: int = 0, **kwargs) -> int:
        x1 = posx
        y1 = posy
        x2 = posx + width
        y2 = posy + height
        square_id = canvas.create_rectangle(x1, y1, x2, y2, **kwargs)
        return square_id

    def state(self) -> bool:
        """ Return the state of the toggle """
        return self.button_active

    def set_state(self, state: bool = False) -> None:
        """ Set a specific state (on/off) for the button """
        if state == True and self.button_active == False:
            self.toggle()
        if state == False and self.button_active == True:
            self.toggle()

    def enabled(self, enable: bool = True) -> None:
        """ Define if the button is clickable or not """
        if enable == True:
            self.button_enabled = True
            self.enabled_colour = self.button_colour
            self.canvas_container.itemconfig(
                self.pill_button,
                fill=self.enabled_colour
            )
        else:
            self.button_enabled = False
            if self.button_active == True:
                self.enabled_colour = self.bkg_active
            else:
                self.enabled_colour = self.bkg_inactive
            self.canvas_container.itemconfig(
                self.pill_button,
                fill=self.enabled_colour
            )

    def is_enabled(self) -> bool:
        """ Return the state of the button (enabled: True, disabled: False) """
        return self.button_enabled

    def toggle(self) -> None:
        """ Toggle between and active and an inactive state """
        if self.button_enabled == True:
            if self.button_active == True:
                self.button_active = False
                self.canvas_container.itemconfig(
                    self.pill_left,
                    fill=self.bkg_inactive
                )
                self.canvas_container.itemconfig(
                    self.pill_right,
                    fill=self.bkg_inactive
                )
                self.canvas_container.itemconfig(
                    self.pill_center,
                    fill=self.bkg_inactive,
                    outline=self.bkg_inactive
                )
                self.canvas_container.moveto(
                    self.pill_button,
                    self.posx + self.ipadx,
                    self.posy + self.ipady
                )
            else:
                self.button_active = True
                self.canvas_container.itemconfig(
                    self.pill_left,
                    fill=self.bkg_active
                )
                self.canvas_container.itemconfig(
                    self.pill_right,
                    fill=self.bkg_active
                )
                self.canvas_container.itemconfig(
                    self.pill_center,
                    fill=self.bkg_active,
                    outline=self.bkg_active
                )
                self.canvas_container.moveto(
                    self.pill_button,
                    self.pill_right_posx,
                    self.posy + self.ipady
                )
            if self.command != None:
                self.command()

    def is_clicked(self, event: tk.Event) -> None:
        # Get the coordinates of the click
        if self.button_enabled == False:
            return
        button_sections = [
            self.pill_button,
            self.pill_center,
            self.pill_left,
            self.pill_right
        ]
        for i in button_sections:
            current_one = self.canvas_container.gettags(i)
            if len(current_one) == 2 and current_one[1] == 'current':
                self.toggle()
                return
        return

    def main(self):
        self.canvas_container = tk.Canvas(
            self.window,
            width=self.width,
            height=self.height,
            background=self.system_bkg_col
        )
        self.canvas_container.pack(expand=True)
        bkg = self.bkg_inactive
        self.pill_left = self.create_circle(
            self.canvas_container,
            x=self.posx,
            y=self.posy,
            radius=self.shell_radius,
            num_points=self.num_points,
            fill=bkg,
            tags="pill_left"
        )
        self.pill_right = self.create_circle(
            self.canvas_container,
            x=self.pill_right_posx,
            y=self.pill_right_posy,
            radius=self.shell_radius,
            num_points=self.num_points,
            fill=bkg,
            # fill="cyan",
            tags="pill_right"
        )
        self.pill_center = self.create_rectangle(
            self.canvas_container,
            width=self.rect_width,
            height=self.rect_height,
            posx=self.rect_posx,
            posy=self.rect_posy,
            fill=bkg,
            # fill="orange",
            outline=bkg,
            # outline="orange",
            tags="pill_center"
        )
        self.pill_button = self.create_circle(
            self.canvas_container,
            x=self.posx+self.ipadx,
            y=self.posy+self.ipady,
            radius=self.radius,
            num_points=self.num_points,
            fill=self.enabled_colour,
            tags="pill_button"
        )
        self.canvas_container.bind("<Button-1>", self.is_clicked)


if __name__ == "__main__":
    sys_bkg_col = "#FFFFFF"
    bkg_active = "#1B73BA"
    bkg_inactive = "#666666"
    button_colour = "#FFFFFF"
    width = 65
    height = 35
    radius = 15
    window_width = 200
    window_height = 250
    root = tk.Tk()
    root['bg'] = "black"
    root.geometry(f"{window_width}x{window_height}")
    toggle = RoundToggleSwitch(
        root,
        sys_bkg_col,
        bkg_active,
        bkg_inactive,
        button_colour,
        width,
        height,
        radius
    )
    tk.Button(
        root,
        text="enable toggle switch",
        command=partial(toggle.enabled, True)
    ).pack(side=tk.TOP)
    tk.Button(
        root,
        text="disable toggle switch",
        command=partial(toggle.enabled, False)
    ).pack(side=tk.TOP)
    root.mainloop()
