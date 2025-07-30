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
from everysk.api.api_resources import File
from everysk.core.unittests import TestCase


###############################################################################
#   File TestCase Implementation
###############################################################################
class APIFileTestCase(TestCase):

    def test_file_class_name(self):
        self.assertEqual(File.class_name(), 'file')
