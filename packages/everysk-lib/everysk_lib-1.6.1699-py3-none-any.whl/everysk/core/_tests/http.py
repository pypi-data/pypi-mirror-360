###############################################################################
#
# (C) Copyright 2023 EVERYSK TECHNOLOGIES
#
# This is an unpublished work containing confidential and proprietary
# information of EVERYSK TECHNOLOGIES. Disclosure, use, or reproduction
# without authorization of EVERYSK TECHNOLOGIES is prohibited.
#
###############################################################################
# pylint: disable=protected-access

import json
from os import environ
from everysk.config import settings
from everysk.core.compress import compress
from everysk.core.exceptions import HttpError, InvalidArgumentError
from everysk.core.http import (
    HttpConnection,
    HttpConnectionConfig,
    HttpGETConnection,
    HttpPOSTConnection,
    HttpPOSTCompressedConnection,
    HttpDELETEConnection,
    HttpHEADConnection,
    HttpOPTIONSConnection,
    HttpPATCHConnection,
    HttpPUTConnection,
    HttpSDKPOSTConnection,
    httpx,
    time,
    log
)
from everysk.core.log import LoggerManager
from everysk.core.object import BaseObjectConfig
from everysk.core.unittests import TestCase, mock


DEFAULT_HEADERS = {
    'Accept-Encoding': 'gzip',
    'Accept-Language': 'en-US, en;q=0.9, pt-BR;q=0.8, pt;q=0.7',
    'Cache-control': 'no-cache',
    'Content-Type': 'text/html; charset=UTF-8',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
}


class FakeResponse:
    # https://everysk.atlassian.net/browse/COD-1047
    def __bool__(self):
        return False


class HttpConnectionConfigTestCase(TestCase):

    def test_default_attributes(self):
        obj = HttpConnectionConfig()
        self.assertEqual(obj.retry_end_seconds, 30)
        self.assertEqual(obj.retry_limit, 5)
        self.assertEqual(obj.retry_start_seconds, 5)
        self.assertIsInstance(HttpConnection._config, HttpConnectionConfig)

    def test_get_ssl_verify(self):
        obj = HttpConnectionConfig()
        self.assertTrue(obj.get_ssl_verify())
        obj.ssl_verify = False
        self.assertFalse(obj.get_ssl_verify())

    def test_get_ssl_verify_environment(self):
        obj = HttpConnectionConfig()
        self.assertTrue(obj.get_ssl_verify())
        environ['HTTP_REQUESTS_VERIFY'] = 'False'
        self.assertFalse(obj.get_ssl_verify())
        obj.ssl_verify = False
        environ['HTTP_REQUESTS_VERIFY'] = 'True'
        self.assertTrue(obj.get_ssl_verify())
        environ.pop('HTTP_REQUESTS_VERIFY')

    def test_user_agent_list(self):
        obj = HttpConnectionConfig()
        with open(obj.user_agents_file, 'r', encoding='utf-8') as fd:
            user_agents = json.load(fd)

        self.assertListEqual(obj.user_agents, user_agents)

    def test_get_random_agent(self):
        obj = HttpConnectionConfig()
        self.assertIn(obj.get_random_agent(), obj.user_agents)
        self.assertNotEqual(obj.get_random_agent(), obj.get_random_agent())

    def test_inheritance(self):
        self.assertTrue(issubclass(HttpConnectionConfig, BaseObjectConfig))


