###############################################################################
#
# (C) Copyright 2025 EVERYSK TECHNOLOGIES
#
# This is an unpublished work containing confidential and proprietary
# information of EVERYSK TECHNOLOGIES. Disclosure, use, or reproduction
# without authorization of EVERYSK TECHNOLOGIES is prohibited.
#
###############################################################################
# pylint: disable=protected-access

from unittest import IsolatedAsyncioTestCase

import httpx
from starlette.testclient import TestClient

from everysk.config import settings
from everysk.core.compress import compress
from everysk.core.exceptions import HttpError
from everysk.core.serialize import dumps, loads
from everysk.core.unittests import TestCase, mock
from everysk.server.applications import create_application
from everysk.server.endpoints import BaseEndpoint, JSONEndpoint, HealthCheckEndpoint, RedirectEndpoint
from everysk.server.requests import Request, JSONRequest
from everysk.server.responses import Response
from everysk.server.routing import RouteLazy


class FakeEndpoint(BaseEndpoint):

    async def get(self):
        query_params = dict(self.request.query_params)
        if query_params.get('payload') == 'error':
            raise HttpError(status_code=400, msg='Bad Request')
        if query_params.get('payload') == 'error: log':
            raise HttpError(status_code=500, msg='Server error')

        return Response(query_params.get('payload'))

    async def post(self):
        payload = await self.get_http_payload()
        if payload == b'error':
            raise HttpError(status_code=400, msg='Bad Request')
        if payload == b'error: log':
            raise HttpError(status_code=500, msg='Server error')

        return Response(payload)


class BaseEndpointTestCase(TestCase):

    def setUp(self) -> None:
        self.scope = {
            'type': 'http',
            'http_version': '1.1',
            'method': 'POST',
            'scheme': 'http',
            'path': '/',
            'headers': [
                    (b'content-type', b'application/json'),
                    (b'user-agent', b'Everysk Test Agent'),
                    (b'host', b'localhost:8000'),
                ],
            'client': ('127.0.0.1', 49192),
            'server': ('127.0.0.1', 8000),
        }

        self.endpoint = FakeEndpoint(scope=self.scope, receive=None, send=None)

    def test_base_endpoint(self):
        endpoint = FakeEndpoint(scope={'type': 'http'}, receive=None, send=None)
        self.assertIsInstance(endpoint.request, Request)
        self.assertEqual(endpoint._allowed_methods, ['GET', 'POST'])

    def test_base_endpoint_not_http(self):
        with self.assertRaises(HttpError) as context:
            FakeEndpoint(scope={'type': 'websocket'}, receive=None, send=None)
        self.assertEqual(context.exception.status_code, 500)
        self.assertEqual(context.exception.msg, 'Request is not an HTTP request.')

    def test_get_headers(self):
        self.assertDictEqual(
            self.endpoint.get_http_headers(),
            {'content-type': 'application/json', 'host': 'localhost:8000', 'user-agent': 'Everysk Test Agent'}
        )

    def test_get_http_method_function(self):
        self.assertEqual(self.endpoint.get_http_method_function(), self.endpoint.post)

    def test_get_http_method_name(self):
        self.assertEqual(self.endpoint.get_http_method_name(), 'post')

    def test_get_http_method_name_head(self):
        self.endpoint.scope['method'] = 'HEAD'
        self.assertEqual(self.endpoint.get_http_method_name(), 'get')

    def test_make_response(self):
        endpoint = FakeEndpoint(scope={'type': 'http'}, receive=None, send=None)
        response = endpoint._make_response(status_code=200, content=b'Content')
        self.assertIsInstance(response, Response)
        self.assertIsNone(response._response_serializer)

    def test_make_response_serialize(self):
        endpoint = FakeEndpoint(scope={'type': 'http'}, receive=None, send=None)
        endpoint._response_serializer = 'json'
        response = endpoint._make_response(status_code=200, content=b'Content')
        self.assertIsInstance(response, Response)
        self.assertEqual(response._response_serializer, 'json')


