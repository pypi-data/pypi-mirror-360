"""
File: biomatplotlib.py
Description: Drawing aid library for matplotlib.
CreateDate: 2024/7/18
Author: xuwenlin
E-mail: wenlinxu.njfu@outlook.com
"""
from typing import List, Literal
from os import listdir
from numpy import random
from matplotlib.axes import Axes
import matplotlib.colors as mc
from click import echo


def get_font(font_name: str):
    path = '/'.join(__file__.split('/')[:-1]) + '/font'
    all_fonts = [i.split('.')[0] for i in listdir(path)]
    if font_name not in all_fonts:
        msg = f"\033[31mError: {font_name} font not found. Available fonts: {' '.join(all_fonts)}\033[0m"
        echo(msg, err=True)
    else:
        return f'{path}/{font_name}.ttf'


def generate_unique_colors(num_colors: int) -> List[str]:
    """Randomly generates a specified number of non-redundant hexadecimal color codes."""

    def __generate_unique_colors(num_colors):
        colors = set()
        while len(colors) < num_colors:
            r, g, b = random.rand(3)
            color = (r, g, b)
            colors.add(color)
        return colors

    unique_colors = __generate_unique_colors(num_colors)
    hex_colors = [mc.to_hex(color) for color in unique_colors]
    return hex_colors


def rotate_ax_tick_labels(axes: Axes,
                          axis: Literal['x', 'y', 'both'],
                          rotation: int = 0,
                          fontproperties: dict = None):
    """Rotate coordinate axis tick labels and fix Unicode minus signs without changing the scale of the axes and their labels."""
    axis = axis.lower()
    for ax in (["x", "y"] if axis == "both" else [axis]):
        # Dynamically obtain tags and process Unicode negative signs
        labels = [t.get_text().replace("−", "-") for t in getattr(axes, f"get_{ax}ticklabels")()]
        # Dynamically set the scale and rotation Angle of the coordinate axes
        getattr(axes, f"set_{ax}ticks")(
            [float(label) for label in labels],
            labels=labels,
            rotation=rotation,
            fontproperties=fontproperties
        )
