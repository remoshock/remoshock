#!/usr/bin/python3
#
# Copyright nilswinter 2020-2021. License: AGPL
#_______________________________________________

import argparse
import random
import time

from pyshock.core.pyshock import Pyshock
from pyshock.core.action import Action 

pyshock = Pyshock(argparse.Namespace())
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
    receiver = random.randrange(2)
    pyshock.command(Action.BEEP, receiver, 0, 0)
    time.sleep(1);
    pyshock.command(Action.ZAP, receiver, 1, 0)
"""
#pyshock.command(Action.VIB, 0, 5, 5000)
#pyshock.command(Action.VIB, 1, 0, 0)

def beepZapMixed(receiver, duration):
    pyshock.command(Action.BEEP, receiver, 0, 0)
    time.sleep(1.5); # Beep lasts for a while after the message was sent, so add some additional time to 1s
    pyshock.command(Action.ZAP, receiver + 2, 0, duration)

def beepZap(receiver, power, duration):
    pyshock.command(Action.BEEP, receiver, 0, 300)
    time.sleep(1);
    pyshock.command(Action.ZAP, receiver, power, duration)

def test():
    pyshock.command(Action.BEEPZAP, 0, 40, 1050)
    time.sleep(1);
    pyshock.command(Action.BEEPZAP, 1, 40, 1050)
    time.sleep(1);

"""
pyshock.command(Action.ZAP, 2, 0, 500)
time.sleep(1)
pyshock.command(Action.ZAP, 3, 0, 500)
time.sleep(300)

"""

def r():
    while True:
#        time.sleep(random.randrange(5 * 60))
        time.sleep(random.randrange(20 * 60) + 20 * 60)
        pyshock.command(Action.BEEPZAP, random.randrange(2), 40, 1050)


def test2():
        pyshock.command(Action.BEEP, 4, 1, 0)

def r2():
    while True:
        time.sleep(random.randrange(20 * 60) + 20 * 60)
        pyshock.command(Action.ZAP, 4, 0, 130)


#test2();
#r2();

time.sleep(30)
test()
r()