class HttpConnectionTestCase(TestCase):

    def setUp(self) -> None:
        self.headers = DEFAULT_HEADERS.copy()

    def test_get_url(self):
        http = HttpConnection(url='https://test.com')
        self.assertEqual(http.url, 'https://test.com')
        self.assertEqual(http.get_url(), 'https://test.com')

    def test_clean_response_200(self):
        response = mock.MagicMock()
        response.status_code = 200
        http = HttpConnection()
        self.assertEqual(http._clean_response(response), response)

    def test_clean_response_201(self):
        response = mock.MagicMock()
        response.status_code = 201
        http = HttpConnection()
        self.assertEqual(http._clean_response(response), response)

    def test_clean_response_202(self):
        response = mock.MagicMock()
        response.status_code = 200
        http = HttpConnection()
        self.assertEqual(http._clean_response(response), response)

    def test_clean_response_303(self):
        response = mock.MagicMock()
        response.status_code = 303
        http = HttpConnection()
        self.assertEqual(http._clean_response(response), response)

    def test_clean_response_500(self):
        response = mock.MagicMock()
        response.status_code = 500
        http = HttpConnection()
        self.assertRaises(HttpError, http._clean_response, response)

    def test_clean_without_status_code(self):
        # https://everysk.atlassian.net/browse/COD-1047
        response = FakeResponse()
        self.assertFalse(response)
        http = HttpConnection()
        http._clean_response(response)

    def test_get_headers(self):
        http = HttpConnection()
        self.assertDictEqual(http.get_headers(), self.headers)

    def test_get_headers_attribute(self):
        http = HttpConnection(headers={'key': 'value'})
        self.headers.update({'key': 'value'})
        self.assertDictEqual(http.get_headers(), self.headers)

    def test_gcp_headers(self):
        http = HttpConnection()
        self.assertDictEqual(http._get_headers(), self.headers)

    def test_gcp_headers_with_manager_traceparent(self):
        header = {'traceparent': '00-4bfa9e049143840bef864a7859f2e5df-1c6c592f9e46e3fb-01'}
        http = HttpConnection()
        self.headers.update(header)
        with LoggerManager(http_headers=header):
            self.assertDictEqual(http._get_headers(), self.headers)

    def test_gcp_headers_with_manager_x_cloud_trace_context(self):
        header = {'x-cloud-trace-context': '4bfa9e049143840bef864a7859f2e5df/2048109991600514043;o=1'}
        http = HttpConnection()
        self.headers.update(header)
        with LoggerManager(http_headers=header):
            self.assertDictEqual(http._get_headers(), self.headers)

    def test_get_random_agent(self):
        obj = HttpConnection()
        self.assertEqual(obj.get_headers()['User-Agent'], obj.get_headers()['User-Agent'])
        with mock.patch('os.environ', {'HTTP_USE_RANDOM_USER_AGENT': 1}):
            self.assertNotEqual(obj.get_headers()['User-Agent'], obj.get_headers()['User-Agent'])

    def test_message_error_check(self):
        self.assertFalse(HttpConnection().message_error_check('text', 500))

    def test_get_response_from_url(self):
        self.assertIsNone(HttpConnection()._get_response_from_url())

    @mock.patch.object(HttpConnection, '_clean_response', return_value='response')
    def test_get_response(self, _clean_response: mock.MagicMock):
        self.assertEqual(HttpConnection().get_response(), 'response')
        _clean_response.assert_called_once_with(None)

    @mock.patch.object(HttpConnection, '_clean_response', side_effect=HttpError('Error'))
    @mock.patch.object(HttpConnection, 'message_error_check', return_value=True)
    @mock.patch.object(time, 'sleep')
    def test_get_response_error(
        self, sleep: mock.MagicMock, message_error_check: mock.MagicMock, _clean_response: mock.MagicMock
    ):
        self.assertRaises(HttpError, HttpConnection().get_response)
        self.assertEqual(sleep.call_count, 4)
        self.assertEqual(message_error_check.call_count, 5)
        self.assertEqual(_clean_response.call_count, 5)

    @mock.patch.object(HttpConnection._config, 'get_client')
    def test_manager(self, get_client: mock.MagicMock):
        client = mock.MagicMock(spec=httpx.Client)
        get_client.return_value = client
        with HttpConnection() as conn:
            self.assertEqual(conn._client, client)

        get_client.return_value.close.assert_called_once()
        self.assertIsNone(conn._client)

    @mock.patch.object(HttpConnection._config, 'get_client')
    def test_manager_with_params(self, get_client: mock.MagicMock):
        client = mock.MagicMock(spec=httpx.Client)
        get_client.return_value = client
        with HttpConnection() as conn:
            conn(url='https://test.com', headers={'key': 'value'})
            self.assertEqual(conn.url, 'https://test.com')
            self.assertDictEqual(conn.headers, {'key': 'value'})

        get_client.return_value.close.assert_called_once()
        self.assertIsNone(conn._client)

    @mock.patch.object(HttpConnection, '_clean_response', mock.MagicMock(side_effect=HttpError('Error')))
    @mock.patch.object(HttpConnection, 'message_error_check', mock.MagicMock(return_value=True))
    @mock.patch.object(time, 'sleep', mock.MagicMock())
    @mock.patch.dict('os.environ', {'EVERYSK_HTTP_LOG_RETRY': '1'})
    @mock.patch.object(log, 'debug')
    def test_get_response_retry_log(self, debug: mock.MagicMock):
        self.assertRaises(HttpError, HttpConnection(url='http://localhost').get_response)
        debug.assert_has_calls([
            mock.call('Retry: http://localhost - 500 -> error.'),
            mock.call('Retry: http://localhost - 500 -> error.'),
            mock.call('Retry: http://localhost - 500 -> error.'),
            mock.call('Retry: http://localhost - 500 -> error.')
        ])


