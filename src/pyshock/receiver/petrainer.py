#!/usr/bin/python3
#
# Copyright nilswinter 2020-2021. License: AGPL
# _____________________________________________


import re
import threading

from pyshock.core.action import Action
from pyshock.receiver.receiver import Receiver
from pyshock.scheduler.commandtask import CommandTask
from pyshock.scheduler.scheduler import scheduler
from pyshock.scheduler.periodictask import PeriodicTask


lock = threading.RLock()


class Petrainer(Receiver):
    """communication with Petainer collars. Note there are many brandnames for the same product."""

    channel_codes_normal  = ["1000", "1111"]  # noqa: E221
    channel_codes_inverse = ["1110", "0000"]  # noqa: E221

    action_code_normal = {
        Action.LIGHT:   "1000",  # noqa: E241
        Action.BEEP:    "0100",  # noqa: E241
        Action.VIBRATE: "0010",  # noqa: E241
        Action.SHOCK:   "0001"   # noqa: E241
    }

    action_code_inverse = {
        Action.LIGHT:   "1110",  # noqa: E241
        Action.BEEP:    "1101",  # noqa: E241
        Action.VIBRATE: "1011",  # noqa: E241
        Action.SHOCK:   "0111"   # noqa: E241
    }


    def __init__(self, name, color, transmitter_code, channel):
        super().__init__(name, color)
        self.transmitter_code = transmitter_code
        self.channel = channel

    def validate_config(self):
        """validates pyshock.ini configuration and prints errors"""

        if re.fullmatch("^[01]{16}$", self.transmitter_code) is None:
            print("ERROR: Invalid transmitter_code \"" + self.transmitter_code + "\" in pyshock.ini.")
            print("The transmitter_code must be sequence of length 16 consisting of the characters 0 and 1")
            return False

        if self.channel < 1 or self.channel > 2:
            print("ERROR: Invalid channel \"" + str(self.channel) + "\" in pyshock.ini.")
            print("This parameter needs to be a whole number between 1 and 2 inclusive.")
            return False

        return True


    def is_sdr_required(self):
        """we require a SDR (software defined radio) transmitter.
        There is an alternative implementation which uses Arduino."""
        return True


    def boot(self, pyshock, receiver, _arduino_manader, sdr_sender):
        """keep a references to the sdr_sender for later use
        and schedules keep-awake messages"""
        self.sender = sdr_sender

        # schedule keep awake timer
        command_task = CommandTask(None, None, None, pyshock, receiver, Action.LIGHT, 0, 250)
        periodic_task = PeriodicTask(5 * 60 / 2 - 10, command_task)
        scheduler().schedule_task(periodic_task)


    def generate(self, action, power):
        """generates the data structure for a single command.

        This method returns the logical data-structure without transmission-encoding.

        @param action action
        @param power power level in the scale of 0-100
        """
        data = self.channel_codes_normal[self.channel - 1] + self.action_code_normal[action] \
            + self.transmitter_code + format(power, '08b') \
            + self.action_code_inverse[action] + self.channel_codes_inverse[self.channel - 1]
        return data


    def encode_for_transmission(self, data):
        """encodes a command data structure for transmission over the air.

        This methods adds the synchronization prefix and suffx as well.
        """
        prefix = "111111000"
        suffix = "1"
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
        # TODO duration of simples, heading, tailing, etc.
        self.sender.send(
            frequency=433.98e6,
            sample_rate=2e6,
            carrier_frequency=0e3,
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

        message = ""
        if action == Action.BEEPSHOCK:
            message = self.encode_for_transmission(self.generate(Action.BEEP, 1))
            message = message + message + message + "/1.1s "
            action = Action.SHOCK

        if duration <= 500:
            duration = 500
        if duration > 10000:
            duration = 10000


        # at least 1 repeats of the message
        # one message takes 45.75ms (after transfer encoding: 170 symbols,
        # 500 samples/symbols, 2000000 samples/second)
        #
        #  500ms ==> 1 messages
        # 1000ms ==> messages for  500ms, followed by 1 message
        # 1500ms ==> messages for 1000ms, followed by 1 message
        repeats = round((duration - 500) / 42.5 + 1)
        message_template = self.encode_for_transmission(self.generate(action, power))
        for _ in range(0, repeats):
            message = message + message_template

        self.send(message)