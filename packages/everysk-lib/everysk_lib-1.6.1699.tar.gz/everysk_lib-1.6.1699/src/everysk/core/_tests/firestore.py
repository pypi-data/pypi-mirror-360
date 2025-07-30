###############################################################################
#
# (C) Copyright 2023 EVERYSK TECHNOLOGIES
#
# This is an unpublished work containing confidential and proprietary
# information of EVERYSK TECHNOLOGIES. Disclosure, use, or reproduction
# without authorization of EVERYSK TECHNOLOGIES is prohibited.
#
###############################################################################
# pylint: disable=invalid-name, protected-access
from os import environ
from everysk.config import settings
from everysk.core import firestore, redis as redis_module
from everysk.core.compress import compress
from everysk.core.datetime import Date, DateTime
from everysk.core.exceptions import FieldValueError
from everysk.core.object import BaseDict
from everysk.core.threads import ThreadPool
from everysk.core.unittests import TestCase, mock


def _test_connection(Client: mock.MagicMock):
    doc = firestore.FirestoreClient(project_name='P01', database_name='D01')
    assert doc.connection == Client.return_value

@mock.patch.object(firestore.firestore, 'Client')
class FirestoreClientTestCase(TestCase):

    def setUp(self) -> None:
        firestore.FirestoreClient._connections = {}

    def test_connections(self, Client: mock.MagicMock):
        doc01 = firestore.FirestoreClient(project_name='P01', database_name='D01')
        self.assertEqual(doc01.project_name, 'P01')
        self.assertEqual(doc01.database_name, 'D01')
        self.assertEqual(doc01.connection, Client.return_value)
        Client.assert_called_once_with(project='P01', database='D01')

        Client.reset_mock()
        doc02 = firestore.FirestoreClient(project_name='P02', database_name='D02')
        self.assertEqual(doc02.project_name, 'P02')
        self.assertEqual(doc02.database_name, 'D02')
        self.assertEqual(doc02.connection, Client.return_value)
        Client.assert_called_once_with(project='P02', database='D02')

    def test_concurrent_connections(self, Client: mock.MagicMock):
        pool = ThreadPool(4)
        for i in range(0, 13): # pylint: disable=unused-variable
            pool.add(
                target=_test_connection,
                kwargs={'Client': Client}
            )
        pool.wait()
        Client.assert_called_once_with(project='P01', database='D01')

    @mock.patch.object(firestore, 'RedisLock')
    def test_connection_lock(self, RedisLock: mock.MagicMock, Client: mock.MagicMock):
        doc01 = firestore.FirestoreClient(project_name='P01', database_name='D01')
        doc01.connection # pylint: disable=pointless-statement
        Client.assert_called_once_with(project='P01', database='D01')
        RedisLock.assert_called_once_with(name='everysk-lib-firestore-lock-connection-P01-D01', timeout=600)
        RedisLock.return_value.acquire.assert_called_once_with(blocking=True)
        RedisLock.return_value.release.assert_called_once_with()

    @mock.patch.object(firestore, 'RedisLock')
    def test_connection_error(self, RedisLock: mock.MagicMock, Client: mock.MagicMock):
        Client.side_effect = AttributeError('Erro')
        doc01 = firestore.FirestoreClient(project_name='P01', database_name='D01')
        with self.assertRaisesRegex(AttributeError, 'Erro'):
            doc01.connection # pylint: disable=pointless-statement
        Client.assert_called_once_with(project='P01', database='D01')
        RedisLock.assert_called_once_with(name='everysk-lib-firestore-lock-connection-P01-D01', timeout=600)
        RedisLock.return_value.acquire.assert_called_once_with(blocking=True)
        RedisLock.return_value.release.assert_called_once_with()

    def test_init_default(self, Client: mock.MagicMock):
        client = firestore.FirestoreClient()
        self.assertEqual(client.database_name, firestore._DEFAULT_DATABASE)
        self.assertEqual(client.project_name, settings.EVERYSK_GOOGLE_CLOUD_PROJECT)
        Client.assert_not_called()

    def test_init_params(self, Client: mock.MagicMock):
        client = firestore.FirestoreClient(project_name='PROJECT', database_name='DATABASE')
        self.assertEqual(client.database_name, 'DATABASE')
        self.assertEqual(client.project_name, 'PROJECT')
        Client.assert_not_called()

    def test_get_collection(self, Client: mock.MagicMock):
        client = firestore.FirestoreClient()
        collection = client.get_collection('my-collection')
        self.assertEqual(collection, Client.return_value.collection.return_value)
        Client.return_value.collection.assert_called_once_with('my-collection')

    def test_environment_values(self, Client: mock.MagicMock):
        environ['EVERYSK_GOOGLE_CLOUD_PROJECT'] = 'PROJECT'
        client = firestore.FirestoreClient()
        self.assertEqual(client.project_name, 'PROJECT')
        Client.assert_not_called()
        del environ['EVERYSK_GOOGLE_CLOUD_PROJECT']


