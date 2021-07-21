#!/usr/bin/python3
#
# Copyright nilswinter 2020-2021. License: AGPL
#_______________________________________________

import configparser
import sys

from pyshock.core.config import ConfigManager

from pyshock.receiver.arshock import ArduinoManager
from pyshock.receiver.pacdog import Pacdog

class Pyshock:

    def __init__(self, args):
        self.args = args

    def __instantiate_receiver(self, section):
        receiver_type = self.config.get(section, "type")
        name = self.config.get(section, "name")
        color = self.config.get(section, "color")
        code = self.config.get(section, "transmitter_code")
        button = self.config.getint(section, "button")

        if receiver_type.lower() == "pac":
            receiver = Pacdog(name, color, code, button)
        else:
            print("ERROR: Unknown receiver type \"" + receiver_type + "\" in pyshock.ini. Supported types: pac")
            return None

        if receiver.validate_config():
            return receiver

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
            print("Supported devices are (upper/lower case is important):") 
            print("HackRF, LimeSDR")
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
            sender = UrhInternalSender(self.args.verbose)
            print("Yeah! Driver initialized successfully.")
            print()
            return sender

        if sdr.lower() == "hackrfcli":
            sdr = "HackRF"

        print("Using " + sdr + " via urh_cli")
        from pyshock.sdr.urhcli import UrhCliSender
        return UrhCliSender(sdr, self.args.verbose)


    def _setup_from_config(self):
        self.config = ConfigManager().config
        receivers = []
        for receiver in self.config.sections():
            if receiver.startswith("receiver"):
                try:
                    receiver = self.__instantiate_receiver(receiver)
                    if receiver != None:
                        receivers.append(receiver)
                except configparser.NoOptionError as e:
                    print("Error reading configuration file: " + str(e))

        if len(receivers) == 0:
            print()
            print("ERROR: No valid receivers configured in pyshock.ini")
            sys.exit(1)
        self.receivers = receivers


    def boot(self):
        self._setup_from_config()
        arduino_required = False
        sdr_required = False
        
        for receiver in self.receivers:
            if receiver.is_arduino_required():
                arduino_required = True
            if receiver.is_sdr_required():
                sdr_required = True

        arduino_manager = None
        if arduino_required:
            arduino_manager = ArduinoManager()
            arduino_manager.boot()

        sdr_sender = None
        if sdr_required:
            sdr_sender = self.__instantitate_sdr_sender()

        for receiver in self.receivers:
            receiver.boot(arduino_manager, sdr_sender)


    def command(self, action, receiver, level, duration):
        self.receivers[receiver].command(action, level, duration)


    def get_config(self):
        result = []
        for receiver in self.receivers:
            result.append(receiver.get_config())
        return result



class PyshockMock(Pyshock):

    def __init__(self, args):
        self.args = args

    def command(self, action, receiver, level, duration):
        print("command: " + str(action) + ", receiver: " + str(receiver) + ", level: " + str(level) + ", duration: " + str(duration))


    def boot(self):
        self._setup_from_config()
        print("Loaded mock")
