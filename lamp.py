import abc
import sys
import socket
import json
import math
import traceback
from random import random, randint, seed
from math import fmod, sin, pi
from time import sleep, time
from neopixel import *
import paho.mqtt.client as mqtt
from colorsys import hsv_to_rgb, rgb_to_hsv, rgb_to_hsv

import config

TOPIC = config.NAME + "/set"


CHANNEL_0     = 0
CHANNEL_1     = 1
CHANNEL_BOTH  = 2
INITIAL_BRIGHTNESS = 30

from effect import solid_effect
from effect import bootie_call_effect
from effect import chill_bed_time_effect

class LEDStripLamp(object):


    def __init__(self):
        self.state = False
        self.brightness = 0

        self.effect_list = []
        self.current_effect = None
        self.current_effect_index = -1

        self.strips = [ Adafruit_NeoPixel(config.NUM_LEDS, config.CH0_LED_PIN, 800000, 10, False, 255, 0),
                        Adafruit_NeoPixel(config.NUM_LEDS, config.CH1_LED_PIN, 800000, 10, False, 255, 1) ]
        for s in self.strips:
            s.begin()

        self.mqttc = None


    def publish(self, topic, payload):
        if not self.mqttc:
            return

        self.mqttc.publish(topic, payload)


    def set_color(self, col, channel=CHANNEL_BOTH):
        for i in range(config.NUM_LEDS):
            if channel == CHANNEL_0 or channel == CHANNEL_BOTH:
                self.strips[0].setPixelColor(i, Color(col[1], col[0], col[2]))
            if channel == CHANNEL_1 or channel == CHANNEL_BOTH:
                self.strips[1].setPixelColor(i, Color(col[1], col[0], col[2]))


    def set_led_color(self, led, col, channel=CHANNEL_BOTH):
        if channel == CHANNEL_0 or channel == CHANNEL_BOTH:
            self.strips[0].setPixelColor(led, Color(col[1], col[0], col[2]))
        if channel == CHANNEL_1 or channel == CHANNEL_BOTH:
            self.strips[1].setPixelColor(led, Color(col[1], col[0], col[2]))


    def show(self, channel=CHANNEL_BOTH):
        if channel == CHANNEL_0 or channel == CHANNEL_BOTH:
            self.strips[0].show()
        if channel == CHANNEL_1 or channel == CHANNEL_BOTH:
            self.strips[1].show()


    def clear(self, channel=CHANNEL_BOTH):
        self.set_color((0,0,0), channel)
        self.show(channel)

    def turn_on(self):
        self.state = True

    def turn_off(self):
        self.state = False

    def set_effect(self, effect_name, brightness=None):
        print("effect: %s" % effect_name)
        for i, effect in enumerate(self.effect_list):
            if effect.name == effect_name:
                self.turn_off()
                self.current_effect = effect 
                self.current_effect.setup()
                self.current_effect_index = i
                if brightness is not None:
                    self.brightness = brightness
                self.turn_on()
                break
        else:
            print("Unknown effect %s" % effect_name)

    def set_color_effect(self, color, brightness=None):
        for i, effect in enumerate(self.effect_list):
            if effect.name == "solid":
                self.turn_off()
                self.current_effect = effect 
                self.current_effect.setup()
                self.current_effect_index = i
                self.current_effect.set_color(color)
                if brightness is not None:
                    self.brightness = brightness
                self.turn_on()
                break

    def add_effect(self, effect):
        self.effect_list.append(effect)
        if len(self.effect_list) == 1:
            self.current_effect = effect 
            self.current_effect.setup()
            self.current_effect_index = 0


    def next_effect(self):
        if self.brightness:
            index = (self.current_effect_index + 1) % len(self.effect_list)
            self.set_effect(str(self.effect_list[index].name))


    def previous_effect(self):
        if self.brightness:
            index = (self.current_effect_index + len(self.effect_list) - 1) % len(self.effect_list)
            self.set_effect(str(self.effect_list[index].name))


    def nudge_effect(self):
        if self.brightness and self.current_effect:
            print("nudge effect")
            self.current_effect.nudge()

    def startup(self):

        colors = ( (128, 0, 128), (128, 30, 0) )

        for p in range(100):
            self.set_led_color(randint(0, config.NUM_LEDS-1), colors[randint(0, 1)], 0)
            self.set_led_color(randint(0, config.NUM_LEDS-1), colors[randint(0, 1)], 1)
            self.show()
            sleep(.002)

        self.clear()


    @staticmethod
    def on_message(mqttc, user_data, msg):
        try:
            mqttc.__led._handle_message(mqttc, msg)
        except Exception as err:
            traceback.print_exc(file=sys.stdout)


    def _handle_message(self, mqttc, msg):

        payload = str(msg.payload, 'utf-8')
        print("%s: %s" % (msg.topic, payload))
        if msg.topic == SET_TOPIC:
            try:
                js = json.loads(str(msg.payload, 'utf-8'))
                state = js["state"]
            except KeyError:
                return

            brightness = js.get("brightness", None)
            rgb = js.get("rgb", None)
            effect = js.get("effect", None)

            print(js)

            if brightness is not None and (brightness < 0 or brightness > 100):
                return

            if not state:
                self.turn_off() 
                return

            if effect is None and rgb is None:
                return

            if effect is not None:
                print("set effect", effect)
                self.set_effect(effect, brightness)
            else:
                print("set color", rgb)
                self.set_color_effect(rgb, brightness)

            return
        

    def setup(self):
        self.clear()

        self.mqttc = mqtt.Client(CLIENT_ID)
        self.mqttc.on_message = Lips.on_message
        self.mqttc.connect("10.1.1.2", 1883, 60)
        self.mqttc.loop_start()
        self.mqttc.__led = self

        effect_name_list = []
        for effect in self.effect_list:
            print("adding effect %s" % effect.name)
            effect_name_list.append(effect.name)

        self.mqttc.subscribe(SET_TOPIC)


    def loop(self):
        if self.current_effect and self.state:
            self.current_effect.loop()

            # If we come out of an update loop and we got turned off, oops. clean up
            if not self.state:
                self.clear()


if __name__ == "__main__":
    seed()
    a = Lips()
#    a.add_effect(color_amble_effect.ColorAmbleEffect(a))
    a.add_effect(solid_effect.SolidEffect(a))
    a.add_effect(chill_bed_time_effect.ChillBedTimeEffect(a))
#    a.add_effect(sparkle_effect.SparkleEffect(a))
#    a.add_effect(dynamic_colorcycle_effect.DynamicColorCycleEffect(a))
#    a.add_effect(undulating_effect.UndulatingEffect(a))
    a.add_effect(bootie_call_effect.BootieCallEffect(a, .0005))
#    a.add_effect(test_effect.TestEffect(a))

    a.setup()
    if config.TURN_ON_AT_START:
        a.turn_on()
    try:
        while True:
            a.loop()
            sleep(.001)
    except KeyboardInterrupt:
        a.turn_off()
        a.mqttc.disconnect()
        a.mqttc.loop_stop()
