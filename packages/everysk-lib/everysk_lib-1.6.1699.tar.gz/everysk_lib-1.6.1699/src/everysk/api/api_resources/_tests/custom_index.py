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
from everysk.api.api_resources import CustomIndex
from everysk.core.unittests import TestCase


###############################################################################
#   Custom Index TestCase Implementation
###############################################################################
class APICustomIndexTestCase(TestCase):

    def test_class_name(self):
        self.assertEqual(CustomIndex.class_name(), 'custom_index')
