#
# Copyright nilswinter 2020-2022. License: AGPL
# _____________________________________________

import argparse
import sys

from remoshock.core.remoshock import Remoshock, RemoshockMock
from remoshock.core.action import Action
from remoshock.core.version import VERSION


class RemoshockCli:
    """a commandline tool to send a command to a receiver"""

    def __parse_args(self):
        """parses command line arguments"""
        parser = argparse.ArgumentParser(description="Shock collar remote",
                                         epilog="Please see https://remoshock.github.io/applications.html for documentation.")

        parser.add_argument("-C", "--configfile",
                            help="custom configuration file. Defaults to ~/.config/remoshock.ini")
        parser.add_argument("-S", "--settingsfile",
                            help="custom settings file. Defaults to ~/.config/remoshock.dat")
        parser.add_argument("-r", "--receiver",
                            type=int,
                            default=1,
                            metavar="n",
                            help="number of receiver entry from remoshock.ini, starting at 1")
        parser.add_argument("-a", "--action",
                            default="BEEP",
                            choices=["LIGHT", "BEEP", "VIBRATE", "SHOCK", "BEEPSHOCK"],
                            help="Action to perform",
                            type=str.upper)
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
                            default=1,
                            metavar="n",
                            help="power level (1-100)")
        parser.add_argument("--experimental",
                            action="store_true",
                            help=argparse.SUPPRESS)
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


    def __boot_remoshock(self):
        """starts up the remoshock infrastructure"""
        if self.args.mock:
            self.remoshock = RemoshockMock(self.args)
        else:
            self.remoshock = Remoshock(self.args)
        self.remoshock.boot()


    def __process_action(self):
        """sends the specified command to the specified receiver"""
        action = Action[self.args.action]
        self.remoshock.command(self.args.receiver, action, self.args.power, self.args.duration)


    def start(self):
        """starts up remoshockcli"""
        self.__parse_args()
        self.__boot_remoshock()
        self.__process_action()


def main():
    try:
        RemoshockCli().start()
    except KeyboardInterrupt:
        print("Stopped by Ctrl+c.")
        sys.exit(0)