class HttpGETConnectionTestCase(TestCase):

    def setUp(self) -> None:
        self.headers = DEFAULT_HEADERS.copy()
        self.old_get = httpx.Client.get
        self.response = mock.MagicMock()
        self.response.status_code = 200
        httpx.Client.get = mock.MagicMock()
        httpx.Client.get.return_value = self.response

    def tearDown(self) -> None:
        httpx.Client.get = self.old_get

    def test_get_params(self):
        http = HttpGETConnection(url='https://test.com')

        self.assertIsNone(http.get_params())
        http.params = {'key': 'value'}
        self.assertDictEqual(http.get_params(), {'key': 'value'})

    def test_get_request_params(self):
        http = HttpGETConnection(url='https://test.com')
        self.assertDictEqual(http.get_request_params(), {
            'url': 'https://test.com',
            'headers': self.headers,
            'params': None,
            'timeout': httpx.Timeout(timeout=30)
        })
        self.assertIsNone(http.get_params()) # get_request_params() doesn't affect http.params

    def test_get_response(self):
        http = HttpGETConnection(url='https://test.com', params={'p1': 1, 'p2': 2})
        response = http.get_response()
        httpx.Client.get.assert_called_once_with( # pylint: disable=no-member
            url='https://test.com',
            headers=self.headers,
            params={'p1': 1, 'p2': 2},
            timeout=http.get_timeout()
        )
        self.assertEqual(response, httpx.Client.get.return_value) # pylint: disable=no-member

    def test_get_response_with_gcp_headers(self):
        header = {'traceparent': '00-4bfa9e049143840bef864a7859f2e5df-1c6c592f9e46e3fb-01'}
        http = HttpGETConnection(url='https://test.com')
        self.headers.update(header)
        with LoggerManager(http_headers=header):
            response = http.get_response()

        httpx.Client.get.assert_called_once_with( # pylint: disable=no-member
            url='https://test.com',
            headers=self.headers,
            params=None,
            timeout=http.get_timeout()
        )
        self.assertEqual(response, httpx.Client.get.return_value) # pylint: disable=no-member

    def test_user(self):
        http = HttpGETConnection(
            url='https://test.com',
            params={'p1': 1, 'p2': 2},
            user='user',
            password='pass'
        )
        response = http.get_response()
        httpx.Client.get.assert_called_once_with( # pylint: disable=no-member
            url='https://test.com',
            headers=self.headers,
            params={'p1': 1, 'p2': 2},
            timeout=http.get_timeout(),
            auth=('user', 'pass')
        )
        self.assertEqual(response, httpx.Client.get.return_value) # pylint: disable=no-member

    @mock.patch.object(log, 'debug')
    def test_http_log_response(self, debug: mock.MagicMock):
        http = HttpGETConnection(url='https://test.com', params={'p1': 1, 'p2': 2}, user='user', password='pass')
        settings.EVERYSK_HTTP_LOG_RESPONSE = True
        response = http.get_response()
        settings.EVERYSK_HTTP_LOG_RESPONSE = False
        debug.assert_has_calls([
            mock.call('HTTP %s request: %s', 'GET', 'https://test.com', extra={'labels': {'url': 'https://test.com', 'headers': self.headers, 'params': {'p1': 1, 'p2': 2}, 'timeout': http.get_timeout(), 'auth': ('user', '***********')}}),
            mock.call('HTTP %s response: %s', 'GET', 'https://test.com', extra={'labels': {'status_code': 200, 'time': self.response.elapsed.total_seconds.return_value, 'headers': self.response.headers, 'content': self.response.content}})
        ])
        self.assertEqual(response, httpx.Client.get.return_value) # pylint: disable=no-member

    @mock.patch.object(HttpGETConnection._config, 'get_client')
    def test_manager_with_params(self, get_client: mock.MagicMock):
        client = mock.MagicMock(spec=httpx.Client)
        client.is_closed = False
        get_client.return_value = client
        with HttpGETConnection() as conn:
            conn(url='https://test.com', params={'key': 'value'})._get_response_from_url()
            self.assertEqual(conn.url, 'https://test.com')
            self.assertDictEqual(conn.params, {'key': 'value'})

        get_client.return_value.get.assert_called_once_with(
            url='https://test.com',
            headers=DEFAULT_HEADERS,
            params={'key': 'value'},
            timeout=httpx.Timeout(timeout=30)
        )
        get_client.return_value.close.assert_called_once()
        self.assertIsNone(conn._client)

