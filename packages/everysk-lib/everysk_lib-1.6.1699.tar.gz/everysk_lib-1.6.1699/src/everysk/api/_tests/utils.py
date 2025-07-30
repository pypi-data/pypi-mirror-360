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
from everysk.api.utils import EveryskObject, EveryskList, dumps_json, to_object, to_list, sleep, create_api_requestor
from everysk.core.unittests import TestCase, mock


###############################################################################
#   Everysk Object TestCase Implementation
###############################################################################
class EveryskObjectTestCase(TestCase):

    def setUp(self):
        self.retrieve_params = {}  # Mocked retrieve params if needed
        self.initial_params = {'id': '123', 'name': 'Test Object', 'valid_attr': 'value'}
        self.obj = EveryskObject(self.retrieve_params, self.initial_params)

    def test_initialization(self):
        self.assertEqual(self.obj['id'], '123')
        self.assertEqual(self.obj['name'], 'Test Object')
        self.assertEqual(self.obj.get_unsaved_values(), {})

    def test_attribute_access(self):
        self.assertEqual(self.obj.name, 'Test Object')
        self.obj.new_attr = 'New Value'
        self.assertEqual(self.obj.new_attr, 'New Value')

    def test_get_existing_attribute(self):
        self.assertEqual(self.obj.valid_attr, 'value')

    def test_access_private_attribute(self):
        # Attempt to access a "private" attribute (name starts with an underscore)
        with self.assertRaises(AttributeError) as context:
            _ = self.obj._private_attr # pylint: disable=protected-access
        self.assertEqual(context.exception.args[0], '_private_attr')

    def test_get_non_existing_attribute(self):
        # Attempt to access an attribute that does not exist
        with self.assertRaises(AttributeError) as context:
            _ = self.obj.non_existing_attr
        self.assertEqual(context.exception.args[0], 'non_existing_attr')

    def test_get_attribute_with_underscore(self):
        # Directly test the behavior with a key starting with an underscore
        # Since keys should not be private attributes, this case simulates direct dict access
        self.obj['_hidden'] = 'hidden value'
        with self.assertRaises(AttributeError) as context:
            _ = self.obj._hidden # pylint: disable=protected-access
        self.assertEqual(context.exception.args[0], '_hidden')

    def test_unsaved_values_tracking(self):
        self.obj.new_attr = 'New Value'
        self.assertIn('new_attr', self.obj.get_unsaved_values())
        self.obj.clear_unsaved_values()
        self.assertNotIn('new_attr', self.obj.get_unsaved_values())

    def test_str_representation(self):
        object_str = str(self.obj)
        self.assertIn('"id": "123"', object_str)
        self.assertIn('"name": "Test Object"', object_str)

    def test_repr_representation(self):
        object_repr = repr(self.obj)
        self.assertIn('EveryskObject', object_repr)
        self.assertIn('id=123', object_repr)
        self.assertIn('JSON: {', object_repr)

    def test_item_set_get(self):
        self.obj['new_item'] = 'Item Value'
        self.assertEqual(self.obj['new_item'], 'Item Value')
        self.assertIn('new_item', self.obj.get_unsaved_values())

    def test_del_attribute(self):
        self.obj.new_attr = 'To Be Deleted'
        del self.obj.new_attr
        with self.assertRaises(AttributeError):
            _ = self.obj.new_attr

    def test_del_attribute_with_underscore(self):
        self.obj._new_attr = 'To Be Deleted'
        del self.obj._new_attr
        with self.assertRaises(AttributeError):
            _ = self.obj._new_attr

    def test_del_item(self):
        self.obj['to_delete'] = 'Delete Me'
        del self.obj['to_delete']
        with self.assertRaises(KeyError):
            _ = self.obj['to_delete']

class MockItem:
    def __init__(self, data, params):
        self.data = data
        self.params = params

