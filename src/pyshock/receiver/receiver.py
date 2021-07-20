#!/usr/bin/python3
#
# Copyright nilswinter 2020-2021. License: AGPL
#_______________________________________________


class Receiver:
    def __init__(self, name, color):
        self.name = name
        self.color = color

    def is_arduino_required(self):
        return False

    def is_sdr_required(self):
        return False

    def boot(self, _arduino_manager, _sdr_sender):
        pass

    def command(self, action, level, duration):
        pass

    def get_config(self):
        config = {
            "name": self.name,
            "color": self.color,
            "power": 10,
            "duration": 500,
            "durationIncrement": 250
        }
        return config
