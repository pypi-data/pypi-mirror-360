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
from everysk.api.api_resources import PrivateSecurity
from everysk.core.unittests import TestCase


###############################################################################
#   Private Security TestCase Implementation
###############################################################################
class APIPrivateSecurityTestCase(TestCase):

    def test_private_security_class_name(self):
        self.assertEqual(PrivateSecurity.class_name(), 'private_security')
