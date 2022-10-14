from time import sleep
from math import fmod
from random import random, shuffle, seed
import palette
import effect
import config


class ColorAmbleEffect(effect.Effect):

    NAME = "color-amble"
    PERIOD = 3

    def __init__(self, led_art):
        effect.Effect.__init__(self, led_art, self.NAME)
        seed()
        self.palette = palette.ColorSchemePalette([(255, 0, 0), (255, 160, 0), (255, 0, 255)])
        self.hue = random()
        self.next_color()
        self.leds = []
        self.init = True

    def reset(self):
        self.init = True
        self.leds = []
        self.next_color()

    def nudge(self):
        self.next_color()

    def set_color(self, color):
        self.color = color
        self.leds = []

    def next_color(self):
        self.hue = fmod(self.hue + .1 + (random() * .05), 1.0)
        self.color = self.palette.color(self.hue)

    def loop(self):

        if self.init:
            self.init = False
            self.led_art.set_color(self.color)
            self.led_art.show()
            self.next_color()

        if not self.leds:
            self.leds = [ i for i in range(config.NUM_LEDS) ]
            shuffle(self.leds)
            self.next_color()

        if self.leds:
            self.led_art.set_led_color(self.leds.pop(), self.color)

        self.led_art.show()
        sleep(.1)
