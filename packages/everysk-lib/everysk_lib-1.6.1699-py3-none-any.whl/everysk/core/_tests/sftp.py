###############################################################################
#
# (C) Copyright 2025 EVERYSK TECHNOLOGIES
#
# This is an unpublished work containing confidential and proprietary
# information of EVERYSK TECHNOLOGIES. Disclosure, use, or reproduction
# without authorization of EVERYSK TECHNOLOGIES is prohibited.
#
###############################################################################
# pylint: disable=protected-access
import os
from everysk.config import settings
from everysk.core import sftp
from everysk.core.datetime import Date
from everysk.core.object import BaseDict
from everysk.core.unittests import TestCase, mock


class KnownHostsTestCase(TestCase):

    @classmethod
    def remove_known_hosts(cls):
        try:
            os.remove(f'{settings.EVERYSK_SFTP_DIR}/known_hosts')
        except FileNotFoundError:
            pass

    @classmethod
    def setUpClass(cls):
        cls.remove_known_hosts()
        cls.server = 'files.everysk.com'
        cls.content = 'files.everysk.com rsa BBBBBB'
        cls.known_hosts = sftp.KnownHosts()

    def setUp(self):
        self.known_hosts.delete(self.server)

    @classmethod
    def tearDownClass(cls):
        cls.remove_known_hosts()

    def test_filename(self):
        self.assertEqual(self.known_hosts.filename, '/tmp/sftp/known_hosts')

    @mock.patch.object(sftp, 'command')
    def test_add(self, command: mock.MagicMock):
        command.return_value.stdout.decode.return_value = self.content
        self.known_hosts.add(self.server)
        self.assertDictEqual(self.known_hosts.content, {self.server: self.content})
        command.assert_called_once_with(['ssh-keyscan', self.server], stdout=-1, check=False, stderr=-3)
        command.return_value.stdout.decode.assert_called_once_with('utf-8')
        with open(self.known_hosts.filename, 'rb') as fd:
            result = fd.read()
            self.assertEqual(result, self.content.encode('utf-8'))

    def test_check(self):
        self.known_hosts.content[self.server] = self.content
        self.assertTrue(self.known_hosts.check('files.everysk.com'))
        self.assertFalse(self.known_hosts.check('sftp.everysk.com'))

    def test_verify_file_exist(self):
        # Ensure that the file does not exists
        KnownHostsTestCase.remove_known_hosts()
        self.assertFalse(os.path.exists(self.known_hosts.filename))
        # Verify and create it
        self.assertTrue(self.known_hosts._verify_file_exist())
        self.assertTrue(os.path.exists(self.known_hosts.filename))