@mock.patch.object(firestore.firestore, 'Client')
class BaseDocumentConfigTestCase(TestCase):

    def setUp(self) -> None:
        firestore.FirestoreClient._connections = {}

    def test_client(self, Client: mock.MagicMock):
        obj = firestore.BaseDocumentConfig(collection_name='test-collection')
        self.assertIsInstance(obj.client, firestore.FirestoreClient)
        Client.assert_not_called()

    def test_collection(self, Client: mock.MagicMock):
        obj = firestore.BaseDocumentConfig(collection_name='test-collection')
        self.assertEqual(obj.collection, Client.return_value.collection.return_value)
        Client.return_value.collection.assert_called_once_with('test-collection')

    def test_collection_empty(self, Client: mock.MagicMock):
        obj = firestore.BaseDocumentConfig()
        with self.assertRaisesRegex(AttributeError, 'The collection_name is empty.'):
            obj.collection # pylint: disable=pointless-statement
        Client.return_value.collection.assert_not_called()

    def test_excluded_keys(self, Client: mock.MagicMock):
        obj = firestore.BaseDocumentConfig(collection_name='test-collection')
        self.assertListEqual(obj.excluded_keys, [])
        Client.assert_not_called()


class FakeObject:
    """ Used to test pickle and unpickle """
    value: int = 1

    def __eq__(self, __value: object) -> bool:
        return self.__class__ == __value.__class__ and self.value == __value.value


