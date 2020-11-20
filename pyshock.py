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
        if (data[0] == Action.ACKNOWLEDGE):
            break
        params = ser.read(data[1])
        print(data[0])
        print(params)
        print(" ")

def send():
    ser.write(data)
    read_responses()


ser = serial.Serial('/dev/ttyACM0')
ser.flushInput()

send(bytes.fromhex("C900"))

"""
for i in range (0, 20):
  send(bytes.fromhex("0A 04  00 04  00 00"))
  time.sleep(30);
for i in range (0, 20):
  send(bytes.fromhex("0B 04  00 04  00 00"))
  time.sleep(2);

send(bytes.fromhex("0C 04  00 01  00 00"))
"""

time.sleep(10);
for i in range (1, 9):
  send(bytes.fromhex("0B 04  00 04  00 00"))
  time.sleep(1);
  send(bytes.fromhex("0D 04  00 0" + str(i) + "  00 00"))
  time.sleep(10);


ser.close();

