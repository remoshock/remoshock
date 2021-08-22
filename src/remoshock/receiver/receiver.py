#
# Copyright nilswinter 2020-2021. License: AGPL
# _____________________________________________


class Receiver:
    """parent class for all receivers"""

    def __init__(self, name, color):
        """constructs a Receiver

        @param name name used on website
        @param color background color used on website
        """
        self.name = name
        self.color = color


    def is_arduino_required(self):
        """does this receiver require arshock on Arduino?"""
        return False


    def is_sdr_required(self):
        """does this receiver require a SDR (software defined radio) transmitter?"""
        return False


    def boot(self, _remoshock, _receiver, _arduino_manager, _sdr_sender):
        """initializes the receiver, sub-classes will do something useful here

        @param _remoshock a reference to the manager class
        @param _receiver receiver number if this instance
        @param _arduino_manager reference to the arduino manager
        @param _sdr_sender reference to the software defined radio transmitter
        """


    def command(self, action, power, duration):
        """transmit a command to the receiver, sub-classes will do something useful here"""


    def get_impulse_duration(self):
        """duration of one impulse in milliseconds"""
        return 250

    def get_config(self):
        """returns configuration information for the website

        Most notable name, color, initial power and initial duration settings
        as well as the duration increment (e. g. 250ms for PAC and 500ms for Petainer)."""
        config = {
            "name": self.name,
            "color": self.color,
            "power": 10,
            "duration": 500,
            "durationIncrement": self.get_impulse_duration()
        }
        return config