class BaseEndpointTestCaseAsync(IsolatedAsyncioTestCase):

    def setUp(self) -> None:
        self.app = create_application(routes=[RouteLazy('/', FakeEndpoint)])
        self.client = TestClient(self.app)

    async def test_get_http_payload_get(self):
        response = self.client.get('/', params={'payload': 'payload'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'payload')

    async def test_get_http_payload_post(self):
        response = self.client.post('/', data='payload')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'payload')

    async def test_get_http_exception_response_get(self):
        response = self.client.get('/', params={'payload': 'error'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content, b'400 -> Bad Request')

    async def test_get_http_exception_response_post(self):
        response = self.client.post('/', data='error')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content, b'400 -> Bad Request')

    async def test_method_not_allowed(self):
        response = self.client.delete('/')
        self.assertEqual(response.status_code, 405)
        self.assertEqual(response.content, b'405 -> Method DELETE not allowed.')

    async def test_get_http_response(self):
        async def receive():
            return {'type': 'http.request', 'body': b''}

        endpoint = FakeEndpoint(scope={'type': 'http', 'method': 'POST'}, receive=receive, send=None)
        response = await endpoint.get_http_response()
        self.assertEqual(response.status_code, 200)

    async def test_dispatch(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'')

    async def test_dispatch_error(self):
        response = self.client.post('/', data='error')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content, b'400 -> Bad Request')

    @mock.patch('logging.Logger.log')
    async def test_dispatch_error_log_get(self, log: mock.MagicMock):
        response = self.client.get('/', params={'payload': 'error: log'})
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.content, b'500 -> Server error')
        log.assert_called_once_with(
            40,
            '500 -> Server error',
            extra={
                'labels': {},
                'traceback': (
                    'Traceback (most recent call last):\n'
                    '  File "/var/app/src/everysk/server/endpoints.py", line 131, in dispatch\n'
                    '    response = await self.get_http_response()\n'
                    '               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n'
                    '  File "/var/app/src/everysk/server/endpoints.py", line 176, in get_http_response\n'
                    '    response = await method_function()\n'
                    '               ^^^^^^^^^^^^^^^^^^^^^^^\n'
                    '  File "/var/app/src/everysk/server/_tests/endpoints.py", line 36, in get\n'
                    '    raise HttpError(status_code=500, msg=\'Server error\')\n'
                    'everysk.core.exceptions.HttpError: 500 -> Server error\n'
                ),
            },
            stacklevel=3
        )

    @mock.patch('logging.Logger.log')
    async def test_dispatch_error_log_post(self, log: mock.MagicMock):
        response = self.client.post('/', data='error: log')
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.content, b'500 -> Server error')
        log.assert_called_once_with(
            40,
            '500 -> Server error',
            extra={
                'http_payload': b'error: log',
                'labels': {},
                'traceback': (
                    'Traceback (most recent call last):\n'
                    '  File "/var/app/src/everysk/server/endpoints.py", line 131, in dispatch\n'
                    '    response = await self.get_http_response()\n'
                    '               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n'
                    '  File "/var/app/src/everysk/server/endpoints.py", line 176, in get_http_response\n'
                    '    response = await method_function()\n'
                    '               ^^^^^^^^^^^^^^^^^^^^^^^\n'
                    '  File "/var/app/src/everysk/server/_tests/endpoints.py", line 45, in post\n'
                    '    raise HttpError(status_code=500, msg=\'Server error\')\n'
                    'everysk.core.exceptions.HttpError: 500 -> Server error\n'
                ),
            },
            stacklevel=3
        )

    async def test_gzip_body(self):
        response = self.client.post('/', data=compress('Body', protocol='gzip', serialize=None), headers={'Content-Encoding': 'gzip'})
        self.assertEqual(response.content, b'Body')


class FakeJSONEndpoint(JSONEndpoint):

    async def get(self):
        query_params = dict(self.request.query_params)
        if query_params.get('payload') == 'error':
            raise HttpError(status_code=400, msg='Bad Request')
        if query_params.get('payload') == 'error: log':
            raise HttpError(status_code=500, msg='Server error')

        return {'payload': query_params.get('payload')}

    async def post(self):
        payload = await self.get_http_payload()

        if payload == 'error':
            raise HttpError(status_code=400, msg='Bad Request')
        if payload == 'error: log':
            raise HttpError(status_code=500, msg='Server error')

        return {'payload': payload}

class FakeJSONEndpointPublic(FakeJSONEndpoint):
    rest_key_name: str = None
    rest_key_value: str = None

class FakeJSONEndpointPrivate(FakeJSONEndpoint):
    rest_key_name: str = 'key'
    rest_key_value: str = '12345'