class HttpPOSTConnectionTestCase(TestCase):

    def setUp(self) -> None:
        self.headers = DEFAULT_HEADERS.copy()
        self.headers.update({'Content-Type': 'application/json; charset=utf-8'})
        self.old_post = httpx.Client.post
        self.response = mock.MagicMock()
        self.response.status_code = 200
        httpx.Client.post = mock.MagicMock()
        httpx.Client.post.return_value = self.response

    def tearDown(self) -> None:
        httpx.Client.post = self.old_post

    def test_get_headers(self):
        http = HttpPOSTConnection(url='https://test.com')
        self.assertDictEqual(http._get_headers(), DEFAULT_HEADERS)

    def test_get_payload(self):
        http = HttpPOSTConnection(url='https://test.com')
        self.assertIsNone(http.get_payload())
        http.payload = {'key': 'value'}
        self.assertDictEqual(http.get_payload(), {'key': 'value'})

    def test_get_request_params(self):
        http = HttpPOSTConnection(url='https://test.com')
        http.payload = {'key': 'value'}

        self.assertDictEqual(http.get_request_params(), {
            'url': 'https://test.com',
            'headers': self.headers,
            'timeout': httpx.Timeout(timeout=30),
            'json': {'key': 'value'}
        })

    def test_get_response(self):
        http = HttpPOSTConnection(url='https://test.com', payload={'p1': 1, 'p2': 2})
        response = http.get_response()
        httpx.Client.post.assert_called_once_with( # pylint: disable=no-member
            headers=self.headers,
            json={'p1': 1, 'p2': 2},
            url='https://test.com',
            timeout=http.get_timeout()
        )
        self.assertEqual(response, httpx.Client.post.return_value) # pylint: disable=no-member

    def test_post_not_json(self):
        http = HttpPOSTConnection(url='https://test.com', is_json=False, payload={'p1': 1, 'p2': 2})
        self.headers.update({'Content-Type': 'application/x-www-form-urlencoded'})
        response = http.get_response()
        httpx.Client.post.assert_called_once_with( # pylint: disable=no-member
            headers=self.headers,
            data={'p1': 1, 'p2': 2},
            url='https://test.com',
            timeout=http.get_timeout()
        )

        self.assertEqual(response, httpx.Client.post.return_value) # pylint: disable=no-member

    @mock.patch.object(log, 'debug')
    def test_http_log_response(self, debug: mock.MagicMock):
        http = HttpPOSTConnection(url='https://test.com', is_json=False, payload={'p1': 1, 'p2': 2})
        self.headers.update({'Content-Type': 'application/x-www-form-urlencoded'})
        settings.EVERYSK_HTTP_LOG_RESPONSE = True
        response = http.get_response()
        settings.EVERYSK_HTTP_LOG_RESPONSE = False
        debug.assert_has_calls([
            mock.call('HTTP %s request: %s', 'POST', 'https://test.com', extra={'labels': {'url': 'https://test.com', 'headers': self.headers, 'data': {'p1': 1, 'p2': 2}, 'timeout': http.get_timeout()}}),
            mock.call('HTTP %s response: %s', 'POST', 'https://test.com', extra={'labels': {'status_code': 200, 'time': self.response.elapsed.total_seconds.return_value, 'headers': self.response.headers, 'content': self.response.content}})
        ])
        self.assertEqual(response, httpx.Client.post.return_value) # pylint: disable=no-member

    @mock.patch.object(HttpPOSTConnection._config, 'get_client')
    def test_manager_with_params(self, get_client: mock.MagicMock):
        client = mock.MagicMock(spec=httpx.Client)
        client.is_closed = False
        get_client.return_value = client
        with HttpPOSTConnection() as conn:
            conn(url='https://test.com', payload={'key': 'value'})._get_response_from_url()
            self.assertEqual(conn.url, 'https://test.com')
            self.assertDictEqual(conn.payload, {'key': 'value'})

        headers = DEFAULT_HEADERS.copy()
        headers.update({'Content-Type': 'application/json; charset=utf-8'})
        get_client.return_value.post.assert_called_once_with(
            url='https://test.com',
            headers=headers,
            json={'key': 'value'},
            timeout=httpx.Timeout(timeout=30)
        )
        get_client.return_value.close.assert_called_once()
        self.assertIsNone(conn._client)

    def test_headers_and_payload(self):
        # https://everysk.atlassian.net/browse/COD-10307
        class PostSelf(HttpPOSTConnection):
            headers: dict = {'header': 'teste'}
            payload: dict = {'body': 'teste'}

        class PostMethod(HttpPOSTConnection):

            def get_headers(self):
                headers = super().get_headers()
                headers['header'] = 'teste'
                return headers

            def get_payload(self):
                return {'body': 'teste'}

        params = {
            'headers': {
                'Accept-Encoding': 'gzip',
                'Accept-Language': 'en-US, en;q=0.9, pt-BR;q=0.8, pt;q=0.7',
                'Cache-control': 'no-cache',
                'Content-Type': 'application/json; charset=utf-8',
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
                'header': 'teste'
            },
            'json': {'body': 'teste'},
            'timeout': httpx.Timeout(timeout=30),
            'url': None
        }
        # JSON
        obj = PostSelf(is_json=True)
        self.assertDictEqual(obj.get_request_params(), params)

        obj = PostMethod(is_json=True)
        self.assertDictEqual(obj.get_request_params(), params)

        # FormData
        params['headers']['Content-Type'] = 'application/x-www-form-urlencoded'
        params['data'] = params.pop('json')
        obj = PostSelf(is_json=False)
        self.assertDictEqual(obj.get_request_params(), params)

        obj = PostMethod(is_json=False)
        self.assertDictEqual(obj.get_request_params(), params)

    def test_keep_content_type_from_class(self):
        # https://everysk.atlassian.net/browse/COD-10307
        class PostSelf(HttpPOSTConnection):
            headers: dict = {'Content-Type': 'teste/bla'}
            payload: dict = {'body': 'teste'}

        class PostMethod(HttpPOSTConnection):

            def get_headers(self):
                headers = super().get_headers()
                headers['Content-Type'] = 'teste/bla'
                return headers

            def get_payload(self):
                return {'body': 'teste'}

        params = {
            'headers': {
                'Accept-Encoding': 'gzip',
                'Accept-Language': 'en-US, en;q=0.9, pt-BR;q=0.8, pt;q=0.7',
                'Cache-control': 'no-cache',
                'Content-Type': 'teste/bla',
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
            },
            'json': {'body': 'teste'},
            'timeout': httpx.Timeout(timeout=30),
            'url': None
        }
        # JSON
        obj = PostSelf(is_json=True)
        self.assertDictEqual(obj.get_request_params(), params)

        obj = PostMethod(is_json=True)
        self.assertDictEqual(obj.get_request_params(), params)

        # FormData
        params['data'] = params.pop('json')
        obj = PostSelf(is_json=False)
        self.assertDictEqual(obj.get_request_params(), params)

        obj = PostMethod(is_json=False)
        self.assertDictEqual(obj.get_request_params(), params)


