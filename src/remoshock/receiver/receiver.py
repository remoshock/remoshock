#
# Copyright nilswinter 2020-2021. License: AGPL
# _____________________________________________


class Receiver:
    """parent class for all receivers"""

    def __init__(self, receiver_properties):
        """constructs a Receiver

        @param receiver_properties receiver_properties
        """
        self.receiver_properties = receiver_properties


    def is_arduino_required(self):
        """does this receiver require arshock on Arduino?"""
        return False


    def is_sdr_required(self):
        """does this receiver require a SDR (software defined radio) transmitter?"""
        return False


    def boot(self, _arduino_manager, _sdr_sender):
        """initializes the receiver, sub-classes will do something useful here

        @param _arduino_manager reference to the arduino manager
        @param _sdr_sender reference to the software defined radio transmitter
        """


    def command(self, action, power, duration):
        """transmit a command to the receiver, sub-classes will do something useful here"""


    def get_config(self):
        """returns configuration information for the website

        Most notable name, color, initial power and initial duration settings
        as well as the duration increment (e. g. 250ms for PAC and 500ms for Petrainer)."""
        config = {
            "name": self.receiver_properties.name,
            "color": self.receiver_properties.color,
            "power": 10,
            "duration": 500,
            "durationIncrement": self.receiver_properties.duration_increment_ms
        }
        return config