class JSONEndpointTestCase(TestCase):

    def test_json_endpoint(self):
        endpoint = FakeJSONEndpoint(scope={'type': 'http'}, receive=None, send=None)
        self.assertIsInstance(endpoint.request, JSONRequest)
        self.assertEqual(endpoint._allowed_methods, ['GET', 'POST'])
        self.assertEqual(endpoint.rest_key_name, settings.EVERYSK_SERVER_REST_KEY_NAME)
        self.assertEqual(endpoint.rest_key_value, settings.EVERYSK_SERVER_REST_KEY_VALUE)

    def test_check_rest_key_default(self):
        endpoint = FakeJSONEndpoint(scope={'type': 'http', 'headers': [(b'x-rest-key', b'12345')]}, receive=None, send=None)
        self.assertTrue(endpoint.check_rest_key())

    def test_check_rest_key_none(self):
        endpoint = FakeJSONEndpoint(scope={'type': 'http', 'headers': []}, receive=None, send=None)
        self.assertFalse(endpoint.check_rest_key())

    def test_check_rest_key_wrong(self):
        endpoint = FakeJSONEndpoint(scope={'type': 'http', 'headers': [(b'x-rest-key', b'54321')]}, receive=None, send=None)
        self.assertFalse(endpoint.check_rest_key())

    def test_check_rest_key_public_default(self):
        endpoint = FakeJSONEndpointPublic(scope={'type': 'http', 'headers': [(b'x-rest-key', b'12345')]}, receive=None, send=None)
        self.assertTrue(endpoint.check_rest_key())

    def test_check_rest_key_public_none(self):
        endpoint = FakeJSONEndpointPublic(scope={'type': 'http', 'headers': []}, receive=None, send=None)
        self.assertTrue(endpoint.check_rest_key())

    def test_check_rest_key_public_wrong(self):
        endpoint = FakeJSONEndpointPublic(scope={'type': 'http', 'headers': [(b'x-rest-key', b'54321')]}, receive=None, send=None)
        self.assertTrue(endpoint.check_rest_key())

    def test_check_rest_key_private_default(self):
        endpoint = FakeJSONEndpointPrivate(scope={'type': 'http', 'headers': [(b'x-rest-key', b'12345')]}, receive=None, send=None)
        self.assertFalse(endpoint.check_rest_key())

    def test_check_rest_key_private_none(self):
        endpoint = FakeJSONEndpointPrivate(scope={'type': 'http', 'headers': []}, receive=None, send=None)
        self.assertFalse(endpoint.check_rest_key())

    def test_check_rest_key_private_wrong(self):
        endpoint = FakeJSONEndpointPrivate(scope={'type': 'http', 'headers': [(b'x-rest-key', b'54321')]}, receive=None, send=None)
        self.assertFalse(endpoint.check_rest_key())

    def test_check_rest_key_private_custom(self):
        endpoint = FakeJSONEndpointPrivate(scope={'type': 'http', 'headers': [(b'key', b'12345')]}, receive=None, send=None)
        self.assertTrue(endpoint.check_rest_key())


