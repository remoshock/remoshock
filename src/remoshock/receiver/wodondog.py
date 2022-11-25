#
# Copyright nilswinter 2021. License: AGPL
# ________________________________________


import re
import threading

from remoshock.core.action import Action
from remoshock.receiver.receiver import Receiver

lock = threading.RLock()


class Wodondog(Receiver):

    action_codes = {
        Action.BEEP: 3,
        Action.VIBRATE: 2,
        Action.SHOCK: 1
    }

    def __init__(self, receiver_properties, transmitter_code, channel):
        super().__init__(receiver_properties)
        self.receiver_properties.capabilities(action_light=True, action_beep=True, action_vibrate=True, action_shock=True)
        self.receiver_properties.timings(duration_min_ms=500, duration_increment_ms=500, awake_time_s=5 * 60)
        self.transmitter_code = transmitter_code
        self.channel = channel


    def validate_config(self):
        """validates remoshock.ini configuration and prints errors"""

        if re.fullmatch("^[01]{16}$", self.transmitter_code) is None:
            print("ERROR: Invalid transmitter_code \"" + self.transmitter_code + "\" in remoshock.ini.")
            print("The transmitter_code must be sequence of length 16 consisting of the characters 0 and 1")
            return False

        if self.channel < 1 or self.channel > 3:
            print("ERROR: Invalid channel \"" + str(self.channel) + "\" in remoshock.ini.")
            print("This parameter needs to be a whole number between 1 and 3 inclusive.")
            return False

        return True


    def is_sdr_required(self):
        """we require a SDR (software defined radio) transmitter."""
        return True


    def boot(self, _arduino_manader, sdr_sender):
        """keep a references to the sdr_sender for later use
        and schedules keep-awake messages"""
        self.sender = sdr_sender


    def generate(self, action, power):
        """generates the data structure (without transfer encoding)"""

        # 16 bits  transmitter code
        #  4 bits  action: 1: shock, 2: vibreate, 3: beep
        #  4 bits  channel
        #  8 bits  power
        #  8 bits  sum of the previous bytes modulo 256

        action_code = self.action_codes.get(action, 3)
        if power > 99:
            power = 99

        data = self.transmitter_code \
            + format(self.channel - 1, '04b') \
            + format(action_code, '04b') \
            + format(power, '08b')

        checksum = (int(data[0:8], 2) + int(data[8:16], 2) + int(data[16:24], 2) + int(data[24:32], 2)) % 256
        data = data + format(checksum, '08b')

        return data


    def encode_for_transmission(self, data):
        """encodes a command data structure for transmission over the air.

        This methods adds the synchronization prefix and suffix as well.
        """
        prefix = "111111000"
        suffix = "1000100010000"
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
            frequency=433.85e6,
            sample_rate=2e6,
            carrier_frequency=6e3,
            modulation_type="ASK",
            samples_per_symbol=500,
            low_frequency="0",
            high_frequency="100",
            pause=0,
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
            action = Action.VIBRATE
            power = 0
            duration = 250


        message = ""
        if action == Action.BEEPSHOCK:
            message = self.encode_for_transmission(self.generate(Action.BEEP, 1))
            delay = self.receiver_properties.beep_shock_delay_ms / 1000 + 0.1
            message = message + message + message + "/" + str(delay) + "s "
            action = Action.SHOCK

        if action == Action.LIGHT:
            # TODO handle "flashlight" on/off mode
            action = Action.VIBRATE
            power = 0

        if duration <= 500:
            duration = 500
        if duration > 10000:
            duration = 10000


        # at least 3 repeats of the message
        # one message takes 45.75ms (after transfer encoding: 183 symbols,
        # 500 samples/symbols, 2000000 samples/second)
        #
        #  500ms ==> 3 messages
        # 1000ms ==> messages for  500ms, followed by 3 messages
        # 1500ms ==> messages for 1000ms, followed by 3 messages
        repeats = round((duration - 500) / 45.75 + 3)
        message_template = self.encode_for_transmission(self.generate(action, power))
        for _ in range(0, repeats):
            message = message + message_template

        self.send(message)
