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
from everysk.config import settings
from everysk.core.compress import compress
from everysk.core.exceptions import FieldValueError, InvalidArgumentError
from everysk.core.http import HttpSDKPOSTConnection, httpx
from everysk.core.unittests import TestCase, mock

from everysk.sdk.entities.portfolio.base import Portfolio
from everysk.sdk.entities.script import Script


###############################################################################
#   Script TestCase Implementation
###############################################################################
class ScriptTestCase(TestCase):
    def setUp(self):
        self.mock_klass = mock.MagicMock()
        self.script = Script(Portfolio)
        self.headers = HttpSDKPOSTConnection().get_headers()
        self.api_url = HttpSDKPOSTConnection().get_url()

    def test_script_fetch_return_is_none(self):
        result = Portfolio.script.fetch(None, 'someVariant', 'someWorkspace')
        self.assertIsNone(result)

        result = Portfolio.script.fetch('', 'someVariant', 'someWorkspace')
        self.assertIsNone(result)

    def test_script_fetch_multi_none_user_input(self):
        result = Portfolio.script.fetch_multi(None, 'previousWorkers', 'someWorkspace')
        self.assertIsInstance(result, list)

    def test_script_query_previous_workers_without_id(self):
        user_input = {"someField": "someValue"}
        result = Portfolio.script.fetch(user_input, 'previousWorkers', 'someWorkspace')
        self.assertIsInstance(result, Portfolio)

    def test_script_query_tag_latest_variant(self):
        expected_content = compress({'class_name': 'Script', 'method_name': 'inner_fetch', 'self_obj': {'_klass': 'Portfolio', '__class_path__': 'everysk.sdk.entities.script.Script'}, 'params': {'user_input': {'tags': 'someTag'}, 'variant': 'tagLatest', 'workspace': 'someWorkspace'}}, protocol='gzip', serialize='json')

        with mock.patch('httpx.Client.post') as mock_post:
            mock_post.return_value.content = '{}'
            mock_post.return_value.status_code = 200
            Portfolio.script.fetch({"tags": "someTag"}, 'tagLatest', 'someWorkspace')

        expected_content = compress({'class_name': 'Script', 'method_name': 'inner_fetch', 'self_obj': Portfolio.script.to_dict(add_class_path=True), 'params': {'user_input': {'tags': 'someTag'}, 'variant': 'tagLatest', 'workspace': 'someWorkspace'}}, protocol='gzip', serialize='json')
        mock_post.assert_called_with(
            url=self.api_url,
            headers=self.headers,
            timeout=httpx.Timeout(timeout=30, read=settings.EVERYSK_SDK_HTTP_DEFAULT_TIMEOUT),
            content=expected_content
        )

    def test_script_query_when_response_is_a_list(self):
        with mock.patch('httpx.Client.post') as mock_post, \
            mock.patch('everysk.core.http.compress') as mock_dumps:
            mock_dumps.return_value = 'test'
            mock_post.return_value.content = '[{}, {}, null]'
            mock_post.return_value.status_code = 200
            result = Portfolio.script.fetch_list(['tag1', 'tag2'], 'tagList', 'someWorkspace')

        mock_dumps.assert_called_once_with(
            {
                'class_name': 'Script',
                'method_name': 'inner_fetch_list',
                'self_obj': Portfolio.script,
                'params': {
                    'user_input': ['tag1', 'tag2'],
                    'variant': 'tagList',
                    'workspace': 'someWorkspace'
                }
            },
            protocol='gzip',
            serialize='json',
            use_undefined=True,
            add_class_path=True
        )
        mock_post.assert_called_with(
            url=self.api_url,
            headers=self.headers,
            timeout=httpx.Timeout(timeout=30, read=settings.EVERYSK_SDK_HTTP_DEFAULT_TIMEOUT),
            content=mock_dumps.return_value
        )
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 3)
        self.assertIsInstance(result[0], Portfolio)
        self.assertIsInstance(result[1], Portfolio)
        self.assertIsNone(result[2])

    def test_script_fetch_multi_when_response_is_a_list(self):
        with mock.patch('httpx.Client.post') as mock_post, \
            mock.patch('everysk.core.http.compress') as mock_dumps:
            mock_dumps.return_value = 'test'
            mock_post.return_value.content = '[{}, {}]'
            mock_post.return_value.status_code = 200
            result = Portfolio.script.fetch_multi([['tag1', 'tag2']], ['tagList'], ['someWorkspace'])

        mock_dumps.assert_called_once_with(
            {
                'class_name': 'Script',
                'method_name': 'inner_fetch_multi',
                'self_obj': Portfolio.script,
                'params': {
                    'user_input_list': [['tag1', 'tag2']],
                    'variant_list': ['tagList'],
                    'workspace_list': ['someWorkspace']
                }
            },
            protocol='gzip',
            serialize='json',
            use_undefined=True,
            add_class_path=True
        )
        mock_post.assert_called_with(
            url=self.api_url,
            headers=self.headers,
            timeout=httpx.Timeout(timeout=30, read=settings.EVERYSK_SDK_HTTP_DEFAULT_TIMEOUT),
            content=mock_dumps.return_value
        )
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)
        self.assertIsInstance(result[0], Portfolio)
        self.assertIsInstance(result[1], Portfolio)

    def test_script_query_upstream_when_response_is_entity(self):
        portfolio = Portfolio(**{'name': 'Test portfolio'})

        result = Portfolio.script.fetch(portfolio, 'previousWorkers', 'someWorkspace')

        self.assertIsInstance(result, Portfolio)

    def test_script_query_when_response_is_an_empty_list(self):
        result = Portfolio.script.fetch_list(None, 'tagList', 'someWorkspace')
        self.assertEqual(result, [])

        result = Portfolio.script.fetch_list('', 'tagList', 'someWorkspace')
        self.assertEqual(result, [])

    def test_persist_transient(self):
        entity = Portfolio(name='test', workspace='someWorkspace')

        with mock.patch('httpx.Client.post') as mock_post, \
            mock.patch('everysk.core.http.compress') as mock_compress:
            mock_compress.return_value = 'test'
            mock_post.return_value.content = '{}'
            mock_post.return_value.status_code = 200

            result = Portfolio.script.persist(entity, 'transient')


        mock_compress.assert_called_once_with(
            {
                'class_name': 'Script',
                'method_name': 'persist',
                'self_obj': Portfolio.script,
                'params': {
                    'entity': entity,
                    'persist': 'transient',
                    'consistency_check': False
                }
            },
            protocol='gzip',
            serialize='json',
            use_undefined=True,
            add_class_path=True
        )
        mock_post.assert_called_with(
            url=self.api_url,
            headers=self.headers,
            timeout=httpx.Timeout(timeout=30, read=settings.EVERYSK_SDK_HTTP_DEFAULT_TIMEOUT),
            content=mock_compress.return_value
        )
        self.assertIsInstance(result, Portfolio)

    def test_storage_transient(self):
        entity = Portfolio(name='test', workspace='someWorkspace')

        with mock.patch('httpx.Client.post') as mock_post, \
            mock.patch('everysk.core.http.compress') as mock_compress:
            mock_compress.return_value = 'test'
            mock_post.return_value.content = '{}'
            mock_post.return_value.status_code = 200
            storage_settings = {
                'storage_mode': 'transient',
                'consistency_check': False,
                'validate': True,
                'create_fallback': True
            }
            result = Portfolio.script.storage(entity, storage_settings)

        mock_compress.assert_called_once_with(
            {
                'class_name': 'Script',
                'method_name': 'inner_storage',
                'self_obj': Portfolio.script,
                'params': {
                    'entity': entity,
                    'storage_settings': {
                        'storage_mode': 'transient',
                        'consistency_check': False,
                        'validate': True,
                        'create_fallback': True
                    }
                }
            },
            protocol='gzip',
            serialize='json',
            use_undefined=True,
            add_class_path=True
        )
        mock_post.assert_called_with(
            url=self.api_url,
            headers=self.headers,
            timeout=httpx.Timeout(timeout=30, read=settings.EVERYSK_SDK_HTTP_DEFAULT_TIMEOUT),
            content=mock_compress.return_value
        )
        self.assertIsInstance(result, Portfolio)

    def test_storage_transient_validate(self):
        entity = Portfolio(name='test', workspace='someWorkspace')
        storage_settings = {
            'storage_mode': 'transient',
            'consistency_check': False,
            'validate': False,
            'create_fallback': True
        }
        result = Portfolio.script.storage(entity, storage_settings)
        self.assertIsInstance(result, Portfolio)

    def test_storage_raises_entity_equal_none(self):

        with self.assertRaises(InvalidArgumentError) as context:
            Portfolio.script.storage(None, {})
        self.assertIn('Entity should not be empty.', str(context.exception))

    def test_init_(self):
        # pylint: disable=protected-access
        script = Portfolio.script
        self.assertEqual(script._klass, Portfolio)

        script = Script(Portfolio)
        self.assertEqual(script._klass, Portfolio)

        script = Script(_klass=Portfolio)
        self.assertEqual(script._klass, Portfolio)

        script = Script(_klass='Portfolio')
        self.assertEqual(script._klass, Portfolio)

        self.assertRaisesRegex(
            FieldValueError,
            "The _klass value 'Foo' must be a class or a string with the class name",
            Script,
            _klass='Foo'
        )