class JSONEndpointTestCaseAsync(IsolatedAsyncioTestCase):

    def setUp(self) -> None:
        self.app = create_application(routes=[RouteLazy('/', FakeJSONEndpointPublic)])
        self.client = TestClient(self.app)

    async def test_request_response(self):
        data = dumps({'data': Undefined}, protocol='json', use_undefined=True)
        response = self.client.post('/', data=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'payload': {'data': {'__undefined__': None}}})

    async def test_get_http_payload_get(self):
        response = self.client.get('/', params={'payload': 'payload'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'{"payload":"payload"}')

    async def test_get_http_payload_post(self):
        response = self.client.post('/', json='payload')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'{"payload":"payload"}')

    async def test_get_http_exception_response_get(self):
        response = self.client.get('/', params={'payload': 'error'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content, b'{"error":"400 -> Bad Request","code":400,"trace_id":""}')

    async def test_get_http_exception_response_post(self):
        response = self.client.post('/', json='error')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content, b'{"error":"400 -> Bad Request","code":400,"trace_id":""}')

    async def test_method_not_allowed(self):
        response = self.client.delete('/')
        self.assertEqual(response.status_code, 405)
        self.assertEqual(response.content, b'{"error":"405 -> Method DELETE not allowed.","code":405,"trace_id":""}')

    async def test_get_http_response(self):
        async def receive():
            return {'type': 'http.request', 'body': b''}

        endpoint = FakeEndpoint(scope={'type': 'http', 'method': 'POST'}, receive=receive, send=None)
        response = await endpoint.get_http_response()
        self.assertEqual(response.status_code, 200)

    async def test_dispatch_get(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'{"payload":null}')

    async def test_dispatch_post(self):
        response = self.client.post('/')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content, b'{"error":"400 -> Invalid Payload","code":400,"trace_id":""}')

    async def test_dispatch_error(self):
        response = self.client.post('/', json='error')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content, b'{"error":"400 -> Bad Request","code":400,"trace_id":""}')

    async def test_get_http_payload_with_invalid_json_raises_exception(self):
        data = loads(dumps(''))

        result = self.client.post('/', data=data)

        self.assertEqual(result.content, b'{"error":"400 -> Invalid Payload","code":400,"trace_id":""}')
        self.assertEqual(result.status_code, 400)

    @mock.patch('logging.Logger.log')
    async def test_dispatch_error_log_get(self, log: mock.MagicMock):
        response = self.client.get('/', params={'payload': 'error: log'})
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.content, b'{"error":"500 -> Server error","code":500,"trace_id":""}')
        log.assert_called_once_with(
            40,
            '500 -> Server error',
            extra={
                'labels': {},
                'traceback': (
                    'Traceback (most recent call last):\n'
                    '  File "/var/app/src/everysk/server/endpoints.py", line 131, in dispatch\n'
                    '    response = await self.get_http_response()\n'
                    '               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n'
                    '  File "/var/app/src/everysk/server/endpoints.py", line 283, in get_http_response\n'
                    '    response = await super().get_http_response()\n'
                    '               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n'
                    '  File "/var/app/src/everysk/server/endpoints.py", line 176, in get_http_response\n'
                    '    response = await method_function()\n'
                    '               ^^^^^^^^^^^^^^^^^^^^^^^\n'
                    '  File "/var/app/src/everysk/server/_tests/endpoints.py", line 225, in get\n'
                    '    raise HttpError(status_code=500, msg=\'Server error\')\n'
                    'everysk.core.exceptions.HttpError: 500 -> Server error\n'
                ),
            },
            stacklevel=3
        )

    @mock.patch('logging.Logger.log')
    async def test_dispatch_error_log_post(self, log: mock.MagicMock):
        response = self.client.post('/', json='error: log')
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.content, b'{"error":"500 -> Server error","code":500,"trace_id":""}')
        log.assert_called_once_with(
            40,
            '500 -> Server error',
            extra={
                'http_payload': 'error: log',
                'labels': {},
                'traceback': (
                    'Traceback (most recent call last):\n'
                    '  File "/var/app/src/everysk/server/endpoints.py", line 131, in dispatch\n'
                    '    response = await self.get_http_response()\n'
                    '               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n'
                    '  File "/var/app/src/everysk/server/endpoints.py", line 283, in get_http_response\n'
                    '    response = await super().get_http_response()\n'
                    '               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n'
                    '  File "/var/app/src/everysk/server/endpoints.py", line 176, in get_http_response\n'
                    '    response = await method_function()\n'
                    '               ^^^^^^^^^^^^^^^^^^^^^^^\n'
                    '  File "/var/app/src/everysk/server/_tests/endpoints.py", line 235, in post\n'
                    '    raise HttpError(status_code=500, msg=\'Server error\')\n'
                    'everysk.core.exceptions.HttpError: 500 -> Server error\n'
                ),
            },
            stacklevel=3
        )

    @mock.patch('logging.Logger.log')
    async def test_dispatch_error_log_trace_get(self, log: mock.MagicMock):
        response = self.client.get('/', params={'payload': 'error: log'}, headers={'traceparent': '00-4bfa9e049143840bef864a7859f2e5df-1c6c592f9e46e3fb-01'})
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.content, b'{"error":"500 -> Server error","code":500,"trace_id":"projects/None/traces/4bfa9e049143840bef864a7859f2e5df"}')
        log.assert_called_once_with(
            40,
            '500 -> Server error',
            extra={
                'http_headers': {'traceparent': '00-4bfa9e049143840bef864a7859f2e5df-1c6c592f9e46e3fb-01'},
                'labels': {},
                'traceback': (
                    'Traceback (most recent call last):\n'
                    '  File "/var/app/src/everysk/server/endpoints.py", line 131, in dispatch\n'
                    '    response = await self.get_http_response()\n'
                    '               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n'
                    '  File "/var/app/src/everysk/server/endpoints.py", line 283, in get_http_response\n'
                    '    response = await super().get_http_response()\n'
                    '               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n'
                    '  File "/var/app/src/everysk/server/endpoints.py", line 176, in get_http_response\n'
                    '    response = await method_function()\n'
                    '               ^^^^^^^^^^^^^^^^^^^^^^^\n'
                    '  File "/var/app/src/everysk/server/_tests/endpoints.py", line 225, in get\n'
                    '    raise HttpError(status_code=500, msg=\'Server error\')\n'
                    'everysk.core.exceptions.HttpError: 500 -> Server error\n'
                ),
            },
            stacklevel=3
        )

    @mock.patch('logging.Logger.log')
    async def test_dispatch_error_log_trace_post(self, log: mock.MagicMock):
        response = self.client.post('/', json='error: log', headers={'traceparent': '00-4bfa9e049143840bef864a7859f2e5df-1c6c592f9e46e3fb-01'})
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.content, b'{"error":"500 -> Server error","code":500,"trace_id":"projects/None/traces/4bfa9e049143840bef864a7859f2e5df"}')
        log.assert_called_once_with(
            40,
            '500 -> Server error',
            extra={
                'http_headers': {'traceparent': '00-4bfa9e049143840bef864a7859f2e5df-1c6c592f9e46e3fb-01'},
                'http_payload': 'error: log',
                'labels': {},
                'traceback': (
                    'Traceback (most recent call last):\n'
                    '  File "/var/app/src/everysk/server/endpoints.py", line 131, in dispatch\n'
                    '    response = await self.get_http_response()\n'
                    '               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n'
                    '  File "/var/app/src/everysk/server/endpoints.py", line 283, in get_http_response\n'
                    '    response = await super().get_http_response()\n'
                    '               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n'
                    '  File "/var/app/src/everysk/server/endpoints.py", line 176, in get_http_response\n'
                    '    response = await method_function()\n'
                    '               ^^^^^^^^^^^^^^^^^^^^^^^\n'
                    '  File "/var/app/src/everysk/server/_tests/endpoints.py", line 235, in post\n'
                    '    raise HttpError(status_code=500, msg=\'Server error\')\n'
                    'everysk.core.exceptions.HttpError: 500 -> Server error\n'
                ),
            },
            stacklevel=3
        )

    async def test_gzip_body(self):
        response = self.client.post('/', data=compress('Body', protocol='gzip', serialize='json'), headers={'Content-Encoding': 'gzip'})
        self.assertEqual(response.content, b'{"payload":"Body"}')

    def test_json_serializer(self):
        endpoint = FakeJSONEndpoint(scope={'type': 'http'}, receive=None, send=None)
        response = endpoint._make_response(status_code=200, content={'key': 'value'})
        self.assertEqual(endpoint._response_serializer, 'json')
        self.assertEqual(response._response_serializer, 'json')
        self.assertEqual(response.render({'key': 'value'}), b'{"key":"value"}')

    def test_json_serializer_orjson(self):
        endpoint = FakeJSONEndpoint(scope={'type': 'http'}, receive=None, send=None)
        endpoint._response_serializer = 'orjson'
        response = endpoint._make_response(status_code=200, content={'key': float('NaN')})
        self.assertEqual(endpoint._response_serializer, 'orjson')
        self.assertEqual(response._response_serializer, 'orjson')
        self.assertEqual(response.render({'key': float('NaN')}), b'{"key":null}')


