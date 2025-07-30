###############################################################################
#
# (C) Copyright 2023 EVERYSK TECHNOLOGIES
#
# This is an unpublished work containing confidential and proprietary
# information of EVERYSK TECHNOLOGIES. Disclosure, use, or reproduction
# without authorization of EVERYSK TECHNOLOGIES is prohibited.
#
###############################################################################

###############################################################################
#   Imports
###############################################################################
import os

from everysk.config import settings
from everysk.core.serialize import dumps
from everysk.core.compress import compress
from everysk.core.object import BaseDict
from everysk.core.exceptions import HttpError, SDKError
from everysk.core.http import HttpSDKPOSTConnection, httpx
from everysk.core.unittests import TestCase, mock

from everysk.sdk.base import BaseSDK, handler_input_args
from everysk.sdk.entities.portfolio.base import Portfolio

###############################################################################
#   BaseSDK TestCase Implementation
###############################################################################
class TestBaseSDK(TestCase):
# pylint: disable=no-name-in-module
# pylint: disable=import-outside-toplevel
# pylint: disable=unused-import

    def setUp(self):
        self.default_kwargs = {
            'class_name': 'BaseSDK',
            'method_name': 'setUp',  # This will be overridden in each test method.
            'self_obj': None,
            'params': {}
        }
        self.old_post = httpx.Client.post
        self.headers = {
            'Accept-Encoding': 'gzip',
            'Accept-Language': 'en-US, en;q=0.9, pt-BR;q=0.8, pt;q=0.7',
            'Cache-control': 'no-cache',
            'Content-Type': 'text/html; charset=UTF-8',
            'Content-Encoding': 'gzip',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
            'Authorization': 'Bearer SID:TOKEN'
        }
        os.environ['EVERYSK_API_URL_SCHEME'] = 'https'
        os.environ['EVERYSK_API_URL_DOMAIN'] = 'test.com'
        os.environ['EVERYSK_API_SID'] = 'SID'
        os.environ['EVERYSK_API_TOKEN'] = 'TOKEN'
        response = mock.MagicMock()
        response.content = dumps({'my_SID': 'teste'})
        response.status_code = 200
        httpx.Client.post = mock.MagicMock()
        httpx.Client.post.return_value = response

    def tearDown(self) -> None:
        httpx.Client.post = self.old_post

    def test_import_from_sdk_path(self):
        from everysk.sdk.entities import Portfolio as root_Portfolio

        self.assertEqual(root_Portfolio, Portfolio)

        with self.assertRaisesRegex(ImportError, "cannot import name 'Module' from 'everysk.sdk.entities'"):
            from everysk.sdk.entities import Module

    def test_defaults_are_set(self):
        # Using the context manager to mock HttpSDKPOSTConnection
        BaseSDK.get_response(**self.default_kwargs)

        httpx.Client.post.assert_called_once_with( # pylint: disable=no-member
            url='https://test.com/v1/sdk_function',
            headers=self.headers,
            timeout=httpx.Timeout(timeout=30, read=settings.EVERYSK_SDK_HTTP_DEFAULT_TIMEOUT),
            content=compress(self.default_kwargs, protocol='gzip', serialize='json')
        )

    def test_automatic_class_name_assignment(self):
        # In this scenario, we are not passing 'class_name'.
        # Directly calling get_response from BaseSDK
        kwargs = {'method_name': 'test_automatic_class_name_assignment'}
        BaseSDK.get_response(**kwargs)

        expected_kwargs = {**self.default_kwargs, **kwargs, 'class_name': 'BaseSDK'}

        httpx.Client.post.assert_called_once_with( # pylint: disable=no-member
            url='https://test.com/v1/sdk_function',
            headers=self.headers,
            timeout=httpx.Timeout(timeout=30, read=settings.EVERYSK_SDK_HTTP_DEFAULT_TIMEOUT),
            content=compress(expected_kwargs, protocol='gzip', serialize='json')
        )

    def test_automatic_method_name_assignment(self):
        # In this scenario, we are not passing 'class_name'.
        # Directly calling get_response from BaseSDK
        kwargs = {'class_name': 'BaseSDK'}
        BaseSDK.get_response(**kwargs)

        expected_kwargs = {**self.default_kwargs, **kwargs, 'method_name': 'test_automatic_method_name_assignment'}

        httpx.Client.post.assert_called_once_with( # pylint: disable=no-member
            url='https://test.com/v1/sdk_function',
            headers=self.headers,
            timeout=httpx.Timeout(timeout=30, read=settings.EVERYSK_SDK_HTTP_DEFAULT_TIMEOUT),
            content=compress(expected_kwargs, protocol='gzip', serialize='json')
        )

    def test_get_response_raises_sdk_error_on_http_error(self):
        with mock.patch.object(HttpSDKPOSTConnection, 'get_response', side_effect=HttpError("Test HTTP Error")):
            with self.assertRaises(SDKError) as context:
                BaseSDK.get_response()
            self.assertEqual(str(context.exception), "Test HTTP Error")

    def test_get_response_with_sdk_error(self):
        with mock.patch.object(HttpSDKPOSTConnection, 'get_response', return_value={'error_module':'everysk.core.exceptions.SDKError', 'error_message':'SDK sample error'}):
            with self.assertRaisesRegex(SDKError, 'SDK sample error'):
                BaseSDK.get_response()

    ###############################################################################
    #   handler input args TestCase Implementation
    ###############################################################################
    def test_args_handler_with_no_args(self):
        input_dct = dict()
        expected = BaseDict()
        res = handler_input_args(input_dct)
        self.assertDictEqual(res, expected)
        self.assertIsInstance(res, BaseDict)

    def test_args_handler_with_args(self):
        input_dct = {'a': 1, 'b': 2}
        expected = BaseDict(**input_dct)
        res = handler_input_args(input_dct)
        self.assertDictEqual(res, expected)
        self.assertIsInstance(res, BaseDict)

    def test_args_handler_with_non_dict(self):
        self.assertEqual(handler_input_args(None), None)

    def test_args_handler_with_complex_dict(self):
        input_dct = {'a': 1, 'b': {'c': 2}}
        expected = BaseDict(a=1, b=BaseDict(c=2))
        res = handler_input_args(input_dct)

        self.assertDictEqual(res, expected)
        self.assertIsInstance(res, BaseDict)

    def test_args_handler_with_complex_dict_and_list(self):
        input_dct = {'a': 1, 'b': {'c': [{'a': [{'a': 'b'}]}, 3]}}
        expected = BaseDict(a=1, b=BaseDict(c=[BaseDict(a=[BaseDict(a='b')]), 3]))
        res = handler_input_args(input_dct)
        self.assertDictEqual(res, expected)
        self.assertIsInstance(handler_input_args(res), BaseDict)
        self.assertIsInstance(res['b'], BaseDict)
        self.assertIsInstance(res['b']['c'][0], BaseDict)
        self.assertIsInstance(res['b']['c'][0]['a'][0], BaseDict)

    def test_args_handler_with_string(self):
        expected = '123'
        res = handler_input_args(expected)
        self.assertEqual(expected, res)
        self.assertNotIsInstance(res, BaseDict)

    def test_arg_handler_with_integer(self):
        expected = 123
        res = handler_input_args(expected)
        self.assertEqual(expected, res)
        self.assertNotIsInstance(res, BaseDict)

    def test_arg_handler_with_float(self):
        expected = 3.14
        res = handler_input_args(expected)
        self.assertEqual(expected, res)
        self.assertNotIsInstance(res, BaseDict)
        self.assertIsInstance(res, float)

    def test_arg_handler_with_complex_list(self):
        input_args = [42, 3.14, 'a', ['b', 1], [{'d': 2, 'e': 6, 'list': [1, 2, 3, 4, 5]}]]
        expected = [42, 3.14, 'a', ['b', 1], [BaseDict(d=2, e=6, list=[1, 2, 3, 4, 5])]]
        res = handler_input_args(input_args)
        self.assertIsInstance(res, list)
        self.assertIsInstance(res[3], list)
        self.assertIsInstance(res[4][0]['list'], list)
        self.assertEqual(expected, res)
