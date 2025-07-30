###############################################################################
#
# (C) Copyright 2025 EVERYSK TECHNOLOGIES
#
# This is an unpublished work containing confidential and proprietary
# information of EVERYSK TECHNOLOGIES. Disclosure, use, or reproduction
# without authorization of EVERYSK TECHNOLOGIES is prohibited.
#
###############################################################################
from starlette.applications import Starlette

from everysk.core.unittests import TestCase
from everysk.server.applications import create_application
from everysk.server.endpoints import JSONEndpoint
from everysk.server.middlewares import BaseHTTPMiddleware, Middleware
from everysk.server.routing import RouteLazy


class FakeMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request, call_next):
        return await call_next(request)


class FakeEndpoint(JSONEndpoint):
    rest_key_name: str = None
    rest_key_value: str = None

    async def get(self):
        return {}


class ServerApplication(TestCase):

    def test_routes_requires(self):
        with self.assertRaisesRegex(TypeError, r"create_application\(\) missing 1 required keyword-only argument: 'routes'"):
            create_application() # pylint: disable=missing-kwoa

    def test_routes(self):
        app = create_application(routes=[RouteLazy('/', FakeEndpoint)])
        self.assertListEqual(app.routes, [RouteLazy('/', FakeEndpoint)])

    def test_instance_starlette(self):
        app = create_application(routes=[])
        self.assertIsInstance(app, Starlette)

    def test_default_middlewares(self):
        app = create_application(routes=[])
        self.assertListEqual(
            [middleware.cls.__name__ for middleware in app.user_middleware],
            ['GZipMiddleware', 'SecurityHeadersMiddleware']
        )

    def test_add_middlewares(self):
        app = create_application(routes=[], middlewares=[Middleware(FakeMiddleware)])
        self.assertListEqual(
            [middleware.cls.__name__ for middleware in app.user_middleware],
            ['GZipMiddleware', 'FakeMiddleware', 'SecurityHeadersMiddleware']
        )

    def test_debug_default(self):
        app = create_application(routes=[])
        self.assertFalse(app.debug)

    def test_debug_true(self):
        app = create_application(routes=[], debug=True)
        self.assertTrue(app.debug)

    def test_exception_handlers_default(self):
        app = create_application(routes=[])
        self.assertDictEqual(app.exception_handlers, {})

    def test_exception_handlers(self):
        def handler(request, exc): # pylint: disable=unused-argument
            pass

        app = create_application(routes=[], exception_handlers={404: handler})
        self.assertDictEqual(app.exception_handlers, {404: handler})
