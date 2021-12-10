#
# Copyright nilswinter 2020-2021. License: AGPL
# _____________________________________________

import unittest

from remoshock.core.receiverproperties import ReceiverProperties
from remoshock.receiver.dogtra import Dogtra


class DogtraTestCase(unittest.TestCase):

    def test_encoding(self):
        dogtra = Dogtra(ReceiverProperties("dogtra200ncp"), "010110110", 1)
        expected = "11100010010010010011010010011011011011011010011010010011100000011111101000000"
        data = "00001001111101001100000011111101000000"
        encoded = dogtra.encode_for_transmission(data)
        self.assertEqual(expected, encoded, "encoding")


    def test_calculate_intensity_code(self):
        dogtra = Dogtra(ReceiverProperties("dogtra200ncp"), "010110110", 1)
        self.assertEqual("0101000000000000000000", dogtra.calculate_intensity_code(0), "intensity 0% / 0")
        self.assertEqual("0000101000000000000000", dogtra.calculate_intensity_code(20), "intensity 20% / 30")
        self.assertEqual("0000000111101000000000", dogtra.calculate_intensity_code(40), "intensity 40% / 63")
        self.assertEqual("1011110100000000000000", dogtra.calculate_intensity_code(60), "intensity 60% / 103")
        self.assertEqual("1000000001010000000000", dogtra.calculate_intensity_code(80), "intensity 80% / 170")
        self.assertEqual("1100000011111101000000", dogtra.calculate_intensity_code(100), "intensity 100% / 255")
