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
import json
import zoneinfo

from everysk.config import settings
from everysk.core.compress import compress
from everysk.core.datetime import DateTime, timezone
from everysk.core.exceptions import RequiredError, SDKValueError, FieldValueError
from everysk.core.fields import StrField
from everysk.core.http import HttpSDKPOSTConnection, httpx
from everysk.core.unittests import TestCase, mock

from everysk.sdk.entities.query import Query
from everysk.sdk.entities.base import BaseEntity
from everysk.sdk.entities.portfolio.base import Portfolio
from everysk.sdk.entities.portfolio.securities import Securities


###############################################################################
#   Base Entity TestCase Implementation
###############################################################################
class TestBaseEntity(TestCase):

    def setUp(self):
        self.headers = HttpSDKPOSTConnection().get_headers()
        self.api_url = HttpSDKPOSTConnection().get_url()
        self.expected_response = {
            '_klass': Portfolio,
            'filters': [],
            'order': [],
            'projection': None,
            'limit': None,
            'offset': None,
            'page_size': None,
            'page_token': None,
            'distinct_on': []
        }
        self.sample_portfolio_data = {
            'id': 'port_1234567891011211234567890',
            'workspace': 'SampleWorkspace',
            'name': 'SamplePortfolio',
            'tags': ['tag1', 'tag2'],
            'link_uid': 'ABC',
            'description': 'Description',
            'nlv': 1000.0,
            'base_currency': 'USD',
            'date': DateTime(2023, 9, 9, 9, 9, 9, 9),
            'securities': Securities([{'symbol': 'AAPL'}]),
            'version': '1.0',
            'created_on': DateTime(2023, 9, 9, 9, 9, 9, 9),
            'updated_on': DateTime(2023, 9, 9, 9, 9, 9, 9),
            'level': 'HIGH',
            'outstanding_shares': 1000,
            'source_hash': 'XYZ',
            'status': 'OK',
            'portfolio_uid': 'UID123',
            'check_securities': False
        }
        self.portfolio = Portfolio(**self.sample_portfolio_data)

    def test_entity_to_query(self):
        portfolio = self.portfolio.copy()
        self.assertRaisesRegex(
            SDKValueError,
            "Can't filter by Name and Tags at the same time",
            portfolio.to_query
        )

        # test with name
        portfolio.update(tags=None, link_uid=None, date=None)
        _query = portfolio.to_query() # pylint: disable=protected-access
        self.assertDictEqual(_query,
        {
            '_klass': Portfolio,
            'filters': [
                ('workspace', '=', 'SampleWorkspace'),
                ('name', '<', 'sampleportfolip'),
                ('name', '>=', 'sampleportfolio')
            ],
            'order': [],
            'projection': None,
            'limit': None,
            'offset': None,
            'page_size': None,
            'page_token': None,
            'distinct_on': []
        })

        # test with tags
        portfolio.update(tags=['tag1', 'tag2'], name=None)
        _query = portfolio.to_query() # pylint: disable=protected-access
        self.assertListEqual(_query.filters, [
            ('workspace', '=', 'SampleWorkspace'),
            ('tags', '=', 'tag1'),
            ('tags', '=', 'tag2')
        ])

        # test with link_uid
        portfolio.update(tags=None, link_uid='ABC')
        _query = portfolio.to_query() # pylint: disable=protected-access
        self.assertListEqual(_query.filters, [
            ('workspace', '=', 'SampleWorkspace'),
            ('link_uid', '=', 'ABC')
        ])

    def test_check_query_raises_sdk_error_when_filtering_by_name_and_tags(self):
        with self.assertRaises(SDKValueError) as context:
            portfolio : Portfolio = self.portfolio.copy()
            portfolio.to_query(limit=1)

        self.assertEqual(str(context.exception), "Can't filter by Name and Tags at the same time")

    def test_check_query_raises_sdk_error_when_filtering_by_name_and_link(self):
        with self.assertRaises(SDKValueError) as context:
            portfolio: Portfolio = self.portfolio.copy()
            portfolio['tags'] = []
            portfolio.to_query(limit=1)

        self.assertEqual(str(context.exception), "Can't filter by Name and Link UID at the same time")

    def test_check_query_raises_sdk_error_when_date_in_query_order(self):
        with self.assertRaises(SDKValueError) as context:
            portfolio: Portfolio = self.portfolio.copy()
            portfolio['tags'] = []
            portfolio['link_uid'] = ''
            portfolio.to_query(order=['date'])

        self.assertEqual(str(context.exception), "Can't filter by Name and Date at the same time,  must order by updated_on")

    def test_get_id_prefix(self):
        with self.assertRaises(NotImplementedError):
            BaseEntity.get_id_prefix()

    def test_generate_id(self):
        with mock.patch.object(BaseEntity, 'get_id_prefix', return_value='P'), \
                mock.patch('everysk.sdk.entities.base.generate_random_id', return_value='12345'):
            self.assertEqual(BaseEntity().generate_id(), 'P12345')

    def test_validate_id(self):
        class FakeEntityClass(BaseEntity): # pylint: disable=abstract-method
            id = StrField(regex=settings.PORTFOLIO_ID_REGEX, max_size=settings.PORTFOLIO_ID_MAX_SIZE, required_lazy=True, empty_is_none=True)

        self.assertFalse(FakeEntityClass.validate_id('invalid_id'))
        self.assertTrue(FakeEntityClass.validate_id('port_puvGxrtIYc7OupBzfnrwFNVPg'))
        self.assertFalse(FakeEntityClass.validate_id(''))
        self.assertFalse(BaseEntity.validate_id(None))

    def test_validate(self):
        self.assertTrue(BaseEntity(id="my_id", workspace="my_workspace", name="my_name", created_on=DateTime.now(), updated_on=DateTime.now()).validate())

    def test_validate_transient(self):
        class FakeEntity(BaseEntity):
            @staticmethod
            def get_id_prefix():
                return 'fake_'

        entity = FakeEntity(workspace='my_workspace', name='my_name')
        entity['created_on'] = DateTime(2023, 9, 9, 9, 9, 9, 9)
        entity['updated_on'] = DateTime(2023, 9, 9, 9, 9, 9, 9)

        self.assertTrue(FakeEntity.validate_transient(entity))
        self.assertDictEqual(
            entity.__dict__,
            {'version': 'v1', 'created_on': DateTime(2023, 9, 9, 9, 9, 9, 9, tzinfo=zoneinfo.ZoneInfo(key='UTC')), 'updated_on': DateTime(2023, 9, 9, 9, 9, 9, 9, tzinfo=zoneinfo.ZoneInfo(key='UTC')), 'workspace': 'my_workspace', 'id': None, 'name': 'my_name'}
        )

    def test_raises_validate(self):
        base_entity = BaseEntity()
        base_entity['created_on'] = None
        self.assertRaisesRegex(
            RequiredError,
            'The created_on attribute is required.',
            base_entity.validate
        )

    def test_get_query(self):
        """ Test _get_query method """
        expected_response = self.expected_response.copy()
        expected_response['projection'] = ['securities']
        result = Portfolio.query.set_projection('securities') # pylint: disable=protected-access
        self.assertDictEqual(result, expected_response)

    def test_query(self):
        """ Test query method """
        expected_response = self.expected_response.copy()
        expected_response['projection'] = ['securities']
        result = Portfolio.query.set_projection('securities')
        self.assertDictEqual(result, expected_response)

    def test_where(self):
        """ Test where method """
        expected_response = self.expected_response.copy()
        expected_response['filters'] = [('date', '=', DateTime(2023, 8, 10, 12, 0, tzinfo=timezone.utc))]
        result = Portfolio.query.where('date', '=', '2023-08-10')
        self.assertDictEqual(result, expected_response)

    def test_sort_by(self):
        """ Test sort_by method """
        expected_response = self.expected_response.copy()
        expected_response['order'] = ['date']
        result = Portfolio.query.sort_by('date')
        self.assertDictEqual(result, expected_response)

    def test_set_projection(self):
        """ Test set_projection method """
        expected_response = self.expected_response.copy()
        expected_response['projection'] = ['securities']
        result = Portfolio.query.set_projection('securities')
        self.assertDictEqual(result, expected_response)

    def test_set_limit(self):
        """ Test set_limit method """
        expected_response = self.expected_response.copy()
        expected_response['limit'] = 5
        result = Portfolio.query.set_limit(5)
        self.assertDictEqual(result, expected_response)

    def test_set_offset(self):
        """ Test set_offset method """
        expected_response = self.expected_response.copy()
        expected_response['offset'] = 10
        result = Portfolio.query.set_offset(10)
        self.assertDictEqual(result, expected_response)

    def test_set_page_size(self):
        """ Test set_page_size method """
        expected_response = self.expected_response.copy()
        expected_response['page_size'] = 15
        result = Portfolio.query.set_page_size(15)
        self.assertDictEqual(result, expected_response)

    def test_set_page_token(self):
        """ Test set_page_token method """
        expected_response = self.expected_response.copy()
        expected_response['page_token'] = 'my_test_page'
        result = Portfolio.query.set_page_token('my_test_page')
        self.assertDictEqual(result, expected_response)

    def test_load(self):
        with mock.patch('httpx.Client.post') as mock_post:
            mock_post.return_value.content = '{"key": "value"}'
            mock_post.return_value.status_code = 200
            query = Portfolio.query.where('workspace', 'my_workspace')
            result = query.load(offset=5)

        expected_content = compress({'class_name': 'Query', 'method_name': 'load', 'self_obj': query.to_dict(add_class_path=True), 'params': {'offset': 5}}, protocol='gzip', serialize='json')
        mock_post.assert_called_with(url=self.api_url, headers=self.headers, timeout=httpx.Timeout(timeout=30, read=settings.EVERYSK_SDK_HTTP_DEFAULT_TIMEOUT), content=expected_content)
        self.assertIsInstance(result, Portfolio)

    def test_list(self):
        with mock.patch('httpx.Client.post') as mock_post:
            mock_post.return_value.content = '[{"key": "value"}]'
            mock_post.return_value.status_code = 200
            query = Portfolio.query.where('workspace', 'my_workspace')
            result = query.loads(limit=10, offset=5)

        expected_content = compress({'class_name': 'Query', 'method_name': 'loads', 'self_obj': query.to_dict(add_class_path=True), 'params': {'limit': 10, 'offset': 5}}, protocol='gzip', serialize='json')
        mock_post.assert_called_with(url=self.api_url, headers=self.headers, timeout=httpx.Timeout(timeout=30, read=settings.EVERYSK_SDK_HTTP_DEFAULT_TIMEOUT), content=expected_content)
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertIsInstance(result[0], Portfolio)

    def test_page(self):
        query_class = Query(**self.expected_response)
        query_class['filters'] = [('workspace', '=', 'my_workspace')]

        expected_content = compress({'class_name': 'Query', 'method_name': 'page', 'self_obj': query_class.to_dict(add_class_path=True), 'params': {'page_size': 10, 'page_token': 'page_token'}}, protocol='gzip', serialize='json')

        with mock.patch('httpx.Client.post') as mock_post:
            mock_post.return_value.content = json.dumps({
                "entities": [
                    {"key1": "value1", "key2": "value2", "key3": "value3"},
                ]
            })
            mock_post.return_value.status_code = 200
            result = Portfolio.query.where('workspace', 'my_workspace').page(page_size=10, page_token='page_token')

        mock_post.assert_called_with(url=self.api_url, headers=self.headers, timeout=httpx.Timeout(timeout=30, read=settings.EVERYSK_SDK_HTTP_DEFAULT_TIMEOUT), content=expected_content)
        self.assertIsInstance(result['entities'][0], Portfolio)

    def test_pages(self):
        query = Query(**self.expected_response)
        query['filters'] = [('workspace', '=', 'my_workspace')]
        expected_content = compress({'class_name': 'Query', 'method_name': 'page', 'self_obj': query.to_dict(add_class_path=True), 'params': {'page_size': 10, 'page_token': {'__undefined__': None}}}, protocol='gzip', serialize='json')

        with mock.patch('httpx.Client.post') as mock_post:
            mock_post.return_value.content = json.dumps({
                "entities": [
                    {"key1": "value1", "key2": "value2", "key3": "value3"},
                    {"key1": "value4", "key2": "value5", "key3": "value6"},
                    {"key1": "value7", "key2": "value8", "key3": "value9"}
                ]
            })
            mock_post.return_value.status_code = 200
            result = Portfolio.query.where('workspace', 'my_workspace').pages(page_size=10)
            next(result)

        mock_post.assert_called_with(url=self.api_url, headers=self.headers, timeout=httpx.Timeout(timeout=30, read=settings.EVERYSK_SDK_HTTP_DEFAULT_TIMEOUT), content=expected_content)

    def test_script_query(self):
        expected_content = compress({'class_name': 'Script', 'method_name': 'inner_fetch', 'self_obj': {'_klass': 'Portfolio', '__class_path__': 'everysk.sdk.entities.script.Script'}, 'params': {'user_input': 'port_12456', 'variant': 'select', 'workspace': None}}, protocol='gzip', serialize='json')

        with mock.patch('httpx.Client.post') as mock_post:
            mock_post.return_value.content = '{}'
            mock_post.return_value.status_code = 200
            result = Portfolio.script.fetch(user_input='port_12456', variant='select', workspace=None)

        expected_content = compress({'class_name': 'Script', 'method_name': 'inner_fetch', 'self_obj': Portfolio.script.to_dict(add_class_path=True), 'params': {'user_input': 'port_12456', 'variant': 'select', 'workspace': None}}, protocol='gzip', serialize='json')
        mock_post.assert_called_with(url=self.api_url, headers=self.headers, timeout=httpx.Timeout(timeout=30, read=settings.EVERYSK_SDK_HTTP_DEFAULT_TIMEOUT), content=expected_content)
        self.assertIsInstance(result, Portfolio)

    def test_retrieve(self):
        expected_content = compress({'class_name': 'Portfolio', 'method_name': 'retrieve', 'self_obj': None, 'params': {'entity_id': 'port_1234567891011211234567890', 'projection': None}}, protocol='gzip', serialize='json')

        with mock.patch('httpx.Client.post') as mock_post:
            mock_post.return_value.content = '{"name": "Portfolio"}'
            mock_post.return_value.status_code = 200
            Portfolio.retrieve(entity_id=self.sample_portfolio_data['id'])

        mock_post.assert_called_with(url=self.api_url, headers=self.headers, timeout=httpx.Timeout(timeout=30, read=settings.EVERYSK_SDK_HTTP_DEFAULT_TIMEOUT), content=expected_content)

    def test_retrieve_with_projection(self):
        expected_content = compress({'class_name': 'Portfolio', 'method_name': 'retrieve', 'self_obj': None, 'params': {'entity_id': 'port_1234567891011211234567890', 'projection': ['-securities']}}, protocol='gzip', serialize='json')

        with mock.patch('httpx.Client.post') as mock_post:
            mock_post.return_value.content = '{"name": "Portfolio"}'
            mock_post.return_value.status_code = 200
            Portfolio.retrieve(entity_id=self.sample_portfolio_data['id'], projection='-securities')

        mock_post.assert_called_with(url=self.api_url, headers=self.headers, timeout=httpx.Timeout(timeout=30, read=settings.EVERYSK_SDK_HTTP_DEFAULT_TIMEOUT), content=expected_content)

    def test_retrieve_many_with_invalid(self):
        self.assertRaisesRegex(
            FieldValueError,
            "The argument 'entity_id_list' most be a instance of 'list' and not <class 'str'>",
            Portfolio.retrieve_many,
            entity_id_list='port_1234567891011211234567890'
        )

    def test_inner_retrieve_many(self):
        expected_content = compress({'class_name': 'Portfolio', 'method_name': 'inner_retrieve_many', 'self_obj': None, 'params': {'entity_id_list': ['port_1234567891011211234567890'], 'projection': None}}, protocol='gzip', serialize='json')

        with mock.patch('httpx.Client.post') as mock_post:
            mock_post.return_value.content = '[{"name": "Portfolio"}, {"name": "Portfolio"}]'
            mock_post.return_value.status_code = 200
            Portfolio.retrieve_many(entity_id_list=[self.sample_portfolio_data['id']])

        mock_post.assert_called_with(url=self.api_url, headers=self.headers, timeout=httpx.Timeout(timeout=30, read=settings.EVERYSK_SDK_HTTP_DEFAULT_TIMEOUT), content=expected_content)

    def test_inner_retrieve_many_with_projection(self):
        expected_content = compress({'class_name': 'Portfolio', 'method_name': 'inner_retrieve_many', 'self_obj': None, 'params': {'entity_id_list': ['port_1234567891011211234567890'], 'projection': ['-securities', '-name']}}, protocol='gzip', serialize='json')

        with mock.patch('httpx.Client.post') as mock_post:
            mock_post.return_value.content = '[{"name": "Portfolio"}, {"name": "Portfolio"}]'
            mock_post.return_value.status_code = 200
            Portfolio.retrieve_many(entity_id_list=[self.sample_portfolio_data['id']], projection=['-securities', '-name'])

        mock_post.assert_called_with(url=self.api_url, headers=self.headers, timeout=httpx.Timeout(timeout=30, read=settings.EVERYSK_SDK_HTTP_DEFAULT_TIMEOUT), content=expected_content)

    def test_retrieve_with_none(self):
        expected_content = compress({'class_name': 'Portfolio', 'method_name': 'retrieve', 'self_obj': None, 'params': {'entity_id': 'port_1234567891011211234567890', 'projection': None}}, protocol='gzip', serialize='json')

        with mock.patch('httpx.Client.post') as mock_post:
            mock_post.return_value.content = 'null'
            mock_post.return_value.status_code = 200
            Portfolio.retrieve(entity_id=self.sample_portfolio_data['id'])

        mock_post.assert_called_with(url=self.api_url, headers=self.headers, timeout=httpx.Timeout(timeout=30, read=settings.EVERYSK_SDK_HTTP_DEFAULT_TIMEOUT), content=expected_content)

    def test_create(self):
        expected_content = compress({'class_name': 'Portfolio', 'method_name': 'create', 'self_obj': None, 'params': {'entity_dict': {'id': 'port_1234567891011211234567890', 'workspace': 'SampleWorkspace', 'name': 'SamplePortfolio', 'tags': ['tag1', 'tag2'], 'link_uid': 'ABC', 'description': 'Description', 'nlv': 1000.0, 'base_currency': 'USD', 'date': {'__datetime__': '2023-09-09T09:09:09.000009+00:00'}, 'securities': [], 'version': '1.0', 'created_on': {'__datetime__': '2023-09-09T09:09:09.000009+00:00'}, 'updated_on': {'__datetime__': '2023-09-09T09:09:09.000009+00:00'}, 'level': 'HIGH', 'outstanding_shares': 1000, 'source_hash': 'XYZ', 'status': 'OK', 'portfolio_uid': 'UID123', 'check_securities': False}}}, protocol='gzip', serialize='json')
        self.sample_portfolio_data['securities'] = []

        with mock.patch('httpx.Client.post') as mock_post:
            mock_post.return_value.content = '{"creating": "portfolio"}'
            mock_post.return_value.status_code = 200
            Portfolio.create(entity_dict=self.sample_portfolio_data)

        mock_post.assert_called_with(url=self.api_url, headers=self.headers, timeout=httpx.Timeout(timeout=30, read=settings.EVERYSK_SDK_HTTP_DEFAULT_TIMEOUT), content=expected_content)

    def test_modify(self):
        sample_portfolio_data = self.sample_portfolio_data.copy()
        sample_portfolio_data['base_currency'] = 'BRL'
        expected_content = compress({'class_name': 'Portfolio', 'method_name': 'modify', 'self_obj': None, 'params': {'entity_id': 'port_1234567891011211234567890', 'overwrites': {'base_currency': 'BRL'}}}, protocol='gzip', serialize='json')

        with mock.patch('httpx.Client.post') as mock_post:
            mock_post.return_value.content = '{}'
            mock_post.return_value.status_code = 200
            Portfolio.modify(entity_id=self.sample_portfolio_data['id'], overwrites={'base_currency': 'BRL'})

        mock_post.assert_called_with(url=self.api_url, headers=self.headers, timeout=httpx.Timeout(timeout=30, read=settings.EVERYSK_SDK_HTTP_DEFAULT_TIMEOUT), content=expected_content)

    def test_modify_return_none(self):
        sample_portfolio_data = self.sample_portfolio_data.copy()
        sample_portfolio_data['base_currency'] = 'BRL'

        expected_content = compress({'class_name': 'Portfolio', 'method_name': 'modify', 'self_obj': None, 'params': {'entity_id': 'port_1234567891011211234567890', 'overwrites': {'base_currency': 'BRL'}}}, protocol='gzip', serialize='json')

        with mock.patch('httpx.Client.post') as mock_post:
            mock_post.return_value.content = 'null'
            mock_post.return_value.status_code = 200
            Portfolio.modify(entity_id=self.sample_portfolio_data['id'], overwrites={'base_currency': 'BRL'})

        mock_post.assert_called_with(url=self.api_url, headers=self.headers, timeout=httpx.Timeout(timeout=30, read=settings.EVERYSK_SDK_HTTP_DEFAULT_TIMEOUT), content=expected_content)

    def test_remove(self):
        expected_content = compress({'class_name': 'Portfolio', 'method_name': 'remove', 'self_obj': None, 'params': {'entity_id': 'port_1234567891011211234567890'}}, protocol='gzip', serialize='json')

        with mock.patch('httpx.Client.post') as mock_post:
            mock_post.return_value.content = '{"remove": "key"}'
            mock_post.return_value.status_code = 200
            result = Portfolio.remove(entity_id=self.sample_portfolio_data['id'])

        mock_post.assert_called_with(url=self.api_url, headers=self.headers, timeout=httpx.Timeout(timeout=30, read=settings.EVERYSK_SDK_HTTP_DEFAULT_TIMEOUT), content=expected_content)
        self.assertIsInstance(result, Portfolio)

    def test_remove_return_none(self):
        expected_content = compress({'class_name': 'Portfolio', 'method_name': 'remove', 'self_obj': None, 'params': {'entity_id': 'port_1234567891011211234567890'}}, protocol='gzip', serialize='json')

        with mock.patch('httpx.Client.post') as mock_post:
            mock_post.return_value.content = 'null'
            mock_post.return_value.status_code = 200
            result = Portfolio.remove(entity_id=self.sample_portfolio_data['id'])

        mock_post.assert_called_with(url=self.api_url, headers=self.headers, timeout=httpx.Timeout(timeout=30, read=settings.EVERYSK_SDK_HTTP_DEFAULT_TIMEOUT), content=expected_content)
        self.assertIsNone(result)

    def test_clone(self):
        sample_portfolio_data = self.sample_portfolio_data.copy()
        sample_portfolio_data['base_currency'] = 'BRL'
        expected_content = compress({'class_name': 'Portfolio', 'method_name': 'clone', 'self_obj': None, 'params': {'entity_id': 'port_1234567891011211234567890', 'overwrites': {'base_currency': 'BRL'}}}, protocol='gzip', serialize='json')

        with mock.patch('httpx.Client.post') as mock_post:
            mock_post.return_value.content = '{"key": "value"}'
            mock_post.return_value.status_code = 200
            result = Portfolio.clone(entity_id=self.sample_portfolio_data['id'], overwrites={'base_currency': 'BRL'})

        mock_post.assert_called_with(url=self.api_url, headers=self.headers, timeout=httpx.Timeout(timeout=30, read=settings.EVERYSK_SDK_HTTP_DEFAULT_TIMEOUT), content=expected_content)
        self.assertIsInstance(result, Portfolio)

    def test_clone_return_none(self):
        sample_portfolio_data = self.sample_portfolio_data.copy()
        sample_portfolio_data['base_currency'] = 'BRL'
        expected_content = compress({'class_name': 'Portfolio', 'method_name': 'clone', 'self_obj': None, 'params': {'entity_id': 'port_1234567891011211234567890', 'overwrites': {'base_currency': 'BRL'}}}, protocol='gzip', serialize='json')

        with mock.patch('httpx.Client.post') as mock_post:
            mock_post.return_value.content = 'null'
            mock_post.return_value.status_code = 200
            result = Portfolio.clone(entity_id=self.sample_portfolio_data['id'], overwrites={'base_currency': 'BRL'})

        mock_post.assert_called_with(url=self.api_url, headers=self.headers, timeout=httpx.Timeout(timeout=30, read=settings.EVERYSK_SDK_HTTP_DEFAULT_TIMEOUT), content=expected_content)
        self.assertIsNone(result)

    def test_create_many(self):
        sample_portfolio_data = self.sample_portfolio_data.copy()
        sample_portfolio_data['base_currency'] = 'BRL'
        sample_portfolio_data['check_securities'] = True
        sample_portfolio_data['securities'] = []
        self.sample_portfolio_data['securities'] = []

        expected_content = compress({'class_name': 'Portfolio', 'method_name': 'create_many', 'self_obj': None, 'params': {'entity_dict_list': [{'id': 'port_1234567891011211234567890', 'workspace': 'SampleWorkspace', 'name': 'SamplePortfolio', 'tags': ['tag1', 'tag2'], 'link_uid': 'ABC', 'description': 'Description', 'nlv': 1000.0, 'base_currency': 'USD', 'date': {'__datetime__': '2023-09-09T09:09:09.000009+00:00'}, 'securities': [], 'version': '1.0', 'created_on': {'__datetime__': '2023-09-09T09:09:09.000009+00:00'}, 'updated_on': {'__datetime__': '2023-09-09T09:09:09.000009+00:00'}, 'level': 'HIGH', 'outstanding_shares': 1000, 'source_hash': 'XYZ', 'status': 'OK', 'portfolio_uid': 'UID123', 'check_securities': False}, {'id': 'port_1234567891011211234567890', 'workspace': 'SampleWorkspace', 'name': 'SamplePortfolio', 'tags': ['tag1', 'tag2'], 'link_uid': 'ABC', 'description': 'Description', 'nlv': 1000.0, 'base_currency': 'BRL', 'date': {'__datetime__': '2023-09-09T09:09:09.000009+00:00'}, 'securities': [], 'version': '1.0', 'created_on': {'__datetime__': '2023-09-09T09:09:09.000009+00:00'}, 'updated_on': {'__datetime__': '2023-09-09T09:09:09.000009+00:00'}, 'level': 'HIGH', 'outstanding_shares': 1000, 'source_hash': 'XYZ', 'status': 'OK', 'portfolio_uid': 'UID123', 'check_securities': True}]}}, protocol='gzip', serialize='json')
        expected_response = []

        with mock.patch('httpx.Client.post') as mock_post:
            mock_post.return_value.content = '{}'
            mock_post.return_value.status_code = 200
            result = Portfolio.create_many(entity_dict_list=[self.sample_portfolio_data, sample_portfolio_data])

        mock_post.assert_called_with(url=self.api_url, headers=self.headers, timeout=httpx.Timeout(timeout=30, read=settings.EVERYSK_SDK_HTTP_DEFAULT_TIMEOUT), content=expected_content)
        self.assertEqual(result, expected_response)

    def test_modify_many(self):
        original_portfolio_data = self.sample_portfolio_data.copy()
        original_portfolio_data['name'] = 'modified_1'
        Portfolio(**original_portfolio_data)

        sample_portfolio_data = self.sample_portfolio_data.copy()
        sample_portfolio_data['id'] = 'port_1234567891011211234567891'
        sample_portfolio_data['name'] = 'modified_2'
        Portfolio(**sample_portfolio_data)

        expected_content = compress({'class_name': 'Portfolio', 'method_name': 'modify_many', 'self_obj': None, 'params': {'entity_id_list': ['port_1234567891011211234567890', 'port_1234567891011211234567891'], 'overwrites': [{'name': 'modified_1'}, {'name': 'modified_2'}]}}, protocol='gzip', serialize='json')
        expected_response = []

        with mock.patch('httpx.Client.post') as mock_post:
            mock_post.return_value.content = '{}'
            mock_post.return_value.status_code = 200
            result = Portfolio.modify_many(entity_id_list=[self.sample_portfolio_data['id'], sample_portfolio_data['id']], overwrites=[{'name': 'modified_1'}, {'name': 'modified_2'}])

        mock_post.assert_called_with(url=self.api_url, headers=self.headers, timeout=httpx.Timeout(timeout=30, read=settings.EVERYSK_SDK_HTTP_DEFAULT_TIMEOUT), content=expected_content)
        self.assertEqual(result, expected_response)

    def test_remove_many(self):
        sample_portfolio_data = self.sample_portfolio_data.copy()
        sample_portfolio_data['id'] = 'port_1234567891011211234567891'
        sample_portfolio_data['base_currency'] = 'BRL'

        expected_content = compress({'class_name': 'Portfolio', 'method_name': 'remove_many', 'self_obj': None, 'params': {'entity_id_list': ['port_1234567891011211234567890', 'port_1234567891011211234567891']}}, protocol='gzip', serialize='json')
        expected_response = [self.sample_portfolio_data['id'], sample_portfolio_data['id']]

        with mock.patch('httpx.Client.post') as mock_post:
            mock_post.return_value.content = f'["{self.sample_portfolio_data["id"]}", "{sample_portfolio_data["id"]}"]'
            mock_post.return_value.status_code = 200
            result = Portfolio.remove_many(entity_id_list=[self.sample_portfolio_data['id'], sample_portfolio_data['id']])

        mock_post.assert_called_with(url=self.api_url, headers=self.headers, timeout=httpx.Timeout(timeout=30, read=settings.EVERYSK_SDK_HTTP_DEFAULT_TIMEOUT), content=expected_content)
        self.assertEqual(result, expected_response)

    def test_clone_many(self):
        original_portfolio_data = self.sample_portfolio_data.copy()
        original_portfolio_data['name'] = 'modified_1'
        original_portfolio_data['workspace'] = 'modified_1'
        original_portfolio = Portfolio(**original_portfolio_data)

        sample_portfolio_data = self.sample_portfolio_data.copy()
        sample_portfolio_data['id'] = 'port_1234567891011211234567891'
        sample_portfolio_data['name'] = 'modified_2'
        sample_portfolio_data['workspace'] = 'modified_2'
        Portfolio(**sample_portfolio_data)

        entity_id_list = [original_portfolio['id'], sample_portfolio_data['id']]

        expected_content = compress({'class_name': 'Portfolio', 'method_name': 'clone_many', 'self_obj': None, 'params': {'entity_id_list': ['port_1234567891011211234567890', 'port_1234567891011211234567891'], 'overwrites': [{'name': 'modified_1'}, {'name': 'modified_1'}]}}, protocol='gzip', serialize='json')
        expected_response = []

        with mock.patch('httpx.Client.post') as mock_post:
            mock_post.return_value.content = '{}'
            mock_post.return_value.status_code = 200
            result = Portfolio.clone_many(entity_id_list=entity_id_list, overwrites=[{'name': 'modified_1'}, {'name': 'modified_1'}])

        mock_post.assert_called_with(url=self.api_url, headers=self.headers, timeout=httpx.Timeout(timeout=30, read=settings.EVERYSK_SDK_HTTP_DEFAULT_TIMEOUT), content=expected_content)
        self.assertEqual(result, expected_response)

    def test_save(self):
        self.sample_portfolio_data['securities'] = []
        portfolio = Portfolio(**self.sample_portfolio_data)
        expected_content = compress({'class_name': 'Portfolio', 'method_name': 'save', 'self_obj': portfolio.to_dict(add_class_path=True), 'params': {}}, protocol='gzip', serialize='json')

        with mock.patch('httpx.Client.post') as mock_post:
            mock_post.return_value.content = '{"key": "value"}'
            mock_post.return_value.status_code = 200
            result = portfolio.save()

        mock_post.assert_called_with(url=self.api_url, headers=self.headers, timeout=httpx.Timeout(timeout=30, read=settings.EVERYSK_SDK_HTTP_DEFAULT_TIMEOUT), content=expected_content)
        self.assertIsInstance(result, Portfolio)

    def test_delete(self):
        self.sample_portfolio_data['securities'] = []
        portfolio = Portfolio(**self.sample_portfolio_data)
        expected_content = compress({'class_name': 'Portfolio', 'method_name': 'delete', 'self_obj': portfolio.to_dict(add_class_path=True), 'params': {}}, protocol='gzip', serialize='json')

        with mock.patch('httpx.Client.post') as mock_post:
            mock_post.return_value.content = '{}'
            mock_post.return_value.status_code = 200
            result = portfolio.delete()

        mock_post.assert_called_with(url=self.api_url, headers=self.headers, timeout=httpx.Timeout(timeout=30, read=settings.EVERYSK_SDK_HTTP_DEFAULT_TIMEOUT), content=expected_content)
        self.assertIsInstance(result, Portfolio)

    def test_delete_return_none(self):
        self.sample_portfolio_data['securities'] = []
        portfolio = Portfolio(**self.sample_portfolio_data)
        expected_content = compress({'class_name': 'Portfolio', 'method_name': 'delete', 'self_obj': portfolio.to_dict(add_class_path=True), 'params': {}}, protocol='gzip', serialize='json')

        with mock.patch('httpx.Client.post') as mock_post:
            mock_post.return_value.content = 'null'
            mock_post.return_value.status_code = 200
            result = portfolio.delete()

        mock_post.assert_called_with(url=self.api_url, headers=self.headers, timeout=httpx.Timeout(timeout=30, read=settings.EVERYSK_SDK_HTTP_DEFAULT_TIMEOUT), content=expected_content)
        self.assertIsNone(result)

    def test_obj_with_to_dict_as_attribute(self):
        port = Portfolio(securities=[{'symbol': 'AAPL', 'name': 'Apple Inc.', 'price': 150.0}])
        result = port.to_dict()

        self.assertIsInstance(result, dict)
        self.assertIsInstance(result['securities'], list)
        self.assertEqual(result['securities'][0]['symbol'], 'AAPL')
        self.assertNotEqual(result['securities'], [])

    def test_normalize_projection(self):
        self.assertListEqual(self.portfolio._normalize_projection(None), [])
        self.assertListEqual(self.portfolio._normalize_projection('securities'), ['securities'])
        self.assertListEqual(self.portfolio._normalize_projection('-securities'), ['-securities'])
        self.assertListEqual(self.portfolio._normalize_projection(['-securities', '-name']), ['-securities', '-name'])
