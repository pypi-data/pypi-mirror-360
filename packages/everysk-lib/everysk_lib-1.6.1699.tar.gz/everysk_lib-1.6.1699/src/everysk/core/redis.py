###############################################################################
#
# (C) Copyright 2023 EVERYSK TECHNOLOGIES
#
# This is an unpublished work containing confidential and proprietary
# information of EVERYSK TECHNOLOGIES. Disclosure, use, or reproduction
# without authorization of EVERYSK TECHNOLOGIES is prohibited.
#
###############################################################################
import traceback
from hashlib import sha256
from functools import wraps, _HashedSeq
from time import sleep
from typing import Any, Iterable

from redis import Redis, client, exceptions # pylint: disable=import-self
from redis.backoff import ExponentialBackoff # pylint: disable=import-error, no-name-in-module
from redis.lock import Lock # pylint: disable=import-error, no-name-in-module
from redis.retry import Retry # pylint: disable=import-error, no-name-in-module

from everysk.config import settings
from everysk.core.compress import compress, decompress
from everysk.core.exceptions import RedisEmptyListError
from everysk.core.fields import IntField, StrField
from everysk.core.log import Logger
from everysk.core.object import BaseObject
from everysk.core.serialize import dumps, loads


log = Logger(name='everysk-redis')


###############################################################################
#   Cache decorator functions Implementation
###############################################################################
def _make_key(args: tuple, kwargs: dict) -> str:
    """
    Create a key from args and kwargs to be used on cache.
    This function is a based on functools._make_key

    Args:
        args (tuple): The received args.
        kwargs (dict): The received kwargs.
    """
    #/usr/local/lib/python3.11/functools.py: 448 - def _make_key
    key = args
    if kwargs:
        for item in kwargs.items():
            key += item
    elif len(key) == 1 and type(key[0]) in {int, float, str}:
        # To be faster if we have only one item and it's a int, float or str
        # we return it directly
        return str(key[0])

    return str(_HashedSeq(key))

def cache(*, timeout: int):
    """
    Decorator to cache the result of a function in Redis.
    To disable the cache, set the timeout to None otherwise it must be > 0.

    Args:
        timeout (int): The time in seconds that the result will be stored in cache.

    Raises:
        ValueError: If timeout is not an integer or is less than 0.
    """
    if timeout is not None and (not isinstance(timeout, int) or timeout < 1):
        raise ValueError('Timeout must be an integer greater than 0.')

    # Because we have a parameter we need to create another nested function
    def decorator(func):
        info = {'hits': 0, 'misses': 0}
        redis_cache = RedisCache(prefix=func.__name__)

        # We use wraps to keep the original function name and docstring
        @wraps(func)
        def wrapper(*args, **kwargs):
            key = _make_key(args, kwargs)
            value = redis_cache.get(key)
            if value:
                info['hits'] += 1
                return loads(value, protocol='pickle')

            info['misses'] += 1
            value = func(*args, **kwargs)
            redis_cache.set(key, dumps(value, protocol='pickle'), timeout)
            return value

        # We add some extra attributes to the wrapper
        wrapper.info = info
        wrapper.clear = redis_cache.delete_prefix

        return wrapper

    return decorator


###############################################################################
#   RedisClient Class Implementation
###############################################################################
class RedisClient(BaseObject):
    ## Private attributes
    _connection: Redis = None
    _separator = ':'

    ## Public attributes
    prefix: str = None
    host: str = None
    port: int = None

    ## Private methods
    def _connect(self) -> None:
        """ Create a Redis connection and stores to later use. """
        # https://redis-py.readthedocs.io/en/stable/retry.html
        retry = Retry(ExponentialBackoff(), 3)

        # https://github.com/redis/redis-py/issues/722
        # We use RedisClient._connection to create a Singleton connection
        log.debug('Connecting on Redis(%s).....', self.host)
        RedisClient._connection = Redis(
            host=self.host,
            port=self.port,
            health_check_interval=30, # seconds
            socket_keepalive=True,
            socket_timeout=120, # seconds
            retry=retry,
            retry_on_error=[Exception]
        )

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        if self.host is None:
            self.host = settings.REDIS_HOST

        if self.port is None:
            self.port = settings.REDIS_PORT

        if RedisClient._connection is None:
            self._connect()

    @property
    def connection(self) -> Redis:
        """
        We use this property to check if Redis is online
        then returning the working connection.
        """
        try:
            RedisClient._connection.ping()
        except Exception: # pylint: disable=broad-exception-caught
            # Create a new connection
            self._connect()

        return RedisClient._connection

    def flush_all(self) -> bool:
        """ Clear all keys from Redis. """
        return self.connection.flushall()

    def get_hash_key(self, key: bytes | str) -> str:
        """
        Convert the key to Sha256 to avoid strange characters and decrease the chance of generating the same key.

        Args:
            key (bytes | str): The key to be hashed.
        """
        # To be used by SHA256 the key must be bytes
        if isinstance(key, str):
            key = key.encode('utf-8')

        key = sha256(key).hexdigest()
        if self.prefix:
            key = f'{self.prefix}{self._separator}{key}'

        return key


