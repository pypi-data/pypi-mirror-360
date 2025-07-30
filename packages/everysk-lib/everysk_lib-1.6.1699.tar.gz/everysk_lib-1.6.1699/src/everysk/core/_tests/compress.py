###############################################################################
#
# (C) Copyright 2023 EVERYSK TECHNOLOGIES
#
# This is an unpublished work containing confidential and proprietary
# information of EVERYSK TECHNOLOGIES. Disclosure, use, or reproduction
# without authorization of EVERYSK TECHNOLOGIES is prohibited.
#
###############################################################################
from everysk.core import serialize
from everysk.core.compress import compress, decompress, zip_directory_to_str
from everysk.core.datetime import DateTime, Date
from everysk.core.unittests import TestCase, mock


class CompressTestCase(TestCase):
    @mock.patch.object(serialize, 'dumps')
    def test_compress_serialize_none(self, dumps: mock.MagicMock):
        result = compress('a', serialize=None)
        self.assertEqual(result, b'x\x9cK\x04\x00\x00b\x00b')
        dumps.assert_not_called()

    @mock.patch.object(serialize, 'loads')
    def test_decompress_serialize_none(self, loads: mock.MagicMock):
        result = decompress(b'x\x9cK\x04\x00\x00b\x00b', serialize=None)
        self.assertEqual(result, b'a')
        loads.assert_not_called()

    def test_compress_protocol_invalid(self):
        with self.assertRaisesRegex(ValueError, "Unsupported compression protocol 'invalid'. Use 'zlib' or 'gzip'."):
            compress('string', protocol='invalid', serialize='json')

    def test_decompress_protocol_invalid(self):
        with self.assertRaisesRegex(ValueError, "Unsupported decompression protocol 'invalid'. Use 'zlib' or 'gzip'."):
            decompress('string', protocol='invalid', serialize='json')


class CompressZlibJsonTestCase(TestCase):

    def test_compress(self):
        string = 'aa aa aa aa aa aa aa aa'
        self.assertEqual(compress(string, protocol='zlib', serialize='json'), b'x\x9cSJLT\xc0\x86\x94\x00]\xbd\x075')

    def test_decompress(self):
        string = b'x\x9cSJLT\xc0\x86\x94\x00]\xbd\x075'
        self.assertEqual(decompress(string, protocol='zlib', serialize='json'), 'aa aa aa aa aa aa aa aa')

    def test_undefined(self):
        obj_compressed = compress(Undefined, protocol='zlib', serialize='json')
        self.assertEqual(decompress(obj_compressed, protocol='zlib', serialize='json'), Undefined)

    def test_complex_obj(self):
        obj = [
            '2024-01-01',
            {'datetime': DateTime.now()},
            {'a': 1, 'b': True},
            'Test',
            1.1,
            ['1', '2', '3', Date.today()],
            Undefined,
            {'undefined': Undefined}
        ]
        obj_compressed = compress(obj, protocol='zlib', serialize='json')
        self.assertListEqual(decompress(obj_compressed, protocol='zlib', serialize='json'), obj)


class CompressZlibPickleTestCase(TestCase):

    def setUp(self) -> None:
        self.string = 'aa aa aa aa aa aa aa aa'
        self.str_repr = b'x\x9ck`\x99*\xcd\x00\x01=\xe2\x89\x89\n\xd8\xd0\x14=\x00\x9f\xef\t\x8a'

    def test_compress(self):
        self.assertEqual(
            compress(self.string, protocol='zlib', serialize='pickle'),
            self.str_repr
        )

    def test_decompress(self):
        self.assertEqual(
            decompress(self.str_repr, protocol='zlib', serialize='pickle'),
            self.string
        )

    def test_undefined(self):
        obj_compressed = compress(Undefined, protocol='zlib', serialize='pickle')
        self.assertEqual(decompress(obj_compressed, protocol='zlib', serialize='pickle'), Undefined)

    def test_complex_obj(self):
        obj = [
            '2024-01-01',
            {'datetime': DateTime.now()},
            {'a': 1, 'b': True},
            'Test',
            1.1,
            ['1', '2', '3', Date.today()],
            Undefined,
            {'undefined': Undefined}
        ]
        obj_compressed = compress(obj, protocol='zlib', serialize='pickle')
        self.assertListEqual(decompress(obj_compressed, protocol='zlib', serialize='pickle'), obj)

