#
# Copyright nilswinter 2020-2021. License: AGPL
# _____________________________________________

import unittest

from remoshock.core.receiverproperties import ReceiverProperties
from remoshock.receiver.pac import Pac


class PacTestCase(unittest.TestCase):

    def test_encoding(self):
        pacdog = Pac(ReceiverProperties("pac"), "010110110", 1)
        expected = "010101010101010111110010110010110010010110010010010110110010110110010010010010010010110110010"
        data = "010100100011011000000110"
        encoded = pacdog.encode_for_transmission(data)
        self.assertEqual(expected, encoded, "encoding")


    def test_generate(self):
        pacdog = Pac(ReceiverProperties("pac"), "010110110", 1)
        expected = "010100100011011000000110"
        generated = pacdog.generate("010110110", 18, 2, 1)
        self.assertEqual(expected, generated, "generation")


    def test_calculate_intensity_code(self):
        pacdog = Pac(ReceiverProperties("pac"), "010110110", 1)
        self.assertEqual("100000", pacdog.calculate_intensity_code(1), "intensity  1")
        self.assertEqual("000001", pacdog.calculate_intensity_code(32), "intensity 32")
