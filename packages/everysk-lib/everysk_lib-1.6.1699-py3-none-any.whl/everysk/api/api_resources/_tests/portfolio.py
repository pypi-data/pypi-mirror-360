###############################################################################
#
# (C) Copyright 2025 EVERYSK TECHNOLOGIES
#
# This is an unpublished work containing confidential and proprietary
# information of EVERYSK TECHNOLOGIES. Disclosure, use, or reproduction
# without authorization of EVERYSK TECHNOLOGIES is prohibited.
#
###############################################################################

###############################################################################
#   Imports
###############################################################################
from everysk.api.api_resources import Portfolio
from everysk.core.unittests import TestCase

###############################################################################
#   Portfolio TestCase Implementation
###############################################################################
class APIPortfolioTestCase(TestCase):

    def test_class_name(self):
        self.assertEqual(Portfolio.class_name(), 'portfolio')
