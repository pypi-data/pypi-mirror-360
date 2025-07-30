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
from everysk.api import utils
from everysk.api.utils import EveryskList
from everysk.api.api_resources.api_resource import (
    APIResource,
    RetrievableAPIResource,
    ListableAPIResource,
    DeletableAPIResource,
    CreateableAPIResource,
    FilterableAPIResource,
    UpdateableAPIResource
)
from everysk.core.unittests import TestCase, mock


###############################################################################
#   Mocking Classes Implementation
###############################################################################
class MockAPIResource(APIResource):
    @classmethod
    def class_name(cls):
        return 'testresource'

class MockAPIResourceEndsWithY(APIResource):
    @classmethod
    def class_name(cls):
        return 'testresourcey'

class MockAPIResourceEndsWithX(RetrievableAPIResource):
    @classmethod
    def class_name(cls):
        return 'testresourcex'

###############################################################################
#   APIResource TestCase Implementation
###############################################################################
@mock.patch.object(utils, 'create_api_requestor')
class APIResourceTestCase(TestCase):

    def setUp(self):
        self.retrieve_params = {'key1': 'value1', 'key2': 'value2'}
        self.params = {'param1': 'value1', 'param2': 'value2'}
        self.obj = APIResource(self.retrieve_params, self.params)

    def test_refresh_method(self, mock_utils_create_api: mock.MagicMock):
        resource = MockAPIResource({'param': 'value'}, {})
        resource.update = mock.MagicMock()
        resource.clear_unsaved_values = mock.MagicMock()
        api_requestor = mock_utils_create_api.return_value
        api_requestor.get.return_value = {'testresource': {'id': '123', 'name': 'Test Resource'}}
        result = resource.refresh()

        self.assertIsInstance(result, MockAPIResource)

    def test_class_name_list(self,  mock_utils_create_api: mock.MagicMock): # pylint: disable=unused-argument
        self.assertEqual(MockAPIResource.class_name_list(), 'testresources')

    def test_class_name_list_endswith_y(self,  mock_utils_create_api: mock.MagicMock): # pylint: disable=unused-argument
        self.assertEqual(MockAPIResourceEndsWithY.class_name_list(), 'testresourceies')

    def test_class_name_list_endswith_x(self,  mock_utils_create_api: mock.MagicMock): # pylint: disable=unused-argument
        self.assertEqual(MockAPIResourceEndsWithX.class_name_list(), 'testresourcexes')

    def test_class_url(self,  mock_utils_create_api: mock.MagicMock): # pylint: disable=unused-argument
        self.assertEqual(MockAPIResource.class_url(), '/testresources')

###############################################################################
#   Retrievable APIResource TestCase Implementation
###############################################################################
class MockRetrievableAPIResourceClassName(RetrievableAPIResource):

    @classmethod
    def class_name(cls):
        return 'retrievable'

class RetrievableAPIResourceTestCase(TestCase):

    @mock.patch('everysk.api.utils.create_api_requestor')
    def test_retrieve_method(self, mock_create_api_requestor):
        mock_api_requestor = mock.Mock()
        mock_create_api_requestor.return_value = mock_api_requestor

        mock_response_data = {'retrievable': {'id': '123', 'attribute': 'value'}}
        mock_api_requestor.get.return_value = mock_response_data
        test_params = {'key1': 'value1'}
        test_id = '123'
        expected_url = '/retrievables/123'
        response = MockRetrievableAPIResourceClassName.retrieve(test_id, **test_params)

        mock_api_requestor.get.assert_called_with(expected_url, test_params)
        self.assertIsInstance(response, MockRetrievableAPIResourceClassName)

###############################################################################
#   Listable APIResource TestCase Implementation
###############################################################################
class MockListableAPIResourceClassName(ListableAPIResource):

    @classmethod
    def class_name(cls):
        return 'listable'

