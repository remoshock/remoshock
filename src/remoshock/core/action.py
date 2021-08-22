#
# Copyright nilswinter 2020-2021. License: AGPL
# _____________________________________________

from enum import Enum


class Action(Enum):
    """Actions that may be sent to the receivers.

    Note: Not all receivers support all actions. e. g. Vibrate
    BEEPSHOCK will send one beep, wait one second and send a shock.
    """
    LIGHT = 10
    BEEP = 11
    VIBRATE = 12
    SHOCK = 13
    BEEPSHOCK = 99
