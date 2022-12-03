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

    CONFIG_OVERRIDABLE_KEYS = ("shock_min_duration_ms", "shock_max_duration_ms",
                               "shock_min_power_percent", "shock_max_power_percent",
                               "probability_weight")

    def __init__(self):
        self.cli = False
        self.thread = None
        self.threadEvent = None
        self.cfg = {}
        self.probability_weights = []
        self.error = ""


    def __parse_args(self):
        """parses command line arguments"""
        parser = argparse.ArgumentParser(description="Shock collar remote randomizer",
                                         epilog="Please see https://remoshock.github.io/applications.html for documentation.")
        parser.add_argument("--mock",
                            action="store_true",
                            help=argparse.SUPPRESS)
        parser.add_argument("--experimental",
                            action="store_true",
                            help=argparse.SUPPRESS)
        parser.add_argument("--sdr",
                            help=argparse.SUPPRESS)

        parser.add_argument("-C", "--configfile",
                            help="custom configuration file. Defaults to ~/.config/remoshock.ini")
        parser.add_argument("-S", "--settingsfile",
                            help="custom settings file. Defaults to ~/.config/remoshock.dat")
        parser.add_argument("-s", "--section",
                            default="randomizer",
                            help="name of [section] in remoshock.ini to use. Default is [randomizer].")
        parser.add_argument("--skip-startup-beeps",
                            action="store_true",
                            help="skips beeping on collars as test on startup.")
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

            self.cfg["probability_weight"] = 1
            if "probability_weight" in self.remoshock.config:
                self.cfg["probability_weight"] = self.remoshock.config.getint(self.args.section, "probability_weight")

            for receiver in range(1, len(self.remoshock.receivers) + 1):

                receiver_properties = self.remoshock.get_receiver_properties(receiver)
                for key in self.CONFIG_OVERRIDABLE_KEYS:
                    if hasattr(receiver_properties, "random_" + key):
                        value = getattr(receiver_properties, "random_" + key)
                        if value is not None:
                            self.cfg["r" + str(receiver) + "." + key] = value

                probability_weight = receiver_properties.random_probability_weight
                if probability_weight is None:
                    probability_weight = self.cfg["probability_weight"]
                self.cfg["r" + str(receiver) + "." + "probability_weight"] = probability_weight

        except configparser.NoOptionError as e:
            print(e)
            sys.exit(1)

        if self.args.skip_startup_beeps:
            self.cfg["skip_startup_beeps"] = True


    def __parameter_range_check(self, key, min_value, max_value):
        """validates the range of a parameter value"""
        if self.cfg[key] < min_value or self.cfg[key] > max_value:
            self.error = self.error + "ERROR: Randomizer parameter \"" + key + "\" must be between " + str(min_value) + " and " + str(max_value) + ".\n"


    def __parameter_min_smaller_max_check(self, min_key, max_key):
        """validates that the minimum parameter is smaller than the maximum parameter"""
        if self.cfg[min_key] > self.cfg[max_key]:
            self.error = self.error + "ERROR: Randomizer parameter \"" + max_key + "\" (" + str(self.cfg[max_key]) \
                + ") must be equal to or larger than \"" + min_key + "\" (" + str(self.cfg[min_key]) \
                + ").\n"


    def __receiver_parameter_min_smaller_max_check(self, receiver, min_key, max_key):
        """validates that the minimum parameter is smaller than the maximum parameter"""
        min_value = self.get_overridable_config(receiver, min_key)
        max_value = self.get_overridable_config(receiver, max_key)
        if min_value > max_value:
            self.error = self.error + "ERROR: Randomizer parameter \"" + max_key + "\" (" + str(max_value) \
                + ") must be equal to or larger than \"" + min_key + "\" (" + str(min_value) \
                + ") but this is not the case of receiver " + str(receiver) + ".\n"


    def __validate_configuration(self):
        self.__parameter_range_check("beep_probability_percent", 0, 100)
        self.__parameter_range_check("shock_probability_percent", 0, 100)
        self.__parameter_range_check("shock_min_duration_ms", 0, 10000)
        self.__parameter_range_check("shock_max_duration_ms", 0, 10000)
        self.__parameter_range_check("shock_min_power_percent", 0, 100)
        self.__parameter_range_check("shock_max_power_percent", 0, 100)
        self.__parameter_range_check("pause_min_s", 0, 24 * 60 * 60)
        self.__parameter_range_check("pause_max_s", 0, 24 * 60 * 60)
        self.__parameter_range_check("start_delay_min_minutes", 0, 7 * 24 * 60)
        self.__parameter_range_check("start_delay_max_minutes", 0, 7 * 24 * 60)
        self.__parameter_range_check("runtime_min_minutes", 0, 365 * 24 * 60)
        self.__parameter_range_check("runtime_max_minutes", 0, 365 * 24 * 60)
        self.__parameter_min_smaller_max_check("shock_min_duration_ms", "shock_max_duration_ms")
        self.__parameter_min_smaller_max_check("shock_min_power_percent", "shock_max_power_percent")
        self.__parameter_min_smaller_max_check("pause_min_s", "pause_max_s")
        self.__parameter_min_smaller_max_check("start_delay_min_minutes", "start_delay_max_minutes")
        self.__parameter_min_smaller_max_check("runtime_min_minutes", "runtime_max_minutes")
        for receiver in range(1, len(self.remoshock.receivers) + 1):
            self.__receiver_parameter_min_smaller_max_check(receiver, "shock_min_duration_ms", "shock_max_duration_ms")
            self.__receiver_parameter_min_smaller_max_check(receiver, "shock_min_power_percent", "shock_max_power_percent")


    def __test_receivers(self):
        """sends a beep command to all registered receivers to allow users
        to verify that all receivers are turned on and setup correctly"""
        if "skip_startup_beeps" not in self.cfg or not self.cfg["skip_startup_beeps"]:
            for i in range(1, len(self.remoshock.receivers) + 1):
                print("Testing receiver " + str(i))
                self.remoshock.command(i, Action.BEEP, 0, 250)
                time.sleep(1)
            print("Beep command sent to all known receivers. Starting randomizer...")
        else:
            print("Starting randomizer...")

        if self.cli:
            print("Press Ctrl+c to stop.")


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


    def get_overridable_config(self, receiver, key):
        """gets a configuration value which may be overridden in the receiver section"""

        real_key = "r" + str(receiver) + "." + key
        if real_key in self.cfg:
            return self.cfg[real_key]

        return self.cfg[key]


    def init_probability_weight(self):
        """initializes the probability weight array"""
        self.probability_weights.clear()
        for receiver in range(1, len(self.remoshock.receivers) + 1):
            probability_weight = self.get_overridable_config(receiver, "probability_weight")
            self.probability_weights.append(probability_weight)


    def __execute(self, threadEvent):
        """the loop in which all the action happens"""

        try:
            self.init_probability_weight()

            start_delay_s = random.randint(self.cfg["start_delay_min_minutes"] * 60, self.cfg["start_delay_max_minutes"] * 60)

            if start_delay_s > 0:
                print("Waiting according to start_delay_min_minutes and start_delay_max_minutes...")
                if threadEvent.wait(start_delay_s):
                    print("Randomizer canceled")
                    with lock:
                        print("Locked")
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

                receiver = random.choices(range(1, len(self.remoshock.receivers) + 1), weights=(self.probability_weights), k=1)[0]
                action = self.__determine_action()

                power = random.randint(
                    self.get_overridable_config(receiver, "shock_min_power_percent"),
                    self.get_overridable_config(receiver, "shock_max_power_percent")
                )
                if action == Action.BEEP:
                    duration = 250
                else:
                    duration = random.randint(
                        self.get_overridable_config(receiver, "shock_min_duration_ms"),
                        self.get_overridable_config(receiver, "shock_max_duration_ms")
                    )

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
        self.cli = True
        self.__parse_args()
        self.__boot_remoshock()
        self.__load_config()
        self.__validate_configuration()
        if (self.error != ""):
            print(self.error)
            sys.exit(1)
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
        if self.thread is not None:
            self.thread.join()


    def start_in_server_mode(self, config):
        """updates non-persistent configuration and starts a new run.
        If there is already a thread running, it will be stopped"""

        self.stop_in_server_mode()

        with lock:
            for key in self.CONFIG_KEYS:
                self.cfg[key] = int(config[key], base=10)
            for receiver in range(1, len(self.remoshock.receivers) + 1):
                for key in self.CONFIG_OVERRIDABLE_KEYS:
                    real_key = "r" + str(receiver) + "." + key
                    if real_key in config:
                        self.cfg[real_key] = int(config[real_key], base=10)
                    else:
                        self.cfg.pop(real_key, None)

            self.cfg["skip_startup_beeps"] = bool(config["skip_startup_beeps"])

            self.error = ""
            self.__validate_configuration()
            if self.error != "":
                return self.error

            # start thread
            self.threadEvent = threading.Event()
            self.thread = threading.Thread(target=self.__run_in_thread, args=(self.threadEvent, ))
            self.thread.start()
        return ""


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
    try:
        RemoshockRandomizer().start()
    except KeyboardInterrupt:
        print("Stopped by Ctrl+c.")
        sys.exit(0)