class ListableAPIResourceTestCase(TestCase):

    @mock.patch('everysk.api.utils.create_api_requestor')
    def test_list_method(self, mock_create_api_requestor):
        mock_api_requestor = mock.Mock()
        mock_create_api_requestor.return_value = mock_api_requestor

        key_expected = MockListableAPIResourceClassName.class_name_list()
        mock_response_data = {
            key_expected: [{'id': '123', 'name': 'test_object'}]
        }
        mock_api_requestor.get.return_value = mock_response_data
        test_params = {'param1': 'value1'}
        result = MockListableAPIResourceClassName.list(**test_params)
        expected_url = MockListableAPIResourceClassName.class_url()

        mock_api_requestor.get.assert_called_once_with(expected_url, test_params)
        self.assertIsInstance(result, EveryskList)
        self.assertEqual(result[0]['id'], '123')
        self.assertEqual(result[0]['name'], 'test_object')

    @mock.patch('everysk.api.api_resources.api_resource.ListableAPIResource.list')
    def test_auto_paging_iter(self, mock_list):
        MockListableAPIResourceClassName = mock.MagicMock()
        MockListableAPIResourceClassName.class_url.return_value = '/test_url'
        MockListableAPIResourceClassName.class_name.return_value = 'items'

        first_page_response = {
            'items': [{'id': 3}, {'id': 4}],
            'next_page_token': 'token123'
        }
        second_page_response = {
            'items': [{'id': 3}, {'id': 4}],
            'next_page_token': None
        }
        first_page = EveryskList({}, first_page_response, 'items', MockListableAPIResourceClassName)
        second_page = EveryskList({'page_token': 'token123'}, second_page_response, 'items', MockListableAPIResourceClassName)
        mock_list.side_effect = [first_page, second_page]
        all_items = list(ListableAPIResource.auto_paging_iter())

        self.assertEqual(len(all_items), 4)

###############################################################################
#   Deletable APIResource TestCase Implementation
###############################################################################
class MockDeletableAPIResourceClassName(DeletableAPIResource):

    @classmethod
    def class_name(cls):
        return 'ResourceName'

class DeletableAPIResourceTestCase(TestCase):

    def setUp(self):
        retrieve_params = {'param1': 'value1'}
        params = {'params': 'value'}
        self.resource = MockDeletableAPIResourceClassName(retrieve_params, params)
        self.resource.id = '123'
        self.resource.workspace = 'default'

    @mock.patch('everysk.api.utils.create_api_requestor')
    def test_delete_success(self, mock_create_api_requestor):
        mock_requestor = mock.Mock()
        mock_create_api_requestor.return_value = mock_requestor
        mock_response = {'ResourceName': {'id': '123', 'status': 'deleted'}}
        mock_requestor.delete.return_value = mock_response

        result = self.resource.delete()

        expected_url = '/ResourceNames/123?workspace=default'
        mock_requestor.delete.assert_called_with(expected_url)

        # Check the resulting state of the object
        self.assertEqual(result.id, '123')
        self.assertEqual(result.status, 'deleted')

    @mock.patch('everysk.api.utils.create_api_requestor')
    def test_remove_method(self, mock_create_api_requestor):
        mock_api_requestor = mock.Mock()
        mock_create_api_requestor.return_value = mock_api_requestor
        mock_response = {'ResourceName': {'id': '123', 'attribute': 'value'}}
        mock_api_requestor.delete.return_value = mock_response

        # Call the class method 'remove'
        result = MockDeletableAPIResourceClassName.remove('123', workspace='default')

        # Verify API call
        expected_url = '/ResourceNames/123?workspace=default'
        mock_api_requestor.delete.assert_called_with(expected_url)

        # Verify the returned object
        self.assertIsInstance(result, MockDeletableAPIResourceClassName)
        self.assertEqual(result.id, '123')
        self.assertEqual(result.attribute, 'value')

