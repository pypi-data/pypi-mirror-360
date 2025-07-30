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
from everysk.api import get_api_config
from everysk.config import settings
from everysk.core.unittests import TestCase


###############################################################################
#   Implementation
###############################################################################

class TestGetAPIConfig(TestCase):
    def test_full_params_provided(self):
        params = {
            'api_entry': 'https://example.com',
            'api_version': 'v2',
            'api_sid': 'abc',
            'api_token': 'token_example123',
            'verify_ssl_certs': True
        }

        config = get_api_config(params)

        self.assertEqual(config, (
            'https://example.com',
            'v2',
            'abc',
            'token_example123',
            True
        ))

    def test_no_params_provided(self):
        settings.EVERYSK_API_URL = 'https://default.com'
        settings.EVERYSK_API_SID = 'xyz'
        settings.EVERYSK_API_TOKEN = 'default_token'
        settings.EVERYSK_API_VERIFY_SSL_CERTS = False

        config = get_api_config({})

        self.assertEqual(config, (
            'https://default.com',
            'v2',
            'xyz',
            'default_token',
            False
        ))

    def test_partial_params_provided(self):
        params = {
            'api_entry': 'https://partial.com',
            'api_version': 'v3',
        }
        settings.EVERYSK_API_SID = 'partial_sid'
        settings.EVERYSK_API_TOKEN = 'partial_token'
        settings.EVERYSK_API_VERIFY_SSL_CERTS = True

        config = get_api_config(params)

        self.assertEqual(config, (
            'https://partial.com',
            'v3',
            'partial_sid',
            'partial_token',
            True
        ))
