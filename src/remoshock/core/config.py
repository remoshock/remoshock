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

    def __init__(self, args):
        self.__tokens = []

        if "configfile" in args and args.configfile is not None:
            self.config_filename = args.configfile
            if not os.path.exists(args.configfile):
                print("Error configuration file " + args.configfile + " does not exists.")
                print("If you do not specific a configuration file, the default configuration file")
                print("at ~/.config/remoshock.ini will be used. If that file does not exist, ")
                print("the setup wizzard will create it for you.")
                sys.exit(1)
        else:
            self.config_filename = self.__determine_config_folder() + "/remoshock.ini"

        if "setttingsfile" in args and args.settingsfile is not None:
            self.settings_filename = args.settingsfile
        else:
            self.settings_filename = self.__determine_config_folder() + "/remoshock.dat"

        self.__start_setup_assistant_if_config_missing()
        self.__read_configuration_from_file()
        self.__read_settings_from_file()


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
            print("  3 Other (manually edit remoshock.ini)")
            sdr = self.__input_number("Which type of SDR do you use? [1] ", 1, 1, 3) - 1

            number_of_receivers = self.__input_number("How many receivers do you have? [1] ", 1, 0, 100)
            types = []

            for i in range(1, number_of_receivers + 1):
                print()
                print("Type of receiver " + str(i))
                print("  1 PAC / Pacdog  (tested ATX/DTX and ACX)")
                print("  2 Patpet T150")
                print("  3 Petrainer")
                print("  4 Wodondog 433 Mhz with receiver flashlight")
                print("  5 Wodondog 433 Mhz without receiver flashlight")
                receiver_type = self.__input_number("Which type is receiver " + str(i) + "? ", 0, 1, 5)
                types.append(receiver_type - 1)

            config = self.__generate_configuration(sdr, types)
            self.__write_default_configuration(config)
            print()
            print("Default configuration was written with random transmitter codes.")
            print("If you know the code of your transmitter, you can edit the configuration file to use it.")
            print()
            print("Please reset your receiver into pairing mode and run remoshockcli --receiver 1")
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
type=patpett150
name=PatpetT150_[number]
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
type=wodondogb
name=WodondogB[number]
color=[color]
transmitter_code=[transmitter_code_16bit]
channel=1
"""
        ]
        config = """
#
# Configuration file for remoshock. Please see https://remoshock.github.io/setup.html
# Lines starting with a # are ignored.
#

[global]
web_port = 7777
web_authentication_token = [web_authentication_token]
#for https support:
#web_server_certfile=key_and_cert.pem

# URH supports the following hardware, that can transmit on 27.195 MHz (upper/lower case is important):
# HackRF, LimeSDR
[sdr]


[randomizer]
beep_probability_percent = 100
shock_probability_percent = 100
shock_min_duration_ms = 500
shock_max_duration_ms = 500
shock_min_power_percent = 10
shock_max_power_percent = 10
pause_min_s = 900
pause_max_s = 1800
start_delay_min_minutes = 0
start_delay_max_minutes = 0
runtime_min_minutes = 600
runtime_max_minutes = 600
"""

        receiver_static_config = """
#limit_shock_max_power_percent = 100
#limit_shock_max_duration_ms = 10000

#random_probability_weight = 1
#random_shock_min_duration_ms = 500
#random_shock_max_duration_ms = 500
#random_shock_min_power_percent = 10
#random_shock_max_power_percent = 10
"""

        config = config.replace("[sdr]", sdrs[sdr])
        config = config.replace("[web_authentication_token]", self.__generate_web_authentication_token())

        i = 0
        for receiver_type in receiver_types:
            receiver_config = receiver_type_configs[receiver_type]
            receiver_config = receiver_config.replace("[number]", str(i + 1))
            receiver_config = receiver_config.replace("[color]", str(colors[i % len(colors)]))
            receiver_config = receiver_config.replace("[transmitter_code_9bit]", self.__generate_transmitter_code(9))
            receiver_config = receiver_config.replace("[transmitter_code_16bit]", self.__generate_transmitter_code(16))
            config = config + receiver_config + receiver_static_config
            i = i + 1

        return config


    def __write_default_configuration(self, config):
        """write a default configuration to remoshock.ini.
        web_authentication_token and transmitter_code are replaced by random values"""

        print("Writing default configuration file to " + self.config_filename)
        with open(self.config_filename, "w") as f:
            f.write(config)


    def __start_setup_assistant_if_config_missing(self):
        """starts the setup assistent to write a default configuration,
        if there is no configuration file to be found"""

        if not os.path.exists(self.config_filename):
            self.__setup_assistant()


    def __determine_config_folder(self):
        """configuration file should be used from the .config subfolder
        of the user's home directory"""

        config_folder = os.path.expanduser("~") + "/.config"
        if not os.path.exists(config_folder):
            os.makedirs(config_folder)
        return config_folder


    def __read_configuration_from_file(self):
        """reads the configuration from remoshock.ini"""

        print("Using configuration file " + self.config_filename)
        config = configparser.ConfigParser(defaults=None, dict_type=MultiReceiverSectionSupport,
                                           strict=False, default_section="default")
        config.read(self.config_filename, "UTF-8")
        self.config = config


    def __read_settings_from_file(self):
        """reads settings from remoshock.dat"""

        settings = configparser.ConfigParser(defaults=None, strict=False, default_section="default")
        settings.read(self.settings_filename, "UTF-8")
        self.settings = settings


    def save_settings(self, settings):
        """saves settings to remoshock.dat"""

        # read settings from file to reduce race conditions
        self.__read_settings_from_file()

        # update settings
        for section in settings:
            if section not in self.settings:
                self.settings.add_section(section)
            for key in settings[section]:
                self.settings[section][key] = settings[section][key]

        # write to remoshock.dat
        with open(self.settings_filename, 'w') as file:
            file.write("#\n")
            file.write("#     Do not edit this file. Edit remoshock.ini instead.\n")
            file.write("#     This file is automatically generated and will be overwritten.\n")
            file.write("#\n")
            self.settings.write(file)
