#
# Copyright nilswinter 2020-2021. License: AGPL
# _____________________________________________

import argparse
import configparser
import datetime
import random
import sys
import time

from remoshock.core.remoshock import Remoshock, RemoshockMock
from remoshock.core.action import Action
from remoshock.core.version import VERSION
from remoshock.util import powermanager


class RemoshockRandomizer:
    """sends random commands at random intervals as configured"""

    def __parse_args(self):
        """parses command line arguments"""
        parser = argparse.ArgumentParser(description="Shock collar remote randomizer",
                                         epilog="Please see https://github.com/remoshock/remoshock for documentation.")
        parser.add_argument("--mock",
                            action="store_true",
                            help=argparse.SUPPRESS)
        parser.add_argument("-s", "--section",
                            default="randomizer",
                            help="name of [section] in remoshock.ini to use. Default is [randomizer].")
        parser.add_argument("--sdr",
                            help=argparse.SUPPRESS)
        parser.add_argument("-v", "--verbose",
                            action="store_true",
                            help="prints debug messages")
        parser.add_argument("--version",
                            action="version",
                            version=VERSION)

        self.args = parser.parse_args()


    def __boot_remoshock(self):
        """starts up the remoshock infrastructure"""
        if self.args.mock:
            self.remoshock = RemoshockMock(self.args)
        else:
            self.remoshock = Remoshock(self.args)
        self.remoshock.boot()


    def __get_config_value(self, key):
        """reads a configuration setting"""
        return self.remoshock.config.getint(self.args.section, key)


    def __load_config(self):
        """loads configuration from remoshock.ini for the section
        specified on the command line"""
        try:
            self.beep_probability_percent = self.__get_config_value("beep_probability_percent")
            self.shock_probability_percent = self.__get_config_value("shock_probability_percent")
            self.shock_min_duration_ms = self.__get_config_value("shock_min_duration_ms")
            self.shock_max_duration_ms = self.__get_config_value("shock_max_duration_ms")
            self.shock_min_power_percent = self.__get_config_value("shock_min_power_percent")
            self.shock_max_power_percent = self.__get_config_value("shock_max_power_percent")
            self.pause_min_s = self.__get_config_value("pause_min_s")
            self.pause_max_s = self.__get_config_value("pause_max_s")
            self.start_delay_min_minutes = self.__get_config_value("start_delay_min_minutes")
            self.start_delay_max_minutes = self.__get_config_value("start_delay_max_minutes")
            self.runtime_min_minutes = self.__get_config_value("runtime_min_minutes")
            self.runtime_max_minutes = self.__get_config_value("runtime_max_minutes")
        except configparser.NoOptionError as e:
            print(e)
            sys.exit(1)


    def __test_receivers(self):
        """sends a beep command to all registered receivers to allow users
        to verify that all receivers are turned on and setup correctly"""
        for i in range(1, len(self.remoshock.receivers) + 1):
            print("Testing receiver " + str(i))
            self.remoshock.command(i, Action.BEEP, 0, 250)
            time.sleep(1)
        print("Beep command sent to all known receivers. Starting randomizer... Press Ctrl+c to stop.")


    def __determine_action(self):
        """determines whether there should be a beep, a shock, both or
        neither this time based on probabilities for beep and shock"""
        if random.randrange(100) < self.beep_probability_percent:
            if random.randrange(100) < self.shock_probability_percent:
                return Action.BEEPSHOCK
            return Action.BEEP

        if random.randrange(100) < self.shock_probability_percent:
            return Action.SHOCK
        return Action.LIGHT


    def __execute(self):
        """the loop in which all the action happens"""
        try:
            start_delay_s = random.randint(self.start_delay_min_minutes * 60, self.start_delay_max_minutes * 60)

            if start_delay_s > 0:
                print("Waiting according to start_delay_min_minutes and start_delay_max_minutes...")
                time.sleep(start_delay_s)

            runtime_s = random.randint(self.runtime_min_minutes * 60, self.runtime_max_minutes * 60)
            current_time = datetime.datetime.now()
            start_time = current_time

            while (current_time - start_time).total_seconds() < runtime_s:
                time.sleep(random.randint(self.pause_min_s, self.pause_max_s))

                action = self.__determine_action()
                power = random.randint(self.shock_min_power_percent, self.shock_max_power_percent)
                if action == Action.BEEP:
                    duration = 250
                else:
                    duration = random.randint(self.shock_min_duration_ms, self.shock_max_duration_ms)
                receiver = random.randrange(len(self.remoshock.receivers)) + 1

                self.remoshock.command(receiver, action, power, duration)
                current_time = datetime.datetime.now()

            print("Runtime completed.")

        except KeyboardInterrupt:
            print("Stopped by Ctrl+c.")
            sys.exit(0)


    def start(self):
        """starts up remoshockrnd"""
        self.__parse_args()
        self.__boot_remoshock()
        self.__load_config()
        powermanager.inhibit()
        self.__test_receivers()
        self.__execute()


def main():
    RemoshockRandomizer().start()