class HealthCheckEndpointTestCaseAsync(IsolatedAsyncioTestCase):

    def setUp(self) -> None:
        self.app = create_application(routes=[RouteLazy('/', HealthCheckEndpoint)])
        self.client = TestClient(self.app)

    async def test_health_check_get(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'{"status":"SENTA_A_PUA"}')

    async def test_health_check_post(self):
        response = self.client.post('/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'{"status":"SENTA_A_PUA"}')


class FakeRedirectEndpoint(RedirectEndpoint):
    host_url: str = 'https://www.example.com'


class RedirectEndpointTestCase(TestCase):

    def test_required_attributes(self):
        with self.assertRaises(ValueError) as context:
            RedirectEndpoint(scope={'type': 'http'}, receive=None, send=None)
        self.assertEqual(str(context.exception), 'host_url is required for redirect endpoint.')

    def test_get_host(self):
        endpoint = FakeRedirectEndpoint(scope={'type': 'http'}, receive=None, send=None)
        self.assertEqual(endpoint.get_host(), 'www.example.com')

    def test_get_timeout(self):
        endpoint = FakeRedirectEndpoint(scope={'type': 'http'}, receive=None, send=None)
        self.assertEqual(endpoint.get_timeout(), httpx.Timeout(timeout=30, read=endpoint.timeout))


class RedirectEndpointTestCaseAsync(IsolatedAsyncioTestCase):
    # pylint: disable=unnecessary-dunder-call

    def setUp(self) -> None:
        self.app = create_application(routes=[RouteLazy('/path', FakeRedirectEndpoint)])
        self.client = TestClient(self.app)

    @mock.patch('httpx.Client')
    async def test_redirect_get_text(self, client: mock.MagicMock):
        client.return_value.__enter__.return_value.get.return_value = httpx.Response(text='Text', status_code=200)
        response = self.client.get('/path?qs=1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers.get('content-type'), 'text/plain; charset=utf-8')
        self.assertEqual(response.content, b'"Text"')
        client.assert_has_calls([
            mock.call(headers={'host': 'www.example.com', 'accept': '*/*', 'accept-encoding': 'gzip, deflate', 'connection': 'keep-alive', 'user-agent': 'testclient'}),
            mock.call().__enter__(),
            mock.call().__enter__().get('https://www.example.com/path?qs=1', timeout=httpx.Timeout(connect=30, read=600, write=30, pool=30)),
            mock.call().__exit__(None, None, None)
        ])

    @mock.patch('httpx.Client')
    async def test_redirect_get_html(self, client: mock.MagicMock):
        client.return_value.__enter__.return_value.get.return_value = httpx.Response(html='<b>Text</b>', status_code=200)
        response = self.client.get('/path?qs=1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers.get('content-type'), 'text/html; charset=utf-8')
        self.assertEqual(response.content, b'"<b>Text</b>"')
        client.assert_has_calls([
            mock.call(headers={'host': 'www.example.com', 'accept': '*/*', 'accept-encoding': 'gzip, deflate', 'connection': 'keep-alive', 'user-agent': 'testclient'}),
            mock.call().__enter__(),
            mock.call().__enter__().get('https://www.example.com/path?qs=1', timeout=httpx.Timeout(connect=30, read=600, write=30, pool=30)),
            mock.call().__exit__(None, None, None)
        ])

    @mock.patch('httpx.Client')
    async def test_redirect_get_json(self, client: mock.MagicMock):
        client.return_value.__enter__.return_value.get.return_value = httpx.Response(json={'key': 'Text'}, status_code=200)
        response = self.client.get('/path?qs=1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers.get('content-type'), 'application/json')
        self.assertEqual(response.content, b'{"key": "Text"}')
        client.assert_has_calls([
            mock.call(headers={'host': 'www.example.com', 'accept': '*/*', 'accept-encoding': 'gzip, deflate', 'connection': 'keep-alive', 'user-agent': 'testclient'}),
            mock.call().__enter__(),
            mock.call().__enter__().get('https://www.example.com/path?qs=1', timeout=httpx.Timeout(connect=30, read=600, write=30, pool=30)),
            mock.call().__exit__(None, None, None)
        ])

    @mock.patch('httpx.Client')
    async def test_redirect_post_data_text(self, client: mock.MagicMock):
        client.return_value.__enter__.return_value.post.return_value = httpx.Response(text='Text', status_code=200)
        response = self.client.post('/path', data={'key': 'value'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers.get('content-type'), 'text/plain; charset=utf-8')
        self.assertEqual(response.content, b'"Text"')
        client.assert_has_calls([
            mock.call(headers={'host': 'www.example.com', 'accept': '*/*', 'accept-encoding': 'gzip, deflate', 'connection': 'keep-alive', 'user-agent': 'testclient', 'content-length': '9', 'content-type': 'application/x-www-form-urlencoded'}),
            mock.call().__enter__(),
            mock.call().__enter__().post('https://www.example.com/path', content=b'key=value', timeout=httpx.Timeout(connect=30, read=600, write=30, pool=30)),
            mock.call().__exit__(None, None, None)
        ])

    @mock.patch('httpx.Client')
    async def test_redirect_post_data_html(self, client: mock.MagicMock):
        client.return_value.__enter__.return_value.post.return_value = httpx.Response(html='<b>Text</b>', status_code=200)
        response = self.client.post('/path', data={'key': 'value'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers.get('content-type'), 'text/html; charset=utf-8')
        self.assertEqual(response.content, b'"<b>Text</b>"')
        client.assert_has_calls([
            mock.call(headers={'host': 'www.example.com', 'accept': '*/*', 'accept-encoding': 'gzip, deflate', 'connection': 'keep-alive', 'user-agent': 'testclient', 'content-length': '9', 'content-type': 'application/x-www-form-urlencoded'}),
            mock.call().__enter__(),
            mock.call().__enter__().post('https://www.example.com/path', content=b'key=value', timeout=httpx.Timeout(connect=30, read=600, write=30, pool=30)),
            mock.call().__exit__(None, None, None)
        ])

    @mock.patch('httpx.Client')
    async def test_redirect_post_data_json(self, client: mock.MagicMock):
        client.return_value.__enter__.return_value.post.return_value = httpx.Response(json={'key': 'Text'}, status_code=200)
        response = self.client.post('/path', data={'key': 'value'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers.get('content-type'), 'application/json')
        self.assertEqual(response.content, b'{"key": "Text"}')
        client.assert_has_calls([
            mock.call(headers={'host': 'www.example.com', 'accept': '*/*', 'accept-encoding': 'gzip, deflate', 'connection': 'keep-alive', 'user-agent': 'testclient', 'content-length': '9', 'content-type': 'application/x-www-form-urlencoded'}),
            mock.call().__enter__(),
            mock.call().__enter__().post('https://www.example.com/path', content=b'key=value', timeout=httpx.Timeout(connect=30, read=600, write=30, pool=30)),
            mock.call().__exit__(None, None, None)
        ])

    @mock.patch('httpx.Client')
    async def test_redirect_post_json_text(self, client: mock.MagicMock):
        client.return_value.__enter__.return_value.post.return_value = httpx.Response(text='Text', status_code=200)
        response = self.client.post('/path', json={'key': 'value'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers.get('content-type'), 'text/plain; charset=utf-8')
        self.assertEqual(response.content, b'"Text"')
        client.assert_has_calls([
            mock.call(headers={'host': 'www.example.com', 'accept': '*/*', 'accept-encoding': 'gzip, deflate', 'connection': 'keep-alive', 'user-agent': 'testclient', 'content-length': '16', 'content-type': 'application/json'}),
            mock.call().__enter__(),
            mock.call().__enter__().post('https://www.example.com/path', content=b'{"key": "value"}', timeout=httpx.Timeout(connect=30, read=600, write=30, pool=30)),
            mock.call().__exit__(None, None, None)
        ])

    @mock.patch('httpx.Client')
    async def test_redirect_post_json_html(self, client: mock.MagicMock):
        client.return_value.__enter__.return_value.post.return_value = httpx.Response(html='<b>Text</b>', status_code=200)
        response = self.client.post('/path', json={'key': 'value'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers.get('content-type'), 'text/html; charset=utf-8')
        self.assertEqual(response.content, b'"<b>Text</b>"')
        client.assert_has_calls([
            mock.call(headers={'host': 'www.example.com', 'accept': '*/*', 'accept-encoding': 'gzip, deflate', 'connection': 'keep-alive', 'user-agent': 'testclient', 'content-length': '16', 'content-type': 'application/json'}),
            mock.call().__enter__(),
            mock.call().__enter__().post('https://www.example.com/path', content=b'{"key": "value"}', timeout=httpx.Timeout(connect=30, read=600, write=30, pool=30)),
            mock.call().__exit__(None, None, None)
        ])

    @mock.patch('httpx.Client')
    async def test_redirect_post_json_json(self, client: mock.MagicMock):
        client.return_value.__enter__.return_value.post.return_value = httpx.Response(json={'key': 'Text'}, status_code=200)
        response = self.client.post('/path', json={'key': 'value'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers.get('content-type'), 'application/json')
        self.assertEqual(response.content, b'{"key": "Text"}')
        client.assert_has_calls([
            mock.call(headers={'host': 'www.example.com', 'accept': '*/*', 'accept-encoding': 'gzip, deflate', 'connection': 'keep-alive', 'user-agent': 'testclient', 'content-length': '16', 'content-type': 'application/json'}),
            mock.call().__enter__(),
            mock.call().__enter__().post('https://www.example.com/path', content=b'{"key": "value"}', timeout=httpx.Timeout(connect=30, read=600, write=30, pool=30)),
            mock.call().__exit__(None, None, None)
        ])
