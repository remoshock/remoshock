#
# Copyright nilswinter 2020-2021. License: AGPL
# _____________________________________________

import unittest
from remoshock.core.remoshock import Remoshock


class RemoshockTestCase(unittest.TestCase):
    """tests for the manager class"""

    def test_not_debug(self):
        """ensure that we do not do a release with debugging enabled"""

        remoshock = Remoshock(None)
        self.assertFalse(remoshock.debug_duration_in_message_count, "debug_duration_in_message_count must be False")
