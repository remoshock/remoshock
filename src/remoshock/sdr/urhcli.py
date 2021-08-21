#
# Copyright nilswinter 2020-2021. License: AGPL
# _____________________________________________

import subprocess
import threading

from remoshock.sdr.sdrsender import SdrSender


lock = threading.RLock()


class UrhCliSender(SdrSender):
    """sends messages using urh_cli (the Universal Radio Hacker - Command Line Interface)"""

    def __init__(self, sdr, verbose):
        """constructs the UrhCliSender

        @param sdr name of the SDR hardware (e. g. HackRF)
        @param verbose whether to print debug messages"""
        self.sdr = sdr
        self.verbose = verbose


    def send(self, frequency, sample_rate, carrier_frequency,
             modulation_type, samples_per_symbol, low_frequency,
             high_frequency, pause, data):

        with lock:
            cmd = [
                "urh_cli",
                "--transmit",
                "--device", self.sdr,
                "--frequency", str(frequency),
                "--sample-rate", str(sample_rate),
                "--carrier-frequency", str(carrier_frequency),
                "--modulation-type", modulation_type,
                "--samples-per-symbol", str(samples_per_symbol),
                "--parameters", str(low_frequency), str(high_frequency),
                "--pause", str(pause),
                "--if-gain", "47",
                "--messages", data]

            stdout = subprocess.DEVNULL
            if self.verbose:
                print(cmd)
                stdout = None
            subprocess.run(cmd, stdout=stdout)
