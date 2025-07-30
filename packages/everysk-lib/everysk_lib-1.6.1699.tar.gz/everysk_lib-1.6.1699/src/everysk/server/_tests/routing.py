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

from everysk.server.applications import create_application
from everysk.server.endpoints import BaseEndpoint
from everysk.server.responses import Response
from everysk.server.routing import RouteLazy


class FakeEndpoint(BaseEndpoint):

    async def get(self):
        return Response(status_code=200)


class RouteLazyTestCaseAsync(IsolatedAsyncioTestCase):

    def setUp(self) -> None:
        self.app = create_application(routes=[RouteLazy('/', 'everysk.server._tests.routing.FakeEndpoint')])
        self.client = TestClient(self.app)

    async def test_security_headers_middleware(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
