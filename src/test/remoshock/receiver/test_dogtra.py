#
# Copyright nilswinter 2020-2021. License: AGPL
# _____________________________________________

import unittest

from remoshock.receiver.dogtra import Dogtra


class DogtraTestCase(unittest.TestCase):

    def test_encoding(self):
        dogtra = Dogtra("Dogtra1", "#FFF", "010110110", 1)
        expected = "11100010010010010011010010011011011011011010011010010011100000011111101000000"
        data = "00001001111101001100000011111101000000"
        encoded = dogtra.encode_for_transmission(data)
        self.assertEqual(expected, encoded, "encoding")


    def test_calculate_intensity_code(self):
        dogtra = Dogtra("Dogtra1", "#FFF", "010110110", 1)
        self.assertEqual("0101000000000000000000", dogtra.calculate_intensity_code(0), "intensity 0")
        self.assertEqual("0001111111110100000000", dogtra.calculate_intensity_code(28), "intensity 28")
        self.assertEqual("0000000111010000000000", dogtra.calculate_intensity_code(62), "intensity 62")
        self.assertEqual("1011110100000000000000", dogtra.calculate_intensity_code(103), "intensity 103")
        self.assertEqual("1000000001101000000000", dogtra.calculate_intensity_code(171), "intensity 171")
        self.assertEqual("1100000011111101000000", dogtra.calculate_intensity_code(255), "intensity 255")
