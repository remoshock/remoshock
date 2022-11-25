#
# Copyright nilswinter 2020-2021. License: AGPL
# _____________________________________________

import re
import threading

from remoshock.core.action import Action
from remoshock.receiver.receiver import Receiver

lock = threading.RLock()


class Dogtra(Receiver):
    end_one = True

    """communication with Dogtra collars"""
    power_mapping = [
        0, 0, 0, 0, 0, 1, 3, 5, 7, 8,
        10, 12, 14, 16, 18, 20, 22, 24, 26, 28,
        30, 31, 32, 34, 36, 37, 38, 40, 42, 43,
        45, 47, 49, 50, 52, 54, 56, 57, 59, 61,
        63, 64, 65, 66, 68, 70, 72, 74, 76, 78,
        80, 82, 85, 87, 89, 91, 93, 95, 98, 100,
        103, 105, 107, 109, 111, 114, 117, 120, 124, 126,
        128, 132, 137, 140, 144, 149, 154, 157, 161, 165,
        170, 174, 179, 184, 190, 195, 200, 205, 210, 215,
        221, 226, 231, 237, 243, 249, 255, 255, 255, 255,
        255]


    def __init__(self, receiver_properties, transmitter_code, channel):
        super().__init__(receiver_properties)
        self.receiver_properties.capabilities(action_light=False, action_beep=False, action_vibrate=True, action_shock=True)
        self.receiver_properties.timings(duration_min_ms=250, duration_increment_ms=250, awake_time_s=0)  # TODO
        self.transmitter_code = transmitter_code
        self.channel = channel


    def validate_config(self):
        """validates remoshock.ini configuration and prints errors"""

        if re.fullmatch("^[01]{12}$", self.transmitter_code) is None:
            print("ERROR: Invalid transmitter_code \"" + self.transmitter_code + "\" in remoshock.ini.")
            print("The transmitter_code must be sequence of length 12 consisting of the characters 0 and 1")
            return False

        if self.channel < 1 or self.channel > 1:
            print("ERROR: Invalid channel \"" + str(self.channel) + "\" in remoshock.ini.")
            print("This parameter needs to be 1")
            return False

        return True


    def is_sdr_required(self):
        """we require a SDR (software defined radio) transmitter.
        There are no Arduino modules working on the required frequency."""
        return True


    def boot(self, _arduino_manader, sdr_sender):
        """keep a references to the sdr_sender for later use"""
        self.sender = sdr_sender


    def generate(self, transmitter_code, intensity, vibrate):
        """generates the data structure for a single command.

        This method returns the logical data-structure without transmission-encoding.

        @param transmitter_code the unique code of the transmitter as bit string
        @param intensity power level in the Dogtra scale of 0-255 as bit-string
        @param vibrate   true to send a vibration (page-command), false to send a shock
        """
        cmd = "100"
        if vibrate:
            cmd = "001"
        return transmitter_code + "1" + cmd + self.calculate_intensity_code(intensity)


    def calculate_intensity_code(self, power):
        """expands power level (in Dogtra scale from 0-255) from integer to bit-string"""

        #   0% -->   0: 0101000000000000000000
        #  20% -->  28: 0001111111110100000000
        #  40% -->  62: 0000000111010000000000
        #  60% --> 103: 1011110100000000000000
        #  80% --> 171: 1000000001101000000000
        # 100% --> 255: 1100000011111101000000

        # (number of leading 1)   times 100 (may be none, one or two)
        # (number of 0 minus one) times  10
        # (number of 1 minus one) times   1
        # some transmitter have a suffix of 01, others don't have it

        intensity = self.power_mapping[power]

        res = ""
        for _ in range(0, intensity // 100):
            res = res + "1"

        intensity = intensity % 100
        for _ in range(0, intensity // 10 + 1):
            res = res + "0"

        intensity = intensity % 10
        for _ in range(0, intensity + 1):
            res = res + "1"

        if self.end_one:
            res = res + "01"
        else:
            res = res + "00"
        return res.ljust(22, "0")


    def encode_for_transmission(self, data):
        """encodes a command data structure for transmission over the air.

        This methods adds the synchronization prefix as well as the fillers
        between each bit in the first part of the message."""

        if self.end_one:
            prefix = "11100"
        else:
            prefix = "1111100"

        filler = "01"
        res = prefix + filler
        for i in range(0, 16):
            res = res + data[i] + filler
        return res + data[16:]


    def send(self, messages):
        """sends messages over the air using the SDR sender.

        @param messages messages that have already been encoded for transmission"""
        self.sender.send(
            frequency=27.1e6,
            sample_rate=2e6,
            carrier_frequency=27.1e6,
            modulation_type="FSK",
            samples_per_symbol=1500,
            low_frequency=41e3,
            high_frequency=46e3,
            pause=262924,
            data=messages)


    def command(self, action, power, duration):
        """sends a command to the receiver.

        A command may consist of several messages, e. g. one message
        for every 250ms of the duration parameter.

        @param action action perform (e. g. BEEP)
        @param power power level (1-100)
        @param duration duration in ms
        """

        if action == Action.KEEPAWAKE:
            return

        message = ""
        if action == Action.BEEPSHOCK:
            message_template = self.encode_for_transmission(self.generate(self.transmitter_code, 50, 1))
            delay = self.receiver_properties.beep_shock_delay_ms / 1000
            message = message_template + message_template + message_template + "/" + str(delay) + "s "

        beep = 0
        if action == Action.BEEP or action == Action.VIBRATE:
            beep = 1
        if action == Action.LIGHT:
            # Note: even power 0 might create a tiny shock
            power = 0

        if duration < 250:
            duration = 250
        if duration > 10000:
            duration = 10000

        message_template = self.encode_for_transmission(self.generate(self.transmitter_code, power, beep))
        for _ in range(0, round(duration / 60)):
            message = message + message_template

        start_of_transmission = "11111110000000111111100000000000"
        self.send(start_of_transmission + message.strip())
