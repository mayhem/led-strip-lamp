from time import sleep
from math import fmod
from random import random
import palette
import effect


class ThemeEffect(effect.Effect):

    NAME = "theme"

    def __init__(self, led_art):
        effect.Effect.__init__(self, led_art, self.NAME)

    def loop(self):
        self.led_art.set_color((136, 1, 202))
        self.led_art.show()
        sleep(.1)
