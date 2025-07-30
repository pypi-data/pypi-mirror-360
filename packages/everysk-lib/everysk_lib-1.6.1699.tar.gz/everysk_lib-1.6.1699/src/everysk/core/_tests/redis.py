###############################################################################
#
# (C) Copyright 2023 EVERYSK TECHNOLOGIES
#
# This is an unpublished work containing confidential and proprietary
# information of EVERYSK TECHNOLOGIES. Disclosure, use, or reproduction
# without authorization of EVERYSK TECHNOLOGIES is prohibited.
#
###############################################################################
# pylint: disable=protected-access
from concurrent.futures import ThreadPoolExecutor
from os import environ
from time import sleep
from uuid import uuid4
from redis import exceptions, client # pylint: disable=import-self
from everysk.core import redis as redis_module
from everysk.core.redis import (
    RedisCache, RedisCacheCompressed, RedisChannel, RedisClient,
    RedisEmptyListError, RedisList, RedisLock, cache
)
from everysk.core.unittests import TestCase, mock


@cache(timeout=1)
def sum(a: int, b: int) -> int: # pylint: disable=redefined-builtin
    return a + b


class CacheDecoratorTestCase(TestCase):

    def setUp(self) -> None:
        self.obj = RedisCache()
        self.obj.flush_all()

    def test_timeout_value_not_int(self):
        with self.assertRaises(ValueError) as context:
            cache(timeout='1')

        self.assertEqual(str(context.exception), 'Timeout must be an integer greater than 0.')

    def test_timeout_value_zero(self):
        with self.assertRaises(ValueError) as context:
            cache(timeout=0)

        self.assertEqual(str(context.exception), 'Timeout must be an integer greater than 0.')

    def test_timeout_value_negative(self):
        with self.assertRaises(ValueError) as context:
            cache(timeout=-1)

        self.assertEqual(str(context.exception), 'Timeout must be an integer greater than 0.')

    def test_cache_decorator(self):
        self.assertEqual(sum(1, 1), 2)
        self.assertEqual(sum(1, 1), 2)
        self.assertListEqual(
            self.obj.connection.keys(),
            [b'sum:e718fe8edf8a7c2917cd7444286b7048042a74abf5208f1d70933c08dbd6b7e9']
        )
        self.assertDictEqual(sum.info, {'hits': 1, 'misses': 1})
        sleep(1.1)
        self.assertEqual(sum(1, 1), 2)
        self.assertDictEqual(sum.info, {'hits': 1, 'misses': 2})

    def test_cache_decorator_clear(self):
        self.obj.set('key', 1)
        self.assertEqual(sum(1, 1), 2)
        self.assertEqual(sum(1, 2), 3)
        self.assertEqual(sum(1, 3), 4)
        self.assertListEqual(
            sorted(self.obj.connection.keys()),
            [
                b'2c70e12b7a0646f92279f427c7b38e7334d8e5389cff167a1dc30e73f826b683',
                b'sum:3a316d6d3226f84c1e46e4447fa8d5fd800bff4a1bc6498152523cd4a602b69b',
                b'sum:4e3970018fa500922ce5c087f84c734d7b47b0651da2f2e17226801885838032',
                b'sum:e718fe8edf8a7c2917cd7444286b7048042a74abf5208f1d70933c08dbd6b7e9',
            ]
        )
        sum.clear()
        self.assertListEqual(self.obj.connection.keys(), [b'2c70e12b7a0646f92279f427c7b38e7334d8e5389cff167a1dc30e73f826b683'])