###############################################################################
#   RedisCache Class Implementation
###############################################################################
class RedisCache(RedisClient):
    """ Redis cache client """

    def get_set(self, key: str, func: callable, timeout: int = None, **kwargs) -> Any:
        """
        This method execute a get on Redis server, if this returns None then we execute the set method.
        For the set method we use the func(**kwargs).
        To avoid race conditions we use a RedisLock to run only one set method.

        Args:
            key (str): The key that will be used to cache the result from func.
            func (callable): The function that generates the desired cached result.
            timeout (int, optional): The timeout that this key will be keep on cache. Defaults to None.
            *kwargs (dict, optional): Extra params that will be send to the func.

        Returns:
            Any: The result from cache get or the result from func.
        """
        result = self.get(key)
        if result is None:
            # We create a lock on Redis
            lock = RedisLock(name=f'redis-get-set-lock-{key}')
            if lock.acquire():
                # If we can acquire the lock then we don't have race conditions
                # and proceed normally
                try:
                    result = func(**kwargs)
                    self.set(key=key, value=result, timeout=timeout)
                except Exception: # pylint: disable=broad-exception-caught
                    # We generate a log for this exception
                    log.error('Redis get_set method: %s', traceback.format_exc())

                # Then we release the the lock
                lock.release()

            else:
                # If we can't acquire the lock that means we have race condition
                # in this case we need to wait for the key be set or if some error
                # occur the lock will be released.
                result = self.get(key)
                while result is None:
                    result = self.get(key)
                    if result is None and lock.acquire():
                        # Then we release the the lock and exit
                        lock.release()
                        break

                    # We wait 0.5 second until next try
                    sleep(0.5)

        if isinstance(result, bytes):
            result = result.decode('utf-8')

        return result

    def get(self, key: bytes) -> bytes:
        """
        Get the value from key from connection, if it's not found return None.

        Returns:
            bytes: Always return a byte object.
        """
        key = self.get_hash_key(key)
        value = self.connection.get(key)
        return value

    def set(self, key: bytes, value: Any, timeout: int = None) -> None:
        """
        Set key/value on connection for timeout in seconds,
        if timeout is None the key/value will be keep forever.
        Value must be one of these: bytes, str, int or float.
        """
        if not isinstance(value, (bytes, str, int, float)):
            raise ValueError(
                f'Value {type(value)} is not in supported values. (bytes, str, int, float).'
            )

        key = self.get_hash_key(key)
        self.connection.set(key, value, timeout)

    def delete(self, key: bytes | str | Iterable) -> None:
        """
        Delete one or more keys from Redis.

        Args:
            key (bytes | str | Iterable): The key or keys to be deleted.
        """
        if not isinstance(key, (list, set, tuple)):
            keys = [self.get_hash_key(key)]
        else:
            keys = [self.get_hash_key(k) for k in key]

        self.connection.delete(*keys)

    def delete_prefix(self, prefix: str = None) -> None:
        """
        Delete all keys from Redis that start with the given prefix or with the one set in the class.

        Args:
            prefix (str, optional): The same string that was used to create the keys. Defaults to None.
        """
        # If prefix is None, we use the prefix from the class
        prefix = prefix or self.prefix
        # To search for all keys with this prefix we need to add a ':*' at the end
        if '*' not in prefix:
            prefix = f'{prefix}{self._separator}*'

        # We use the scan method to search for all keys with this prefix and pipe to delete them
        pipe = self.connection.pipeline()
        cursor = None
        while cursor != 0:
            cursor, keys = self.connection.scan(cursor=cursor or 0, match=prefix, count=1000)
            if keys:
                pipe.delete(*keys)

        pipe.execute()


###############################################################################
#   RedisCacheCompressed Class Implementation
###############################################################################
class RedisCacheCompressed(RedisCache):
    """
    Store data on Redis server using pickle and zlib
    Use this if you need to store objects ons Redis.
    """

    def get(self, key: bytes) -> Any:
        """
        Retrieve the value associated with the given key from the Redis cache

        Args:
            key (bytes): The key to retrieve the value for

        """
        value = super().get(key)
        if value is not None:
            value = decompress(value, serialize='pickle')

        return value

    def set(self, key: bytes, value: Any, timeout: int = None) -> None:
        """
        Store the provided value in the Redis cache associated with the given key

        Args:
            key (bytes): The key to associate with the value
            value (Any): The value to store in the Redis cache
            timeout (int, optional): Expiration time for the cached item
        """
        value = compress(value, serialize='pickle')
        super().set(key, value, timeout)


