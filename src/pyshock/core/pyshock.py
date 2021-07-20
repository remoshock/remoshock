#!/usr/bin/python3
#
# Copyright nilswinter 2020-2021. License: AGPL
#_______________________________________________

import configparser
import sys

from pyshock.core.config import ConfigManager

from pyshock.device.arshock import ArduinoManager
from pyshock.device.pacdog import Pacdog

class Pyshock:

    def __instantiate_device(self, section):
        device_type = self.config.get(section, "type")
        name = self.config.get(section, "name")
        color = self.config.get(section, "color")
        code = self.config.get(section, "transmitter_code")
        button = self.config.getint(section, "button")

        if device_type.lower() == "pac":
            device = Pacdog(name, color, code, button)
        else:
            print("ERROR: Unknown receiver type \"" + device_type + "\" in pyshock.ini. Supported types: pac")
            return None

        if device.validate_config():
            return device

        return None


    def __instantitate_sdr_sender(self):
        sdr = self.config.get("global", "sdr", fallback=None)
        # TODO: read sdr from CLI args
        if sdr == None:
            print()
            print("SDR (software defined radio) hardware is required to send radio signals.")
            print()
            print("Please edit pyshock.ini and add an entry sdr=... in the [global] section.")
            print()
            print("Supported devices are (upper/lower case is imporant):") 
            print("AirSpy R2, AirSpy Mini, BladeRF, FUNcube, HackRF, LimeSDR, PlutoSDR, SDRPlay, USRP")
            print()
            sys.exit(1)

        print()
        print("Please make sure your SDR sending hardware is connected and ready. Avoid USB hubs.")

        if sdr.lower() == "hackrf":
            print()
            print("We are using internal URH invokation for HackRF. This is recommanded because it")
            print("prevents a one second delay. But it might cause Python errors, if the URH version is")
            print("incompatible. In this case, please specify srd=hackrfcli in pyshock.ini")
            print()
            print("If the device is not connected or not ready, driver initialization will fail right now")
            print("...")
            
            from pyshock.sdr.urhinternal import UrhInternalSender
            return UrhInternalSender()
            print("Yeah! Driver initialized successfully.")
            print()

        if sdr.lower() == "hackrfcli":
            sdr = "HackRF"

        print("Using " + sdr + " via urh_cli")
        from pyshock.sdr.urhcli import UrhCliSender
        return UrhCliSender(sdr)


    def _setup_from_config(self):
        self.config = ConfigManager().config
        devices = []
        for device in self.config.sections():
            if device.startswith("device"):
                try:
                    device = self.__instantiate_device(device)
                    if device != None:
                        devices.append(device)
                except configparser.NoOptionError as e:
                    print("Error reading configuration file: " + str(e))

        if len(devices) == 0:
            print()
            print("ERROR: No valid devices configured in pyshock.ini")
            sys.exit(1)
        self.devices = devices


    def boot(self):
        self._setup_from_config()
        arduino_required = False
        sdr_required = False
        
        for device in self.devices:
            if device.is_arduino_required():
                arduino_required = True
            if device.is_sdr_required():
                sdr_required = True

        arduino_manager = None
        if arduino_required:
            arduino_manager = ArduinoManager()
            arduino_manager.boot()

        sdr_sender = None
        if sdr_required:
            sdr_sender = self.__instantitate_sdr_sender()

        for device in self.devices:
            device.boot(arduino_manager, sdr_sender)


    def command(self, action, device, level, duration):
        self.devices[device].command(action, level, duration)


    def get_config(self):
        result = []
        for device in self.devices:
            result.append(device.get_config())
        return result



class PyshockMock(Pyshock):

    def command(self, action, device, level, duration):
        print("command: " + str(action) + ", device: " + str(device) + ", level: " + str(level) + ", duration: " + str(duration))


    def boot(self):
        self._setup_from_config()
        print("Loaded mock")