class HttpSDKPOSTConnectionTestCase(TestCase):

    def setUp(self) -> None:
        self.headers = DEFAULT_HEADERS.copy()
        self.old_post = httpx.Client.post
        response = mock.MagicMock()
        response.status_code = 200
        httpx.Client.post = mock.MagicMock()
        httpx.Client.post.return_value = response
        settings.EVERYSK_API_SID = 'SID'
        settings.EVERYSK_API_TOKEN = 'TOKEN'
        self.class_name = 'class_name'
        self.method_name = 'method_name'
        self.self_obj = 'self_obj'
        self.param = 'params'

    def tearDown(self) -> None:
        httpx.Client.post = self.old_post

    def test_init_without_url(self):
        http = HttpSDKPOSTConnection()
        self.assertIsNone(http.url)
        self.assertEqual(http.get_url(), 'https://api.everysk.com/v1/sdk_function')

    def test_get_headers_without_SID(self):
        settings.EVERYSK_API_SID = None
        http = HttpSDKPOSTConnection()
        with self.assertRaisesRegex(InvalidArgumentError, 'Invalid API SID'):
            http._get_headers()

    def test_get_headers_without_token(self):
        settings.EVERYSK_API_TOKEN = None
        http = HttpSDKPOSTConnection()
        with self.assertRaisesRegex(InvalidArgumentError, 'Invalid API TOKEN'):
            http._get_headers()

    def test_get_headers(self):
        http = HttpSDKPOSTConnection(url='https://test.com')
        self.headers.update({'Authorization': 'Bearer SID:TOKEN', 'Content-Type': 'text/html; charset=UTF-8', 'Content-Encoding': 'gzip'})
        self.assertDictEqual(http._get_headers(), self.headers)

    def test_get_payload(self):
        http = HttpSDKPOSTConnection(url='https://test.com', class_name='class_name', method_name='method_name', self_obj={'self_obj': 'obj'}, params={})
        self.assertEqual(http.get_payload(), compress({'class_name': 'class_name', 'method_name': 'method_name', 'self_obj': {'self_obj': 'obj'}, 'params': {}}, protocol='gzip', serialize='json'))

    def test_get_url(self):
        http = HttpSDKPOSTConnection()
        expected_url = f'{settings.EVERYSK_SDK_URL}/{settings.EVERYSK_SDK_VERSION}/{settings.EVERYSK_SDK_ROUTE}'
        ret = http.get_url()

        self.assertEqual(ret, expected_url)

