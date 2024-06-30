#!/usr/bin/env python3

import FreeSimpleGUI as sg


# Wrapper classes for sg:

class Header(sg.Text):
    def __init__(self, p, text, **kw):

        # Figure out scaled font size
        scaled_font_size = int(p.font_scale * 11.0)

        #kw.setdefault("p", (2, 2))
        kw.setdefault("p", ((2, 2), (10, 0)))
        kw.setdefault("font", ('Arial', scaled_font_size, "bold"))
        super().__init__(text=text, **kw)


class Text(sg.Text):
    def __init__(self, p, text, **kw):

        # Figure out scaled font size
        scaled_font_size = int(p.font_scale * 10.0)

        kw.setdefault("p", (2, 2))
        kw.setdefault("font", ('Arial', scaled_font_size))
        super().__init__(text=text, **kw)


class Spin(sg.Spin):
    def __init__(self, p, values, initial_value, **kw):

        # Figure out scaled font size
        scaled_font_size = int(p.font_scale * 10.0)

        kw.setdefault("p", (2, 2))
        kw.setdefault("size", (10, 1))
        kw.setdefault("font", ('Arial', scaled_font_size))
        kw.setdefault("enable_events", True)
        super().__init__(values=values, initial_value=initial_value, **kw)


class Input(sg.Input):
    def __init__(self, p, default_value, **kw):

        # Figure out scaled font size
        scaled_font_size = int(p.font_scale * 10.0)

        kw.setdefault("p", (2, 2))
        kw.setdefault("font", ('Arial', scaled_font_size))
        kw.setdefault("enable_events", True)
        super().__init__(default_text=default_value, **kw)


class Slider(sg.Slider):
    def __init__(self, p, type, range, default_value, **kw):

        # Figure out scaled font size
        scaled_font_size = int(p.font_scale * 10.0)

        # Int slider
        if type == "int":
            kw.setdefault("range", range)
        elif type == "float":
            kw.setdefault("range", range)
            kw.setdefault("resolution", 0.1)

        kw.setdefault("p", (2, 0))
        kw.setdefault("orientation", "h")
        kw.setdefault("expand_x", True)
        kw.setdefault("enable_events", True)
        kw.setdefault("font", ('Arial', scaled_font_size))
        super().__init__(default_value=default_value, **kw)


class Button(sg.Button):
    def __init__(self, p, text, **kw):

        # Figure out scaled font size
        scaled_font_size = int(p.font_scale * 10.0)

        kw.setdefault("s", (19, 2))
        kw.setdefault("p", (2, 2))
        kw.setdefault("expand_x", True)
        kw.setdefault("font", ('Arial', scaled_font_size))
        super().__init__(button_text=text, **kw)


class Image(sg.Image):
    def __init__(self, source, **kw):
        super().__init__(source=source, **kw)


class Column(sg.Column):
    def __init__(self, layout, **kw):
        kw.setdefault("vertical_alignment", "top")
        super().__init__(layout=layout, **kw)


class Window(sg.Window):
    def __init__(self, title, layout, **kw):
        kw.setdefault("resizable", True)
        super().__init__(title=title, layout=layout, **kw)