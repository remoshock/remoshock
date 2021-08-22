#
# Copyright nilswinter 2020-2021. License: AGPL
# _____________________________________________

import collections
import configparser
import os
import secrets
import string
import sys


class MultiReceiverSectionSupport(collections.OrderedDict):
    """This class adds an index number at the end of each [receiver] section."""

    index = 0

    def __setitem__(self, key, val):
        if isinstance(val, dict) and key == "receiver":
            self.index = self.index + 1
            key += str(self.index)
        collections.OrderedDict.__setitem__(self, key, val)


class ConfigManager:
    """This class loads configuration from remoshock.ini and writes the
    default configuration with freshly created random values."""

    def __init__(self):
        self.__tokens = []
        self.filename = self.__determine_filename()
        self.__start_setup_assistant_if_config_missing()
        self.__read_configuration_from_file()


    def __generate_web_authentication_token(self):
        """creates a web_authentication_token that is probably unique to this installation."""
        charset = string.ascii_lowercase + string.ascii_uppercase + string.digits
        return ''.join(secrets.choice(charset) for _ in range(8))


    def __generate_transmitter_code(self, length):
        """creates a transmitter_code that is probably unique to this installation.

        @param length number of bits
        """
        # we ensure that transmitter codes are unique with this loop
        # because collisions are more likely than one would expect
        # for a 9 bit value because of the birthday paradox.
        charset = "01"
        while True:
            token = ''.join(secrets.choice(charset) for _ in range(length))
            if token not in self.__tokens:
                self.__tokens.append(token)
                return token


    def __input_number(self, question, default_value, min_value, max_value):
        """Asks the user for a number with validation

        @param question Question to ask the user
        @param default_value value used, if the player hits return without any input
        @param min_value minimal acceptable value
        @param max_value maximal acceptable value
        """
        while True:
            answer = input(question).strip()
            if answer == "":
                answer = str(default_value)
            try:
                num = int(answer, 10)
                if min_value <= num and num <= max_value:
                    return num
                print("ERROR: Expected a number between " + str(min_value) + " and " + str(max_value))
            except ValueError:
                print("ERROR: Expected a number between " + str(min_value) + " and " + str(max_value))


    def __setup_assistant(self):
        """ask the user for configuration information in order to write
        the configuration file."""

        try:
            print()
            print("Type of software defined radio (SDR) hardware")
            print("  1 HackRF")
            print("  2 LimeSDR")
            print("  3 Other (manually edit pyhsock.ini)")
            sdr = self.__input_number("Which type of SDR do you use? [1] ", 1, 1, 3) - 1

            number_of_receivers = self.__input_number("How many receivers do you have? [1] ", 1, 0, 100)
            types = []

            for i in range(1, number_of_receivers + 1):
                print()
                print("Type of receiver " + str(i))
                print("  1 PAC / Pacdog  (tested ATX/DTX and ACX)")
                print("  2 Wodondog 433 Mhz")
                print("  3 Petrainer")
                receiver_type = self.__input_number("Which type is receiver " + str(i) + "? ", 0, 1, 3)
                types.append(receiver_type - 1)

            config = self.__generate_configuration(sdr, types)
            self.__write_default_configuration(config)
            print()
            print("Default configuration was written with random transmitter codes.")
            print("If you know the code of your transmitter, you can edit the configuration file to use it.")
            print()
            print("Please reset your receiver into pairing mode and " + sys.argv[0] + " --receiver 1")
            print()
            sys.exit(0)
        except KeyboardInterrupt:
            print()
            print("Setup aborted. No configuration written.")
            sys.exit(0)


    def __generate_configuration(self, sdr, receiver_types):
        """generates a default configuration with random codes

        @param sdr index of software defined radio
        @param receiver_types array of indexes of receiver types
        """
        sdrs = ["sdr=HackRF", "sdr=LimeSDR", "# sdr= HackRF"]
        colors = ["#FFD", "#DFF", "#DFD", "#DDF", "#FDD", "#DDD", "#FDF", "#FFF", "#DDD"]
        receiver_type_configs = [
            """
[receiver]
type=pac
name=PAC[number]
color=[color]
transmitter_code=[transmitter_code_9bit]
channel=1
""",

            """
[receiver]
type=wodondog
name=Wodondog[number]
color=[color]
transmitter_code=[transmitter_code_16bit]
channel=1
""",

            """
[receiver]
type=petrainer
name=Petrainer[number]
color=[color]
transmitter_code=[transmitter_code_16bit]
channel=1
"""
        ]
        config = """
#
# Configuration file for remoshock. Please see https://github.com/remoshock/remoshock#readme
# Lines starting with a # are ignored.
#

[global]
web_port = 7777
web_authentication_token = [web_authentication_token]
#for https support:
#web_server_certile=key_and_cert.pem

# URH supports the following hardware, that can transmit on 27.195 MHz (upper/lower case is important):
# HackRF, LimeSDR
[sdr]


[randomizer]
beep_probability_percent = 100
shock_probability_percent = 100
shock_min_duration_ms = 250
shock_max_duration_ms = 250
shock_min_power_percent = 5
shock_max_power_percent = 10
pause_min_s = 300
pause_max_s = 900
start_delay_min_minutes = 0
start_delay_max_minutes = 0
runtime_min_minutes = 1440
runtime_max_minutes = 1440
"""

        config = config.replace("[sdr]", sdrs[sdr])
        config = config.replace("[web_authentication_token]", self.__generate_web_authentication_token())

        i = 0
        for receiver_type in receiver_types:
            config = config + receiver_type_configs[receiver_type]
            config = config.replace("[number]", str(i + 1))
            config = config.replace("[color]", str(colors[i % len(colors)]))
            config = config.replace("[transmitter_code_9bit]", self.__generate_transmitter_code(9))
            config = config.replace("[transmitter_code_16bit]", self.__generate_transmitter_code(16))
            i = i + 1

        return config


    def __write_default_configuration(self, config):
        """write a default configuration to remoshock.ini.
        web_authentication_token and transmitter_code are replaced by random values"""

        print("Writing default configuration file to " + self.filename)
        with open(self.filename, "w") as f:
            f.write(config)


    def __start_setup_assistant_if_config_missing(self):
        """starts the setup assistent to write a default configuration,
        if there is no configuration file to be found"""

        if not os.path.exists(self.filename):
            self.__setup_assistant()


    def __determine_filename(self):
        """configuration file should be used from the .config subfolder
        of the user's home directory"""

        config_folder = os.path.expanduser("~") + "/.config"
        if not os.path.exists(config_folder):
            os.makedirs(config_folder)
        return config_folder + "/remoshock.ini"


    def __read_configuration_from_file(self):
        print("Using configuration file " + self.filename)
        config = configparser.ConfigParser(defaults=None, dict_type=MultiReceiverSectionSupport,
                                           strict=False, default_section="default")
        config.read(self.filename, "UTF-8")
        self.config = config
