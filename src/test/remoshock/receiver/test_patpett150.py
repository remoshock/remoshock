#
# Copyright nilswinter 2020-2021. License: AGPL
# _____________________________________________

import unittest

from remoshock.core.action import Action
from remoshock.core.receiverproperties import ReceiverProperties
from remoshock.receiver.patpett150 import PatpetT150


class Nameless915mTestCase(unittest.TestCase):

    def test_encoding(self):
        receiver = PatpetT150(ReceiverProperties("patpett150"), "0101010101010101", 1)
        expected = "11110000100001000010000100001000000001000010000100000000100001000000001000010000000010000100000000100001000000001000010000000010000100000000100001000000001000010000000010000100001000010000100001000010000100001000000001000000001000010000100000000100000000100001000000001"
        data = "0000100101010101010101010000000011001101"

        encoded = receiver.encode_for_transmission(data)
        self.assertEqual(expected, encoded, "encoding")


    def test_generate(self):
        receiver = PatpetT150(ReceiverProperties("patpett150"), "0101010101010101", 1)
        expected = "0000100101010101010101010000000011001101"
        generated = receiver.generate(Action.BEEP, 0)
        self.assertEqual(expected, generated, "generation beep")

        expected = "0000001101010101010101010000010100111101"
        generated = receiver.generate(Action.SHOCK, 5)
        self.assertEqual(expected, generated, "generation shock 1 (5%)")
