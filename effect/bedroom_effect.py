from math import pi, sin
from copy import copy
from colorsys import hsv_to_rgb, rgb_to_hsv, rgb_to_hsv

import config
import gradient
import palette
import effect
from lips import CHANNEL_0, CHANNEL_1, CHANNEL_BOTH

OASIS_COLORS = [(212, 181, 30), (237, 133, 13), (237, 12, 74), (191, 85, 223)]

class BedroomColorSchemeEffect(effect.Effect):

    NAME = "bedtime"

    def __init__(self, led_art):
        effect.Effect.__init__(self, led_art, self.NAME)

    def setup(self):
        self.colors = copy(OASIS_COLORS)

    def reset(self):
        pass

    def set_color(self, color):
        if color in self.colors:
            return

        self.colors[self.color_index] = color
        self.color_index = (self.color_index + 1) % 2


    def loop(self):
        t = self.uoap_index * 2 * pi
        jitter = sin(t) / 4
        p = [ (0.0, self.colors[0]), 
              (0.45 + jitter, self.colors[1]),
              (0.65 + jitter, self.colors[1]),
              (1.0, self.colors[0])
        ]
        g = gradient.Gradient(p, config.NUM_LEDS)
        g.render(self.led_art, CHANNEL_BOTH)

        self.led_art.show()

        self.uoap_index += self.uoap_increment
        if self.uoap_index > 1.0:
            self.uoap_index = 0.0
