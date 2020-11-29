#!/usr/bin/python3

import random
import time

from pyshocklib import Pyshock, Action

pyshock = Pyshock()
pyshock.boot()

#command(Action.BEEP, 0, 5, 5000)

"""
for i in range (0, 20):
  pyshock.command(Action.VIB, 0, 1, 0)
  time.sleep(2);
"""

"""
for i in range (1, 10):
    time.sleep(10);
    device = random.randrange(2)
    pyshock.command(Action.BEEP, device, 0, 0)
    time.sleep(1);
    pyshock.command(Action.ZAP, device, 1, 0)
"""
pyshock.command(Action.VIB, 0, 0, 0)
pyshock.command(Action.VIB, 1, 0, 0)


