#
# Copyright nilswinter 2020-2021. License: AGPL
# _____________________________________________

import re
import threading

from remoshock.core.action import Action
from remoshock.receiver.receiver import Receiver

lock = threading.RLock()


class Pac(Receiver):
    """communication with PAC ACX collars"""

    button_codes = [
        # 8 22 23
        [0, 0, 0],  # E/P left
        [0, 1, 1],  # B1  right 1
        [0, 1, 0],  # B2  right 2, E/P right
        [1, 1, 0],  # B3  right 3
        [1, 0, 0],  # B4  left 1
        [0, 0, 1],  # B5  left 2
        [1, 0, 1],  # B6  left 3
        [1, 1, 1]   # unused
    ]


    def __init__(self, receiver_properties, transmitter_code, channel):
        super().__init__(receiver_properties)
        self.receiver_properties.capabilities(action_light=False, action_beep=True, action_vibrate=False, action_shock=True)
        self.receiver_properties.timings(duration_min_ms=250, duration_increment_ms=250, awake_time_s=0)
        self.transmitter_code = transmitter_code
        self.button = channel


    def validate_config(self):
        """validates remoshock.ini configuration and prints errors"""

        if re.fullmatch("^[01]{9}$", self.transmitter_code) is None:
            print("ERROR: Invalid transmitter_code \"" + self.transmitter_code + "\" in remoshock.ini.")
            print("The transmitter_code must be sequence of length 9 consisting of the characters 0 and 1")
            return False

        if self.button < 0 or self.button > 7:
            print("ERROR: Invalid button \"" + str(self.button) + "\" in remoshock.ini.")
            print("This parameter needs to be a whole number between 0 and 7 inclusive.")
            return False

        return True


    def is_sdr_required(self):
        """we require a SDR (software defined radio) transmitter.
        There are no Arduino modules working on the required frequency."""
        return True


    def boot(self, _arduino_manader, sdr_sender):
        """keep a references to the sdr_sender for later use"""
        self.sender = sdr_sender


    def generate(self, transmitter_code, intensity, button, beep):
        """generates the data structure with checksum for a single command.

        This method returns the logical data-structure without transmission-encoding.

        @param transmitter_code the unique code of the transmitter as bit string
        @param intensity power level in the PAC scale of 0-63 as but-string
        @param button    index of button
        @param beep      true to send a beep, false to send a shock
        """
        pre_checksum = transmitter_code[0:2] + self.calculate_intensity_code(intensity) + str(self.button_codes[button][0]) + transmitter_code[2:]
        post_checksum = str(beep) + str(self.button_codes[button][1]) + str(self.button_codes[button][2])
        data = pre_checksum + "CCCCC" + post_checksum
        return pre_checksum + self.calculate_checksum(data) + post_checksum


    def calculate_intensity_code(self, intensity):
        """expands power level (in PAC scale from 0-63) from integer to bit-string"""
        res = ""
        for i in range(0, 6):
            res = res + str(intensity // 2**i % 2)
        return res


    def calculate_checksum(self, data):
        """calculates the checksum of a command data structure

        @param data the command data structure without transmission encoding
                    but with a placeholder for the checksum bits"""

        # a b c d e f g h i  j  k  l  m  n  o p q  r  s
        # 7 6 5 4 3 2 1 0 15 14 13 12 11 10 9 8 23 22 21
        res =       str((int(data[0]) + int(data[ 8])) % 2)                   # noqa: E201, E222
        res = res + str((int(data[1]) + int(data[ 9]) + int(data[21])) % 2)   # noqa: E201, E222
        res = res + str((int(data[2]) + int(data[10]) + int(data[22])) % 2)
        res = res + str((int(data[3]) + int(data[11]) + int(data[23])) % 2)
        res = res + str((int(data[4]) + int(data[12])) % 2)
        return res


    def encode_for_transmission(self, data):
        """encodes a command data structure for transmission over the air.

        This methods adds the synchronization prefix as well as the fillers
        between each bit."""

        prefix = "0101010101010101111"
        filler = "10"
        res = prefix + filler
        for bit in data:
            res = res + bit + filler
        return res


    def send(self, messages):
        """sends messages over the air using the SDR sender.

        @param messages messages that have already been encoded for transmission"""
        self.sender.send(
            frequency=27.10e6,
            sample_rate=2e6,
            carrier_frequency=27.1e6,
            modulation_type="FSK",
            samples_per_symbol=3100,
            low_frequency=92e3,
            high_frequency=95e3,
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
            delay = self.receiver_properties.beep_shock_delay_ms / 1000
            message = self.encode_for_transmission(self.generate(self.transmitter_code, 0, self.button, 1)) + "/" + str(delay) + "s "

        beep = 0
        if action == Action.BEEP or action == Action.VIBRATE:
            beep = 1
        if action == Action.LIGHT:
            # Note: even power 0 creates a tiny shock
            power = 0

        if duration < 250:
            duration = 250
        if duration > 10000:
            duration = 10000

        message_template = self.encode_for_transmission(self.generate(self.transmitter_code, power * 63 // 100, self.button, beep))
        for _ in range(0, round(duration / 250)):
            message = message + message_template + " "

        self.send(message)
