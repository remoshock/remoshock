#!/usr/bin/python3

import serial
import time
from enum import Enum
from threading import RLock

# type            code, code, channel
#  0  Pettainer,            sender code first byte, seonder code second byte, channel
#  1  Opto-isolator 1,      beep pin,               vib pin,                  shock pin
#  2  Opto-isolator 2,      beep modifier pin,      ignored,                  pin

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


class DeviceType(Enum):
    PETAINER = 0
    OPTOCOUPLER = 1
    OPTOCOUPLER_BEEP_MODIFIER = 2


class Device:
    def is_arduino_required(self):
        return False

    def boot(self, ignore):
        pass

    def command(self, action, level, duration):
        pass


class ArduinoBasedDevice(Device):
    def __init__(self, device_type, arg1, arg2, arg3):
        self.device_type = device_type
        self.arg1 = arg1
        self.arg2 = arg2
        self.arg3 = arg3

    def is_arduino_required(self):
        return True

    def boot(self, arduino_manager):
        self.arduino_manager = arduino_manager
        self.index = arduino_manager.register_device(self.device_type.value, self.arg1, self.arg2, self.arg3)

    def command(self, action, level, duration):
        self.arduino_manager.command(action, self.index, level, duration)


class ArduinoPetainer(ArduinoBasedDevice):
    def __init__(self, code_first_byte, code_second_byte, channel):
        super().__init__(DeviceType.PETAINER, code_first_byte, code_second_byte, channel)


class ArduinoOptocoupler(ArduinoBasedDevice):
    def __init__(self, pin_beep, pin_vib, pin_zap):
        super().__init__(DeviceType.OPTOCOUPLER, pin_beep, pin_vib, pin_zap)


class ArduinoOptocouplerBeepModifier(ArduinoBasedDevice):
    def __init__(self, pin_modifier_beep, pin_button):
        super().__init__(DeviceType.OPTOCOUPLER_BEEP_MODIFIER, pin_modifier_beep, 0, pin_button)


class ArduinoManager():
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
        self.device_index = -1

        with self.serLock:
            time.sleep(1)
            self.ser.flushInput()

            self.ser.write(bytes([Action.BOOT.value, 0]))
            self.read_responses(Action.BOOTED)
            self.read_responses()

    def register_device(self, device_type, arg1, arg2, arg3):
        with self.serLock:
            self.send(bytes([Action.ADD.value, 4, device_type, arg1, arg2, arg3]))
        self.device_index = self.device_index + 1
        return self.device_index

