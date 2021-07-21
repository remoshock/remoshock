#!/usr/bin/python3
#
# Copyright nilswinter 2020-2021. License: AGPL
#_______________________________________________

import argparse
import random
import time


from pyshock.core.pyshock import Pyshock, PyshockMock
from pyshock.core.action import Action 

class PyshockRandomizer:

    def __parse_args(self):
        parser = argparse.ArgumentParser(description="Shock collar remote randomizer",
                                         epilog="Please see https://github.com/pyshock/pyshock for documentation.")
        parser.add_argument("--mock",
                            action="store_true",
                            help=argparse.SUPPRESS)
        parser.add_argument("-v", "--verbose",
                            action="store_true",
                            help="prints debug messages")
        parser.add_argument("--version",
                            action="version",
                            version="0.1")
    
        self.args = parser.parse_args()


    def __boot_pyshock(self):
        if self.args.mock:
            self.pyshock = PyshockMock(self.args)
        else:
            self.pyshock = Pyshock(self.args)
        self.pyshock.boot()


    def __load_config(self):
        self.beep_probability_percent = self.pyshock.config.getint("randomizer", "beep_probability_percent")
        self.zap_probability_percent = self.pyshock.config.getint("randomizer", "zap_probability_percent")
        self.zap_min_duration_ms = self.pyshock.config.getint("randomizer", "zap_min_duration_ms")
        self.zap_max_duration_ms = self.pyshock.config.getint("randomizer", "zap_max_duration_ms")
        self.zap_min_power_percent = self.pyshock.config.getint("randomizer", "zap_min_power_percent")
        self.zap_max_power_percent = self.pyshock.config.getint("randomizer", "zap_max_power_percent")
        self.pause_min_s = self.pyshock.config.getint("randomizer", "pause_min_s")
        self.pause_max_s = self.pyshock.config.getint("randomizer", "pause_max_s")


    def __test_receivers(self):

        for i in range(0, len(self.pyshock.receivers)):
            print("Testing receiver " + str(i))
            self.pyshock.command(i, Action.BEEP, 0, 250)
            time.sleep(1)
        print("Beep command sent to all known receivers. Starting randomizer... Press Ctrl+c to stop.")

    
    def __determine_action(self):
        if random.randrange(100) < self.beep_probability_percent:
            if random.randrange(100) < self.zap_probability_percent:
                return Action.BEEPZAP
            else:
                return Action.BEEP
        else:
            if random.randrange(100) < self.zap_probability_percent:
                return Action.ZAP
            return Action.LED


    def __execute(self):
        while True:
            time.sleep(random.randint(self.pause_min_s, self.pause_max_s))

            action = self.__determine_action()
            power = random.randint(self.zap_min_power_percent, self.zap_max_power_percent)
            if action == Action.BEEP:
                duration = 250
            else:
                duration = random.randint(self.zap_min_duration_ms, self.zap_max_duration_ms)
            receiver = random.randrange(len(self.pyshock.receivers))
   
            self.pyshock.command(action, receiver, power, duration)


    def start(self):
        self.__parse_args()
        self.__boot_pyshock()
        self.__load_config()
        self.__test_receivers()
        self.__execute()