###############################################################################
#   RedisList Class Implementation
###############################################################################
class RedisList(RedisClient):
    """
    First in, first out Redis list implementation.
    -> https://redis.io/docs/data-types/lists/
    -> https://koalatea.io/python-redis-lists/

    """
    name = StrField(required=True)

    def bpop(self, timeout: int = 0) -> tuple:
        """
        Pop the first item from the list, blocking until a item exists
        or timeout was reached.
        If timeout is 0, then block indefinitely.

        Returns:
            tuple: (list name, value)
        """
        value = self.connection.blpop(self.name, timeout=timeout)
        if value is None:
            raise RedisEmptyListError(f"The RedisList(name='{self.name}') is empty.")

        name, value = value
        if isinstance(name, bytes):
            name = name.decode()

        return (name, decompress(value, serialize='pickle'))

    def pop(self) -> Any:
        """
        Pop the first item from the list.

        Raises:
            RedisEmptyListError: If the return is None/empty.
        """
        value = self.connection.lpop(self.name)
        if value is None:
            raise RedisEmptyListError(f"The RedisList(name='{self.name}') is empty.")

        value = decompress(value, serialize='pickle')
        return value

    def push(self, value: Any) -> None:
        """
        Puts value on the last position of the list.

        Args:
            value (Any): the value to be inserted into the last position
        """
        value = compress(value, serialize='pickle')
        self.connection.rpush(self.name, value)

    def clear(self) -> None:
        """
        Clear all keys
        """
        self.connection.delete(self.name)


###############################################################################
#   RedisChannel Class Implementation
###############################################################################
class RedisChannel(RedisClient):
    """
    Base class to work with channels on Redis.
    https://blog.devgenius.io/how-to-use-redis-pub-sub-in-your-python-application-b6d5e11fc8de
    """
    _channel: client.PubSub = None
    exit_message = StrField(default='exit', readonly=True)
    name = StrField(required=True)

    def send(self, message: dict) -> None:
        self.connection.publish(self.name, message)

    @property
    def channel(self) -> client.PubSub:
        """ Create a connection with name """
        if self._channel is None:
            self._channel = self.connection.pubsub()
            self._channel.subscribe(self.name)

        return self._channel

    def parse_message(self, message: dict) -> tuple:
        """
        Convert message data from bytes to str

        Args:
            message (dict): The message dictionary to be parsed.

        Returns:
            tuple: Containing the channel name and its corresponding data.
        """
        # message format
        # {'type': None, 'pattern': None, 'channel': None, 'data': None}
        channel_name = None
        data = None
        if message:
            channel_name = message.get('channel', None) or None
            data = message.get('data', '') or ''
            if isinstance(channel_name, bytes):
                channel_name = channel_name.decode()
            if isinstance(data, bytes):
                data = data.decode()

        return (channel_name, data)

    def consume(self, callback: callable = None) -> None:
        """ Loop for consume message from channel when they arrive. """
        for message in self.channel.listen():
            channel_name, data = self.parse_message(message)
            # Only care if the message is sent to this channel
            if channel_name == self.name:
                # Stop iteration on exit_message
                if data == self.exit_message:
                    break

                # We can use a function for callback or self.process_message
                if callback:
                    callback(data)
                else:
                    self.process_message(data)

    def process_message(self, message: str) -> None:
        """ Use it on child classes to manipulate the received message. """
        pass


###############################################################################
#   RedisLock Class Implementation
###############################################################################
class RedisLock(RedisClient):
    """
    Class used to create a lock on Redis
    https://rohansaraf.medium.com/distributed-locking-with-redis-ecb0773e7695
    https://redis-py.readthedocs.io/en/latest/lock.html
    """
    ## Private attributes
    _lock = None

    ## Public attributes
    name = StrField(required=True)
    timeout = IntField(default=None) # timeout indicates a maximum life for the lock in seconds.

    ## Private methods
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        if self._lock is None:
            self._lock = Lock(redis=self.connection, name=self._get_name(), timeout=self.timeout)

    def _get_name(self) -> str:
        """
        Convert self.name to a SHA256 hash, this avoid strange chars on name that can broke Redis.
        """
        return self.get_hash_key(self.name)

    ## Public methods
    def acquire(self, blocking: bool = False, blocking_timeout: float = None) -> bool:
        """
        Try to acquire a lock with self.name, if lock is already acquired returns False.
        If blocking is False, always return immediately, if blocking is True it will waiting until block can be acquired.
        blocking_timeout specifies the maximum number of seconds to wait trying to acquire the lock.
        """
        return self._lock.acquire(blocking=blocking, blocking_timeout=blocking_timeout)

    def owned(self) -> bool:
        """ Returns True if this key is locked by this lock, otherwise False. """
        return self._lock.owned()

    def release(self, force: bool = False) -> bool:
        """
        Try to release this lock, will be True only if this lock is owned by this process.
        If force is True, the lock will be released even if it is not owned.
        """
        if force:
            self.connection.delete(self._get_name())
            return True

        try:
            self._lock.release()
            return True
        except (exceptions.LockError, exceptions.LockNotOwnedError):
            pass

        return False
