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
#pyshock.command(Action.VIB, 0, 5, 5000)
#pyshock.command(Action.VIB, 1, 0, 0)

def beepZapMixed(device, duration):
    pyshock.command(Action.BEEP, device, 0, 0)
    time.sleep(1.5); # Beep lasts for a while after the message was sent, so add some additional time to 1s
    pyshock.command(Action.ZAP, device + 2, 0, duration)

def beepZap(device, duration):
    pyshock.command(Action.BEEP, device, 0, 300)
    time.sleep(1);
    pyshock.command(Action.ZAP, device, 0, duration)

def test():
    pyshock.command(Action.BEEP, 0, 0, 300)
    time.sleep(1);
    pyshock.command(Action.ZAP, 0, 0, 300)
    time.sleep(1);
    pyshock.command(Action.BEEP, 1, 0, 300)
    time.sleep(1);
    pyshock.command(Action.ZAP, 1, 0, 300)
    time.sleep(1);

"""
pyshock.command(Action.ZAP, 2, 0, 500)
time.sleep(1)
pyshock.command(Action.ZAP, 3, 0, 500)
time.sleep(300)

"""

def r():
    while True:
        time.sleep(random.randrange(120))
        beepZap(random.randrange(2), 1150)

#test();
r();