@mock.patch.object(firestore.firestore, 'Client')
class DocumentTestCase(TestCase):

    def setUp(self) -> None:
        firestore.FirestoreClient._connections = {}
        firestore.Document._config._client = None

    def test_config(self, Client: mock.MagicMock):
        doc = firestore.Document()
        self.assertIsInstance(doc._config, firestore.BaseDocumentConfig)
        Client.assert_not_called()

    @mock.patch.object(firestore.DateTime, 'now', return_value='2022-01-01T10:00:00+00:00')
    def test_init(self, now: mock.MagicMock, Client: mock.MagicMock):
        doc = firestore.Document(key='value', firestore_id='my-id')
        self.assertEqual(doc.firestore_id, 'my-id')
        self.assertEqual(doc.created_at, DateTime.fromisoformat('2022-01-01T10:00:00+00:00'))
        self.assertEqual(doc.key, 'value')
        now.assert_called_once_with()
        Client.assert_not_called()

    def test_parse_in(self, Client: mock.MagicMock):
        doc = firestore.Document(
            dct={'a': 1},
            lst=[1, 2, 3],
            date='2022-01-01',
            datetime='2022-01-01T10:00:00+00:00',
            obj=compress(FakeObject(), serialize='pickle'),
            byte=b'Text',
            base_dict=BaseDict(key='2022-01-01'),
            str_not_date='20240101'
        )
        self.assertDictEqual(doc.dct, {'a': 1})
        self.assertListEqual(doc.lst, [1, 2, 3])
        self.assertEqual(doc.date, Date.fromisoformat('2022-01-01'))
        self.assertEqual(doc.datetime, DateTime.fromisoformat('2022-01-01T10:00:00+00:00'))
        self.assertEqual(doc.obj, FakeObject())
        self.assertEqual(doc.byte, b'Text')
        self.assertDictEqual(doc.base_dict, BaseDict(key=Date.fromisoformat('2022-01-01')))
        self.assertEqual(doc.str_not_date, '20240101')
        Client.assert_not_called()

    def test_parse_in_with_invalid_str_date(self, Client: mock.MagicMock):
        doc = firestore.Document(
            dct={'a': 1},
            lst=[1, 2, 3],
            date='b-a-t',
            datetime='2022-01-01T10:00:00+00:00',
            obj=compress(FakeObject(), serialize='pickle'),
            byte=b'Text',
            base_dict=BaseDict(key='2022-01-01'),
            str_not_date='20240101'
        )
        self.assertDictEqual(doc.dct, {'a': 1})
        self.assertListEqual(doc.lst, [1, 2, 3])
        self.assertEqual(doc.date, 'b-a-t')
        self.assertEqual(doc.datetime, DateTime.fromisoformat('2022-01-01T10:00:00+00:00'))
        self.assertEqual(doc.obj, FakeObject())
        self.assertEqual(doc.byte, b'Text')
        self.assertDictEqual(doc.base_dict, BaseDict(key=Date.fromisoformat('2022-01-01')))
        self.assertEqual(doc.str_not_date, '20240101')
        Client.assert_not_called()

    def test_parser_out(self, Client: mock.MagicMock):
        doc = firestore.Document()
        self.assertDictEqual(doc._parser_out({'a': 1}), {'a': 1})
        self.assertListEqual(doc._parser_out([1, 2, 3]), [1, 2, 3])
        self.assertEqual(doc._parser_out(Date.fromisoformat('2022-01-01')), '2022-01-01')
        self.assertEqual(
            doc._parser_out(DateTime.fromisoformat('2022-01-01T10:00:00+00:00')), '2022-01-01T10:00:00+00:00'
        )
        obj = FakeObject()
        self.assertEqual(doc._parser_out(obj), compress(obj, serialize='pickle'))
        self.assertDictEqual(doc._parser_out(BaseDict(key=Date.fromisoformat('2022-01-01'))), {'key': '2022-01-01'})
        self.assertDictEqual(
            doc._parser_out(BaseDict(key=DateTime.fromisoformat('2022-01-01T10:00:00+00:00'))),
            {'key': '2022-01-01T10:00:00+00:00'}
        )
        Client.assert_not_called()

    def test_loads(self, Client: mock.MagicMock):
        firestore.Document._config.collection_name = 'my-collection'
        Client.return_value.collection.return_value.where.return_value.order_by.return_value.limit.return_value.get.return_value = [
            firestore.Document(firestore_id='id01', type='1', mic='XYSX', created_at='2023-04-03T00:00:00+00:00')
        ]
        doc = firestore.Document.loads(field='firestore_id', condition='==', value='my-id')
        Client.return_value.collection.return_value.where.assert_called_once_with('firestore_id', '==', 'my-id')
        Client.return_value.collection.return_value.where.return_value.order_by.assert_called_once_with('firestore_id')
        self.assertListEqual(
            doc,
            [firestore.Document(**{
                'created_at': DateTime.fromisoformat('2023-04-03T00:00:00+00:00'),
                'firestore_id': 'id01',
                'mic': 'XYSX',
                'type': '1',
                'updated_at': None
            })]
        )
        firestore.Document._config.collection_name = None

    def test_get_firestore_id(self, Client: mock.MagicMock):
        doc = firestore.Document()
        self.assertNotEqual(doc.get_firestore_id(), doc.get_firestore_id())
        doc = firestore.Document(firestore_id='Test')
        self.assertEqual(doc.get_firestore_id(), 'Test')
        Client.assert_not_called()

    def test_load(self, Client: mock.MagicMock):
        firestore.Document._config.collection_name = 'my-collection'
        Client.return_value.collection.return_value.document.return_value.get.return_value.exists = True
        Client.return_value.collection.return_value.document.return_value.get.return_value.to_dict.return_value = {
            'created_at': '2023-04-03T00:00:00+00:00',
            'dct': {'a': 1},
            'lst': [1, 2, 3],
            'date': '2022-01-01',
            'datetime': '2022-01-01T10:00:00+00:00',
            'obj': compress(FakeObject(), serialize='pickle'),
            'byte': b'Text'
        }
        doc = firestore.Document(firestore_id='my-id')
        doc.load()
        Client.return_value.collection.return_value.document.assert_called_once_with('my-id')
        self.assertDictEqual(
            doc,
            {
                'byte': b'Text',
                'created_at': DateTime.fromisoformat('2023-04-03T00:00:00+00:00'),
                'date': Date(2022, 1, 1),
                'datetime': DateTime.fromisoformat('2022-01-01T10:00:00+00:00'),
                'dct': {'a': 1},
                'firestore_id': 'my-id',
                'lst': [1, 2, 3],
                'obj': FakeObject(),
                'updated_at': None
            }
        )
        firestore.Document._config.collection_name = None

    @mock.patch.object(firestore.DateTime, 'now', return_value='2023-10-11T00:00:00+00:00')
    def test_load_no_exists(self, now: mock.MagicMock, Client: mock.MagicMock):
        firestore.Document._config.collection_name = 'my-collection'
        Client.return_value.collection.return_value.document.return_value.get.return_value.exists = False
        Client.return_value.collection.return_value.document.return_value.get.return_value.to_dict.return_value = {
            'created_at': '2023-04-03T00:00:00+00:00',
            'dct': {'a': 1},
            'lst': [1, 2, 3],
            'date': '2022-01-01',
            'datetime': '2022-01-01T10:00:00+00:00',
            'obj': compress(FakeObject(), serialize='pickle'),
            'byte': b'Text'
        }
        doc = firestore.Document(firestore_id='my-id')
        doc.load()
        Client.return_value.collection.return_value.document.assert_called_once_with('my-id')
        self.assertDictEqual(
            doc,
            {
                'created_at': DateTime.fromisoformat('2023-10-11T00:00:00+00:00'),
                'firestore_id': 'my-id',
                'updated_at': None
            }
        )
        firestore.Document._config.collection_name = None
        now.assert_called_once_with()

    @mock.patch.object(firestore.DateTime, 'now', return_value='2023-10-11T00:00:00+00:00')
    def test_save(self, now: mock.MagicMock, Client: mock.MagicMock):
        firestore.Document._config.collection_name = 'my-collection'
        doc = firestore.Document(firestore_id='my-id', var='1', created_at='2023-04-03T00:00:00+00:00')
        doc.save()
        Client.return_value.collection.return_value.document.assert_called_once_with('my-id')
        Client.return_value.collection.return_value.document.return_value.set.assert_called_once_with(
            document_data={
                'created_at': '2023-04-03T00:00:00+00:00',
                'firestore_id': 'my-id',
                'updated_at': '2023-10-11T00:00:00+00:00',
                'var': '1'
            },
            merge=True,
            timeout=60.0
        )
        now.assert_called_once_with()
        firestore.Document._config.collection_name = None

    def test_to_dict(self, Client: mock.MagicMock):
        obj = FakeObject()
        doc = firestore.Document(
            byte=b'Text',
            created_at=DateTime.fromisoformat('2023-04-03T00:00:00+00:00'),
            date=Date(2022, 1, 1),
            datetime=DateTime.fromisoformat('2022-01-01T10:00:00+00:00'),
            dct={'a': 1},
            firestore_id='my-id',
            lst=[1, 2, 3],
            obj=obj,
            updated_at=None
        )
        self.assertDictEqual(
            doc.to_dict(),
            {
                'byte': b'Text',
                'created_at': '2023-04-03T00:00:00+00:00',
                'date': '2022-01-01',
                'datetime': '2022-01-01T10:00:00+00:00',
                'dct': {'a': 1},
                'firestore_id': 'my-id',
                'lst': [1, 2, 3],
                'obj': compress(obj, serialize='pickle'),
                'updated_at': None
            }
        )
        Client.assert_not_called()

    def test_to_dict_excluded_keys(self, Client: mock.MagicMock):
        doc = firestore.Document(firestore_id='my-id', created_at='2023-04-03T00:00:00+00:00')
        self.assertDictEqual(
            doc.to_dict(),
            {
                'created_at': '2023-04-03T00:00:00+00:00',
                'firestore_id': 'my-id',
                'updated_at': None
            }
        )
        firestore.Document._config.excluded_keys = ['created_at', 'updated_at']
        self.assertDictEqual(doc.to_dict(), {'firestore_id': 'my-id'})
        firestore.Document._config.excluded_keys = []
        Client.assert_not_called()


