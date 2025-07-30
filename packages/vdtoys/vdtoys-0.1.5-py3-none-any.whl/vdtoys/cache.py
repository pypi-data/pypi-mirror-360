# -*- coding: utf-8 -*-
#
# Author: GavinGong aka VisualDust
# Github: github.com/visualDust
# Date:   20250301


class CachedDict(dict):
    def __init__(self, generator_func):
        """
        Initializes the CachedDict with a generator function.

        Parameters:
        - generator_func: A function that takes a key and returns a value.
        """
        self.generator_func = generator_func
        self._cache = {}

    def __getitem__(self, key):
        """
        Returns the value associated with 'key'. If the key is not in the cache,
        the generator function is called with the key to produce the value.
        """
        if key not in self._cache:
            self._cache[key] = (
                self.generator_func(*key)  # Unpack the keys as arguments
                if isinstance(key, tuple)
                else self.generator_func(key)
            )
        return self._cache[key]

    def __contains__(self, key):
        """
        Checks if the key has already been generated and stored.
        """
        return key in self._cache

    def __setitem__(self, key, value):
        """
        Optionally, allow setting a key directly.
        """
        self._cache[key] = value

    def __eq__(self, value):
        """
        Checks if the cached value is equal to the given value.
        """
        return self._cache == value

    def __bool__(self):
        """
        Checks if the cache is not empty.
        """
        return bool(self._cache)

    def get(self, key, default=None):
        """
        Returns the value for key if key is in the cache; otherwise, returns default.
        """
        try:
            return self.__getitem__(key)
        except Exception:
            return default

    def keys(self):
        """
        Returns the cached keys.
        """
        return self._cache.keys()

    def values(self):
        """
        Returns the cached values.
        """
        return self._cache.values()

    def items(self):
        """
        Returns the cached items.
        """
        return self._cache.items()

    def clear(self):
        """
        Clears the cached values.
        """
        self._cache.clear()

    def __repr__(self):
        return f"{self.__class__.__name__}({self._cache})"