###############################################################################
#   File Handling Test Case Implementation
###############################################################################
class FileHandlingTestCase(TestCase):

    @mock.patch('os.walk')
    @mock.patch('zipfile.ZipFile.write')
    def test_zip_directory_to_str_returns_expected_data(self, mock_write: mock.MagicMock, mock_walk: mock.MagicMock):
        expected_base64 = 'UEsFBgAAAAAAAAAAAAAAAAAAAAAAAA=='
        mock_walk.return_value = [
            ['/worker', '_', ['main.py']],
            ['/worker/config', '_', ['utils.py', 'config.json']],
            ['/worker/tests', '_', ['main.py']],
            ['/worker/tests/fixtures', '_', ['data.json']]
        ]

        result = zip_directory_to_str('engine/portfolio/tests', 'zip_root_folder', ['config.json'], ['**/tests*'])
        mock_write.assert_has_calls((
            mock.call('/worker/main.py', 'zip_root_folder/../../../../../worker/main.py'),
            mock.call('/worker/config/utils.py', 'zip_root_folder/../../../../../worker/config/utils.py')
        ))
        self.assertEqual(result, expected_base64)

    @mock.patch('os.walk')
    @mock.patch('zipfile.ZipFile.write')
    def test_zip_directory_to_str_without_ignore_roots(self, mock_write: mock.MagicMock, mock_walk: mock.MagicMock):
        expected_base64 = 'UEsFBgAAAAAAAAAAAAAAAAAAAAAAAA=='
        mock_walk.return_value = [
            ['/worker', '_', ['main.py']],
            ['/worker/config', '_', ['utils.py', 'config.json']],
            ['/worker/tests', '_', ['main.py']],
            ['/worker/tests/fixtures', '_', ['data.json']]
        ]

        result = zip_directory_to_str('engine/portfolio/tests', 'zip_root_folder', ['config.json'])
        mock_write.assert_has_calls((
            mock.call('/worker/main.py', 'zip_root_folder/../../../../../worker/main.py'),
            mock.call('/worker/config/utils.py', 'zip_root_folder/../../../../../worker/config/utils.py'),
            mock.call('/worker/tests/main.py', 'zip_root_folder/../../../../../worker/tests/main.py'),
            mock.call('/worker/tests/fixtures/data.json', 'zip_root_folder/../../../../../worker/tests/fixtures/data.json')
        ))
        self.assertEqual(result, expected_base64)

    @mock.patch('os.walk')
    @mock.patch('zipfile.ZipFile.write')
    def test_zip_directory_to_str_with_list_instances(self, mock_write: mock.MagicMock, mock_walk: mock.MagicMock):
        expected_base64 = 'UEsFBgAAAAAAAAAAAAAAAAAAAAAAAA=='
        mock_walk.return_value = [
            ['/worker', '_', ['main.py']],
            ['/worker/config', '_', ['utils.py', 'config.json']],
            ['/worker/tests', '_', ['main.py']],
            ['/worker/tests/fixtures', '_', ['data.json']]
        ]

        result = zip_directory_to_str('engine/portfolio/tests', 'zip_root_folder', ['config.json'], ['tests'])
        mock_write.assert_has_calls((
            mock.call('/worker/main.py', 'zip_root_folder/../../../../../worker/main.py'),
            mock.call('/worker/config/utils.py', 'zip_root_folder/../../../../../worker/config/utils.py')
        ))
        self.assertEqual(result, expected_base64)

    def test_zip_directory_to_str_with_different_size_lists_raises_error(self):
        with self.assertRaises(ValueError) as context:
            zip_directory_to_str(['engine/portfolio/tests', 'workers/libs'], 'zip_root_folder', ['config.json'], ['tests'])
        self.assertEqual(str(context.exception), 'The length of path_list and path_name_list should be the same.')

    @mock.patch('os.walk')
    @mock.patch('zipfile.ZipFile.write')
    def test_zip_directory_to_str_with_list_as_arguments(self, mock_write: mock.MagicMock, mock_walk: mock.MagicMock):
        expected_base64 = 'UEsFBgAAAAAAAAAAAAAAAAAAAAAAAA=='
        mock_walk.return_value = [
            ['/worker', '_', ['main.py']],
            ['/worker/config', '_', ['utils.py', 'config.json']],
            ['/worker/tests', '_', ['main.py']],
            ['/worker/tests/fixtures', '_', ['data.json']]
        ]

        result = zip_directory_to_str(['engine/portfolio/tests'], ['zip_root_folder'], ['config.json'], ['tests'])
        mock_write.assert_has_calls((
            mock.call('/worker/main.py', 'zip_root_folder/../../../../../worker/main.py'),
            mock.call('/worker/config/utils.py', 'zip_root_folder/../../../../../worker/config/utils.py')
        ))
        self.assertEqual(result, expected_base64)

class CompressGzipJsonTestCase(TestCase):

    def test_undefined(self):
        obj_compressed = compress(Undefined, protocol='gzip', serialize='json')
        self.assertEqual(decompress(obj_compressed, protocol='gzip', serialize='json'), Undefined)

    def test_complex_obj(self):
        obj = [
            '2024-01-01',
            {'datetime': DateTime.now()},
            {'a': 1, 'b': True},
            'Test',
            1.1,
            ['1', '2', '3', Date.today()],
            Undefined,
            {'undefined': Undefined}
        ]
        obj_compressed = compress(obj, protocol='gzip', serialize='json')
        self.assertListEqual(decompress(obj_compressed, protocol='gzip', serialize='json'), obj)


class CompressGzipPickleTestCase(TestCase):

    def test_undefined(self):
        obj_compressed = compress(Undefined, protocol='gzip', serialize='pickle')
        self.assertEqual(decompress(obj_compressed, protocol='gzip', serialize='pickle'), Undefined)

    def test_complex_obj(self):
        obj = [
            '2024-01-01',
            {'datetime': DateTime.now()},
            {'a': 1, 'b': True},
            'Test',
            1.1,
            ['1', '2', '3', Date.today()],
            Undefined,
            {'undefined': Undefined}
        ]
        obj_compressed = compress(obj, protocol='gzip', serialize='pickle')
        self.assertListEqual(decompress(obj_compressed, protocol='gzip', serialize='pickle'), obj)