@mock.patch.object(firestore.firestore, 'Client')
class LoadsPaginatedTestCase(TestCase):
    # pylint: disable=invalid-name

    @classmethod
    def setUpClass(cls) -> None:
        firestore.Document._config.collection_name = 'my-collection'

    @classmethod
    def tearDownClass(cls) -> None:
        firestore.Document._config.collection_name = None

    def setUp(self) -> None:
        firestore.FirestoreClient._connections = {}
        firestore.Document._config._client = None
        self.response = [
            firestore.Document(firestore_id='id01', type='1', mic='XYSX', created_at='2023-04-03T00:00:00+00:00'),
            firestore.Document(firestore_id='id02', type='2', mic='XZAG', created_at='2023-04-03T00:00:00+00:00'),
            firestore.Document(firestore_id='id03', type='3', mic='XZIM', created_at='2023-04-03T00:00:00+00:00'),
            firestore.Document(firestore_id='id04', type='4', mic='ZARX', created_at='2023-04-03T00:00:00+00:00')
        ]

    def test_loads_paginated_default(self, Client: mock.MagicMock):
        response = self.response.copy()
        Client.return_value.collection.return_value.order_by.return_value.limit.return_value.get.return_value = response
        result = firestore.Document.loads_paginated()
        self.assertListEqual(result, self.response)
        Client.return_value.collection.assert_called_once_with('my-collection')
        Client.return_value.collection.return_value.select.assert_not_called()
        Client.return_value.collection.return_value.order_by.assert_called_once_with('firestore_id')
        Client.return_value.collection.return_value.order_by.return_value.limit.assert_called_once_with(500)
        Client.return_value.collection.return_value.order_by.return_value.limit.return_value.get.assert_called_once_with()

    def test_loads_paginated_default_limit(self, Client: mock.MagicMock):
        response = self.response.copy()
        Client.return_value.collection.return_value.order_by.return_value.limit.return_value.get.return_value = response
        result = firestore.Document.loads_paginated(limit=100)
        self.assertListEqual(result, self.response)
        Client.return_value.collection.assert_called_once_with('my-collection')
        Client.return_value.collection.return_value.select.assert_not_called()
        Client.return_value.collection.return_value.order_by.assert_called_once_with('firestore_id')
        Client.return_value.collection.return_value.order_by.return_value.limit.assert_called_once_with(100)
        Client.return_value.collection.return_value.order_by.return_value.limit.return_value.get.assert_called_once_with()

    def test_loads_paginated_default_limit_more_query(self, Client: mock.MagicMock):
        response = self.response.copy()
        Client.return_value.collection.return_value.order_by.return_value.limit.return_value.get.return_value = response
        Client.return_value.collection.return_value.order_by.return_value.limit.return_value.start_after.return_value.get.return_value = response[0:3]
        result = firestore.Document.loads_paginated(limit=4)
        self.assertListEqual(result, self.response + self.response[0:3])
        Client.return_value.collection.assert_called_once_with('my-collection')
        Client.return_value.collection.return_value.select.assert_not_called()
        Client.return_value.collection.return_value.order_by.assert_called_once_with('firestore_id')
        Client.return_value.collection.return_value.order_by.return_value.limit.assert_called_once_with(4)
        Client.return_value.collection.return_value.order_by.return_value.limit.return_value.start_after.assert_called_once_with(self.response[-1])
        Client.return_value.collection.return_value.order_by.return_value.limit.return_value.get.assert_called_once_with()

    def test_loads_paginated_default_order_by(self, Client: mock.MagicMock):
        response = self.response.copy()
        Client.return_value.collection.return_value.order_by.return_value.limit.return_value.get.return_value = response
        result = firestore.Document.loads_paginated(order_by='mic', limit=100)
        self.assertListEqual(result, self.response)
        Client.return_value.collection.assert_called_once_with('my-collection')
        Client.return_value.collection.return_value.select.assert_not_called()
        Client.return_value.collection.return_value.order_by.assert_called_once_with('mic')
        Client.return_value.collection.return_value.order_by.return_value.limit.assert_called_once_with(100)
        Client.return_value.collection.return_value.order_by.return_value.limit.return_value.get.assert_called_once_with()

    def test_loads_paginated_default_order_by_error(self, Client: mock.MagicMock):
        response = self.response.copy()
        Client.return_value.collection.return_value.select.return_value.order_by.return_value.limit.return_value.get.return_value = response
        self.assertRaisesRegex(
            ValueError,
            r"The order_by \(type\) must be in fields\(\['mic'\]\).",
            firestore.Document.loads_paginated,
            fields=['mic'],
            order_by='type',
            limit=100
        )
        Client.return_value.collection.assert_called_once_with('my-collection')
        Client.return_value.collection.return_value.select.assert_not_called()
        Client.return_value.collection.return_value.select.return_value.order_by.assert_not_called()
        Client.return_value.collection.return_value.select.return_value.order_by.return_value.limit.assert_not_called()
        Client.return_value.collection.return_value.select.return_value.order_by.return_value.limit.return_value.get.assert_not_called()

    def test_loads_paginated_default_fields(self, Client: mock.MagicMock):
        response = self.response.copy()
        new_response = [doc.fromkeys(['firestore_id', 'created_at', 'updated_at', 'mic']) for doc in response]
        Client.return_value.collection.return_value.select.return_value.order_by.return_value.limit.return_value.get.return_value = new_response
        result = firestore.Document.loads_paginated(fields=['mic'], order_by='mic', limit=100)
        self.assertListEqual(result, new_response)
        Client.return_value.collection.assert_called_once_with('my-collection')
        Client.return_value.collection.return_value.select.assert_called_once_with(field_paths=['created_at', 'firestore_id', 'mic', 'updated_at'])
        Client.return_value.collection.return_value.select.return_value.order_by.assert_called_once_with('mic')
        Client.return_value.collection.return_value.select.return_value.order_by.return_value.limit.assert_called_once_with(100)
        Client.return_value.collection.return_value.select.return_value.order_by.return_value.limit.return_value.get.assert_called_once_with()


