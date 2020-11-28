#!/usr/bin/python3

import serial
import time
import random
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

ser = serial.Serial('/dev/ttyACM0')
serLock = RLock()

def read_responses(readUntil = Action.ACKNOWLEDGE):
    while (True):
        if (ser.in_waiting < 2):
            time.sleep(0.1)
            continue
        data = ser.read(2)
        if (data[0] == readUntil.value):
            break

        params = ser.read(data[1])
        if (data[0] != Action.DEBUG.value):
            print(data[0])
        print(params)
        print(" ")

def send(data):
    """sends data and waits for an acknowledgement.

    @param data bytes data to send
    """
    with serLock:
        ser.write(data)
        read_responses()


def command(action, device, level, duration):
    l = [action.value, 4, device, level, int(duration / 256), duration % 256]
    data = bytes(l)
    send(data)


def boot():
    """Boots the Arduino and registers devices defined in config.py"""

    with serLock:
        time.sleep(1)
        ser.flushInput()

        ser.write(bytes([Action.BOOT.value, 0]))
        read_responses(Action.BOOTED)
        read_responses()

        for device in config.devices:
            send(bytes([Action.ADD.value, 4, device[0], device[1], device[2], device[3]]))

boot()

#command(Action.BEEP, 0, 5, 5000)

"""
for i in range (0, 20):
  command(Action.VIB, 0, 1, 0)
  time.sleep(2);
"""

"""
for i in range (1, 10):
    time.sleep(10);
    device = random.randrange(2)
    command(Action.BEEP, device, 0, 0)
    time.sleep(1);
    command(Action.ZAP, device, 1, 0)
"""
command(Action.VIB, 0, 0, 0)
command(Action.VIB, 1, 0, 0)


