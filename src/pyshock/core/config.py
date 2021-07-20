#!/usr/bin/python3
#
# Copyright nilswinter 2020-2021. License: AGPL
#_______________________________________________

import collections
import configparser
import os
import secrets
import string

class MultireceiverSectionSupport(collections.OrderedDict):
    index = 0   # class variable

    def __setitem__(self, key, val):
        if isinstance(val, dict) and key == "receiver":
            self.index = self.index + 1
            key += str(self.index)
        collections.OrderedDict.__setitem__(self, key, val)


class ConfigManager:

    def __init__(self):
        self.filename = self.__determine_filename()
        self.__write_default_configuration_if_missing()
        self.__read_configuration_from_file()

    def __generate_web_authentication_token(self):
        charset = string.ascii_lowercase + string.ascii_uppercase + string.digits
        return ''.join(secrets.choice(charset) for _ in range(20))

    def __generate_transmitter_code(self):
        charset = "01"
        return ''.join(secrets.choice(charset) for _ in range(9))

    def __write_default_configuration(self):
        default = """
[global]
web_port = 7777    
web_authentication_token = [web_authentication_token]

# URH supports the following hardware (upper/lower case is important): 
# AirSpy R2, AirSpy Mini, BladeRF, FUNcube, HackRF, LimeSDR, PlutoSDR, SDRPlay, USRP

# sdr=HackRF



[receiver]
type=pac
name=PAC1
color=#FFD
transmitter_code=[transmitter_code]
button=1

[receiver]
type=pac
name=PAC2
color=#FFE
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
            self.write_default_configuration(self.filename)


    def __determine_filename(self):
        config_folder = os.path.expanduser("~") + "/.config"
        if not os.path.exists(config_folder):
            os.makedirs(config_folder)
        return config_folder + "/pyshock.ini"


    def __read_configuration_from_file(self):
        print("Using configuration file " + self.filename)
        config = configparser.ConfigParser(defaults=None, dict_type=MultireceiverSectionSupport, strict=False, default_section="default")
        config.read(self.filename, "UTF-8")
        self.config = config

