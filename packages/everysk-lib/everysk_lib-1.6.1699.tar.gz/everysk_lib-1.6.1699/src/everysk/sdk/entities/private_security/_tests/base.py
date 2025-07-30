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

from everysk.sdk.entities.private_security.base import PrivateSecurity


###############################################################################
#   Private Security TestCase Implementation
###############################################################################
class PrivateSecurityTestCase(TestCase):

    def setUp(self):
        self.sample_data = {
            'symbol': 'PRIVATE:SECURITY',
            'name': 'SamplePrivateSecurity',
            'tags': ['tag1', 'tag2'],
            'description': 'Description',
            'currency': 'USD',
            'data': {
                "m2m_spread": 0,
                "principal": 123.456,
                "expiry_date": "20231117",
                "starting_date": "20231108",
                "issue_date": "20231108",
                "method": "PRIVATE",
                "yield": 0,
                "events": [{
                        "date": "20231117",
                        "event_type": "V",
                        "value": 123.03
                }]},
            'instrument_type': 'PrivateFixedIncome',
            'version': '1.0',
            'created_on': DateTime(2023, 9, 9, 9, 9, 9, 9),
            'updated_on': DateTime(2023, 9, 9, 9, 9, 9, 9),
        }
        self.private_security = PrivateSecurity(**self.sample_data)
        self.headers = HttpSDKPOSTConnection().get_headers()
        self.api_url = HttpSDKPOSTConnection().get_url()

    def test_init(self):
        self.assertEqual(self.private_security.symbol, self.private_security.id)
        self.assertEqual(self.private_security.symbol, self.sample_data['symbol'])
        self.assertEqual(self.private_security.name, self.sample_data['name'])
        self.assertEqual(self.private_security.tags, self.sample_data['tags'])
        self.assertEqual(self.private_security.description, self.sample_data['description'])
        self.assertEqual(self.private_security.currency, self.sample_data['currency'])
        self.assertEqual(self.private_security.data, self.sample_data['data'])
        self.assertEqual(self.private_security.instrument_type, self.sample_data['instrument_type'])
        self.assertEqual(self.private_security.version, self.sample_data['version'])
        self.assertEqual(self.private_security.created_on, self.sample_data['created_on'])
        self.assertEqual(self.private_security.updated_on, self.sample_data['updated_on'])

    def test_property_id(self):
        self.assertEqual(self.private_security.id, self.private_security.symbol)

    def test_setter_id(self):
        self.private_security.id = 'PRIVATE:NEW_ID'
        self.assertEqual(self.private_security.id, 'PRIVATE:NEW_ID')
        self.assertEqual(self.private_security.symbol, 'PRIVATE:NEW_ID')
        self.private_security.symbol = 'PRIVATE:NEW_ID_2'
        self.assertEqual(self.private_security.id, 'PRIVATE:NEW_ID_2')
        self.assertEqual(self.private_security.symbol, 'PRIVATE:NEW_ID_2')

    def test_setter_id_with_invalid_value(self):
        with self.assertRaises(FieldValueError) as e:
            self.private_security.id = 'Potato'
        self.assertEqual("The value 'Potato' for field 'symbol' must match with this regex: ^PRIVATE:[A-Z0-9_]*$.", e.exception.msg)

        with self.assertRaises(FieldValueError) as e:
            self.private_security.symbol = 'Potato'
        self.assertEqual("The value 'Potato' for field 'symbol' must match with this regex: ^PRIVATE:[A-Z0-9_]*$.", e.exception.msg)

    def test_get_id_prefix(self):
        self.assertEqual(PrivateSecurity.get_id_prefix(), settings.PRIVATE_SECURITY_SYMBOL_PREFIX)

    def test_validate(self):
        expected_content = compress({'class_name': 'PrivateSecurity', 'method_name': 'validate', 'self_obj': self.private_security.to_dict(add_class_path=True), 'params': {}}, protocol='gzip', serialize='json')
        private_security: PrivateSecurity = self.private_security.copy()

        with mock.patch('httpx.Client.post') as mock_post:
            mock_post.return_value.content = '{}'
            mock_post.return_value.status_code = 200
            private_security.validate()

        mock_post.assert_called_with(
            url=self.api_url,
            headers=self.headers,
            timeout=httpx.Timeout(timeout=30, read=settings.EVERYSK_SDK_HTTP_DEFAULT_TIMEOUT),
            content=expected_content
        )

    def test_validate_transient(self):
        expected_content = compress({'class_name': 'PrivateSecurity', 'method_name': 'validate', 'self_obj': self.private_security.to_dict(add_class_path=True), 'params': {}}, protocol='gzip', serialize='json')
        cmp_entity = self.private_security.copy()
        cmp_entity.update(
            created_on=None,
            updated_on=None,
        )

        with mock.patch('httpx.Client.post') as mock_post, \
            mock.patch('everysk.core.datetime.DateTime.now') as mock_datetime_now:

            mock_datetime_now.return_value = DateTime(2023, 9, 9, 9, 9, 9, 9)
            mock_post.return_value.content = '{}'
            mock_post.return_value.status_code = 200
            PrivateSecurity.validate_transient(self.private_security)

        self.assertIsNone(cmp_entity.created_on)
        self.assertIsNone(cmp_entity.updated_on)

        mock_post.assert_called_with(
            url=self.api_url,
            headers=self.headers,
            timeout=httpx.Timeout(timeout=30, read=settings.EVERYSK_SDK_HTTP_DEFAULT_TIMEOUT),
            content=expected_content
        )


    def test_entity_to_query(self):
        private_security: PrivateSecurity = self.private_security.copy()
        self.assertRaisesRegex(
            SDKValueError,
            "Can't filter by Name and Tags at the same time",
            private_security.to_query
        )

        # test with name
        private_security.update(name='sampleprivatesecurity', tags=None)
        query = private_security.to_query() #pylint: disable=protected-access
        self.assertListEqual(query.filters, [('name', '<', 'sampleprivatesecuritz'), ('name', '>=', 'sampleprivatesecurity')])
        self.assertEqual(query.order, [])
        self.assertEqual(query.projection, None)
        self.assertEqual(query.limit, None)
        self.assertEqual(query.offset, None)
        self.assertEqual(query.page_size, None)
        self.assertEqual(query.page_token, None)
        self.assertEqual(query.distinct_on, [])

        # test with tags
        private_security.update(name=None, tags=['tag1', 'tag2'])
        query = private_security.to_query() #pylint: disable=protected-access
        self.assertListEqual(query.filters, [('tags', '=', 'tag1'), ('tags', '=', 'tag2')])

    def test_modify_many(self):
        with self.assertRaises(NotImplementedError):
            PrivateSecurity.modify_many(entity_id_list=['PRIVATE:SECURITY'], overwrites={})

    def test_clone_many(self):
        with self.assertRaises(NotImplementedError):
            PrivateSecurity.clone_many(entity_id_list=['PRIVATE:SECURITY'], overwrites={})

    def test_to_dict_private_security(self):
        result = self.private_security.to_dict()

        expected_data = {
            'symbol': 'PRIVATE:SECURITY',
            'name': 'SamplePrivateSecurity',
            'tags': ['tag1', 'tag2'],
            'description': 'Description',
            'currency': 'USD',
            'data': {'m2m_spread': 0, 'principal': 123.456, 'expiry_date': '20231117', 'starting_date': '20231108', 'issue_date': '20231108', 'method': 'PRIVATE', 'yield': 0, 'events': [{'date': '20231117', 'event_type': 'V', 'value': 123.03}]},
            'version': '1.0',
            'created': 1694250549,
            'updated': 1694250549,
            'type': 'PrivateFixedIncome'
        }

        self.assertIsInstance(result, dict)
        self.assertEqual(result, expected_data)
