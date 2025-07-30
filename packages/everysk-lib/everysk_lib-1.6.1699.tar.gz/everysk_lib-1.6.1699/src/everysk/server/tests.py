###############################################################################
#
# (C) Copyright 2025 EVERYSK TECHNOLOGIES
#
# This is an unpublished work containing confidential and proprietary
# information of EVERYSK TECHNOLOGIES. Disclosure, use, or reproduction
# without authorization of EVERYSK TECHNOLOGIES is prohibited.
#
###############################################################################
# pylint: disable=unused-import

try:
    from everysk.server._tests.applications import ServerApplication as EveryskLibServerApplication

    from everysk.server._tests.endpoints import (
        BaseEndpointTestCase as EveryskLibBaseEndpointTestCase,
        BaseEndpointTestCaseAsync as EveryskLibBaseEndpointTestCaseAsync,
        JSONEndpointTestCase as EveryskLibJSONEndpointTestCase,
        JSONEndpointTestCaseAsync as EveryskLibJSONEndpointTestCaseAsync,
        HealthCheckEndpointTestCaseAsync as EveryskLibHealthCheckEndpointTestCaseAsync,
        RedirectEndpointTestCase as EveryskLibRedirectEndpointTestCase,
        RedirectEndpointTestCaseAsync as EveryskLibRedirectEndpointTestCaseAsync,
    )

    from everysk.server._tests.middlewares import (
        GZipMiddlewareTestCaseAsync as EveryskLibGZipMiddlewareTestCaseAsync,
        SecurityHeadersMiddlewareTestCaseAsync as EveryskLibSecurityHeadersMiddlewareTestCaseAsync,
        UpdateMiddlewaresTestCase as EveryskLibUpdateMiddlewaresTestCase
    )
    from everysk.server._tests.routing import RouteLazyTestCaseAsync as EveryskLibRouteLazyTestCaseAsync
except ModuleNotFoundError as error:
    # This will prevent running these tests if requests is not installed
    if not error.args[0].startswith("No module named 'starlette'"):
        raise error
