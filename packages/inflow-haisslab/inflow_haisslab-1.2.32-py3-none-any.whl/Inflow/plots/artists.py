# -*- coding: utf-8 -*-
"""
Created on Wed Feb  8 19:56:30 2023

@author: tjostmou
"""

import matplotlib, numpy as np


class DottedYLine(matplotlib.lines.Line2D):
    def __init__(self, x, y):
        super().__init__(np.array([0, x]), np.array([y, y]), linestyle="--", linewidth=0.5, alpha=0.5, color="black")

    def draw(self, renderer):
        _xlim = self.axes.get_xlim()[0]
        _data = self.get_data()
        self.set_data(np.array([_xlim, _data[0][1]]), _data[1])
        super().draw(renderer)


class DelayedYTickAdder(matplotlib.artist.Artist):
    def __init__(self, value):
        self.tick_value_to_add = value
        super().__init__()

    def draw(self, renderer):
        current_yticks = self.axes.get_yticks()
        self.axes.set_yticks(list(current_yticks) + [self.tick_value_to_add])
