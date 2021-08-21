#
# Copyright nilswinter 2020-2021. License: AGPL
# _____________________________________________

import configparser
import logging
import sys
import threading

from remoshock.core.config import ConfigManager

from remoshock.receiver.arshock import ArduinoManager
from remoshock.receiver.wodondog import Wodondog
from remoshock.receiver.pac import Pac
from remoshock.receiver.petrainer import Petrainer

lock = threading.RLock()


class Remoshock:
    """This is the manager class. It basically coordinates everything and
    delegate the actual work to specialized classes."""


    def __init__(self, args):
        """Constructor of the manager class Remoshock

        @param args the command line arguments as returned by argparser"""
        self.args = args


    def __instantiate_receiver(self, section):
        """handles a [receiver] section in remoshock.ini by creating
        the appropriate receiver object with the specified parameters.

        @param section (mangled) name of the section from remoshock.ini
        """

        receiver_type = self.config.get(section, "type")
        name = self.config.get(section, "name")
        color = self.config.get(section, "color")
        code = self.config.get(section, "transmitter_code")

        channel = self.config.get(section, "channel", fallback=None)
        if channel is None:
            button = self.config.getint(section, "button", fallback=None)
            if button is not None:
                print("ERROR: Please rename parameter \"button\" to \"channel\" in remoshock.ini")
                return None
        channel = self.config.getint(section, "channel")

        if receiver_type.lower() == "pac":
            receiver = Pac(name, color, code, channel)
        elif receiver_type.lower() == "wodondog":
            receiver = Wodondog(name, color, code, channel)
        elif receiver_type.lower() == "petrainer":
            receiver = Petrainer(name, color, code, channel)
        else:
            print("ERROR: Unknown receiver type \"" + receiver_type + "\" in remoshock.ini. Supported types: pac, Wodondog, petainer")
            return None

        if receiver.validate_config():
            return receiver

        return None


    def __instantitate_sdr_sender(self):
        """creates a sdr_sender based on the configuration in remoshock.ini or the command line.

        This method triggers a special case handling for HackRF devices.
        """
        sdr = self.config.get("global", "sdr", fallback=None)
        if "sdr" in self.args and self.args.sdr is not None:
            sdr = self.args.sdr
        if sdr is None:
            print()
            print("SDR (software defined radio) hardware is required to send radio signals.")
            print()
            print("Please edit remoshock.ini and add an entry sdr=... in the [global] section.")
            print()
            print("Supported devices are (upper/lower case is important):")
            print("HackRF, LimeSDR")
            print()
            sys.exit(1)

        print()
        print("Please make sure your SDR sending hardware is connected and ready. Avoid USB hubs.")

        if sdr.lower() == "hackrf":
            print()
            print("We are using internal URH invokation for HackRF. This is recommanded because it")
            print("prevents a one second delay. But it might cause Python errors, if the URH version is")
            print("incompatible. In this case, please specify srd=hackrfcli in remoshock.ini")
            print()
            print("If the device is not connected or not ready, driver initialization will fail right now")
            print("...")

            from remoshock.sdr.urhinternal import UrhInternalSender
            sender = UrhInternalSender(self.args.verbose)
            print("Yeah! Driver initialized successfully.")
            print()
            return sender

        if sdr.lower() == "hackrfcli":
            sdr = "HackRF"

        print("Using " + sdr + " via urh_cli")
        from remoshock.sdr.urhcli import UrhCliSender
        return UrhCliSender(sdr, self.args.verbose)


    def _setup_from_config(self):
        try:
            self.config = ConfigManager().config
            receivers = []
            for receiver in self.config.sections():
                if receiver.startswith("receiver"):
                    try:
                        receiver = self.__instantiate_receiver(receiver)
                        if receiver is not None:
                            receivers.append(receiver)
                    except configparser.NoOptionError as e:
                        print("Error reading configuration file: " + str(e))

            if len(receivers) == 0:
                print()
                print("ERROR: No valid receivers configured in remoshock.ini")
                sys.exit(1)
            self.receivers = receivers
        except configparser.NoOptionError as e:
            print(e)
            sys.exit(1)


    def boot(self):
        """starts up remoshock.

        - enable logging
        - read configuration from remoshock.ini
        - initialize receiver configuration
        - initialize SDR, if required by a configured receiver
        - initialize arshock, if required by a configured receiver
        - initialize configured receivers
        """
        logging.basicConfig(
            format='%(asctime)s %(levelname)-8s %(message)s',
            level=logging.INFO,
            datefmt='%Y-%m-%d %H:%M:%S')

        self._setup_from_config()
        arduino_required = False
        sdr_required = False

        for receiver in self.receivers:
            if receiver.is_arduino_required():
                arduino_required = True
            if receiver.is_sdr_required():
                sdr_required = True

        arduino_manager = None
        if arduino_required:
            arduino_manager = ArduinoManager()
            arduino_manager.boot()

        sdr_sender = None
        if sdr_required:
            sdr_sender = self.__instantitate_sdr_sender()

        i = 1
        for receiver in self.receivers:
            receiver.boot(self, i, arduino_manager, sdr_sender)
            i = i + 1


    def _process_command(self, receiver, action, power, duration):
        """sends a command to the indicated receiver

        @param action action to perform (e. g. BEEP)
        @param receiver number of receiver to use
        @param power power level (1-100)
        @param duration duration in ms
        """
        with lock:
            self.receivers[receiver - 1].command(action, power, duration)


    def command(self, receiver, action, power, duration):
        """sends a command to the indicated receiver

        @param action action to perform (e. g. BEEP)
        @param receiver number of receiver to use
        @param power power level (1-100)
        @param duration duration in ms
        """

        if receiver < 1 or receiver > len(self.receivers):
            logging.error("Receiver number \"" + str(receiver) + "\" is out of range. It should be between 1 and " + str(len(self.receivers)))
            return

        if power < 0 or power > 100:
            logging.error("Power level \"" + str(receiver) + "\" is out of range. It should be between 1 and 100")
            return

        impulse_duration = self.receivers[receiver - 1].get_impulse_duration()
        normalized_duration = round(duration / impulse_duration) * impulse_duration
        logging.info("receiver: " + str(receiver) + ", action: " + action.name + ", power: " + str(power) + "%, duration: " + str(normalized_duration) + "ms")

        self._process_command(receiver, action, power, duration)

    def get_config(self):
        """get configuration information for website"""
        result = []
        for receiver in self.receivers:
            result.append(receiver.get_config())
        return result



class RemoshockMock(Remoshock):
    """A mock used for testing without requiring any SDR hardware."""


    def _process_command(self, receiver, action, power, duration):
        """do nothing as this is a mock only"""


    def boot(self):
        """setup receivers based on configuration, but does not
        initialize anything because they will never be accessed
        using this mock"""

        logging.basicConfig(
            format='%(asctime)s %(levelname)-8s %(message)s',
            level=logging.INFO,
            datefmt='%Y-%m-%d %H:%M:%S')

        self._setup_from_config()
        print("Loaded mock")
