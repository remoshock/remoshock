#!/usr/bin/python3
#
# Copyright nilswinter 2020-2021. License: AGPL
#_______________________________________________

from enum import Enum

class Action(Enum):
    LIGHT = 10
    BEEP = 11
    VIBRATE = 12
    SHOCK = 13
    BEEPSHOCK = 99