class SFTPTestCase(TestCase):

    def setUp(self) -> None:
        self.mock_client = mock.MagicMock(spec=sftp.SFTPClient)
        self.obj: sftp.SFTP = sftp.SFTP(
            hostname='files.everysk.com',
            port=2020,
            username='root',
            password='password',
            date=Date(2024, 11, 1),
            _client=self.mock_client
        )

    def test_del(self):
        self.obj.__del__()
        self.mock_client.close.assert_called_once_with()

    def test_enter_exit(self):
        with self.obj as sftp_client:
            self.assertEqual(sftp_client, self.obj)
        self.mock_client.close.assert_called_once_with()
        self.assertIsNone(self.obj._client)

    def test_sort(self):
        self.assertEqual(
            self.obj.sort([BaseDict(name='file1'), BaseDict(name='file3'), BaseDict(name='file2')], 'name'),
            [BaseDict(name='file1'), BaseDict(name='file2'), BaseDict(name='file3')]
        )

    def test_sort_reverse(self):
        self.assertEqual(
            self.obj.sort([BaseDict(name='file1'), BaseDict(name='file3'), BaseDict(name='file2')], 'name', reverse=True),
            [BaseDict(name='file3'), BaseDict(name='file2'), BaseDict(name='file1')]
        )

    def test_get_file(self):
        result = self.obj.get_file('file.csv')
        self.mock_client.open.assert_called_once_with('file.csv', 'rb')
        self.assertEqual(result, self.mock_client.open.return_value.__enter__.return_value.read.return_value)

    def test_get_file_with_date(self):
        result = self.obj.get_file('file_%Y-%b-%d.csv')
        self.mock_client.open.assert_called_once_with('file_2024-Nov-01.csv', 'rb')
        self.assertEqual(result, self.mock_client.open.return_value.__enter__.return_value.read.return_value)

    def test_parse_date(self):
        self.assertEqual(
            self.obj.parse_date('file_%Y-%b-%d.csv', Date(2024, 11, 1)),
            'file_2024-Nov-01.csv'
        )

    @mock.patch.object(sftp, 'command')
    @mock.patch.object(sftp, 'SSHClient')
    def test_get_sftp_client(self, client: mock.MagicMock, command: mock.MagicMock):
        sftp.KnownHosts().delete('files.everysk.com')
        command.return_value.stdout.decode.return_value = 'files.everysk.com rsa BBBBBB'
        result = self.obj.get_sftp_client('files.everysk.com', 2020, 'root', 'password', True, 60)
        # command.assert_has_calls([
        #     mock.call(['ssh-keyscan', 'files.everysk.com'], stdout=-1, check=False, stderr=-3),
        #     mock.call().stdout.decode('utf-8')
        # ])
        client.assert_has_calls([
            mock.call(),
            mock.call().set_missing_host_key_policy(sftp.AutoAddPolicy),
            mock.call().connect(hostname='files.everysk.com', port=2020, username='root', password='password', compress=True, timeout=60),
            mock.call().open_sftp()
        ])
        self.assertEqual(result, client.return_value.open_sftp.return_value)
        # Clear known hosts
        sftp.KnownHosts().delete('files.everysk.com')

    @mock.patch.object(sftp, 'command')
    @mock.patch.object(sftp, 'SSHClient')
    def test_get_sftp_client_with_private_key(self, client: mock.MagicMock, command: mock.MagicMock):
        sftp.KnownHosts().delete('files.everysk.com')
        command.return_value.stdout.decode.return_value = 'files.everysk.com rsa BBBBBB'
        with open('/var/app/src/everysk/core/fixtures/test.pem', mode='r', encoding='utf-8') as f:
            private_key = f.read()

        result = self.obj.get_sftp_client('files.everysk.com', 2020, 'root', private_key=private_key, passphrase='passphrase')
        # command.assert_has_calls([
        #     mock.call(['ssh-keyscan', 'files.everysk.com'], stdout=-1, check=False, stderr=-3),
        #     mock.call().stdout.decode('utf-8')
        # ])

        self.assertEqual(result, client.return_value.open_sftp.return_value)
        # Clear known hosts
        sftp.KnownHosts().delete('files.everysk.com')

    def test_search_by_last_modification_time(self):
        self.mock_client.listdir_attr.return_value = [
            mock.MagicMock(filename='dir01', st_mtime=1000, longname='drwxrwxrwx '),
            mock.MagicMock(filename='dir02', st_mtime=2000, longname='drwxrwxrwx '),
            mock.MagicMock(filename='file.csv', st_mtime=3000, longname='rwxrwxrwx '),
            mock.MagicMock(filename='file2.csv', st_mtime=2000, longname='rwxrwxrwx ')
        ]
        result = self.obj.search_by_last_modification_time('/dir00', 'file')
        self.assertEqual(result, '/dir00/file.csv')

    def test_search_by_last_modification_time_date(self):
        self.mock_client.listdir_attr.return_value = [
            mock.MagicMock(filename='dir01', st_mtime=1000, longname='drwxrwxrwx '),
            mock.MagicMock(filename='dir02', st_mtime=2000, longname='drwxrwxrwx '),
            mock.MagicMock(filename='file_01_11_2024.csv', st_mtime=3000, longname='rwxrwxrwx '),
            mock.MagicMock(filename='file_02_11_2024.csv', st_mtime=4000, longname='rwxrwxrwx ')
        ]
        result = self.obj.search_by_last_modification_time('/dir00', 'file_%d_%m_%Y')
        self.assertEqual(result, '/dir00/file_01_11_2024.csv')

    def test_search_by_last_modification_time_not_found(self):
        self.mock_client.listdir_attr.return_value = [
            mock.MagicMock(filename='file.csv', st_mtime=3000, longname='rwxrwxrwx '),
            mock.MagicMock(filename='file2.csv', st_mtime=2000, longname='rwxrwxrwx ')
        ]
        result = self.obj.search_by_last_modification_time('/dir00', 'file3')
        self.assertIsNone(result)

    def test_search_by_last_modification_time_recursive(self):
        self.mock_client.listdir_attr.side_effect = [
            [
                mock.MagicMock(filename='dir01', st_mtime=1000, longname='drwxrwxrwx ')
            ],
            [
                mock.MagicMock(filename='dir011', st_mtime=4000, longname='drwxrwxrwx ')
            ],
            [
                mock.MagicMock(filename='file1.csv', st_mtime=5000, longname='rwxrwxrwx ')
            ]
        ]
        result = self.obj.search_by_last_modification_time('/dir00', 'file1')
        self.assertEqual(result, '/dir00/dir01/dir011/file1.csv')

    def test_save_file(self):
        self.obj.save_file('/dir01/%Y/%m/file_%Y.csv', b'content')
        self.mock_client.open.assert_called_once_with('/dir01/2024/11/file_2024.csv', 'wb')
        self.mock_client.open.return_value.__enter__.return_value.write.assert_called_once_with(b'content')
        self.mock_client.mkdir.assert_has_calls([
            mock.call('/dir01'),
            mock.call('/dir01/2024'),
            mock.call('/dir01/2024/11')
        ])