class RedisClientTestCase(TestCase):

    def setUp(self) -> None:
        RedisClient._connection = None

    @mock.patch.object(redis_module, 'log')
    def test_environ(self, log: mock.MagicMock):
        environ['REDIS_HOST'] = '0.1.0.1'
        environ['REDIS_PORT'] = '1234'
        redis = RedisClient()
        self.assertEqual(redis.host, environ['REDIS_HOST'])
        self.assertEqual(redis.port, int(environ['REDIS_PORT']))
        del environ['REDIS_HOST']
        del environ['REDIS_PORT']
        log.debug.assert_called_once_with('Connecting on Redis(%s).....', redis.host)

    @mock.patch.object(redis_module, 'log')
    def test_connection_property(self, log: mock.MagicMock):
        redis = RedisClient()
        self.assertEqual(redis.connection, redis._connection)
        self.assertEqual(redis.connection, RedisClient._connection)
        log.debug.assert_called_once()

    @mock.patch.object(redis_module, 'log')
    def test_hash_key(self, log: mock.MagicMock):
        redis = RedisClient()
        self.assertEqual(
            redis.get_hash_key('a'),
            'ca978112ca1bbdcafac231b39a23dc4da786eff8147c4e72b9807785afee48bb'
        )
        # Check again to guarantee the same hash
        self.assertEqual(
            redis.get_hash_key('a'),
            'ca978112ca1bbdcafac231b39a23dc4da786eff8147c4e72b9807785afee48bb'
        )
        log.debug.assert_called_once()

    @mock.patch.object(redis_module, 'log')
    def test_connect(self, log: mock.MagicMock):
        redis = RedisClient()
        log.debug.assert_called_once()
        RedisClient._connection = None
        self.assertIsNone(RedisClient._connection)
        redis._connect()
        self.assertIsNotNone(RedisClient._connection)

    @mock.patch.object(RedisClient, '_connect')
    def test_connection_error_connection(self, _connect: mock.MagicMock):
        with mock.patch.object(RedisClient, '_connection', spec=redis_module.Redis) as _connection:
            _connection.ping.side_effect = exceptions.ConnectionError
            connection = RedisClient().connection # pylint: disable=unused-variable
            _connection.ping.assert_called_once_with()
        _connect.assert_called_once_with()

    @mock.patch.object(redis_module.log, 'debug', mock.MagicMock)
    def test_flush_all(self):
        cli = RedisClient()
        # Generate a random key to test
        key = uuid4().hex
        cli.connection.set(key, 'Flush-test')
        cli.flush_all()
        self.assertIsNone(cli.connection.get(key))


@mock.patch.object(redis_module, 'log', mock.MagicMock())
class RedisCacheTestCase(TestCase):

    def setUp(self) -> None:
        RedisClient._connection = None

    def test_get_hash_key(self):
        obj = RedisCache()
        hash_key = '2c70e12b7a0646f92279f427c7b38e7334d8e5389cff167a1dc30e73f826b683'
        self.assertEqual(obj.get_hash_key('key'), hash_key)
        # Must always be the same value
        self.assertEqual(obj.get_hash_key('key'), hash_key)

    def test_get_set_delete(self):
        obj = RedisCache()
        obj.delete('key')
        self.assertIsNone(obj.get('key'))
        obj.set('key', 'My value.')
        self.assertEqual(obj.get('key'), b'My value.')
        obj.set('key', 1)
        self.assertEqual(obj.get('key'), b'1')
        obj.set('key', b'1.1')
        self.assertEqual(obj.get('key'), b'1.1')
        obj.delete('key')
        self.assertIsNone(obj.get('key'))

    def test_set_error(self):
        obj = RedisCache()
        self.assertRaises(ValueError, obj.set, 'key', ())
        self.assertRaises(ValueError, obj.set, 'key', [])
        self.assertRaises(ValueError, obj.set, 'key', {})
        self.assertRaises(ValueError, obj.set, 'key', obj)

    def test_prefix(self):
        key = b'prefix:2c70e12b7a0646f92279f427c7b38e7334d8e5389cff167a1dc30e73f826b683'
        obj = RedisCache(prefix='prefix')
        self.assertNotIn(key, obj.connection.keys())
        obj.set('key', 1)
        self.assertIn(key, obj.connection.keys())
        obj.delete('key')
        self.assertNotIn(key, obj.connection.keys())

    def test_delete_prefix(self):
        keys = [
            b'other:2c70e12b7a0646f92279f427c7b38e7334d8e5389cff167a1dc30e73f826b683',
            b'prefix:cd42404d52ad55ccfa9aca4adc828aa5800ad9d385a0671fbcbf724118320619',
            b'prefix:2c70e12b7a0646f92279f427c7b38e7334d8e5389cff167a1dc30e73f826b683',
        ]
        # Create a key with another prefix
        obj = RedisCache(prefix='other')
        obj.flush_all()
        obj.set('key', 1)

        obj = RedisCache(prefix='prefix')
        obj.set('key', 1)
        obj.set('value', 1)
        self.assertListEqual(sorted(obj.connection.keys()), sorted(keys))

        # Delete the key with other
        obj.delete_prefix(prefix='other')
        self.assertListEqual(sorted(obj.connection.keys()), sorted(keys[1:]))

        # Delete keys with prefix
        obj.delete_prefix()
        self.assertListEqual(obj.connection.keys(), [])