###############################################################################
#   Creatable APIResource TestCase Implementation
###############################################################################
class MockCreatableAPIResourceClassName(CreateableAPIResource):

    @classmethod
    def class_name(cls):
        return 'creatable'

class CreatableAPIResourceTestCase(TestCase):

    @mock.patch('everysk.api.utils.create_api_requestor')
    def test_create_method(self, mock_create_api_requestor):
        mock_api_requestor = mock.Mock()
        mock_create_api_requestor.return_value = mock_api_requestor

        mock_response_data = {'creatable': {'key': 'data'}}
        mock_api_requestor.post.return_value = mock_response_data
        kwargs = {'param1': 'value1', 'param2': 'value2'}
        expected_url = '/creatables'
        result = MockCreatableAPIResourceClassName.create(**kwargs)

        mock_api_requestor.post.assert_called_once_with(expected_url, kwargs)
        self.assertIsInstance(result, MockCreatableAPIResourceClassName)

###############################################################################
#   Filterable APIResource TestCase Implementation
###############################################################################
class MockFilterableAPIResourceClassName(FilterableAPIResource):

    @classmethod
    def class_name(cls):
        return 'filterable'

class FilterableAPIResourceTestCase(TestCase):

    @mock.patch('everysk.api.utils.create_api_requestor')
    def test_filter_method(self, mock_create_api_requestor):
        mock_api_requestor = mock.Mock()
        mock_api_requestor.post.return_value = mock_api_requestor
        mock_create_api_requestor.return_value = mock_api_requestor

        key_expected = MockFilterableAPIResourceClassName.class_name_list()
        mock_response_data = {
            key_expected : [{'id': '123', 'name': 'test_object'}]
        }
        mock_api_requestor.post.return_value = mock_response_data
        test_params = {'param1': 'value1'}
        expected_url = f'{MockFilterableAPIResourceClassName.class_url()}/filter'
        result = MockFilterableAPIResourceClassName.filter(**test_params)

        mock_api_requestor.post.assert_called_once_with(expected_url, test_params)
        self.assertIsInstance(result, EveryskList)

###############################################################################
#   Updatable APIResource TestCase Implementation
###############################################################################
class MockUpdatableAPIResourceClassName(UpdateableAPIResource):
    @classmethod
    def class_name(cls):
        return 'updatable'

class UpdatableAPIResourceTestCase(TestCase):

    @mock.patch('everysk.api.utils.create_api_requestor')
    def test_modify_method(self, mock_create_api_requestor):
        mock_api_requestor = mock.Mock()
        mock_api_requestor.put.return_value = mock_api_requestor
        mock_create_api_requestor.return_value = mock_api_requestor

        mock_response = {
            'updatable': {'id': '123', 'attribute': 'value'}
        }
        mock_api_requestor.put.return_value = mock_response
        result = MockUpdatableAPIResourceClassName.modify('123', attr='new_value')

        mock_api_requestor.put.assert_called_once_with('/updatables/123', {'attr': 'new_value'})
        self.assertIsInstance(result, MockUpdatableAPIResourceClassName)

    @mock.patch('everysk.api.utils.create_api_requestor')
    def test_save_method(self, mock_create_api_requestor):
        mock_api_requestor = mock.Mock()
        mock_create_api_requestor.return_value = mock_api_requestor

        mock_response = {
            'updatable': {'id': '123', 'attribute': 'new_value'}
        }
        mock_api_requestor.put.return_value = mock_response
        retrieve_params = {'key1': 'value1', 'key2': 'value2'}
        params = {'param1': 'value1', 'param2': 'value2'}
        instance = MockUpdatableAPIResourceClassName(retrieve_params, params)
        instance.id = '123'
        unsaved_values = {'id': '123'}
        instance.save()
        expected_url = '/updatables/123'

        mock_api_requestor.put.assert_called_once_with(expected_url, unsaved_values)
        instance.update(mock_response['updatable'])
        self.assertEqual(instance.get('attribute'), 'new_value')
