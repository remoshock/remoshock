#!/usr/bin/python3

import serial
import time
from enum import Enum

class Action(Enum):
  LED = 10
  BEEP = 11
  VIB = 12
  ZAP = 13

  ACKNOWLEDGE = 200
  PING = 201
  PONG = 202

  DEBUG = 253
  ERROR = 254
  CRASH = 255



def read_responses():
    while (True):
        if (ser.in_waiting < 2):
            time.sleep(0.1)
            continue
        data = ser.read(2)
        if (data[0] == Action.ACKNOWLEDGE.value):
            break
        params = ser.read(data[1])
        print(data[0])
        print(params)
        print(" ")

def send(data):
    ser.write(data)
    read_responses()

def command(action, channel, level, duration):
    l = [action.value, 4, channel, level, int(duration / 256), duration % 256]
    data = bytes(l)
    send(data)

ser = serial.Serial('/dev/ttyACM0')
ser.flushInput()

#command(Action.BEEP, 0, 5, 5000)

"""
for i in range (0, 20):
  send(bytes.fromhex("0A 04  00 04  00 00"))
  time.sleep(30);
for i in range (0, 20):
  command(Action.VIB, 0, 1, 0)
  time.sleep(2);
"""


for i in range (1, 10):
  time.sleep(10);
  command(Action.BEEP, 0, 0, 0)
  time.sleep(1);
  command(Action.VIB, 0, i, 0)

ser.close();

