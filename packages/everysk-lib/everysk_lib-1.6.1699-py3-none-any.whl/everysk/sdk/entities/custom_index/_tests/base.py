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
from everysk.core.datetime import DateTime
from everysk.core.exceptions import FieldValueError, SDKValueError
from everysk.core.http import HttpSDKPOSTConnection, httpx
from everysk.core.unittests import TestCase, mock

from everysk.sdk.entities.custom_index.base import CustomIndex

###############################################################################
#   Custom Index TestCase Implementation
###############################################################################
class CustomIndexTestCase(TestCase):

    def setUp(self):
        self.sample_data = {
            'symbol': 'CUSTOM:INDEX',
            'name': 'SampleCustomIndex',
            'tags': ['tag1', 'tag2'],
            'description': 'Description',
            'currency': 'USD',
            'data': [[1, 2, 3], [4, 5, 6]],
            'periodicity': 'M',
            'data_type': 'PRICE',
            'base_price': 100,
            'version': '1.0',
            'created_on': DateTime(2023, 9, 9, 9, 9, 9, 9),
            'updated_on': DateTime(2023, 9, 9, 9, 9, 9, 9),
        }
        self.custom_index = CustomIndex(**self.sample_data)
        self.headers = HttpSDKPOSTConnection().get_headers()
        self.api_url = HttpSDKPOSTConnection().get_url()

    def test_init(self):
        self.assertEqual(self.custom_index.symbol, self.custom_index.id)
        self.assertEqual(self.custom_index.symbol, self.sample_data['symbol'])
        self.assertEqual(self.custom_index.name, self.sample_data['name'])
        self.assertEqual(self.custom_index.tags, self.sample_data['tags'])
        self.assertEqual(self.custom_index.description, self.sample_data['description'])
        self.assertEqual(self.custom_index.currency, self.sample_data['currency'])
        self.assertEqual(self.custom_index.data, self.sample_data['data'])
        self.assertEqual(self.custom_index.periodicity, self.sample_data['periodicity'])
        self.assertEqual(self.custom_index.data_type, self.sample_data['data_type'])
        self.assertEqual(self.custom_index.base_price, self.sample_data['base_price'])
        self.assertEqual(self.custom_index.version, self.sample_data['version'])
        self.assertEqual(self.custom_index.created_on, self.sample_data['created_on'])
        self.assertEqual(self.custom_index.updated_on, self.sample_data['updated_on'])

    def test_property_id(self):
        self.assertEqual(self.custom_index.id, self.custom_index.symbol)

    def test_setter_id(self):
        self.custom_index.id = 'CUSTOM:NEW_ID'
        self.assertEqual(self.custom_index.id, 'CUSTOM:NEW_ID')
        self.assertEqual(self.custom_index.symbol, 'CUSTOM:NEW_ID')
        self.custom_index.symbol = 'CUSTOM:NEW_ID_2'
        self.assertEqual(self.custom_index.id, 'CUSTOM:NEW_ID_2')
        self.assertEqual(self.custom_index.symbol, 'CUSTOM:NEW_ID_2')

    def test_setter_id_with_invalid_value(self):
        with self.assertRaises(FieldValueError) as e:
            self.custom_index.id = 'Potato'
        self.assertEqual("The value 'Potato' for field 'symbol' must match with this regex: ^CUSTOM:[A-Z0-9_]*$.", e.exception.msg)

        with self.assertRaises(FieldValueError) as e:
            self.custom_index.symbol = 'Potato'
        self.assertEqual("The value 'Potato' for field 'symbol' must match with this regex: ^CUSTOM:[A-Z0-9_]*$.", e.exception.msg)

    def test_get_id_prefix(self):
        self.assertEqual(CustomIndex.get_id_prefix(), settings.CUSTOM_INDEX_SYMBOL_PREFIX)

    def test_validate(self):
        expected_content = compress({'class_name': 'CustomIndex', 'method_name': 'validate', 'self_obj': self.custom_index.to_dict(add_class_path=True), 'params': {}}, protocol='gzip', serialize='json')
        custom_index: CustomIndex = self.custom_index

        with mock.patch('httpx.Client.post') as mock_post:
            mock_post.return_value.content = '{}'
            mock_post.return_value.status_code = 200
            custom_index.validate()

        mock_post.assert_called_with(
            url=self.api_url,
            headers=self.headers,
            timeout=httpx.Timeout(timeout=30, read=settings.EVERYSK_SDK_HTTP_DEFAULT_TIMEOUT),
            content=expected_content
        )

    def test_validate_transient(self):
        expected_content = compress({'class_name': 'CustomIndex', 'method_name': 'validate', 'self_obj': self.custom_index.to_dict(add_class_path=True), "params": {}}, protocol='gzip', serialize='json')
        cmp_entity = self.custom_index.copy()
        cmp_entity.update(
            created_on=None,
            updated_on=None,
        )

        with mock.patch('httpx.Client.post') as mock_post, \
            mock.patch('everysk.core.datetime.DateTime.now') as mock_datetime_now:

            mock_datetime_now.return_value = DateTime(2023, 9, 9, 9, 9, 9, 9)
            mock_post.return_value.content = '{}'
            mock_post.return_value.status_code = 200
            CustomIndex.validate_transient(self.custom_index)

        mock_post.assert_called_with(
            url=self.api_url,
            headers=self.headers,
            timeout=httpx.Timeout(timeout=30, read=settings.EVERYSK_SDK_HTTP_DEFAULT_TIMEOUT),
            content=expected_content
        )

    def test_entity_to_query(self):
        custom_index: CustomIndex = self.custom_index.copy()
        self.assertRaisesRegex(
            SDKValueError,
            "Can't filter by Name and Tags at the same time",
            custom_index.to_query
        )

        # test with name
        custom_index.pop('name')
        query = custom_index.to_query() #pylint: disable=protected-access
        self.assertListEqual(query.filters, [('tags', '=', 'tag1'), ('tags', '=', 'tag2')])
        self.assertEqual(query.order, [])
        self.assertEqual(query.projection, None)
        self.assertEqual(query.limit, None)
        self.assertEqual(query.offset, None)
        self.assertEqual(query.page_size, None)
        self.assertEqual(query.page_token, None)
        self.assertEqual(query.distinct_on, [])

        # test with tags
        custom_index: CustomIndex = self.custom_index.copy()
        custom_index.pop('tags')
        query = custom_index.to_query() #pylint: disable=protected-access
        self.assertListEqual(query.filters, [('name', '<', 'samplecustomindey'), ('name', '>=', 'samplecustomindex')])
        self.assertEqual(query.order, [])
        self.assertEqual(query.projection, None)
        self.assertEqual(query.limit, None)
        self.assertEqual(query.offset, None)
        self.assertEqual(query.page_size, None)
        self.assertEqual(query.page_token, None)
        self.assertEqual(query.distinct_on, [])

    def test_modify_many(self):
        with self.assertRaises(NotImplementedError):
            CustomIndex.modify_many(entity_id_list=['CUSTOM:INDEX'], overwrites={})

    def test_clone_many(self):
        with self.assertRaises(NotImplementedError):
            CustomIndex.clone_many(entity_id_list=['CUSTOM:INDEX'], overwrites={})
