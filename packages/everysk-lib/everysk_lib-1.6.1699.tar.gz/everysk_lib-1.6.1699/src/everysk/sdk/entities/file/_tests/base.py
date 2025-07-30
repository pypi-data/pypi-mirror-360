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
from everysk.core.exceptions import RequiredError, SDKValueError
from everysk.core.http import HttpSDKPOSTConnection, httpx
from everysk.core.unittests import TestCase, mock

from everysk.sdk.entities.file.base import File


###############################################################################
#   File TestCase Implementation
###############################################################################
class FileTestCase(TestCase):

    def setUp(self):
        self.sample_data = {
            'id': 'file_1234567891011211234567890',
            'name': 'SampleFile',
            'tags': ['tag1', 'tag2'],
            'description': 'Description',
            'link_uid': 'link_uid',
            'workspace': 'main',
            'date': DateTime(2023, 9, 9, 9, 9, 9, 9),
            'data': 'base64data',
            'url': '/1234567891011211234567890',
            'content_type': 'text/csv',
            'version': '1.0',
            'created_on': DateTime(2023, 9, 9, 9, 9, 9, 9),
            'updated_on': DateTime(2023, 9, 9, 9, 9, 9, 9),
            'hash': '4a0ed08522000734bb845f5d72673d9d113c8236',
        }
        self.file = File(**self.sample_data)
        self.headers = HttpSDKPOSTConnection().get_headers()
        self.api_url = HttpSDKPOSTConnection().get_url()

    def test_get_id_prefix(self):
        self.assertEqual(File.get_id_prefix(), settings.FILE_ID_PREFIX)

    def test_validate(self):
        expected_content = compress({'class_name': 'File', 'method_name': 'validate', 'self_obj': self.file.to_dict(add_class_path=True), 'params': {}}, protocol='gzip', serialize='json')
        file: File = self.file.copy()

        with mock.patch('httpx.Client.post') as mock_post:
            mock_post.return_value.content = '{}'
            mock_post.return_value.status_code = 200
            file.validate()

        mock_post.assert_called_with(
            url=self.api_url,
            headers=self.headers,
            timeout=httpx.Timeout(timeout=30, read=settings.EVERYSK_SDK_HTTP_DEFAULT_TIMEOUT),
            content=expected_content
        )

    def test_validate_transient(self):
        expected_content = compress({'class_name': 'File', 'method_name': 'validate_transient', 'self_obj': None, 'params': {'entity_dict': self.file.to_dict(add_class_path=True)}}, protocol='gzip', serialize='json')
        file: File = self.file.copy()

        with mock.patch('httpx.Client.post') as mock_post:
            mock_post.return_value.content = '{}'
            mock_post.return_value.status_code = 200
            File.validate_transient(file)

        mock_post.assert_called_with(
            url=self.api_url,
            headers=self.headers,
            timeout=httpx.Timeout(timeout=30, read=settings.EVERYSK_SDK_HTTP_DEFAULT_TIMEOUT),
            content=expected_content
        )

    def test_entity_to_query(self):
        file: File = self.file.copy()
        self.assertRaisesRegex(
            SDKValueError,
            "Can't filter by Name and Tags at the same time",
            file.to_query
        )

        # Test with name
        file.pop('tags')
        file.pop('link_uid')
        file.pop('url')
        query = file.to_query() #pylint: disable=protected-access
        self.assertListEqual(query.filters, [
            ('workspace', '=', 'main'),
            ('name', '<', 'samplefilf'),
            ('name', '>=', 'samplefile'),
            ('date', '>=', self.sample_data['date'].replace(hour=0, minute=0, second=0, microsecond=0)),
            ('date', '<=', self.sample_data['date'].replace(hour=23, minute=59, second=59, microsecond=999999)),
        ])
        self.assertEqual(query.order, [])
        self.assertEqual(query.projection, None)
        self.assertEqual(query.limit, None)
        self.assertEqual(query.offset, None)
        self.assertEqual(query.page_size, None)
        self.assertEqual(query.page_token, None)
        self.assertEqual(query.distinct_on, [])

        # Test with tags
        file.update({'name': None, 'tags': ['tag1', 'tag2']})
        query = file.to_query() #pylint: disable=protected-access
        self.assertListEqual(query.filters, [
            ('workspace', '=', 'main'),
            ('date', '>=', self.sample_data['date'].replace(hour=0, minute=0, second=0, microsecond=0)),
            ('date', '<=', self.sample_data['date'].replace(hour=23, minute=59, second=59, microsecond=999999)),
            ('tags', '=', 'tag1'),
            ('tags', '=', 'tag2')
        ])

        # Test with link_uid
        file.update({'tags': None, 'link_uid': 'link_uid'})
        query = file.to_query() #pylint: disable=protected-access
        self.assertListEqual(query.filters, [
            ('workspace', '=', 'main'),
            ('link_uid', '=', 'link_uid'),
             ('date', '>=', self.sample_data['date'].replace(hour=0, minute=0, second=0, microsecond=0)),
            ('date', '<=', self.sample_data['date'].replace(hour=23, minute=59, second=59, microsecond=999999))
        ])

        # Test with url
        file.update({'link_uid': None, 'url': '/1234567891011211234567890'})
        query = file.to_query() #pylint: disable=protected-access
        self.assertListEqual(query.filters, [
            ('workspace', '=', 'main'),
              ('date', '>=', self.sample_data['date'].replace(hour=0, minute=0, second=0, microsecond=0)),
            ('date', '<=', self.sample_data['date'].replace(hour=23, minute=59, second=59, microsecond=999999)),
            ('url', '=', '/1234567891011211234567890')
        ])

    def test_generate_url(self):
        file: File = self.file.copy()
        url = file.generate_url()
        with mock.patch('everysk.sdk.entities.file.base.generate_unique_id') as mock_generate_unique_id:
            mock_generate_unique_id.return_value = '1234567891011211234567890'
            url = file.generate_url()
        self.assertEqual(url, '/1234567891011211234567890')

    def test_required_fields(self):
        file: File = self.file.copy()
        file.id = None
        self.assertRaisesRegex(
            RequiredError,
            'The id attribute is required.',
            file.validate_required_fields
        )

        file.id = 'file_1234567891011211234567890'
        file.name = None
        self.assertRaisesRegex(
            RequiredError,
            'The name attribute is required.',
            file.validate_required_fields
        )

        file.name = 'SampleFile'
        file.workspace = None
        self.assertRaisesRegex(
            RequiredError,
            'The workspace attribute is required.',
            file.validate_required_fields
        )

        file.workspace = 'main'
        file.date = None
        self.assertRaisesRegex(
            RequiredError,
            'The date attribute is required.',
            file.validate_required_fields
        )

        file.date = DateTime(2023, 9, 9, 9, 9, 9, 9)
        file.hash = None
        self.assertRaisesRegex(
            RequiredError,
            'The hash attribute is required.',
            file.validate_required_fields
        )

        file.hash = '4a0ed08522000734bb845f5d72673d9d113c8236'
        file.data = None
        self.assertRaisesRegex(
            RequiredError,
            'The data attribute is required.',
            file.validate_required_fields
        )

        file.data = 'base64data'
        file.content_type = None
        self.assertRaisesRegex(
            RequiredError,
            'The content_type attribute is required.',
            file.validate_required_fields
        )

        file.content_type = 'text/csv'
        file.url = None
        self.assertRaisesRegex(
            RequiredError,
            'The url attribute is required.',
            file.validate_required_fields
        )

    def test_check_query_raises_sdk_error(self):
        with self.assertRaises(SDKValueError) as context:
            file: File = self.file.copy()
            file['tags'] = []
            file['link_uid'] = ''
            file.to_query(limit=1)

        self.assertEqual(str(context.exception), "Can't filter by URL and Name, Tags or Link UID at the same time")

    def test_to_dict_file(self):
        result = self.file.to_dict()
        expected_data = {
            'id': 'file_1234567891011211234567890',
            'name': 'SampleFile',
            'tags': ['tag1',
            'tag2'],
            'description': 'Description',
            'link_uid': 'link_uid',
            'workspace': 'main',
            'date': '20230909',
            'data': 'base64data',
            'url': '/file/1234567891011211234567890',
            'content_type': 'text/csv',
            'version': '1.0',
            'hash': '4a0ed08522000734bb845f5d72673d9d113c8236',
            'date_time': '20230909 09:09:09',
            'created': 1694250549,
            'updated': 1694250549
        }

        self.assertIsInstance(result, dict)
        self.assertEqual(result, expected_data)

    def test_file_content_types(self):
        file_types = settings.FILE_CONTENT_TYPES
        expected = [
            None,
            'application/csv',
            'application/javascript',
            'application/json',
            'application/msword',
            'application/octet-stream',
            'application/pdf',
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/x-zip-compressed',
            'application/xml',
            'application/zip',
            'image/bmp',
            'image/gif',
            'image/jpeg',
            'image/png',
            'image/svg+xml',
            'image/webp',
            'text/comma-separated-values',
            'text/csv',
            'text/plain',
            'text/x-comma-separated-values',
            'text/xml',
            'audio/mpeg',
            'audio/wav'
        ]
        self.assertEqual(file_types, expected)
