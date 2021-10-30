#
# Copyright nilswinter 2020-2021. License: AGPL
# _____________________________________________


class ReceiverProperties:
    """properties of a receiver such as name and capabilities"""

    def __init__(self,
                 name="receiver", color="#FFF"):
        """
        creates a ReceiverProperties object

        @param name name of the receiver as displayed on the web remote control
        @param color color of the receiver used by the web remote control
        """
        self.name = name
        self.color = color
