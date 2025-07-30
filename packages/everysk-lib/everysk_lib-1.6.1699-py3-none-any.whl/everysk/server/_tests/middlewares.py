###############################################################################
#
# (C) Copyright 2025 EVERYSK TECHNOLOGIES
#
# This is an unpublished work containing confidential and proprietary
# information of EVERYSK TECHNOLOGIES. Disclosure, use, or reproduction
# without authorization of EVERYSK TECHNOLOGIES is prohibited.
#
###############################################################################
from unittest import IsolatedAsyncioTestCase
from starlette.testclient import TestClient

from everysk.core.unittests import TestCase, mock
from everysk.server.applications import create_application
from everysk.server.endpoints import BaseEndpoint
from everysk.server.middlewares import (
    BaseHTTPMiddleware,
    GZipMiddleware,
    Middleware,
    SecurityHeadersMiddleware,
    update_with_default_middlewares
)
from everysk.server.responses import Response
from everysk.server.routing import RouteLazy


class FakeMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request, call_next):
        return await call_next(request)


class UpdateMiddlewaresTestCase(TestCase):

    def test_update_with_default_middlewares_none(self):
        middlewares = update_with_default_middlewares(None)
        self.assertEqual(len(middlewares), 2)
        self.assertEqual(middlewares[0].cls, GZipMiddleware)
        self.assertEqual(middlewares[1].cls, SecurityHeadersMiddleware)

    def test_update_with_default_middlewares_empty(self):
        middlewares = update_with_default_middlewares([])
        self.assertEqual(len(middlewares), 2)
        self.assertEqual(middlewares[0].cls, GZipMiddleware)
        self.assertEqual(middlewares[1].cls, SecurityHeadersMiddleware)

    def test_update_with_default_middlewares_other(self):
        middlewares = update_with_default_middlewares([Middleware(FakeMiddleware)])
        self.assertEqual(len(middlewares), 3)
        self.assertEqual(middlewares[0].cls, GZipMiddleware)
        self.assertEqual(middlewares[1].cls, FakeMiddleware)
        self.assertEqual(middlewares[2].cls, SecurityHeadersMiddleware)

    @mock.patch('os.environ', {'EVERYSK_SERVER_GZIP_MIDDLEWARE_ENABLED': 'False'})
    def test_disable_gzip_middleware(self):
        middlewares = update_with_default_middlewares([Middleware(FakeMiddleware)])
        self.assertEqual(len(middlewares), 2)
        self.assertEqual(middlewares[0].cls, FakeMiddleware)
        self.assertEqual(middlewares[1].cls, SecurityHeadersMiddleware)

    @mock.patch('os.environ', {'EVERYSK_SERVER_SECURITY_MIDDLEWARE_ENABLED': 'False'})
    def test_disable_security_middleware(self):
        middlewares = update_with_default_middlewares([Middleware(FakeMiddleware)])
        self.assertEqual(len(middlewares), 2)
        self.assertEqual(middlewares[0].cls, GZipMiddleware)
        self.assertEqual(middlewares[1].cls, FakeMiddleware)


class FakeEndpoint(BaseEndpoint):

    async def get(self):
        return Response('Body', status_code=200)


class GZipMiddlewareTestCaseAsync(IsolatedAsyncioTestCase):

    def setUp(self) -> None:
        self.app = create_application(routes=[RouteLazy('/', FakeEndpoint)])
        self.client = TestClient(self.app)

    async def test_gzip_middleware(self):
        response = self.client.get('/')
        self.assertEqual(response.headers['Content-Encoding'], 'gzip')
        self.assertEqual(response.content, b'Body')


class SecurityHeadersMiddlewareTestCaseAsync(IsolatedAsyncioTestCase):

    def setUp(self) -> None:
        self.app = create_application(routes=[RouteLazy('/', FakeEndpoint)])
        self.client = TestClient(self.app)

    async def test_security_headers_middleware(self):
        response = self.client.get('/')
        self.assertEqual(response.headers['Strict-Transport-Security'], 'max-age=31536000; includeSubDomains')
        self.assertEqual(response.headers['X-Content-Type-Options'], 'nosniff')
        self.assertEqual(response.headers['X-DNS-Prefetch-Control'], 'off')
        self.assertEqual(response.headers['X-Download-Options'], 'noopen')
        self.assertEqual(response.headers['X-Frame-Options'], 'DENY')
        self.assertEqual(response.headers['X-Permitted-Cross-Domain-Policies'], 'none')
