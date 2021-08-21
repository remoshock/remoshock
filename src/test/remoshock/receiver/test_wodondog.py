#
# Copyright nilswinter 2020-2021. License: AGPL
# _____________________________________________

import unittest

from remoshock.core.action import Action
from remoshock.receiver.wodondog import Wodondog


class WodondogTestCase(unittest.TestCase):
    """test for Wodondog collar"""


    def test_encoding(self):
        """test for the transfer encoding"""
        receiver = Wodondog("Wodondog1", "#FFF", "0101010101010101", 1)
        expected = "11111100010001110100011101000111010001110100011101000111010001110100011101000100010001000100010001110100010001000100010001000100010001110111010001110100011101110100011101000100010000"
        data = "0101010101010101000000100000000110101101"
        encoded = receiver.encode_for_transmission(data)
        self.assertEqual(expected, encoded, "encoding")


    def test_generate(self):
        """test for generating messages"""
        receiver = Wodondog("Wodondog1", "#FFF", "0101010101010101", 1)
        expected = "0101010101010101000000110000000010101101"
        generated = receiver.generate(Action.BEEP, 0)
        self.assertEqual(expected, generated, "generation")

        expected = "0101010101010101000000100000000110101101"
        generated = receiver.generate(Action.VIBRATE, 1)
        self.assertEqual(expected, generated, "generation")

        expected = "0101010101010101000000100110001100001111"
        generated = receiver.generate(Action.VIBRATE, 99)
        self.assertEqual(expected, generated, "generation")