###############################################################################
#   Everysk List TestCase Implementation
###############################################################################
class EveryskListTestCase(TestCase):

    def setUp(self):
        self.retrieve_params = {'page_size': 10}
        self.response = {
            'next_page_token': 'abc123',
            'key_data': [
                {'id': '1', 'value': 'Item1'},
                {'id': '2', 'value': 'Item2'},
                {'id': '3', 'value': 'Item3'},
                {'id': '4', 'value': 'Item4'},
                {'id': '5', 'value': 'Item5'},
            ]
        }
        self.key = 'key_data'
        self.obj = EveryskList(self.retrieve_params, self.response, self.key, MockItem)

    def test_initialization(self):
        self.assertEqual(len(self.obj), 5)
        self.assertEqual(self.obj.page_size(), 10 )
        self.assertEqual(self.obj.next_page_token(), 'abc123')

    def test_page_size(self):
        self.assertEqual(self.obj.page_size(), self.retrieve_params['page_size'])

    def test_next_page_token(self):
        self.assertEqual(self.obj.next_page_token(), self.response['next_page_token'])

###############################################################################
#   Utils TestCase Implementation
###############################################################################
class UtilsTestCase(TestCase):
    def setUp(self):
        self.mock_klass = mock.MagicMock()
        self.mock_klass.return_value = 'mock_instance'

    def test_dumps_json(self):
        obj = {'key2': 'value2', 'key1': 'value1'}
        expected_output = '{\n  "key1": "value1",\n  "key2": "value2"\n}'
        self.assertEqual(dumps_json(obj), expected_output)

    def test_empty_dumps_json(self):
        obj = {}
        expected_output = "{}"
        self.assertEqual(dumps_json(obj), expected_output)

    def test_boolean_dumps_json(self):
        obj = {1: True, 2: False}
        expected_output = '{\n  "1": true,\n  "2": false\n}'
        self.assertEqual(dumps_json(obj), expected_output)

    def test_to_object_is_valid(self):
        response = {'valid_key': {'some': 'data'}}
        retrieve_params = {'param1': 'param2'}
        self.mock_klass.class_name_list = "valid_key"
        self.mock_klass.class_name.return_value = 'valid_key'
        obj = to_object(self.mock_klass, retrieve_params, response)
        self.mock_klass.assert_called_once_with(retrieve_params, response['valid_key'])
        self.assertEqual(obj, 'mock_instance')

    def test_to_object_is_none(self):
        response = {'invalid_key': ['the', 'list']}
        retrieve_params = {'param':'param2'}
        obj = to_object(self.mock_klass, retrieve_params, response)
        self.assertIsNone(obj, 'mock_instance')

    def test_to_list_is_none(self):
        response = {'valid_key': [{'item1': 'data1'}, {'item2': 'data2'}]}
        retrieve_params = {'param1': 'value1'}
        result = to_list(self.mock_klass, retrieve_params, response)
        self.assertIsNone(result)

    def test_to_list_is_valid(self):
        response = {"valid_key": [{}, {}]}
        retrieve_params = {'param1': 'value1', 'param2': 'value2'}
        self.mock_klass.class_name_list.return_value = 'valid_key'
        result = to_list(self.mock_klass, retrieve_params, response)
        self.assertIsInstance(result, EveryskList)

    @mock.patch("time.sleep")
    def test_sleep_function(self, mock_sleep):
        sleep(5)
        mock_sleep.assert_called_once_with(5)

    @mock.patch("time.sleep")
    def test_zero_sleep_value(self, mock_sleep):
        sleep(0)
        mock_sleep.assert_called_once_with(0)

    @mock.patch("time.sleep")
    def test_negative_sleep_value(self, mock_sleep):
        mock_sleep.side_effect = lambda x: exec('raise ValueError("sleep length must be non-negative.")') if x < 0 else None # pylint: disable=exec-used
        with self.assertRaises(ValueError):
            sleep(-1)

    @mock.patch("time.sleep")
    def test_invalid_sleep_value(self, mock_sleep):
        mock_sleep.side_effect = lambda x: exec('raise TypeError("str object cannot be interpreted as an integer.")') if isinstance(x, str) else None # pylint: disable=exec-used
        with self.assertRaises(TypeError):
            sleep("Invalid value")

    @mock.patch('everysk.api.utils.get_api_config')
    @mock.patch('everysk.api.api_requestor.APIRequestor')
    def test_create_api_requestor(self, mock_api_requestor, mock_get_api_config):
        mock_get_api_config.return_value = ('arg1', 'arg2')
        requestor = create_api_requestor({'some': 'params'})
        mock_get_api_config.assert_called_once_with({'some': 'params'})
        mock_api_requestor.assert_called_once_with('arg1', 'arg2')
        self.assertIsInstance(requestor, mock.MagicMock)
