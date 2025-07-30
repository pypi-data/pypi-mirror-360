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

from everysk.sdk.engines.cache import UserCache


###############################################################################
#   Cache Test Case Implementation
###############################################################################
class CacheTestCase(TestCase):
    def setUp(self) -> None:
        self.headers = HttpSDKPOSTConnection().get_headers()
        self.api_url = HttpSDKPOSTConnection().get_url()
        self.expected_error_message = 'Invalid time value. The time value should be an integer greater than 0 and less than or equal to the default expiration time.'
        return super().setUp()

    ###############################################################################
    #   Get Method Test Case Implementation
    ###############################################################################
    def test_get_method_assert_is_called(self):
        cache = UserCache()
        expected_content = compress({'class_name': 'UserCache', 'method_name': 'get', 'self_obj': cache.to_dict(add_class_path=True), 'params': {'key': 'key', 'prefix': ''}}, protocol='gzip', serialize='json')
        expected_result = {}

        with mock.patch('httpx.Client.post') as mock_post:
            mock_post.return_value.content = '{}'
            mock_post.return_value.status_code = 200
            result = cache.get("key")

        mock_post.assert_called_with(
            url=self.api_url,
            headers=self.headers,
            timeout=httpx.Timeout(timeout=30, read=settings.EVERYSK_SDK_HTTP_DEFAULT_TIMEOUT),
            content=expected_content
        )
        self.assertEqual(result, expected_result)

    ###############################################################################
    #   Get Multi Method Test Case Implementation
    ###############################################################################
    def test_get_multi_method_assert_is_called(self):
        cache = UserCache()
        expected_content = compress({'class_name': 'UserCache', 'method_name': 'get_multi', 'self_obj': cache.to_dict(add_class_path=True), 'params': {'keys': ['key1', 'key2'], 'prefix': ''}}, protocol='gzip', serialize='json')
        expected_result = {}

        with mock.patch('httpx.Client.post') as mock_post:
            mock_post.return_value.content = '{}'
            mock_post.return_value.status_code = 200
            result = cache.get_multi(['key1', 'key2'])

        mock_post.assert_called_with(
            url=self.api_url,
            headers=self.headers,
            timeout=httpx.Timeout(timeout=30, read=settings.EVERYSK_SDK_HTTP_DEFAULT_TIMEOUT),
            content=expected_content
        )
        self.assertEqual(result, expected_result)

    ###############################################################################
    #   Set Method Test Case Implementation
    ###############################################################################
    def test_set_assert_is_called(self):
        cache = UserCache()
        expected_content = compress({'class_name': 'UserCache', 'method_name': 'set', 'self_obj': cache.to_dict(add_class_path=True), 'params': {'key': 'key', 'data': 'value', 'time': 14400, 'prefix': ''}}, protocol='gzip', serialize='json')
        expected_result = {}

        with mock.patch('httpx.Client.post') as mock_post:
            mock_post.return_value.content = '{}'
            mock_post.return_value.status_code = 200
            result = cache.set(key="key", data="value")

        mock_post.assert_called_with(
            url=self.api_url,
            headers=self.headers,
            timeout=httpx.Timeout(timeout=30, read=settings.EVERYSK_SDK_HTTP_DEFAULT_TIMEOUT),
            content=expected_content
        )
        self.assertEqual(result, expected_result)

    def test_set_raises_error_with_invalid_time(self):
        with self.assertRaises(ValueError) as context:
            UserCache().set(key="key", data="value", time='123')

        self.assertEqual(self.expected_error_message, str(context.exception))

    def test_set_raises_error_with_negative_time(self):
        with self.assertRaises(ValueError) as context:
            UserCache().set(key="key", data="value", time=-2)

        self.assertEqual(self.expected_error_message, str(context.exception))

    def test_set_raises_error_with_greater_time(self):
        with self.assertRaises(ValueError) as context:
            UserCache().set(key="key", data="value", time=settings.ENGINES_CACHE_EXECUTION_EXPIRATION_TIME + 10)

        self.assertEqual(self.expected_error_message, str(context.exception))

    ###############################################################################
    #   Set Multi Method Test Case Implementation
    ###############################################################################
    def test_set_multi_assert_is_called(self):
        cache = UserCache()
        expected_content = compress({'class_name': 'UserCache', 'method_name': 'set_multi', 'self_obj': cache.to_dict(add_class_path=True), 'params': {'data_dict': {'key1': 'value1', 'key2': 'value2'}, 'time': 14400, 'prefix': ''}}, protocol='gzip', serialize='json')
        with mock.patch('httpx.Client.post') as mock_post:
            mock_post.return_value.content = '{}'
            mock_post.return_value.status_code = 200
            cache.set_multi({'key1': 'value1', 'key2': 'value2'})

        mock_post.assert_called_with(
            url=self.api_url,
            headers=self.headers,
            timeout=httpx.Timeout(timeout=30, read=settings.EVERYSK_SDK_HTTP_DEFAULT_TIMEOUT),
            content=expected_content
        )

    def test_set_multi_raises_error_with_invalid_time(self):
        with self.assertRaises(ValueError) as context:
            UserCache().set_multi(data_dict={'key1': 'value1', 'key2': 'value2'}, time='123')

        self.assertEqual(self.expected_error_message, str(context.exception))

    def test_set_multi_raises_error_with_negative_time(self):
        with self.assertRaises(ValueError) as context:
            UserCache().set_multi(data_dict={'key1': 'value1', 'key2': 'value2'}, time=-1)

        self.assertEqual(self.expected_error_message, str(context.exception))

    def test_set_multi_raises_error_with_greater_time(self):
        with self.assertRaises(ValueError) as context:
            UserCache().set_multi(data_dict={'key1': 'value1', 'key2': 'value2'}, time=settings.ENGINES_CACHE_EXECUTION_EXPIRATION_TIME + 10)

        self.assertEqual(self.expected_error_message, str(context.exception))

    ###############################################################################
    #   Incr Method Test Case Implementation
    ###############################################################################
    def test_incr_assert_is_called(self):
        cache = UserCache()
        expected_content = compress({'class_name': 'UserCache', 'method_name': 'incr', 'self_obj': cache.to_dict(add_class_path=True), 'params': {'key': 'key', 'delta': 1, 'initial_value': 0, 'time': 14400}}, protocol='gzip', serialize='json')
        with mock.patch('httpx.Client.post') as mock_post:
            mock_post.return_value.content = '{}'
            mock_post.return_value.status_code = 200
            cache.incr(key='key', delta=1, initial_value=0)

        mock_post.assert_called_with(
            url=self.api_url,
            headers=self.headers,
            timeout=httpx.Timeout(timeout=30, read=settings.EVERYSK_SDK_HTTP_DEFAULT_TIMEOUT),
            content=expected_content
        )

    def test_incr_raises_error_with_invalid_time(self):
        with self.assertRaises(ValueError) as context:
            UserCache().incr(key=1, delta=1, initial_value=0, time='123')

        self.assertEqual(self.expected_error_message, str(context.exception))

    def test_incr_raises_error_with_negative_time(self):
        with self.assertRaises(ValueError) as context:
            UserCache().incr(key=1, delta=1, initial_value=0, time=-1)

        self.assertEqual(self.expected_error_message, str(context.exception))

    def test_incr_raises_error_with_greater_time(self):
        with self.assertRaises(ValueError) as context:
            UserCache().incr(key=1, delta=1, initial_value=0, time=settings.ENGINES_CACHE_EXECUTION_EXPIRATION_TIME + 10)

        self.assertEqual(self.expected_error_message, str(context.exception))

    ###############################################################################
    #   Decr Method Test Case Implementation
    ###############################################################################
    def test_decr_assert_is_called(self):
        cache = UserCache()
        expected_content = compress({'class_name': 'UserCache', 'method_name': 'decr', 'self_obj': cache.to_dict(add_class_path=True), 'params': {'key': 'key', 'delta': 1, 'initial_value': 0, 'time': 14400}}, protocol='gzip', serialize='json')
        with mock.patch('httpx.Client.post') as mock_post:
            mock_post.return_value.content = '{}'
            mock_post.return_value.status_code = 200
            cache.decr(key='key', delta=1, initial_value=0)

        mock_post.assert_called_with(
            url=self.api_url,
            headers=self.headers,
            timeout=httpx.Timeout(timeout=30, read=settings.EVERYSK_SDK_HTTP_DEFAULT_TIMEOUT),
            content=expected_content
        )

    def test_decr_raises_error_with_invalid_time(self):
        with self.assertRaises(ValueError) as context:
            UserCache().decr(key='key', delta=1, initial_value=0, time='123')

        self.assertEqual(self.expected_error_message, str(context.exception))

    def test_decr_raises_error_with_negative_time(self):
        with self.assertRaises(ValueError) as context:
            UserCache().decr(key='key', delta=1, initial_value=0, time=-1)

        self.assertEqual(self.expected_error_message, str(context.exception))

    def test_decr_raises_error_with_greater_time(self):
        with self.assertRaises(ValueError) as context:
            UserCache().decr(key='key', delta=1, initial_value=0, time=settings.ENGINES_CACHE_EXECUTION_EXPIRATION_TIME + 10)

        self.assertEqual(self.expected_error_message, str(context.exception))

    ###############################################################################
    #   Delete Method Test Case Implementation
    ###############################################################################
    def test_delete_assert_is_called(self):
        cache = UserCache()
        expected_content = compress({'class_name': 'UserCache', 'method_name': 'delete', 'self_obj': cache.to_dict(add_class_path=True), 'params': {'key': 'key'}}, protocol='gzip', serialize='json')
        with mock.patch('httpx.Client.post') as mock_post:
            mock_post.return_value.content = '{}'
            mock_post.return_value.status_code = 200
            cache.delete(key='key')

        mock_post.assert_called_with(
            url=self.api_url,
            headers=self.headers,
            timeout=httpx.Timeout(timeout=30, read=settings.EVERYSK_SDK_HTTP_DEFAULT_TIMEOUT),
            content=expected_content
        )

    ###############################################################################
    #   Delete Multi Method Test Case Implementation
    ###############################################################################
    def test_delete_multi_assert_is_called(self):
        cache = UserCache()
        expected_content = compress({'class_name': 'UserCache', 'method_name': 'delete_multi', 'self_obj': cache.to_dict(add_class_path=True), 'params': {'keys': ['key1', 'key2']}}, protocol='gzip', serialize='json')
        with mock.patch('httpx.Client.post') as mock_post:
            mock_post.return_value.content = '{}'
            mock_post.return_value.status_code = 200
            cache.delete_multi(keys=['key1', 'key2'])

        mock_post.assert_called_with(
            url=self.api_url,
            headers=self.headers,
            timeout=httpx.Timeout(timeout=30, read=settings.EVERYSK_SDK_HTTP_DEFAULT_TIMEOUT),
            content=expected_content
        )
