#!/usr/bin/python3

import serial
import time

ser = serial.Serial('/dev/ttyACM0')
ser.flushInput()

ser.write(bytes.fromhex("C900"))

ser.write(bytes.fromhex("0B 04  00 05  10 00"))

while (True):
    if (ser.in_waiting < 2):
        time.sleep(0.1);
        continue;
    data = ser.read(2);
    params = ser.read(data[1]);
    print(data);
    print(params);
    print(" ");
    

ser.close();
