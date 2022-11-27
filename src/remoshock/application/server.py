#
# Copyright nilswinter 2020-2022. License: AGPL
# _____________________________________________

import argparse
import sys

from remoshock.core.remoshock import Remoshock, RemoshockMock
from remoshock.core.version import VERSION
from remoshock.httpserver.httpserver import HttpServer
from remoshock.util import powermanager
from remoshock.application.randomizer import RemoshockRandomizer


class RemoshockServer:
    """remoshockserver is a web server that provides the remote-control user-interface """

    def __parse_args(self):
        """parses command line arguments"""
        parser = argparse.ArgumentParser(description="Shock collar remote control",
                                         epilog="Please see https://remoshock.github.io/applications.html for documentation.")
        parser.add_argument("--mock",
                            action="store_true",
                            help=argparse.SUPPRESS)
        parser.add_argument("--experimental",
                            action="store_true",
                            help=argparse.SUPPRESS)
        parser.add_argument("--sdr",
                            help=argparse.SUPPRESS)

        parser.add_argument("-C", "--configfile",
                            help="custom configuration file. Defaults to ~/.config/remoshock.ini")
        parser.add_argument("-S", "--settingsfile",
                            help="custom settings file. Defaults to ~/.config/remoshock.dat")
        parser.add_argument("-v", "--verbose",
                            action="store_true",
                            help="prints debug messages")
        parser.add_argument("--version",
                            action="version",
                            version=VERSION)

        self.args = parser.parse_args()


    def __boot_remoshock(self):
        """starts up the remoshock infrastructure"""
        if self.args.mock:
            remoshock = RemoshockMock(self.args)
        else:
            remoshock = Remoshock(self.args)

        remoshock.boot()
        self.remoshock = remoshock


    def start(self):
        """starts up remoshockserver"""
        self.__parse_args()
        self.__boot_remoshock()
        powermanager.inhibit()
        randomizer = RemoshockRandomizer()
        randomizer.prepare_in_server_mode(self.remoshock)
        HttpServer(self.remoshock, self.args, randomizer).start_web_server()


def main():
    try:
        RemoshockServer().start()
    except KeyboardInterrupt:
        print("Stopped by Ctrl+c.")
        sys.exit(0)
