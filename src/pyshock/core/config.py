#!/usr/bin/python3
#
# Copyright nilswinter 2020-2021. License: AGPL
#_______________________________________________

import collections
import configparser
import os
import secrets
import string

class MultiReceiverSectionSupport(collections.OrderedDict):
    """This class adds an index number at the end of each [receiver] section."""

    index = 0

    def __setitem__(self, key, val):
        if isinstance(val, dict) and key == "receiver":
            self.index = self.index + 1
            key += str(self.index)
        collections.OrderedDict.__setitem__(self, key, val)


class ConfigManager:
    """This class loads configuration from pyshock.ini and writes the
    default configuration with freshly created random values."""

    def __init__(self):
        self.filename = self.__determine_filename()
        self.__write_default_configuration_if_missing()
        self.__read_configuration_from_file()


    def __generate_web_authentication_token(self):
        """creates a web_authentication_token that is probably unique to this installation."""
        charset = string.ascii_lowercase + string.ascii_uppercase + string.digits
        return ''.join(secrets.choice(charset) for _ in range(20))


    def __generate_transmitter_code(self):
        """creates a transmitter_code that is probably unique to this installation."""
        charset = "01"
        return ''.join(secrets.choice(charset) for _ in range(9))


    def __write_default_configuration(self):
        """write a default configuration to pyshock.ini.
        web_authentication_token and transmitter_code are replaced by random values"""
        default = """
[global]
web_port = 7777    
web_authentication_token = [web_authentication_token]
#for https support:
#web_server_certile=key_and_cert.pem

# URH supports the following hardware, that can transmit on 27.195 MHz (upper/lower case is important): 
# HackRF, LimeSDR

# sdr=HackRF


[randomizer]
beep_probability_percent = 100
shock_probability_percent = 100
shock_min_duration_ms = 250
shock_max_duration_ms = 250
shock_min_power_percent = 5
shock_max_power_percent = 10
pause_min_s = 300
pause_max_s = 900
runtime_min_minutes = 1440
runtime_max_minutes = 1440

[receiver]
type=pac
name=PAC1
color=#FFD
transmitter_code=[transmitter_code]
button=1

[receiver]
type=pac
name=PAC2
color=#DDF
transmitter_code=[transmitter_code]
button=2

[receiver]
type=pac
name=PAC3
color=#FDF
transmitter_code=[transmitter_code]
button=3

[receiver]
type=pac
name=PAC4
color=#DFF
transmitter_code=[transmitter_code]
button=4

"""
        config = default.replace("[web_authentication_token]", self.__generate_web_authentication_token())
        config = config.replace("[transmitter_code]", self.__generate_transmitter_code())

        print("Writing default configuration file to " + self.filename)
        with open(self.filename, "w") as f:
            f.write(config)


    def __write_default_configuration_if_missing(self):
        if not os.path.exists(self.filename):
            self.__write_default_configuration()


    def __determine_filename(self):
        """configuration file should be used from the .config subfolder
        of the user's home directory"""

        config_folder = os.path.expanduser("~") + "/.config"
        if not os.path.exists(config_folder):
            os.makedirs(config_folder)
        return config_folder + "/pyshock.ini"


    def __read_configuration_from_file(self):
        print("Using configuration file " + self.filename)
        config = configparser.ConfigParser(defaults=None, dict_type=MultiReceiverSectionSupport,
                                           strict=False, default_section="default")
        config.read(self.filename, "UTF-8")
        self.config = config
