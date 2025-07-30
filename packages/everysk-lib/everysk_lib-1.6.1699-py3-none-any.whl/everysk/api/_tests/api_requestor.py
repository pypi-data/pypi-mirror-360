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
import json

from everysk.api.api_requestor import APIRequestor
from everysk.core.exceptions import APIError
from everysk.core.unittests import TestCase, mock


###############################################################################
#  API Requestor Test Case Implementation
###############################################################################
class APIRequestorTestCase(TestCase):

    def setUp(self) -> None:
        self.api_requestor = APIRequestor(
            api_entry='https://api.example.com',
            api_version='v2',
            api_sid='your_api_sid',
            api_token='your_api_token',
            verify_ssl_certs=True,
        )
        return super().setUp()

    def test_api_requestor_initialization_without_api_entry_raises_value_error(self):
        with self.assertRaises(ValueError) as context:
            api_requestor = APIRequestor(
            api_entry='',
            api_version='v2',
            api_sid='your_api_sid',
            api_token='your_api_token',
            verify_ssl_certs=True
        )

        self.assertIn("Empty api_entry", str(context.exception))

    def test_api_requestor_initialization_with_wrong_api_version_raises_value_error(self):
        with self.assertRaises(ValueError) as context:
            api_requestor = APIRequestor(
                api_entry='https://api.example.com',
                api_version='v1',
                api_sid='your_api_sid',
                api_token='your_api_token',
                verify_ssl_certs=True
            )

        self.assertIn('Invalid api_version (supported version: "v2")', str(context.exception))

    def test_api_requestor_initialization_without_api_sid_raises_value_error(self):
        with self.assertRaises(ValueError) as context:
            api_requestor = APIRequestor(
                api_entry='https://api.example.com',
                api_version='v2',
                api_sid='',
                api_token='your_api_token',
                verify_ssl_certs=True
            )

        self.assertIn('Invalid api_sid', str(context.exception))

    def test_api_requestor_initialization_without_api_token_raises_value_error(self):
        with self.assertRaises(ValueError) as context:
            api_requestor = APIRequestor(
                api_entry='https://api.example.com',
                api_version='v2',
                api_sid='your_api_sid',
                api_token='',
                verify_ssl_certs=True
            )

        self.assertIn('Invalid api_token', str(context.exception))

    def test_api_requestor_initialization_with_headers_returns_expected_data(self):
        api_requestor = APIRequestor(
            api_entry='https://api.example.com',
            api_version='v2',
            api_sid='your_api_sid',
            api_token='your_api_token',
            verify_ssl_certs=True
        )
        expected_headers = {
            'Accept-Encoding': 'gzip',
            'Accept-Language': 'en-US, en;q=0.9, pt-BR;q=0.8, pt;q=0.7',
            'Cache-control': 'no-cache',
            'Content-Type': 'application/json',
            'User-Agent': 'Everysk PythonBindings/v2',
            'Authorization': 'Bearer your_api_sid:your_api_token'
        }

        self.assertEqual(api_requestor.headers, expected_headers)

    def test_clean_response_without_expected_status_code_raises_api_error(self):
        api_requestor = APIRequestor(
            api_entry='https://api.example.com',
            api_version='v2',
            api_sid='your_api_sid',
            api_token='your_api_token',
            verify_ssl_certs=True,
        )
        with self.assertRaises(APIError) as context:
            api_requestor._clean_response(400, json.dumps('bad request'))

        self.assertIn('bad request', str(context.exception))

    def test_clean_response_with_expected_status_code_returns_expected_data(self):
        api_requestor = APIRequestor(
            api_entry='https://api.example.com',
            api_version='v2',
            api_sid='your_api_sid',
            api_token='your_api_token',
            verify_ssl_certs=True,
        )
        response = api_requestor._clean_response(200, json.dumps('ok'))

        self.assertEqual(response, 'ok')

    def test_api_requestor_get_method_returns_expected_response(self):
        with mock.patch('everysk.api.http_client.RequestsClient.request') as mock_request:
            mock_request.return_value = (200, json.dumps('ok'))
            response = self.api_requestor.get('/path', {'param': 'value'})

        self.assertEqual(response, 'ok')

    def test_api_requestor_post_method_returns_expected_response(self):
        with mock.patch('everysk.api.http_client.RequestsClient.request') as mock_request:
            mock_request.return_value = (200, json.dumps('ok'))
            response = self.api_requestor.post('/path', {'param': 'value'})

        self.assertEqual(response, 'ok')

    def test_api_requestor_put_method_returns_expected_response(self):
        with mock.patch('everysk.api.http_client.RequestsClient.request') as mock_request:
            mock_request.return_value = (200, json.dumps('ok'))
            response = self.api_requestor.put('/path', {'param': 'value'})

        self.assertEqual(response, 'ok')

    def test_api_requestor_delete_method_returns_expected_response(self):
        with mock.patch('everysk.api.http_client.RequestsClient.request') as mock_request:
            mock_request.return_value = (200, json.dumps('ok'))
            response = self.api_requestor.delete('/path')

        self.assertEqual(response, 'ok')