class HttpPOSTCompressedConnectionTestCase(TestCase):

    def test_get_payload(self):
        http = HttpPOSTCompressedConnection(url='https://test.com', payload={'p1': 1, 'p2': 2})
        self.assertEqual(http.get_payload(),  compress({'p1': 1, 'p2': 2}, protocol='gzip', serialize='json'))

class HttpDELETEConnectionTestCase(TestCase):

    def setUp(self) -> None:
        self.headers = DEFAULT_HEADERS.copy()
        self.old_delete = httpx.Client.delete
        self.response = mock.MagicMock()
        self.response.status_code = 200
        httpx.Client.delete = mock.MagicMock()
        httpx.Client.delete.return_value = self.response

    def tearDown(self) -> None:
        httpx.Client.delete = self.old_delete

    def test_get_response(self):
        http = HttpDELETEConnection(url='https://test.com')
        response = http.get_response()
        httpx.Client.delete.assert_called_once_with( # pylint: disable=no-member
            url='https://test.com',
            headers=self.headers,
            params=http.get_params(),
            timeout=http.get_timeout()
        )
        self.assertEqual(response, httpx.Client.delete.return_value) # pylint: disable=no-member

    @mock.patch.object(log, 'debug')
    def test_http_log_response(self, debug: mock.MagicMock):
        http = HttpDELETEConnection(url='https://test.com', params={'p1': 1, 'p2': 2}, user='user', password='pass')
        settings.EVERYSK_HTTP_LOG_RESPONSE = True
        response = http.get_response()
        settings.EVERYSK_HTTP_LOG_RESPONSE = False
        debug.assert_has_calls([
            mock.call('HTTP %s request: %s', 'DELETE', 'https://test.com', extra={'labels': {'url': 'https://test.com', 'headers': self.headers, 'params': {'p1': 1, 'p2': 2}, 'timeout': http.get_timeout(), 'auth': ('user', '***********')}}),
            mock.call('HTTP %s response: %s', 'DELETE', 'https://test.com', extra={'labels': {'status_code': 200, 'time': self.response.elapsed.total_seconds.return_value, 'headers': self.response.headers, 'content': self.response.content}})
        ])
        self.assertEqual(response, httpx.Client.delete.return_value) # pylint: disable=no-member


