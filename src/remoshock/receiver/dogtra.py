#
# Copyright nilswinter 2020-2021. License: AGPL
# _____________________________________________

import re
import threading

from remoshock.core.action import Action
from remoshock.receiver.receiver import Receiver

lock = threading.RLock()


class Dogtra(Receiver):
    """communication with Dogtra collars"""

    def __init__(self, name, color, transmitter_code, channel):
        super().__init__(name, color)
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

        print("Dogtra is not supported, yet.")
        return False


    def is_sdr_required(self):
        """we require a SDR (software defined radio) transmitter.
        There are no Arduino modules working on the required frequency."""
        return True


    def boot(self, _remoshock, _receiver, _arduino_manader, sdr_sender):
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


    def calculate_intensity_code(self, intensity):
        """expands power level (in Dogtra scale from 0-255) from integer to bit-string"""

        #   0% -->   0: 0101000000000000000000
        #  20% -->  28: 0001111111110100000000
        #  40% -->  62: 0000000111010000000000
        #  60% --> 103: 1011110100000000000000
        #  80% --> 171: 1000000001101000000000
        # 100% --> 255: 1100000011111101000000

        res = ""
        for _ in range(0, intensity // 100):
            res = res + "1"

        intensity = intensity % 100
        for _ in range(0, intensity // 10 + 1):
            res = res + "0"

        intensity = intensity % 10
        for _ in range(0, intensity + 1):
            res = res + "1"

        res = res + "01"
        return res.ljust(22, "0")


    def encode_for_transmission(self, data):
        """encodes a command data structure for transmission over the air.

        This methods adds the synchronization prefix as well as the fillers
        between each bit in the first part of the message."""

        prefix = "11100"
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

# urh_cli --transmit --device HackRF --frequency 27135000.0 --sample-rate 2000000.0 --carrier-frequency 27135000.0 --modulation-type FSK --samples-per-symbol 1500 --parameters 6000.0 11000.0 --pause 262924 --if-gain 47 --messages 11111110000000111111100000000000111000100100100100110110100100110110110110110110100100100011111111101000000001110001001001001001101101001001101101101101101101001001000111111111010000000011100010010010010011011010010011011011011011011010010010001111111110100000000111000100100100100110110100100110110110110110110100100100011111111101000000001110001001001001001101101001001101101101101101101001001000111111111010000000011100010010010010011011010010011011011011011011010010010001111111110100000000111000100100100100110110100100110110110110110110100100100011111111101000000001110001001001001001101101001001101101101101101101001001000111111111010000000011100010010010010011011010010011011011011011011010010010001111111110100000000111000100100100100110110100100110110110110110110100100110001111111110100000000111000100100100100110110100100110110110110110110100100100011111111101000000001110001001001001001101101001001101101101101101101001001000111111111010000000011100010010010010011011010010011011011011011011010010010001111111110100000000111000100100100100110110100100110110110110110110100100100011111111101000000001110001001001001001101101001001101101101101101101001001000111111111010000000

# urh_cli --transmit --device HackRF --frequency 27135000.0 --sample-rate 2000000.0 --carrier-frequency 27135000.0 --modulation-type FSK --samples-per-symbol 1500 --parameters 6000.0 11000.0 --pause 262924 --if-gain 47 --messages 111111100000001111111000000000001110001001001001001101101001001101101101101101101001001000111111111010000000011100010010010010011011010010011011011011011011010010010001111111110100000000




    def command(self, action, power, duration):
        """sends a command to the receiver.

        A command may consist of several messages, e. g. one message
        for every 250ms of the duration parameter.

        @param action action perform (e. g. BEEP)
        @param power power level (1-100)
        @param duration duration in ms
        """

        message = ""
        if action == Action.BEEPSHOCK:
            message = self.encode_for_transmission(self.generate(self.transmitter_code, 0, 1)) + "/1s"

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

        # TODO: the mapping from power% to intensity code is not linear
        message_template = self.encode_for_transmission(self.generate(self.transmitter_code, power * 255 // 100, beep))
        # TODO: duration
        duration = 500
        for _ in range(0, round(duration / 250)):
            message = message + message_template

        start_of_transmission = "11111110000000111111100000000000"
        self.send(start_of_transmission + message.strip())
