#
# Copyright nilswinter 2020-2022. License: AGPL
# _____________________________________________

import argparse
import configparser
import datetime
import random
import sys
import threading
import time

from remoshock.core.remoshock import Remoshock, RemoshockMock
from remoshock.core.action import Action
from remoshock.core.version import VERSION
from remoshock.util import powermanager

lock = threading.RLock()


class RemoshockRandomizer:
    """sends random commands at random intervals as configured"""

    CONFIG_KEYS = ("beep_probability_percent", "shock_probability_percent",
                   "shock_min_duration_ms", "shock_max_duration_ms",
                   "shock_min_power_percent", "shock_max_power_percent",
                   "pause_min_s", "pause_max_s",
                   "start_delay_min_minutes", "start_delay_max_minutes",
                   "runtime_min_minutes", "runtime_max_minutes")

    def __init__(self):
        self.threadEvent = None
        self.cfg = {}


    def __parse_args(self):
        """parses command line arguments"""
        parser = argparse.ArgumentParser(description="Shock collar remote randomizer",
                                         epilog="Please see https://remoshock.github.io/applications.html for documentation.")
        parser.add_argument("--mock",
                            action="store_true",
                            help=argparse.SUPPRESS)
        parser.add_argument("-s", "--section",
                            default="randomizer",
                            help="name of [section] in remoshock.ini to use. Default is [randomizer].")
        parser.add_argument("--experimental",
                            action="store_true",
                            help=argparse.SUPPRESS)
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


    def __load_config(self):
        """loads configuration from remoshock.ini for the section
        specified on the command line"""
        try:
            for key in self.CONFIG_KEYS:
                self.cfg[key] = self.remoshock.config.getint(self.args.section, key)
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
        if random.randrange(100) < self.cfg["beep_probability_percent"]:
            if random.randrange(100) < self.cfg["shock_probability_percent"]:
                return Action.BEEPSHOCK
            return Action.BEEP

        if random.randrange(100) < self.cfg["shock_probability_percent"]:
            return Action.SHOCK
        return Action.LIGHT


    def __execute(self, threadEvent):
        """the loop in which all the action happens"""

        try:
            start_delay_s = random.randint(self.cfg["start_delay_min_minutes"] * 60, self.cfg["start_delay_max_minutes"] * 60)

            if start_delay_s > 0:
                print("Waiting according to start_delay_min_minutes and start_delay_max_minutes...")
                if threadEvent.wait(start_delay_s):
                    print("Randomizer canceled")
                    with lock:
                        if self.threadEvent == threadEvent:
                            self.threadEvent = None
                    return

            runtime_s = random.randint(self.cfg["runtime_min_minutes"] * 60, self.cfg["runtime_max_minutes"] * 60)
            current_time = datetime.datetime.now()
            start_time = current_time

            while (current_time - start_time).total_seconds() < runtime_s:
                wait_time_s = random.randint(self.cfg["pause_min_s"], self.cfg["pause_max_s"])
                if threadEvent.wait(wait_time_s):
                    print("Randomizer canceled")
                    with lock:
                        if self.threadEvent == threadEvent:
                            self.threadEvent = None
                    return

                action = self.__determine_action()
                power = random.randint(self.cfg["shock_min_power_percent"], self.cfg["shock_max_power_percent"])
                if action == Action.BEEP:
                    duration = 250
                else:
                    duration = random.randint(self.cfg["shock_min_duration_ms"], self.cfg["shock_max_duration_ms"])
                receiver = random.randrange(len(self.remoshock.receivers)) + 1

                self.remoshock.command(receiver, action, power, duration)
                current_time = datetime.datetime.now()

            print("Runtime completed.")

            with lock:
                if self.threadEvent == threadEvent:
                    self.threadEvent = None

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
        self.__execute(threading.Event())


    def prepare_in_server_mode(self, remoshock):
        """prepares remoshockrnd for being used by the REST server"""

        self.__parse_args()
        self.remoshock = remoshock
        self.__load_config()


    def stop_in_server_mode(self):
        """stops the randomizer run"""

        with lock:
            if (self.threadEvent):
                self.threadEvent.set()


    def start_in_server_mode(self, config):
        """updates non-persistent configuration and starts a new run.
        If there is already a thread running, it will be stopped"""

        with lock:
            self.stop_in_server_mode()

            for key in self.CONFIG_KEYS:
                self.cfg[key] = int(config[key], base=10)

            # start thread
            self.threadEvent = threading.Event()
            thread = threading.Thread(target=self.__run_in_thread, args=(self.threadEvent, ))
            thread.start()

    def __run_in_thread(self, threadEvent):
        self.__test_receivers()
        self.__execute(threadEvent)


    def get_status_and_config(self):
        """returns status and current config"""

        status = "inactive"
        if (self.threadEvent):
            status = "running"
        self.cfg["status"] = status
        return self.cfg


def main():
    RemoshockRandomizer().start()
