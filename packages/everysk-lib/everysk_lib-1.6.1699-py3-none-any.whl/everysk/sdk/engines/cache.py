###############################################################################
#
# (C) Copyright 2025 EVERYSK TECHNOLOGIES
#
# This is an unpublished work containing confidential and proprietary
# information of EVERYSK TECHNOLOGIES. Disclosure, use, or reproduction
# without authorization of EVERYSK TECHNOLOGIES is prohibited.
#
###############################################################################
from typing import Any

from everysk.config import settings
from everysk.sdk.base import BaseSDK


###############################################################################
#   UserCache Class Implementation
###############################################################################
class UserCache(BaseSDK):

    def get(self, key: str, prefix: str = '') -> Any:
        """
        Get the value of a key from the cache.

        Args:
            key (str): The key to get the value of.
            prefix (str): The prefix of the key.

        Returns:
            Any: The value of the key.

        Example:
            >>> cache = UserCache()
            >>> cache.get('key')
        """
        return self.get_response(self_obj=self, params={'key': key, 'prefix': prefix})

    def get_multi(self, keys: list[str], prefix: str = '') -> dict[str, Any]:
        """
        Get the values of multiple keys from the cache.

        Args:
            keys (list[str]): The keys to get the values of.
            prefix (str): The prefix of the keys.

        Returns:
            dict[str, Any]: The values of the keys.

        Example:
            >>> cache = UserCache()
            >>> cache.get_multi(['key1', 'key2'])
            {
                'key1': 'value1',
                'key2': 'value2'
            }
        """
        return self.get_response(self_obj=self, params={'keys': keys, 'prefix': prefix})

    def set(self, key: str, data: Any, time: int = settings.ENGINES_CACHE_EXECUTION_EXPIRATION_TIME, prefix: str = '') -> bool:
        """
        Set the value of a key in the cache.

        Args:
            key (str): The key to set the value of.
            data (Any): The value to set.
            time (int): The expiration time of the key in seconds.
            prefix (str): The prefix of the key.

        Returns:
            bool: True if the key is set, False otherwise.

        Example:
            >>> cache = UserCache()
            >>> cache.set('key', 'value')
        """
        if not isinstance(time, int) or time <= 0 or time > settings.ENGINES_CACHE_EXECUTION_EXPIRATION_TIME:
            raise ValueError('Invalid time value. The time value should be an integer greater than 0 and less than or equal to the default expiration time.')
        return self.get_response(self_obj=self, params={'key': key, 'data': data, 'time': time, 'prefix': prefix})

    def set_multi(self, data_dict: dict, time: int = settings.ENGINES_CACHE_EXECUTION_EXPIRATION_TIME, prefix: str = '') -> list:
        """
        Set the values of multiple keys in the cache.

        Args:
            data_dict (dict): The keys and values to set.
            time (int): The expiration time of the keys in seconds.
            prefix (str): The prefix of the keys.

        Returns:
            list: The keys that are set.

        Example:
            >>> cache = UserCache()
            >>> cache.set_multi({'key1': 'value1', 'key2': 'value2'})
            ['key1', 'key2']
        """
        if not isinstance(time, int) or time <= 0 or time > settings.ENGINES_CACHE_EXECUTION_EXPIRATION_TIME:
            raise ValueError('Invalid time value. The time value should be an integer greater than 0 and less than or equal to the default expiration time.')
        return self.get_response(self_obj=self, params={'data_dict': data_dict, 'time': time, 'prefix': prefix})

    def incr(self, key: str, delta: int = 1, initial_value: Any = None, time: int = settings.ENGINES_CACHE_EXECUTION_EXPIRATION_TIME) -> int:
        """
        Increment the value of a key in the cache.

        Args:
            key (str): The key to increment the value of.
            delta (int): The amount to increment the value by.
            initial_value (Any): The initial value of the key.
            time (int): The expiration time of the key in seconds.

        Returns:
            int: The new value of the key.

        Example:
            >>> cache = UserCache()
            >>> cache.incr('key', 1, 0)
            1
        """
        if not isinstance(time, int) or time <= 0 or time > settings.ENGINES_CACHE_EXECUTION_EXPIRATION_TIME:
            raise ValueError('Invalid time value. The time value should be an integer greater than 0 and less than or equal to the default expiration time.')
        return self.get_response(self_obj=self, params={'key': key, 'delta': delta, 'initial_value': initial_value, 'time': time})

    def decr(self, key: str, delta: int = 1, initial_value: Any = None, time: int = settings.ENGINES_CACHE_EXECUTION_EXPIRATION_TIME) -> int | None:
        """
        Decrement the value of a key in the cache.

        Args:
            key (str): The key to decrement the value of.
            delta (int): The amount to decrement the value by.
            initial_value (Any): The initial value of the key.
            time (int): The expiration time of the key in seconds.

        Returns:
            int: The new value of the key.

        Example:
            >>> cache = UserCache()
            >>> cache.decr('key', 1, 0)
            0
        """
        if not isinstance(time, int) or time <= 0 or time > settings.ENGINES_CACHE_EXECUTION_EXPIRATION_TIME:
            raise ValueError('Invalid time value. The time value should be an integer greater than 0 and less than or equal to the default expiration time.')
        return self.get_response(self_obj=self, params={'key': key, 'delta': delta, 'initial_value': initial_value, 'time': time})

    def delete(self, key: str) -> bool:
        """
        Delete a key from the cache.

        Args:
            key (str): The key to delete.

        Returns:
            bool: True if the key is deleted, False otherwise.

        Example:
            >>> cache = UserCache()
            >>> cache.delete('key')
            True
        """
        return self.get_response(self_obj=self, params={'key': key})

    def delete_multi(self, keys: list[str]) -> bool:
        """
        Delete multiple keys from the cache.

        Args:
            keys (list[str]): The keys to delete.

        Returns:
            bool: True if the keys are deleted, False otherwise.

        Example:
            >>> cache = UserCache()
            >>> cache.delete_multi(['key1', 'key2'])
            True
        """
        return self.get_response(self_obj=self, params={'keys': keys})
