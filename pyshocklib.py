#!/usr/bin/python3

from enum import Enum
from pyshocklibdevices import ArduinoManager

import config

class Action(Enum):
    LED = 10
    BEEP = 11
    VIB = 12
    ZAP = 13

    BOOT = 100
    BOOTED = 101
    ADD = 102

    ACKNOWLEDGE = 200
    PING = 201
    PONG = 202

    DEBUG = 253
    ERROR = 254
    CRASH = 255

class Pyshock:
    def boot(self):
        arduino_required = False
        for device in config.devices:
            if device.is_arduino_required():
                arduino_required = True
                break
        
        arduino_manager = None
        if arduino_required:
            arduino_manager = ArduinoManager()
            arduino_manager.boot()

        for device in config.devices:
            device.boot(arduino_manager)


    def command(self, action, device, level, duration):
        config.devices[device].command(action, level, duration)


class PyshockMock:
    def command(self, action, device, level, duration):
        print("command: " + str(action) + ", device: " + str(device) + ", level: " + str(level) + ", duration: " + str(duration))
    
    def boot(self):
        print("Loaded mock")
