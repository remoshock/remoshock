import unittest

from pyshock.receiver.pacdog import Pacdog


class TestPacdog(unittest.TestCase):

    def assertThat(self, message, expected, actual):
        if expected == actual:
            print(message + ": pass")
        else:
            print(message + ": FAILED")
            print("   Expected: " + expected)
            print("   Actual  : " + actual)

    def test_encoding(self):
        pacdog = Pacdog("PAC1", "#FFF", "010110110", 1)
        expected = "010101010101010111110010110010110010010110010010010110110010110110010010010010010010110110010"
        data = "010100100011011000000110"
        encoded = pacdog.encode(data)
        self.assertThat("encoding", expected, encoded)

    def test_generate(self):
        pacdog = Pacdog("PAC1", "#FFF", "010110110", 1)
        expected = "010100100011011000000110"
        generated = pacdog.generate("010110110", 18, 2, 1)
        self.assertThat("generation", expected, generated)

    def test_calculate_intensity_code(self):
        pacdog = Pacdog("PAC1", "#FFF", "010110110", 1)
        self.assertThat("intensity  1", "100000", pacdog.calculate_intensity_code(1))
        self.assertThat("intensity 32", "000001", pacdog.calculate_intensity_code(32))


if __name__ == '__main__':
    unittest.main()