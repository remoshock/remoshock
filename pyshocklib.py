#!/usr/bin/python3

import time
from enum import Enum
from pyshocklibdevices import Action, ArduinoManager

import config

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
