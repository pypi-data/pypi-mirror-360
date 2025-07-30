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
from everysk.api.http_client import HTTPClient, RequestsClient, new_default_http_client
from everysk.core.object import BaseDict
from everysk.core.unittests import TestCase, mock


###############################################################################
#   HTTP Client Test Case Implementation
###############################################################################
class HTTPClientTestCase(TestCase):

    def test_initialization_with_default_values(self):
        client = HTTPClient()
        self.assertEqual(client.timeout, 3600)
        self.assertEqual(client.verify_ssl_certs, True)
        self.assertEqual(client.allow_redirects, False)

    def test_initialization_with_custom_values(self):
        client = HTTPClient(1000, False, True)
        self.assertEqual(client.timeout, 1000)
        self.assertEqual(client.verify_ssl_certs, False)
        self.assertEqual(client.allow_redirects, True)

    def test_request(self):
        client = HTTPClient()
        with self.assertRaises(NotImplementedError):
            client.request("GET", 'http://example.com', {})

###############################################################################
#   Requests Client TestCase Implementation
###############################################################################
class RequestsClientTestCase(TestCase):

    def test_request_method(self):
        expected_status_code = 200
        expected_content = 'Test Content'

        client = RequestsClient()
        with mock.patch('requests.request') as mock_request:
            mock_response = mock.Mock()
            mock_response.content = expected_content
            mock_response.status_code = expected_status_code
            mock_request.return_value = mock_response

            status_code, content = client.request("GET", "http://example.com", {})

        self.assertEqual(status_code, expected_status_code)
        self.assertEqual(content, expected_content)
        mock_request.assert_called_once_with(method="GET", url="http://example.com", headers={}, params=None, timeout=3600, verify=True, allow_redirects=False)

    def test_request_method_with_base_dict(self):
        expected_status_code = 200
        expected_content = 'Test Content'

        client = RequestsClient()
        with mock.patch('requests.request') as mock_request:
            mock_response = mock.Mock()
            mock_response.content = expected_content
            mock_response.status_code = expected_status_code
            mock_request.return_value = mock_response

            status_code, content = client.request("POST", "http://example.com", {}, {}, BaseDict(key='value'))

        self.assertEqual(status_code, expected_status_code)
        self.assertEqual(content, expected_content)
        mock_request.assert_called_once_with(method="POST", url="http://example.com", headers={}, params={}, data='{"key": "value"}', timeout=3600, verify=True, allow_redirects=False)

###############################################################################
#   Standard HTTP Client TestCase Implementation
###############################################################################
class StandardHTTPClientTestCase(TestCase):
    @mock.patch('everysk.api.http_client.RequestsClient')
    def test_new_default_http_client(self, mock_requests_client):
        timeout = 3000
        verify_ssl_certs = False
        allow_redirects = True
        client = new_default_http_client(timeout=timeout, verify_ssl_certs=verify_ssl_certs, allow_redirects=allow_redirects)

        mock_requests_client.assert_called_once_with(timeout=timeout, verify_ssl_certs=verify_ssl_certs, allow_redirects=allow_redirects)
        self.assertEqual(client, mock_requests_client.return_value)