@mock.patch.object(redis_module.log, 'debug', mock.MagicMock)
class BaseDocumentCachedConfigTestCase(TestCase):

    def test_readonly_attributes(self):
        msg = "The field 'key_prefix' value cannot be changed."
        self.assertRaisesRegex(FieldValueError, msg, firestore.BaseDocumentCachedConfig, key_prefix='BANANA')
        with self.assertRaisesRegex(FieldValueError, msg):
            firestore.BaseDocumentCachedConfig(key_prefix='BANANA')

    def test_cache_property(self):
        obj1 = firestore.BaseDocumentCachedConfig()
        self.assertIsInstance(obj1.cache, firestore.RedisCacheCompressed)
        obj2 = firestore.BaseDocumentCachedConfig()
        self.assertNotEqual(obj1, obj2)

    def test_inheritance(self):
        self.assertEqual(
            firestore.BaseDocumentCachedConfig.__base__,
            firestore.BaseDocumentConfig
        )


@mock.patch.object(firestore.firestore, 'Client')
class DocumentCachedTestCase(TestCase):
    # pylint: disable=invalid-name

    @classmethod
    def setUpClass(cls) -> None:
        firestore.DocumentCached._config.collection_name = 'my-collection'
        cls.redis = redis_module.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)
        cls.key = '86085ac4d100a96d4e1739e87857bd4e266f6a2e4ad62b7ac5bee2aa62f88d2e'

    @classmethod
    def tearDownClass(cls) -> None:
        firestore.DocumentCached._config.collection_name = None

    def setUp(self) -> None:
        firestore.FirestoreClient._connections = {}
        firestore.DocumentCached._config._client = None
        self.redis.delete(self.key)

    def test_init(self, Client: mock.MagicMock):
        doc = firestore.DocumentCached(firestore_id='my-id', created_at='2023-04-03T00:00:00+00:00')
        self.assertDictEqual(
            doc,
            {
                'created_at': DateTime.fromisoformat('2023-04-03T00:00:00+00:00'),
                'firestore_id': 'my-id',
                'redis_key': self.key,
                'updated_at': None
            }
        )
        Client.return_value.collection.assert_called_once_with('my-collection')
        Client.return_value.collection.return_value.document.assert_called_once_with('my-id')
        Client.return_value.collection.return_value.document.return_value.get.assert_called_once_with()

    def test_clear_cache_key(self, Client: mock.MagicMock):
        doc = firestore.DocumentCached(firestore_id='my-id')
        self.assertIsNotNone(doc._config.cache.get(doc.get_cache_key()))
        doc.clear_cache_key()
        self.assertIsNone(doc._config.cache.get(doc.get_cache_key()))
        Client.return_value.collection.assert_called_once_with('my-collection')
        Client.return_value.collection.return_value.document.assert_called_once_with('my-id')
        Client.return_value.collection.return_value.document.return_value.get.assert_called_once_with()

    def test_get_cache_key(self, Client: mock.MagicMock):
        doc = firestore.DocumentCached(firestore_id='my-id')
        self.assertEqual(doc.get_cache_key(), 'firestore-document-redis-cached-my-collection-my-id')
        Client.return_value.collection.assert_called_once_with('my-collection')
        Client.return_value.collection.return_value.document.assert_called_once_with('my-id')
        Client.return_value.collection.return_value.document.return_value.get.assert_called_once_with()

    def test_load_cache(self, Client: mock.MagicMock):
        # The first time that we load, if it is not on Redis we get it from Firestore and stores on Redis
        doc = firestore.DocumentCached(firestore_id='my-id', created_at='2023-11-11T00:00:00+00:00')
        # The second time that we load, it will get the info on Redis and update the object
        doc = firestore.DocumentCached(firestore_id='my-id', created_at='2023-04-03T00:00:00+00:00')
        self.assertDictEqual(
            doc,
            {
                'created_at': DateTime.fromisoformat('2023-11-11T00:00:00+00:00'),
                'firestore_id': 'my-id',
                'redis_key': '86085ac4d100a96d4e1739e87857bd4e266f6a2e4ad62b7ac5bee2aa62f88d2e',
                'updated_at': None
            }
        )
        Client.return_value.collection.assert_called_once_with('my-collection')
        Client.return_value.collection.return_value.document.assert_called_once_with('my-id')
        Client.return_value.collection.return_value.document.return_value.get.assert_called_once_with()

    @mock.patch.object(firestore.DateTime, 'now', return_value='2023-11-11T00:00:00+00:00')
    def test_save(self, now: mock.MagicMock, Client: mock.MagicMock):
        doc = firestore.DocumentCached(firestore_id='my-id', created_at='2023-04-03T00:00:00+00:00')
        self.assertIsNotNone(doc._config.cache.get(doc.get_cache_key()))
        doc.save()
        self.assertIsNone(doc._config.cache.get(doc.get_cache_key()))
        Client.return_value.collection.return_value.document.return_value.set.assert_called_once_with(
            document_data={
                'firestore_id': 'my-id',
                'created_at': '2023-04-03T00:00:00+00:00',
                'updated_at': '2023-11-11T00:00:00+00:00',
                'redis_key': '86085ac4d100a96d4e1739e87857bd4e266f6a2e4ad62b7ac5bee2aa62f88d2e'
            },
            merge=True,
            timeout=60
        )
        now.assert_called_once_with()
