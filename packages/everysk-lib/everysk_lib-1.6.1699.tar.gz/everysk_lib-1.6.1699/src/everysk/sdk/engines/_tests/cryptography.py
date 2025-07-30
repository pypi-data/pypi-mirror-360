###############################################################################
#
# (C) Copyright 2023 EVERYSK TECHNOLOGIES
#
# This is an unpublished work containing confidential and proprietary
# information of EVERYSK TECHNOLOGIES. Disclosure, use, or reproduction
# without authorization of EVERYSK TECHNOLOGIES is prohibited.
#
###############################################################################

###############################################################################
#   Imports
###############################################################################
from everysk.config import settings
from everysk.core.unittests import TestCase
from everysk.sdk.engines import cryptography

SYMBOL_ID_MAX_LEN = settings.SYMBOL_ID_MAX_LEN

###############################################################################
#   Cryptography TestCase Implementation
###############################################################################
class TestCryptography(TestCase):

    def test_generate_unique_id_with_characters(self):
        """ Test generate_unique_id method with a characters """
        length = 10
        characters = 'abcd123'
        result = cryptography.generate_random_id(length=length, characters=characters)
        self.assertTrue(len(result), length)
        self.assertTrue(all(char in characters for char in result))

    def test_generate_unique_id_with_length(self):
        """ Test generate_unique_id method with length """
        result = cryptography.generate_random_id(length=10)
        self.assertEqual(len(result), 10)

    def test_generate_simple_unique_id(self):
        """ Test generate_simple_unique_id method """
        result = cryptography.generate_short_random_id()
        self.assertIsInstance(result, str)
        self.assertEqual(len(result), settings.SIMPLE_UNIQUE_ID_LENGTH)
