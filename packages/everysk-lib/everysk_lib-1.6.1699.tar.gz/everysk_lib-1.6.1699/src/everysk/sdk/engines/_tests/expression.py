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
from everysk.config import settings
from everysk.core.compress import compress
from everysk.core.http import HttpSDKPOSTConnection, httpx
from everysk.core.unittests import TestCase, mock

from everysk.sdk.engines.expression import Expression


###############################################################################
#   Expression Test Case Implementation
###############################################################################
class ExpressionTestCase(TestCase):

    def setUp(self) -> None:
        self.headers = HttpSDKPOSTConnection().get_headers()
        self.api_url = HttpSDKPOSTConnection().get_url()
        return super().setUp()

    ###############################################################################
    #   Get Tokens Method Test Case
    ###############################################################################
    def test_get_tokens(self):
        engine = Expression()
        expected_content = compress({'class_name': 'Expression', 'method_name': 'get_tokens', 'self_obj': engine.to_dict(add_class_path=True), 'params': {'expression': 'a + b', 'data_types': ['cpp_var', 'str_var']}}, protocol='gzip', serialize='json')

        with mock.patch('httpx.Client.post') as mock_post:
            mock_post.return_value.content = '{}'
            mock_post.return_value.status_code = 200
            engine.get_tokens('a + b')

        mock_post.assert_called_with(
            url=self.api_url,
            headers=self.headers,
            timeout=httpx.Timeout(timeout=30, read=settings.EVERYSK_SDK_HTTP_DEFAULT_TIMEOUT),
            content=expected_content
        )

    ###############################################################################
    #   Solve Method Test Case
    ###############################################################################
    def test_solve_method(self):
        engine = Expression()
        expected_content = compress({'class_name': 'Expression', 'method_name': 'solve', 'self_obj': engine.to_dict(add_class_path=True), 'params': {'expression': 'a + b', 'user_args': {'a': 1, 'b': 2}}}, protocol='gzip', serialize='json')

        with mock.patch('httpx.Client.post') as mock_post:
            mock_post.return_value.content = '{}'
            mock_post.return_value.status_code = 200
            engine.solve('a + b', {'a': 1, 'b': 2})

        mock_post.assert_called_with(
            url=self.api_url,
            headers=self.headers,
            timeout=httpx.Timeout(timeout=30, read=settings.EVERYSK_SDK_HTTP_DEFAULT_TIMEOUT),
            content=expected_content
        )
