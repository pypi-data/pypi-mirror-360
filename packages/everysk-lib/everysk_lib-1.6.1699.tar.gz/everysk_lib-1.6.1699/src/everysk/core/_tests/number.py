###############################################################################
#
# (C) Copyright 2023 EVERYSK TECHNOLOGIES
#
# This is an unpublished work containing confidential and proprietary
# information of EVERYSK TECHNOLOGIES. Disclosure, use, or reproduction
# without authorization of EVERYSK TECHNOLOGIES is prohibited.
#
###############################################################################

from everysk.core.number import is_float_convertible
from everysk.core.unittests import TestCase


class NumberTestCase(TestCase):

    def test_is_float_convertible(self):
        self.assertFalse(is_float_convertible(None))
        self.assertFalse(is_float_convertible('invalid'))
        self.assertTrue(is_float_convertible('25.1545'))
        self.assertTrue(is_float_convertible(25.1545))
