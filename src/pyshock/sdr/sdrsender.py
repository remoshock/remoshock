#
# Copyright nilswinter 2020-2021. License: AGPL
# _____________________________________________


class SdrSender:
    """parent class for SDR based senders"""

    def send(self, frequency, sample_rate, carrier_frequency,
             modulation_type, samples_per_symbol, low_frequency,
             high_frequency, pause, data):
        pass
