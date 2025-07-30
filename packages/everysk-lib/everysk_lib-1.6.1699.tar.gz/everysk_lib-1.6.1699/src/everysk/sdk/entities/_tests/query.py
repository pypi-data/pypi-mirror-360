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
from everysk.core.datetime import Date, DateTime, ZoneInfo
from everysk.core.exceptions import SDKValueError, FieldValueError, SDKTypeError
from everysk.core.unittests import TestCase, mock

from everysk.sdk.entities.portfolio.base import Portfolio
from everysk.sdk.entities.query import Query


class MockPortfolio(Portfolio):
    _orderable_attributes = ['name', 'date']


###############################################################################
#   Query TestCase Implementation
###############################################################################
class QueryTestCase(TestCase):

    def setUp(self):
        self.mock_klass = MockPortfolio
        self.query = Query(Portfolio)
        self.default_data = {
            'filters': [['name', '=', 'test']],
            'order': ['name'],
            'projection': ['name'],
            'distinct_on': ['date'],
            'limit': 5,
            'offset': 2,
            'page_size': 10,
            'page_token': 'token123'
        }

    def test_init(self):
        # pylint: disable=protected-access
        query = Portfolio.query
        self.assertEqual(query._klass, Portfolio)

        query = Query(Portfolio)
        self.assertEqual(query._klass, Portfolio)

        query = Query(_klass=Portfolio)
        self.assertEqual(query._klass, Portfolio)

        query = Query(_klass='Portfolio')
        self.assertEqual(query._klass, Portfolio)

        self.assertRaisesRegex(
            FieldValueError,
            "The _klass value 'Foo' must be a class or a string with the class name",
            Query,
            _klass='Foo'
        )

        query = Query(Portfolio, _clean_order=['name', 'date'])
        self.assertIsInstance(query._clean_order, set)
        self.assertEqual(query._clean_order, {'name', 'date'})

        self.assertRaisesRegex(
            FieldValueError,
            f'Key _clean_order must be {set}',
            Query,
            Portfolio,
            _clean_order='Foo'
        )

        with mock.patch.object(Query, 'sort_by') as mock_sort_by, \
                mock.patch.object(Query, 'where') as mock_where, \
                mock.patch.object(Query, 'set_projection') as mock_set_projection, \
                mock.patch.object(Query, 'set_distinct_on') as mock_set_distinct_on, \
                mock.patch.object(Query, 'set_limit') as mock_set_limit, \
                mock.patch.object(Query, 'set_offset') as mock_set_offset, \
                mock.patch.object(Query, 'set_page_size') as mock_set_page_size, \
                mock.patch.object(Query, 'set_page_token') as mock_set_page_token:

            Query(Portfolio, **self.default_data)

        # Asserting the methods were called correctly
        mock_sort_by.assert_called_once_with(self.default_data['order'][0])
        mock_where.assert_called_once_with(*self.default_data['filters'][0])
        mock_set_projection.assert_called_once_with(self.default_data['projection'])
        mock_set_distinct_on.assert_called_once_with(self.default_data['distinct_on'])
        mock_set_limit.assert_called_once_with(self.default_data['limit'])
        mock_set_offset.assert_called_once_with(self.default_data['offset'])
        mock_set_page_size.assert_called_once_with(self.default_data['page_size'])
        mock_set_page_token.assert_called_once_with(self.default_data['page_token'])

    def test_init_from_query_dict(self):
        query = Query(Portfolio)
        query.where('name', 'test')
        query.where('tags', ['tag1', 'tag2'])
        query.where('created_on', '2023-08-10')
        query.where('date', '2023-08-10')
        query.sort_by('name')
        query.set_projection(['name', 'date'])
        query.set_distinct_on(['date'])
        query.set_limit(5)
        query.set_offset(2)
        query.set_page_size(10)
        query.set_page_token('token')

        new_query = Query(Portfolio, **query)

        self.assertDictEqual(query, new_query)

    def test_find_or_fail(self):
        self.assertFalse(self.query._find_or_fail) # pylint: disable=protected-access
        self.query.set_find_or_fail(True)
        self.assertTrue(self.query._find_or_fail) # pylint: disable=protected-access

    def test_where_with_invalid_operator(self):
        query = Query(self.mock_klass)
        self.assertRaisesRegex(
            SDKValueError,
            "Invalid operator: invalid_operator for property property",
            query.where,
            'property',
            'invalid_operator',
            'value'
        )

    def test_where_with_operator_for_certain_properties(self):
        query = Query(self.mock_klass)
        self.assertRaisesRegex(
            SDKValueError,
            'Filter by property operator must be \'=\'',
            query.where,
            'property',
            '>',
            'value'
        )

    def test_where_value_none(self):
        self.query.where('property', None)
        self.assertListEqual(self.query.filters, [('property', '=', None)])

    def test_where_2_arguments(self):
        self.query.where('property', 'value')
        self.assertListEqual(self.query.filters, [('property', '=', 'value')])

    def test_where_3_arguments(self):
        query = Query(self.mock_klass)
        query.where('property', '=', 'value')
        self.assertListEqual(query.filters, [('property', '=', 'value')])

    def test_where_4_arguments(self):
        query = Query(self.mock_klass)
        with self.assertRaises(SDKValueError):
            query.where('property', '=', 'value', 'banana')

    def test_where_invalid_operator(self):
        query = Query(self.mock_klass)
        with self.assertRaises(SDKValueError):
            query.where('property', '<>', 'value')

    def test_where_date_property(self):
        query = Query(self.mock_klass)
        query.where('date', '=', '20230810')
        self.assertListEqual(query.filters, [('date', '>=', DateTime(2023, 8, 10, 0, 0, 0, 0, tzinfo=ZoneInfo('UTC'))), ('date', '<=', DateTime(2023, 8, 10, 23, 59, 59, 999999, tzinfo=ZoneInfo('UTC')))])

    def test_where_date_property_with_hyphen(self):
        query = Query(self.mock_klass)
        query.where('date', '=', '2023-08-10')
        self.assertListEqual(query.filters, [('date', '>=', DateTime(2023, 8, 10, 0, 0, 0, 0, tzinfo=ZoneInfo('UTC'))), ('date', '<=', DateTime(2023, 8, 10, 23, 59, 59, 999999, tzinfo=ZoneInfo('UTC')))])

    def test_where_date_instance_property(self):
        query = Query(self.mock_klass)
        query.where('date', '=', Date(2023, 8, 10))
        self.assertListEqual(query.filters, [('date', '>=', DateTime(2023, 8, 10, 0, 0, 0, 0, tzinfo=ZoneInfo('UTC'))), ('date', '<=', DateTime(2023, 8, 10, 23, 59, 59, 999999, tzinfo=ZoneInfo('UTC')))])

    def test_where_tags_property(self):
        query = Query(self.mock_klass)
        query.where('tags', ['tag1', 'tag2'])
        self.assertListEqual(query.filters, [('tags', '=', 'tag1'), ('tags', '=', 'tag2')])

        query = Query(self.mock_klass)
        query.where('tags', 'tag')
        self.assertListEqual(query.filters, [('tags', '=', 'tag')])

    def test_where_tags_invalid(self):
        with self.assertRaisesRegex(SDKTypeError, 'The tags value must be a string or a list of strings'):
            query = Query(self.mock_klass)
            query.where('tags', {'tag1': 'tag2'})

    def test_where_name_property(self):
        query = Query(self.mock_klass)
        query.where('name', 'value')
        expected_filters = [('name', '<', 'valuf'), ('name', '>=', 'value')]
        self.assertListEqual(query.filters, expected_filters)

    def test_where_name_property_special_case(self):
        query = Query(self.mock_klass)
        query.where('name', 'z')
        expected_filters = [('name', '<', '{'), ('name', '>=', 'z')]
        self.assertListEqual(query.filters, expected_filters)

    def test_sort_by_valid_property(self):
        query = Query(self.mock_klass)
        property_name = 'date'
        result = query.sort_by(property_name)

        self.assertEqual(query.order, [property_name])
        self.assertEqual(query._clean_order, {property_name}) # pylint: disable=protected-access
        self.assertIs(result, query)

    def test_sort_by_invalid_property(self):
        query = Query(self.mock_klass)
        property_name = 'invalid_property'
        with self.assertRaises(ValueError):
            query.sort_by(property_name)

    def test_sort_by_duplicate_property(self):
        query = Query(self.mock_klass)
        property_name = 'date'
        query.order.append(property_name)
        query._clean_order.add(property_name) # pylint: disable=protected-access
        with self.assertRaises(ValueError):
            query.sort_by(property_name)

    def test_set_projection_valid_properties(self):
        properties = ['name', 'date']
        result = self.query.set_projection(properties)

        self.assertEqual(self.query.projection, properties)
        self.assertIs(result, self.query)

    def test_set_projection_only_inverse_projection(self):
        properties = ['-name', '-date']
        result = self.query.set_projection(properties)

        self.assertEqual(self.query.projection, properties)
        self.assertIs(result, self.query)

    def test_set_projection_id_on_custom_index(self):
        from everysk.sdk.entities.custom_index.base import CustomIndex # pylint: disable=import-outside-toplevel
        properties = ['id']
        query = Query(CustomIndex)
        result = query.set_projection(properties)

        self.assertEqual(query.projection, properties)
        self.assertIs(result, query)

    def test_set_projection_id_on_private_security(self):
        from everysk.sdk.entities.private_security.base import PrivateSecurity # pylint: disable=import-outside-toplevel
        properties = ['id']
        query = Query(PrivateSecurity)
        result = query.set_projection(properties)

        self.assertEqual(query.projection, properties)
        self.assertIs(result, query)

    def test_set_query_to_search_content_type_in_list(self):
        from everysk.sdk.entities.file.base import File # pylint: disable=import-outside-toplevel
        property_name = 'content_type'
        content_types = ['text/csv', 'pdf']
        query = Query(File)
        result = query.where(property_name, 'IN', content_types)

        self.assertEqual(query.filters, [(property_name, 'IN', content_types)])
        self.assertIs(result, query)

    def test_set_projection_mixed_projection(self):
        properties = ['name', '-date']
        with self.assertRaises(ValueError) as context:
            self.query.set_projection(properties)

        self.assertEqual(str(context.exception), 'Projection and Inverse Projection should not be set in the same query')

    def test_set_projection_invalid_properties(self):
        properties = ['invalid_property']
        with self.assertRaises(ValueError) as context:
            self.query.set_projection(properties)

        self.assertEqual(str(context.exception), 'Projection properties does not belongs to Portfolio: invalid_property')

    def test_set_projection_string_property(self):
        property_name = 'name'
        result = self.query.set_projection(property_name)

        self.assertEqual(self.query.projection, [property_name])
        self.assertIs(result, self.query)

    def test_set_distinct_on_string_property(self):
        property_name = 'name'
        result = self.query.set_distinct_on(property_name)

        self.assertEqual(self.query.distinct_on, [property_name])
        self.assertIs(result, self.query)

    def test_set_distinct_on_list_property(self):
        properties = ['name', 'date']
        result = self.query.set_distinct_on(properties)

        self.assertEqual(self.query.distinct_on, properties)
        self.assertIs(result, self.query)

    def test_set_limit(self):
        limit_value = 10
        result = self.query.set_limit(limit_value)

        self.assertEqual(self.query.limit, limit_value)
        self.assertIs(result, self.query)

        self.assertRaisesRegex(
            SDKValueError,
            'The limit value must be greater than or equal to 0.',
            self.query.set_limit,
            -1
        )
        self.assertRaisesRegex(
            SDKValueError,
            'The limit value must be an integer.',
            self.query.set_limit,
            [1]
        )

    def test_set_offset(self):
        offset_value = 5
        result = self.query.set_offset(offset_value)

        self.assertEqual(self.query.offset, offset_value)
        self.assertIs(result, self.query)

        self.assertRaisesRegex(
            SDKValueError,
            'The offset value must be greater than or equal to 0.',
            self.query.set_offset,
            -1
        )

        self.assertRaisesRegex(
            SDKValueError,
            'The offset value must be an integer.',
            self.query.set_offset,
            [1]
        )

    def test_set_page_size(self):
        page_size_value = 20
        result = self.query.set_page_size(page_size_value)

        self.assertEqual(self.query.page_size, page_size_value)
        self.assertIs(result, self.query)

        self.assertRaisesRegex(
            SDKValueError,
            'The page_size value must be greater than or equal to 0.',
            self.query.set_page_size,
            -1
        )

        self.assertRaisesRegex(
            SDKValueError,
            'The page_size value must be an integer.',
            self.query.set_page_size,
            [1]
        )

    def test_set_page_token(self):
        token = 'sample_token'
        result = self.query.set_page_token(token)

        self.assertEqual(self.query.page_token, token)
        self.assertIs(result, self.query)

    def test_load_with_offset(self):
        with mock.patch('everysk.sdk.entities.portfolio.base.Portfolio.generate_id', return_value='port_druyZmYpHsXbgTbC8IMmS4B2Q'):
            entity = {'id': Portfolio().generate_id(), 'name': 'Test Portfolio'}
            self.query.get_response = mock.MagicMock(return_value=entity)

            result = self.query.load(offset=1)
        self.assertIsInstance(result, Portfolio)
        self.assertEqual(result.name, 'Test Portfolio')

    def test_load_without_offset(self):
        with mock.patch('everysk.sdk.entities.portfolio.base.Portfolio.generate_id', return_value='port_druyZmYpHsXbgTbC8IMmS4B2Q'):
            entity = {'id': Portfolio().generate_id(), 'name': 'Test Portfolio'}
            self.query.get_response = mock.MagicMock(return_value=entity)

            result = self.query.load()
        self.assertIsInstance(result, Portfolio)
        self.assertEqual(result.name, 'Test Portfolio')

    def test_loads_with_limit_and_offset(self):
        with mock.patch('everysk.sdk.entities.portfolio.base.Portfolio.generate_id', return_value='port_druyZmYpHsXbgTbC8IMmS4B2Q'):

            entities = [{'id': Portfolio().generate_id(), 'name': 'Test Portfolio 1'}, {'id': Portfolio().generate_id(), 'name': 'Test Portfolio 2'}]
            self.query.get_response = mock.MagicMock(return_value=entities)

            results = self.query.loads(limit=2, offset=1)
        self.assertEqual(len(results), 2)
        self.assertIsInstance(results[0], Portfolio)
        self.assertEqual(results[0].name, 'Test Portfolio 1')

    def test_loads_without_limit_and_offset(self):
        with mock.patch('everysk.sdk.entities.portfolio.base.Portfolio.generate_id', return_value='port_druyZmYpHsXbgTbC8IMmS4B2Q'):
            entities = [{'id': Portfolio().generate_id(), 'name': 'Test Portfolio'}]
            self.query.get_response = mock.MagicMock(return_value=entities)

            results = self.query.loads()
        self.assertEqual(len(results), 1)
        self.assertIsInstance(results[0], Portfolio)
        self.assertEqual(results[0].name, 'Test Portfolio')

    def test_page_with_page_size_and_token(self):
        with mock.patch('everysk.sdk.entities.portfolio.base.Portfolio.generate_id', return_value='port_druyZmYpHsXbgTbC8IMmS4B2Q'):

            response = {
                'entities': [{'id': Portfolio().generate_id(), 'name': 'Test Portfolio'}],
                'next_page_token': 'next_token'
            }
            self.query.get_response = mock.MagicMock(return_value=response)

            result = self.query.page(page_size=10, page_token='sample_token')
        self.assertEqual(len(result['entities']), 1)
        self.assertIsInstance(result['entities'][0], Portfolio)
        self.assertEqual(result['next_page_token'], 'next_token')

    def test_page_without_token(self):
        with mock.patch('everysk.sdk.entities.portfolio.base.Portfolio.generate_id', return_value='port_druyZmYpHsXbgTbC8IMmS4B2Q'):

            response = {
                'entities': [{'id': Portfolio().generate_id(), 'name': 'Test Portfolio'}]
            }
            self.query.get_response = mock.MagicMock(return_value=response)

            result = self.query.page(page_size=10)
        self.assertEqual(len(result['entities']), 1)
        self.assertIsInstance(result['entities'][0], Portfolio)

    def test_pages(self):
        portfolio1 = Portfolio(id='port_druyZmYpHsXbgTbC8IMmS4B2Q', name='Test Portfolio 1')
        portfolio2 = Portfolio(id='port_druyZmYpHsXbgTbC8IMmS4B3Q', name='Test Portfolio 2')

        response1 = {
            'entities': [portfolio1],
            'next_page_token': 'next_token'
        }
        response2 = {
            'entities': [portfolio2]
        }

        self.query.page = mock.MagicMock(side_effect=[response1, response2])

        pages_gen = self.query.pages(page_size=10)
        first_page = next(pages_gen)
        self.assertEqual(len(first_page), 1)
        self.assertIsInstance(first_page[0], Portfolio)
        self.assertEqual(first_page[0].name, 'Test Portfolio 1')

        second_page = next(pages_gen)
        self.assertEqual(len(second_page), 1)
        self.assertIsInstance(second_page[0], Portfolio)
        self.assertEqual(second_page[0].name, 'Test Portfolio 2')

    def test_pages_break_condition(self):
        with mock.patch.object(Query, 'page') as mock_page:
            # Simulate two pages of results. First has next_page_token, second doesn't.
            mock_page.side_effect = [
                {'entities': ['entity1', 'entity2'], 'next_page_token': 'next_token'},
                {'entities': ['entity3'], 'next_page_token': None}
            ]

            pages_generator = self.query.pages(page_size=2)
            first_page = next(pages_generator)
            second_page = next(pages_generator)

            # Assert the expected values are being yielded
            self.assertEqual(first_page, ['entity1', 'entity2'])
            self.assertEqual(second_page, ['entity3'])

            # Assert the generator has exhausted
            with self.assertRaises(StopIteration):
                next(pages_generator)

            # Ensure the mock was called twice
            self.assertEqual(mock_page.call_count, 2)

    def test_fetch_ids(self):
        with mock.patch('everysk.sdk.base.BaseSDK.get_response') as mock_get_response:
            mock_get_response.return_value = ['port_druyZmYpHsXbgTbC8IMmS4B2Q']
            result = self.query.fetch_ids(limit=1, offset=2)

        self.assertListEqual(result, ['port_druyZmYpHsXbgTbC8IMmS4B2Q'])
        mock_get_response.assert_called_once_with(self_obj=self.query, params={'limit': 1, 'offset': 2})

        with mock.patch('everysk.sdk.base.BaseSDK.get_response') as mock_get_response:
            mock_get_response.return_value = []
            result = self.query.fetch_ids()

        self.assertListEqual(result, [])
        mock_get_response.assert_called_once_with(self_obj=self.query, params={'limit': Undefined, 'offset': Undefined})

    def test_fetch_id(self):
        with mock.patch('everysk.sdk.base.BaseSDK.get_response') as mock_get_response:
            mock_get_response.return_value = 'port_druyZmYpHsXbgTbC8IMmS4B2Q'
            result = self.query.fetch_id(offset=2)

        self.assertEqual(result, 'port_druyZmYpHsXbgTbC8IMmS4B2Q')
        mock_get_response.assert_called_once_with(self_obj=self.query, params={'offset': 2})

        with mock.patch('everysk.sdk.base.BaseSDK.get_response') as mock_get_response:
            mock_get_response.return_value = None
            result = self.query.fetch_id()

        self.assertIsNone(result)
        mock_get_response.assert_called_once_with(self_obj=self.query, params={'offset': Undefined})