class HttpHEADConnectionTestCase(TestCase):
    def setUp(self) -> None:
        self.headers = DEFAULT_HEADERS.copy()
        self.old_head = httpx.Client.head
        self.response = mock.MagicMock()
        self.response.status_code = 200
        httpx.Client.head = mock.MagicMock()
        httpx.Client.head.return_value = self.response

    def tearDown(self) -> None:
        httpx.Client.head = self.old_head

    def test_get_response(self):
        http = HttpHEADConnection(url='https://test.com')
        response = http.get_response()
        httpx.Client.head.assert_called_once_with( # pylint: disable=no-member
            url='https://test.com',
            headers=self.headers,
            params=http.get_params(),
            timeout=http.get_timeout()
        )
        self.assertEqual(response, httpx.Client.head.return_value) # pylint: disable=no-member

    @mock.patch.object(log, 'debug')
    def test_http_log_response(self, debug: mock.MagicMock):
        http = HttpHEADConnection(url='https://test.com', params={'p1': 1, 'p2': 2}, user='user', password='pass')
        settings.EVERYSK_HTTP_LOG_RESPONSE = True
        response = http.get_response()
        settings.EVERYSK_HTTP_LOG_RESPONSE = False
        debug.assert_has_calls([
            mock.call('HTTP %s request: %s', 'HEAD', 'https://test.com', extra={'labels': {'url': 'https://test.com', 'headers': self.headers, 'params': {'p1': 1, 'p2': 2}, 'timeout': http.get_timeout(), 'auth': ('user', '***********')}}),
            mock.call('HTTP %s response: %s', 'HEAD', 'https://test.com', extra={'labels': {'status_code': 200, 'time': self.response.elapsed.total_seconds.return_value, 'headers': self.response.headers, 'content': self.response.content}})
        ])
        self.assertEqual(response, httpx.Client.head.return_value) # pylint: disable=no-member

class HttpOPTIONSConnectionTestCase(TestCase):
    def setUp(self) -> None:
        self.headers = DEFAULT_HEADERS.copy()
        self.old_options = httpx.Client.options
        self.response = mock.MagicMock()
        self.response.status_code = 200
        httpx.Client.options = mock.MagicMock()
        httpx.Client.options.return_value = self.response

    def tearDown(self) -> None:
        httpx.Client.options = self.old_options

    def test_get_response(self):
        http = HttpOPTIONSConnection(url='https://test.com')
        response = http.get_response()
        httpx.Client.options.assert_called_once_with( # pylint: disable=no-member
            url='https://test.com',
            headers=self.headers,
            params=http.get_params(),
            timeout=http.get_timeout()
        )
        self.assertEqual(response, httpx.Client.options.return_value) # pylint: disable=no-member

    @mock.patch.object(log, 'debug')
    def test_http_log_response(self, debug: mock.MagicMock):
        http = HttpOPTIONSConnection(url='https://test.com', params={'p1': 1, 'p2': 2}, user='user', password='pass')
        settings.EVERYSK_HTTP_LOG_RESPONSE = True
        response = http.get_response()
        settings.EVERYSK_HTTP_LOG_RESPONSE = False
        debug.assert_has_calls([
            mock.call('HTTP %s request: %s', 'OPTIONS', 'https://test.com', extra={'labels': {'url': 'https://test.com', 'headers': self.headers, 'params': {'p1': 1, 'p2': 2}, 'timeout': http.get_timeout(), 'auth': ('user', '***********')}}),
            mock.call('HTTP %s response: %s', 'OPTIONS', 'https://test.com', extra={'labels': {'status_code': 200, 'time': self.response.elapsed.total_seconds.return_value, 'headers': self.response.headers, 'content': self.response.content}})
        ])
        self.assertEqual(response, httpx.Client.options.return_value) # pylint: disable=no-member

