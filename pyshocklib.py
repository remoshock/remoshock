#!/usr/bin/python3

import serial
import time
from enum import Enum
from threading import RLock

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

    def read_responses(self, readUntil = Action.ACKNOWLEDGE):
        while (True):
            if (self.ser.in_waiting < 2):
                time.sleep(0.1)
                continue
            data = self.ser.read(2)
            if (data[0] == readUntil.value):
                break

            params = self.ser.read(data[1])
            if (data[0] != Action.DEBUG.value):
                print(data[0])
            print(params)
            print(" ")

    def send(self, data):
        """sends data and waits for an acknowledgement.

        @param data bytes data to send
        """
        with self.serLock:
            self.ser.write(data)
            self.read_responses()


    def command(self, action, device, level, duration):
        l = [action.value, 4, device, level, int(duration / 256), duration % 256]
        data = bytes(l)
        self.send(data)


    def boot(self):
        """Boots the Arduino and registers devices defined in config.py"""

        self.ser = serial.Serial('/dev/ttyACM0')
        self.serLock = RLock()

        with self.serLock:
            time.sleep(1)
            self.ser.flushInput()

            self.ser.write(bytes([Action.BOOT.value, 0]))
            self.read_responses(Action.BOOTED)
            self.read_responses()

            for device in config.devices:
                self.send(bytes([Action.ADD.value, 4, device[0], device[1], device[2], device[3]]))


