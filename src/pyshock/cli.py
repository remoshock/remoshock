#!/usr/bin/python3
#
# Copyright nilswinter 2020-2021. License: AGPL
#_______________________________________________


import argparse
import sys

from pyshock.core.pyshock import Pyshock, PyshockMock
from pyshock.core.action import Action
from pyshock.core.version import VERSION

class PyshockCli:
    """a commandline tool to send a command to a receiver"""

    def __parse_args(self):
        """parses command line arguments"""
        parser = argparse.ArgumentParser(description="Shock collar remote",
                                         epilog="Please see https://github.com/pyshock/pyshock for documentation.")
        parser.add_argument("-r", "--receiver",
                            type=int,
                            default=0,
                            metavar="n",
                            help="index of receiver entry from pyshock.ini, starting at 0")
        parser.add_argument("-a", "--action", 
                            default="BEEP",
                            choices=["LED", "BEEP", "VIB", "ZAP", "BEEPZAP"], 
                            help="Action to perform")
        parser.add_argument("-d", "--duration", 
                            type=int,
                            default=250,
                            metavar="n",
                            help="duration in ms  (Note: PAC uses an impulse duration of 250ms)")
        parser.add_argument("--mock",
                            action="store_true",
                            help=argparse.SUPPRESS)
        parser.add_argument("-p", "--power",
                            type=int,
                            default=0,
                            metavar="n",
                            help="power level (0-100)")
        parser.add_argument("--sdr",
                            help=argparse.SUPPRESS)
        parser.add_argument("-v", "--verbose",
                            action="store_true",
                            help="prints debug messages")
        parser.add_argument("--version",
                            action="version",
                            version=VERSION)
    
        self.args = parser.parse_args()
        print("Command: " + sys.argv[0] + " --receiver " + str(self.args.receiver) + " --action " + self.args.action
               + " --power " + str(self.args.power) + " --duration " + str(self.args.duration))


    def __boot_pyshock(self):
        """starts up the pyshock infrastructure"""
        if self.args.mock:
            self.pyshock = PyshockMock(self.args)
        else:
            self.pyshock = Pyshock(self.args)
        self.pyshock.boot()


    def __process_action(self):
        """sends the specified command to the specified receiver"""
        action = Action[self.args.action]
        self.pyshock.command(action, self.args.receiver, self.args.power, self.args.duration)

    
    def start(self):
        """starts up pyshockcli"""
        self.__parse_args()
        self.__boot_pyshock()
        self.__process_action()