class HttpPATCHConnectionTestCase(TestCase):

    def setUp(self) -> None:
        self.headers = DEFAULT_HEADERS.copy()
        self.headers.update({'Content-Type': 'application/json; charset=utf-8'})
        self.old_patch = httpx.Client.patch
        self.response = mock.MagicMock()
        self.response.status_code = 200
        httpx.Client.patch = mock.MagicMock()
        httpx.Client.patch.return_value = self.response

    def tearDown(self) -> None:
        httpx.Client.patch = self.old_patch

    def test_get_response(self):
        http = HttpPATCHConnection(url='https://test.com', payload={'p1': 1, 'p2': 2})
        response = http.get_response()
        httpx.Client.patch.assert_called_once_with( # pylint: disable=no-member
            headers=self.headers,
            json={'p1': 1, 'p2': 2},
            url='https://test.com',
            timeout=http.get_timeout()
        )
        self.assertEqual(response, httpx.Client.patch.return_value) # pylint: disable=no-member

    @mock.patch.object(log, 'debug')
    def test_http_log_response(self, debug: mock.MagicMock):
        http = HttpPATCHConnection(url='https://test.com', is_json=False, payload={'p1': 1, 'p2': 2})
        self.headers.update({'Content-Type': 'application/x-www-form-urlencoded'})
        settings.EVERYSK_HTTP_LOG_RESPONSE = True
        response = http.get_response()
        settings.EVERYSK_HTTP_LOG_RESPONSE = False
        debug.assert_has_calls([
            mock.call('HTTP %s request: %s', 'PATCH', 'https://test.com', extra={'labels': {'url': 'https://test.com', 'headers': self.headers, 'data': {'p1': 1, 'p2': 2}, 'timeout': http.get_timeout()}}),
            mock.call('HTTP %s response: %s', 'PATCH', 'https://test.com', extra={'labels': {'status_code': 200, 'time': self.response.elapsed.total_seconds.return_value, 'headers': self.response.headers, 'content': self.response.content}})
        ])
        self.assertEqual(response, httpx.Client.patch.return_value) # pylint: disable=no-member

class HttpPUTConnectionTestCase(TestCase):

    def setUp(self) -> None:
        self.headers = DEFAULT_HEADERS.copy()
        self.headers.update({'Content-Type': 'application/json; charset=utf-8'})
        self.old_put = httpx.Client.put
        self.response = mock.MagicMock()
        self.response.status_code = 200
        httpx.Client.put = mock.MagicMock()
        httpx.Client.put.return_value = self.response

    def tearDown(self) -> None:
        httpx.Client.put = self.old_put


    def test_get_response(self):
        http = HttpPUTConnection(url='https://test.com', payload={'p1': 1, 'p2': 2})
        response = http.get_response()
        httpx.Client.put.assert_called_once_with( # pylint: disable=no-member
            headers=self.headers,
            json={'p1': 1, 'p2': 2},
            url='https://test.com',
            timeout=http.get_timeout()
        )
        self.assertEqual(response, httpx.Client.put.return_value) # pylint: disable=no-member


    @mock.patch.object(log, 'debug')
    def test_http_log_response(self, debug: mock.MagicMock):
        http = HttpPUTConnection(url='https://test.com', is_json=False, payload={'p1': 1, 'p2': 2})
        self.headers.update({'Content-Type': 'application/x-www-form-urlencoded'})
        settings.EVERYSK_HTTP_LOG_RESPONSE = True
        response = http.get_response()
        settings.EVERYSK_HTTP_LOG_RESPONSE = False
        debug.assert_has_calls([
            mock.call('HTTP %s request: %s', 'PUT', 'https://test.com', extra={'labels': {'url': 'https://test.com', 'headers': self.headers, 'data': {'p1': 1, 'p2': 2}, 'timeout': http.get_timeout()}}),
            mock.call('HTTP %s response: %s', 'PUT', 'https://test.com', extra={'labels': {'status_code': 200, 'time': self.response.elapsed.total_seconds.return_value, 'headers': self.response.headers, 'content': self.response.content}})
        ])
        self.assertEqual(response, httpx.Client.put.return_value) # pylint: disable=no-member
