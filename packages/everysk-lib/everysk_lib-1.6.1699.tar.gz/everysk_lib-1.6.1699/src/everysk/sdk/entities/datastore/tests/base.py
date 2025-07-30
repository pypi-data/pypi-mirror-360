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
from everysk.core.exceptions import RequiredError, FieldValueError
from everysk.core.http import HttpSDKPOSTConnection, httpx
from everysk.core.unittests import TestCase, mock
from everysk.core.object import BaseDict

from everysk.sdk.entities.datastore.base import Datastore


###############################################################################
#   Datastore TestCase Implementation
###############################################################################
class DatastoreTestCase(TestCase):

    def setUp(self):
        self.sample_data = {
            'id': 'dats_12345678',
            'name': 'My Datastore',
            'description': 'This is a sample datastore.',
            'tags': ['tag1', 'tag2'],
            'link_uid': None,
            'workspace': 'my_workspace',
            'date': DateTime(2023, 9, 9, 9, 9, 9, 9),
            'level': '1',
            'data': {'key1': 'value1', 'key2': 'value2'},
            'version': 'v1',
            'created_on': DateTime(2023, 9, 9, 9, 9, 9, 9),
            'updated_on': DateTime(2023, 9, 9, 9, 9, 9, 9)
        }
        self.datastore = Datastore(**self.sample_data)
        self.headers = HttpSDKPOSTConnection().get_headers()
        self.api_url = HttpSDKPOSTConnection().get_url()

    def test_get_id_prefix(self):
        self.assertEqual(Datastore.get_id_prefix(), settings.DATASTORE_ID_PREFIX)

    def test_validate(self):
        expected_content = compress({'class_name': 'Datastore', 'method_name': 'validate', 'self_obj': self.datastore.to_dict(add_class_path=True), 'params': {}}, protocol='gzip', serialize='json')
        datastore: Datastore = self.datastore.copy()

        with mock.patch('httpx.Client.post') as mock_post:
            mock_post.return_value.content = '{}'
            mock_post.return_value.status_code = 200
            datastore.validate()

        mock_post.assert_called_with(
            url=self.api_url,
            headers=self.headers,
            timeout=httpx.Timeout(timeout=30, read=settings.EVERYSK_SDK_HTTP_DEFAULT_TIMEOUT),
            content=expected_content
        )

    def test_validate_error(self):
        class A:
            pass
        datastore: Datastore = self.datastore.copy()
        datastore.data = A()
        with self.assertRaisesRegex(FieldValueError, "Datastore data is not a valid json"):
            datastore.validate()

        datastore.data = None
        with self.assertRaisesRegex(RequiredError, "The data attribute is required"):
            datastore.validate()

    def test_validate_type_data(self):
        datastore: Datastore = self.datastore.copy()
        datastore.data = DateTime.now()
        datastore.validate_type_data()

        datastore.data = BaseDict(key='value')
        datastore.validate_type_data()

        datastore.data = Datastore(id='dats_1234567891011211234567890', name='SampleDatastore', workspace='SampleWorkspace')
        datastore.validate_type_data()

        datastore.data = None
        with self.assertRaisesRegex(RequiredError, "The data attribute is required"):
            datastore.validate_type_data()

    def test_query_load_with_id(self):
        expected_content = compress({'class_name': 'Datastore', 'method_name': 'retrieve', 'self_obj': None, 'params': {'entity_id': 'dats_1234567891011211234567890', 'projection': None}}, protocol='gzip', serialize='json')

        with mock.patch('httpx.Client.post') as mock_post:
            mock_post.return_value.content = '{}'
            mock_post.return_value.status_code = 200
            Datastore(id='dats_1234567891011211234567890', workspace='SampleWorkspace').load()

        mock_post.assert_called_with(
            url=self.api_url,
            headers=self.headers,
            timeout=httpx.Timeout(timeout=30, read=settings.EVERYSK_SDK_HTTP_DEFAULT_TIMEOUT),
            content=expected_content
        )

    def test_query_load(self):
        datastore = Datastore(link_uid='SampleLinkUID', workspace='SampleWorkspace')
        with mock.patch('httpx.Client.post') as mock_post:
            mock_post.return_value.content = '{}'
            mock_post.return_value.status_code = 200
            datastore.load()

        expected_content = compress({'class_name': 'Query', 'method_name': 'load', 'self_obj': datastore.to_query().to_dict(add_class_path=True), 'params': {'offset': None}}, protocol='gzip', serialize='json')
        mock_post.assert_called_with(
            url=self.api_url,
            headers=self.headers,
            timeout=httpx.Timeout(timeout=30, read=settings.EVERYSK_SDK_HTTP_DEFAULT_TIMEOUT),
            content=expected_content
        )
