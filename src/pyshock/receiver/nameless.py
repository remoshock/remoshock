#
# Copyright nilswinter 2021. License: AGPL
# ________________________________________


import re
import threading

from pyshock.core.action import Action
from pyshock.receiver.receiver import Receiver

lock = threading.RLock()


class Nameless(Receiver):

    def __init__(self, name, color, transmitter_code, button):
        super().__init__(name, color)
        self.transmitter_code = transmitter_code
        self.button = button


    def validate_config(self):
        """validates pyshock.ini configuration and prints errors"""

        if re.fullmatch("^[01]{16}$", self.transmitter_code) is None:
            print("ERROR: Invalid transmitter_code \"" + self.transmitter_code + "\" in pyshock.ini.")
            print("The transmitter_code must be sequence of length 16 consisting of the characters 0 and 1")
            return False

        if self.button < 1 or self.button > 3:
            print("ERROR: Invalid button \"" + str(self.button) + "\" in pyshock.ini.")
            print("This parameter needs to be a whole number between 1 and 3 inclusive.")
            return False

        return True


    def is_sdr_required(self):
        """we require a SDR (software defined radio) transmitter."""
        return True


    def boot(self, _arduino_manader, sdr_sender):
        """keep a references to the sdr_sender for later use"""
        self.sender = sdr_sender
        # TODO schedule keep awake timer


    def generate(self, action, power):
        ## TODO generate messages
        return "xxx"


    def encode_for_transmission(self, data):
        """encodes a command data structure for transmission over the air.

        This methods adds the synchronization prefix, suffx as well"""

        prefix = "111111000"
        suffix="1000100010000"
        res = prefix
        for bit in data:
            if bit == "0":
                res = res + "1000"
            else:
                res = res + "1110"
        res = res + suffix
        return res


    def send(self, messages):
        """sends messages over the air using the SDR sender.

        @param messages messages that have already been encoded for transmission"""
        self.sender.send(
            frequency=433.92e6,
            sample_rate=2e6,
            carrier_frequency=30.716e3,
            modulation_type="ASK",
            samples_per_symbol=500,
            low_frequency=0,
            high_frequency=100,
            pause=262924,  # TODO
            data=messages)


    def command(self, action, power, duration):
        """sends a command to the receiver.

        A command may consist of several messages, e. g. one message
        for every 250ms of the duration parameter.

        @param action action perform (e. g. BEEP)
        @param power power level (1-100)
        @param duration duration in ms
        """

        # TODO validate action, power and duration

        message = ""
        message_template = self.encode_for_transmission(self.generate(action, power))

        # TODO handle repeats for duration
        for _ in range(0, 3):
            message = message + " " + message_template

        self.send(message)
