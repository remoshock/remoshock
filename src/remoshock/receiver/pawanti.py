#!/usr/bin/python3
#
# Copyright nilswinter 2020-2025. License: AGPL
# _____________________________________________


import re
import threading
import time

from remoshock.core.action import Action
from remoshock.receiver.receiver import Receiver


lock = threading.RLock()


class Pawanti(Receiver):
    """communication with pawanti collars"""

    action_code = {
        Action.BEEP:    "011",  # noqa: E241
        Action.VIBRATE: "010",  # noqa: E241
        Action.SHOCK:   "001"   # noqa: E241
    }


    def __init__(self, receiver_properties, transmitter_code, channel):
        super().__init__(receiver_properties)

        print("Using experimental Pawanti receive. Note: This receiver does not work very reliable (timing issue?)")

        receiver_properties.capabilities(action_light=True, action_beep=True, action_vibrate=True, action_shock=True)
        receiver_properties.timings(duration_min_ms=500, duration_increment_ms=500)
        self.transmitter_code = transmitter_code
        self.channel = channel
        self.checksum = None


    def validate_config(self):
        """validates remoshock.ini configuration and prints errors"""

        if re.fullmatch("^[01]{24}$", self.transmitter_code) is None:
            print("ERROR: Invalid transmitter_code \"" + self.transmitter_code + "\" in remoshock.ini.")
            print("The transmitter_code must be sequence of length 24 consisting of the characters 0 and 1")
            return False

        # TODO: remove False
        # False and
        if self.transmitter_code != "011001010000000000001011" and self.transmitter_code != "011000000000000000001011":
            print("ERROR: Unsupported transmitter_code \"" + self.transmitter_code + "\" in remoshock.ini.")
            print("The transmitter_code must be either 011001010000000000001011 or 011000000000000000001011")
            print(" because the checksum is only known for these specific transmitter codes.")
            return False

        if self.channel < 1 or self.channel > 3:
            print("ERROR: Invalid channel \"" + str(self.channel) + "\" in remoshock.ini.")
            print("This parameter needs to be a whole number between 1 and 3 inclusive.")
            return False

        return True


    def is_sdr_required(self):
        """we require a SDR (software defined radio) transmitter.
        There is an alternative implementation which uses Arduino."""
        return True


    def boot(self, _arduino_manader, sdr_sender):
        """keep a references to the sdr_sender for later use
        and schedules keep-awake messages"""
        self.sender = sdr_sender


    def generate(self, action, power):
        """generates the data structure for a single command.

        This method returns the logical data-structure without transmission-encoding.

        @param action action
        @param power power level in the scale of 0-100
        """
        channel = format(self.channel, '02b')
        action_code = self.action_code[action]
        intensity = format(min(int(power / 100 * 9) + 1, 9), '04b')
        if action == Action.BEEP:
            intensity = "0000"


        if self.checksum is None:
            checksum = self.calcualte_checksum(action_code, intensity)
        else:
            checksum = format(self.checksum, '04b')
        data = "00" + channel + checksum + "0" + action_code + intensity + self.transmitter_code + "1"
        return data


    def calcualte_checksum(self, action_code, intensity_code):
        """calculates the checksum.

        @param action_code binary values of action
        @param intensity_code binary value of power intensity
        """

        # I have no idea how the checksum works so this is a simple
        # lookup table of known values. The channel is not part
        # of the checksum.
        # ...
        # my code:
        if self.transmitter_code == "011001010000000000001011":
            checksum_table = {
                "0110000": "1010",  # noqa: E241
                "0100001": "1000",  # noqa: E241
                "0100010": "1011",  # noqa: E241
                "0100011": "1010",  # noqa: E241
                "0100100": "1101",  # noqa: E241
                "0100101": "1100",  # noqa: E241
                "0100110": "1111",  # noqa: E241
                "0100111": "1110",  # noqa: E241
                "0101000": "0001",  # noqa: E241
                "0101001": "0000",  # noqa: E241
                "0010001": "1001",  # noqa: E241
                "0010010": "1010",  # noqa: E241
                "0010011": "1011",  # noqa: E241
                "0010100": "1100",  # noqa: E241
                "0010101": "1101",  # noqa: E241
                "0010110": "1110",  # noqa: E241
                "0010111": "1111",  # noqa: E241
                "0011000": "0000",  # noqa: E241
                "0011001": "0001",  # noqa: E241
                "1000101": "1100",  # noqa: E241
                "1001010": "0001",  # noqa: E241
            }
            return checksum_table[action_code + intensity_code]
        elif self.transmitter_code == "011000000000000000001011":
            checksum_table = {
                "0110000": "0010",  # noqa: E241
                "0100001": "0100",  # noqa: E241
                "0100010": "0101",  # noqa: E241
                "0100011": "0110",  # noqa: E241
                "0100100": "0111",  # noqa: E241
                "0100101": "0001",  # noqa: E241
                "0100110": "1000",  # noqa: E241
                "0100111": "1011",  # noqa: E241
                "0101000": "1010",  # noqa: E241
                "0101001": "1101",  # noqa: E241
                "0010001": "1011",  # noqa: E241
                "0010010": "1010",  # noqa: E241
                "0010011": "1001",  # noqa: E241
                "0010100": "1000",  # noqa: E241
                "0010101": "1000",  # noqa: E241
                "0010110": "1001",  # noqa: E241
                "0010111": "1010",  # noqa: E241
                "0011000": "1011",  # noqa: E241
                "0011001": "1100",  # noqa: E241
                "1000101": "1011",  # noqa: E241
                "1001010": "1110",  # noqa: E241
            }
            return checksum_table[action_code + intensity_code]
        elif self.transmitter_code == "011100000000000000001011":
            checksum_table = {
                "0110000": "0001",  # noqa: E241
                "0100001": "0101",  # noqa: E241
                "0100010": "0100",  # noqa: E241
                "0100011": "0111",  # noqa: E241
                "0100100": "0110",  # noqa: E241
                "0100101": "1010",  # noqa: E241
                "0100110": "1011",  # noqa: E241
                "0100111": "1000",  # noqa: E241
                "0101000": "1001",  # noqa: E241
                "0101001": "1110",  # noqa: E241
                "0010001": "0110",  # noqa: E241
                "0010010": "1000",  # noqa: E241
                "0010011": "0010",  # noqa: E241
                "0010100": "0011",  # noqa: E241
                "0010101": "",  # noqa: E241
                "0010110": "",  # noqa: E241
                "0010111": "",  # noqa: E241
                "0011000": "",  # noqa: E241
                "0011001": "",  # noqa: E241
                "1000101": "",  # noqa: E241
                "1001010": "",  # noqa: E241
            }
            return checksum_table[action_code + intensity_code]
        print("ERROR: Unsupported transmitter_code")
        return "0000"



    def encode_for_transmission(self, data):
        """encodes a command data structure for transmission over the air.

        This methods adds the synchronization prefix as well as the fillers
        between each bit."""

        prefix = "00000000000000000000000000000000000"
        filler = "0011"
        res = prefix
        for bit in data:
            res = res + filler + bit + bit
        return res


    def send(self, messages):
        """sends messages over the air using the SDR sender.

        @param messages messages that have already been encoded for transmission"""
        self.sender.send(
            frequency=433e6,
            sample_rate=2e6,
            carrier_frequency=433e6,
            modulation_type="FSK",
            samples_per_symbol=500,
            low_frequency="859000",
            high_frequency="928000",
            pause=357599,
            data=messages)


    def command(self, action, power, duration, beep_shock_delay_ms=None):
        """sends a command to the receiver.

        A command may consist of several messages.

        @param action action perform (e. g. BEEP)
        @param power power level (1-100)
        @param duration duration in ms
        """

        if action == Action.KEEPAWAKE:
            action = Action.VIBRATE
            power = 0
            duration = 250
        message = "01010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101"

        if action == Action.BEEPSHOCK:
            message_template = self.encode_for_transmission(self.generate(Action.BEEP, 1))
            delay = (beep_shock_delay_ms or self.receiver_properties.beep_shock_delay_ms) + 100
            message = message + message_template + message_template + message_template + "/" + str(delay) + "ms "
            action = Action.SHOCK

        if action == Action.LIGHT:
            action = Action.VIBRATE
            power = 0

        if duration <= 500:
            duration = 500
        if duration > 10000:
            duration = 10000

        repeats = round((duration - 500) / 48 + 5)

        """
        message = "01010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101"
        for self.checksum in range(0, 16):
            message_template = self.encode_for_transmission(self.generate(action, power))
            for _ in range(0, repeats):
                message = message + message_template
            message = message + " "
        self.send(message)
        """

        if True:
            print(self.checksum)
            message_template = self.encode_for_transmission(self.generate(action, power))
            for _ in range(0, repeats):
                message = message + message_template
            self.send(message)

        else:
            for self.checksum in range(0, 16):

                time.sleep(.2)
                # input()
                print(self.checksum)
                message = "01010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101"
                message_template = self.encode_for_transmission(self.generate(action, power))
                for _ in range(0, repeats):
                    message = message + message_template
                self.send(message)
