#!/usr/bin/python3
#
# Copyright nilswinter 2020-2021. License: AGPL
#_______________________________________________

from enum import Enum

class Action(Enum):
    LED = 10
    BEEP = 11
    VIB = 12
    ZAP = 13
    BEEPZAP = 99