class RedisCacheGetSetTestCase(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        RedisClient._connection = None
        with mock.patch.object(redis_module.log, 'debug') as debug:
            cls.cache = RedisCache()
            debug.assert_called_once_with('Connecting on Redis(%s).....', '0.0.0.0')

        cls.key = 'redis-get-set-test-case'

    def setUp(self) -> None:
        self.cache.delete(self.key)
        self.mock = mock.MagicMock()

    def func(self, **kwargs):
        sleep(0.1)
        self.mock(**kwargs)
        return f'return: {kwargs}'

    def test_redis_get_set(self):
        obj01 = RedisCache()
        obj02 = RedisCache()
        with ThreadPoolExecutor() as executor:
            task01 = executor.submit(obj01.get_set, key=self.key, func=self.func, keyword='value01')
            sleep(0.05) # This is just to guarantee that value1 will always be called first
            task02 = executor.submit(obj02.get_set, key=self.key, func=self.func, keyword='value02')
            self.assertEqual(task01.result(), task02.result())
        self.mock.assert_called_once_with(keyword='value01')

    @mock.patch.object(redis_module.log, 'error')
    def test_get_set_func_error_both_exit(self, error: mock.MagicMock):
        self.mock.side_effect = AttributeError
        obj01 = RedisCache()
        obj02 = RedisCache()
        with ThreadPoolExecutor() as executor:
            task01 = executor.submit(obj01.get_set, key=self.key, func=self.func, keyword='value01')
            sleep(0.05) # This is just to guarantee that value1 will always be called first
            task02 = executor.submit(obj02.get_set, key=self.key, func=self.func, keyword='value02')
            self.assertIsNone(task01.result())
            self.assertIsNone(task02.result())

        self.mock.assert_called_once_with(keyword='value01')
        error.assert_called_once()

    @mock.patch.object(redis_module.log, 'error')
    def test_get_set_func_error(self, error: mock.MagicMock):
        self.mock.side_effect = AttributeError
        result = RedisCache().get_set(key=self.key, func=self.func)
        self.assertIsNone(result)
        self.mock.assert_called_once_with()
        error.assert_called_once()


@mock.patch.object(redis_module, 'log', mock.MagicMock())
class RedisCacheCompressedTestCase(TestCase):

    def setUp(self) -> None:
        RedisClient._connection = None

    def test_get_hash_key(self):
        obj = RedisCacheCompressed()
        hash_key = '2c70e12b7a0646f92279f427c7b38e7334d8e5389cff167a1dc30e73f826b683'
        self.assertEqual(obj.get_hash_key('key'), hash_key)
        # Must always be the same value
        self.assertEqual(obj.get_hash_key('key'), hash_key)

    def test_get_set_delete(self):
        obj = RedisCacheCompressed()
        self.assertIsNone(obj.get('key'))
        lst = [1, 'test', 1.1, {'key': 'value'}]
        obj.set('key', lst)
        self.assertListEqual(obj.get('key'), lst)
        dct = {'lst': [1, 't'], 'dct': {'key': 'value'}, 'key': 1}
        obj.set('key', dct)
        self.assertDictEqual(obj.get('key'), dct)
        obj.delete('key')
        self.assertIsNone(obj.get('key'))


@mock.patch.object(redis_module, 'log', mock.MagicMock())
class RedisListTestCase(TestCase):

    def setUp(self) -> None:
        RedisClient._connection = None
        self.name = 'redis-list-test-case'

    def test_push_pop(self):
        lst = RedisList(name=self.name)
        lst.clear() # Clear all elements
        self.assertRaises(RedisEmptyListError, lst.pop)
        obj = {'lst': [1, 1.1, 'test', True]}
        lst.push(obj)
        self.assertEqual(lst.pop(), obj)

    def test_bpop_timeout(self):
        lst = RedisList(name=self.name)
        lst.clear() # Clear all elements
        self.assertRaises(RedisEmptyListError, lst.bpop, 0.5)

    def test_bpop(self):
        lst = RedisList(name=self.name)
        lst.clear() # Clear all elements
        obj = {'lst': [1, 1.1, 'test', True]}
        lst.push(obj)
        self.assertTupleEqual(lst.bpop(0.5), (self.name, obj))

    def test_clear(self):
        lst = RedisList(name=self.name)
        lst.clear() # Clear all elements
        self.assertRaises(RedisEmptyListError, lst.pop)
        obj = {'lst': [1, 1.1, 'test', True]}
        lst.push(obj)
        lst.clear()
        self.assertRaises(RedisEmptyListError, lst.pop)


@mock.patch.object(redis_module, 'log', mock.MagicMock())
@mock.patch.object(RedisChannel, '_channel', spec=client.PubSub)
class RedisChannelTestCase(TestCase):

    def setUp(self) -> None:
        self.name = 'tests'
        RedisClient._connection = None

    @mock.patch.object(RedisClient, '_connection', spec=redis_module.Redis)
    def test_send(self, _connection: mock.MagicMock, _channel: mock.MagicMock):
        channel = RedisChannel(name=self.name)
        channel.send('Hi')
        _connection.publish.assert_called_once_with(channel.name, 'Hi')
        _channel.assert_not_called()

    @mock.patch.object(RedisClient, '_connection', spec=redis_module.Redis)
    def test_channel(self, _connection: mock.MagicMock, _channel: mock.MagicMock):
        channel = RedisChannel(name=self.name)
        channel._channel = None
        _connection.pubsub.return_value = _channel
        channel.channel # Call the property - pylint: disable=pointless-statement
        _connection.pubsub.assert_called_once_with()
        _channel.subscribe.assert_called_once_with(channel.name)

    def test_parse_message(self, _channel: mock.MagicMock):
        channel = RedisChannel(name=self.name)
        message = {'channel': self.name.encode('utf-8'), 'data': b'data'}
        self.assertTupleEqual(channel.parse_message(message), (self.name, 'data'))
        _channel.assert_not_called()

    def test_consume_process_message(self, _channel: mock.MagicMock):
        channel = RedisChannel(name=self.name)
        message = {'channel': self.name.encode('utf-8'), 'data': b'data'}
        _channel.listen.return_value = [message]
        channel.process_message = mock.MagicMock()
        channel.consume()
        channel.process_message.assert_called_once_with('data')

    def test_process(self, _channel: mock.MagicMock):
        channel = RedisChannel(name=self.name)
        self.assertIsNone(channel.process_message('data'))
        _channel.assert_not_called()

    def test_consume_callback(self, _channel: mock.MagicMock):
        channel = RedisChannel(name=self.name)
        message = {'channel': self.name.encode('utf-8'), 'data': b'data'}
        _channel.listen.return_value = [message]
        callback = mock.MagicMock()
        channel.consume(callback)
        callback.assert_called_once_with('data')

    def test_consume_break(self, _channel: mock.MagicMock):
        channel = RedisChannel(name=self.name)
        message = {'channel': self.name.encode('utf-8'), 'data': b'data'}
        exit_message = {'channel': self.name.encode('utf-8'), 'data': RedisChannel.exit_message}
        _channel.listen.return_value = [exit_message, message]
        callback = mock.MagicMock()
        channel.consume(callback)
        callback.assert_not_called()


@mock.patch.object(redis_module, 'log', mock.MagicMock())
class RedisLockTestCase(TestCase):

    def setUp(self) -> None:
        self.name = 'tests'
        RedisClient._connection = None

    def tearDown(self) -> None:
        RedisLock(name=self.name).release(force=True)

    def test_acquire(self):
        lock01 = RedisLock(name=self.name)
        lock02 = RedisLock(name=self.name)
        self.assertTrue(lock01.acquire())
        self.assertFalse(lock02.acquire())

    @mock.patch.object(RedisLock, '_lock')
    def test_acquire_blocking(self, lock: mock.MagicMock):
        lock01 = RedisLock(name=self.name)
        lock01.acquire(blocking=True, blocking_timeout=1.0)
        lock.acquire.assert_called_once_with(blocking=True, blocking_timeout=1.0)

    def test_timeout(self):
        lock01 = RedisLock(name=self.name, timeout=1)
        lock02 = RedisLock(name=self.name, timeout=1)
        self.assertTrue(lock01.acquire())
        self.assertFalse(lock02.acquire())
        sleep(1.5) # With 1 second the test breaks sometimes
        self.assertTrue(lock02.acquire())

    def test_owned(self):
        lock01 = RedisLock(name=self.name)
        lock02 = RedisLock(name=self.name)
        lock01.acquire()
        lock02.acquire()
        self.assertTrue(lock01.owned())
        self.assertFalse(lock02.owned())

    def test_release(self):
        lock01 = RedisLock(name=self.name)
        lock02 = RedisLock(name=self.name)
        lock01.acquire()
        lock02.acquire()
        self.assertFalse(lock02.release())
        self.assertFalse(lock02.acquire())
        self.assertTrue(lock01.release())
        self.assertTrue(lock02.acquire())

    def test_release_force(self):
        lock01 = RedisLock(name=self.name)
        lock02 = RedisLock(name=self.name)
        lock01.acquire()
        lock02.acquire()
        self.assertTrue(lock02.release(force=True))
        self.assertTrue(lock02.acquire())
        self.assertFalse(lock01.release())
        self.assertFalse(lock01.acquire())
