#!/usr/bin/python3
#
# Copyright nilswinter 2020-2021. License: AGPL
#_______________________________________________

import argparse
import random
import time


from pyshock.core.pyshock import Pyshock, PyshockMock
from pyshock.core.action import Action 
from pyshock.core.version import VERSION

class PyshockRandomizer:
    """sends random commands at random intervals as configured"""

    def __parse_args(self):
        """parses command line arguments"""
        parser = argparse.ArgumentParser(description="Shock collar remote randomizer",
                                         epilog="Please see https://github.com/pyshock/pyshock for documentation.")
        parser.add_argument("--mock",
                            action="store_true",
                            help=argparse.SUPPRESS)
        parser.add_argument("-s", "--section",
                            default="randomizer",
                            help="name of [section] in pyshock.ini to use. Default is [randomizer].")
        parser.add_argument("--sdr",
                            help=argparse.SUPPRESS)
        parser.add_argument("-v", "--verbose",
                            action="store_true",
                            help="prints debug messages")
        parser.add_argument("--version",
                            action="version",
                            version=VERSION)
    
        self.args = parser.parse_args()


    def __boot_pyshock(self):
        """starts up the pyshock infrastructure"""
        if self.args.mock:
            self.pyshock = PyshockMock(self.args)
        else:
            self.pyshock = Pyshock(self.args)
        self.pyshock.boot()


    def __getvalue(self, key):
        """reads a configuration setting"""
        return self.pyshock.config.getint(self.args.section, key)


    def __load_config(self):
        """loads configuration from pyshock.ini for the section
        specified on the command line"""
        self.beep_probability_percent = self.__get_config_value("beep_probability_percent")
        self.shock_probability_percent = self.__get_config_value("shock_probability_percent")
        self.shock_min_duration_ms = self.__get_config_value("shock_min_duration_ms")
        self.shock_max_duration_ms = self.__get_config_value("shock_max_duration_ms")
        self.shock_min_power_percent = self.__get_config_value("shock_min_power_percent")
        self.shock_max_power_percent = self.__get_config_value("shock_max_power_percent")
        self.pause_min_s = self.__get_config_value("pause_min_s")
        self.pause_max_s = self.__get_config_value("pause_max_s")


    def __test_receivers(self):
        """sends a beep command to all registered receivers to allow users
        to verify that all receivers are turned on and setup correctly"""
        for i in range(1, len(self.pyshock.receivers) + 1):
            print("Testing receiver " + str(i))
            self.pyshock.command(i, Action.BEEP, 0, 250)
            time.sleep(1)
        print("Beep command sent to all known receivers. Starting randomizer... Press Ctrl+c to stop.")

    
    def __determine_action(self):
        """determines whether there should be a beep, a shock, both or 
        neither this time based on probabilities for beep and shock"""
        if random.randrange(100) < self.beep_probability_percent:
            if random.randrange(100) < self.shock_probability_percent:
                return Action.BEEPSHOCK
            else:
                return Action.BEEP
        else:
            if random.randrange(100) < self.shock_probability_percent:
                return Action.SHOCK
            return Action.LIGHT


    def __execute(self):
        """the loop in which all the action happens"""
        while True:
            time.sleep(random.randint(self.pause_min_s, self.pause_max_s))

            action = self.__determine_action()
            power = random.randint(self.shock_min_power_percent, self.shock_max_power_percent)
            if action == Action.BEEP:
                duration = 250
            else:
                duration = random.randint(self.shock_min_duration_ms, self.shock_max_duration_ms)
            receiver = random.randrange(len(self.pyshock.receivers)) + 1
   
            self.pyshock.command(action, receiver, power, duration)


    def start(self):
        """starts up pyshockrnd"""
        self.__parse_args()
        self.__boot_pyshock()
        self.__load_config()
        self.__test_receivers()
        self.__execute()

