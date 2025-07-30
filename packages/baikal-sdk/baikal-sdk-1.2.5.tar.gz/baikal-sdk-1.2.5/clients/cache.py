"""lru cache that include a ttl, a negative ttl (for failures)
allow dictionaries as positional arguments"""
__author__ = "4th Platform team"
__license__ = "see LICENSE file"

import logging
import time
from collections import namedtuple
from functools import update_wrapper
from threading import RLock

logger = logging.getLogger(__name__)

_CacheInfo = namedtuple("CacheInfo", ["hits", "misses", "maxsize", "currsize"])
_CacheValue = namedtuple("CacheValue", ["ttl_expiry", "nttl_expiry", "value"])


class _HashableDict(dict):
    """Utility hash for consider dicts as arguments"""

    def __key(self):
        return tuple((k, self[k]) for k in sorted(self))

    def __hash__(self):
        return hash(self.__key())

    def __eq__(self, other):
        # pylint:disable=protected-access
        return self.__key() == other.__key()


class _HashedSeq(list):
    """Utility class for storing the cache key as optional and kw arguments"""

    __slots__ = ("hashvalue",)

    def __init__(self, tup, _hash=hash):  # @ReservedAssignment
        self[:] = tup
        self.hashvalue = _hash(tup)

    def __hash__(self):
        return self.hashvalue


def _make_key(
    args,
    kwds,
    typed,
    kwd_mark=(object(),),
    fasttypes=(int, str, frozenset, type(None)),
    _sorted=sorted,
    _tuple=tuple,
    _type=type,
    _len=len,
):  # @ReservedAssignment
    # Make a cache key from optionally typed positional and keyword arguments'
    key = _tuple(map(lambda x: _HashableDict(
        x) if isinstance(x, dict) else x, args))
    if kwds:
        sorted_items = _sorted(kwds.items())
        key += kwd_mark
        for item in sorted_items:
            if isinstance(item[1], dict):
                key += (item[0], _HashableDict(item[1]))
            else:
                key += item
    if typed:
        key += _tuple(_type(v) for v in args)
        if kwds:
            key += _tuple(_type(v) for k, v in sorted_items)  # @UnusedVariable
    elif _len(key) == 1 and _type(key[0]) in fasttypes:
        return key[0]
    return _HashedSeq(key)

# pylint:disable=too-many-arguments


def _update_cache_key(cache, key, cache_value, link, link_prev, link_next):
    if isinstance(link, list):
        cache[key] = [link_prev, link_next, key, cache_value]
    else:
        cache[key] = cache_value


# pylint:disable=too-many-arguments
def _check_refresh_ttl(link, ttl, nttl, now, cache, user_function, args, kwds):
    """
    Internal method for the logic of ttl expiration:
    When ttr has expired, the cache should be updated by calling the user_function
    The cache key is then updated with the recovered value
    If the user_function raises exception, the exception is raised
    """
    # unpack the cache value if needed
    if isinstance(link, list):
        link_prev, link_next, key, cache_value = link
    else:
        key = None
        link_prev = None
        link_next = None
        cache_value = link  # max

    if cache_value.ttl_expiry < now:
        logger.debug("Refreshing an expired cache element")
        try:
            result = user_function(*args, **kwds)

            # pack the result_function in CacheValue
            cache_value = _CacheValue(now + ttl, now + nttl, result)
            _update_cache_key(cache, key, cache_value, link, link_prev, link_next)
        # pylint:disable=broad-exception-caught
        except Exception as error:
            logger.info("Error when refreshing an expired cache element")
            if cache_value.nttl_expiry < now:
                del cache[key]
                raise error

            # Reuse old cache value and refresh ttl
            cache_value = _CacheValue(
                now + ttl, cache_value.nttl_expiry, cache_value.value
            )
            _update_cache_key(cache, key, cache_value, link, link_prev, link_next)

    return cache_value.value

# pylint:disable=too-many-statements


def lru_cache(max_size=100, typed=False, ttl=60 * 60, nttl=0):
    """Least-recently-used cache decorator.

    If *typed* is True, arguments of different types will be cached separately.
    For example, f(3.0) and f(3) will be treated as distinct calls with
    distinct results.
    When some positional argument is a dict, typed=True should be used.

    The expiration time of the element in cache is controlled by ttl:

    ttl defines the time within the element of the cache
    would be returned without calling the function.

    If no element is cached or ttl has expired, the decorated
    function will be called and the returned value will be cached; ttl will be updated

    if nttl is specified (in seconds) when the cache has some value stored,
    the ttl expires, the nttl has not expired  and the fucntion fails when invoking,
    instead of clearing the cache, the old value is keeped as new for ttl time

    View the cache statistics named tuple (hits, misses, maxsize, currsize) with
    f.cache_info().  Clear the cache and statistics with f.cache_clear().
    Access the underlying function with f.__wrapped__.
    """

    # Users should only access the lru_cache through its public API:
    #       cache_info, cache_clear, and f.__wrapped__
    # The internals of the lru_cache are encapsulated for thread safety and
    # to allow the implementation to change (including a possible C version).

    def decorating_function(user_function):
        # pylint:disable=too-many-statements,too-many-locals
        cache = {}
        stats = [0, 0]  # make statistics updateable non-locally
        # pylint:disable=invalid-name
        HITS, MISSES = 0, 1  # names for the stats fields
        make_key = _make_key
        cache_get = cache.get  # bound method to lookup key or return None
        _len = len  # localize the global len() function
        lock = RLock()  # because linkedlist updates aren't threadsafe
        root = []  # root of the circular doubly linked list
        root[:] = [root, root, None, None]  # initialize by pointing to self
        nonlocal_root = [root]  # make updateable non-locally
        # pylint:disable=invalid-name
        PREV, NEXT, KEY, RESULT = 0, 1, 2, 3  # names for the link fields

        def wrapper(*args, **kwds):
            now = time.time()
            # size limited caching that tracks accesses by recency
            key = make_key(args, kwds, typed) if kwds or typed else args
            with lock:
                link = cache_get(key)
                if link is not None:
                    # record recent use of the key by moving it to the front of the list
                    (root,) = nonlocal_root
                    link_prev, link_next, key, result = link
                    link_prev[NEXT] = link_next
                    link_next[PREV] = link_prev
                    last = root[PREV]
                    last[NEXT] = root[PREV] = link
                    link[PREV] = last
                    link[NEXT] = root
                    stats[HITS] += 1
                    result = _check_refresh_ttl(
                        link, ttl, nttl, now, cache, user_function, args, kwds
                    )
                    return result
            result = user_function(*args, **kwds)
            with lock:
                (root,) = nonlocal_root
                if key in cache:
                    # getting here means that this same key was added to the
                    # cache while the lock was released.  since the link
                    # update is already done, we need only return the
                    # computed result and update the count of misses.
                    pass
                elif _len(cache) >= max_size:
                    # use the old root to store the new key and result
                    oldroot = root
                    oldroot[KEY] = key
                    oldroot[RESULT] = _CacheValue(
                        now + ttl, now + nttl, result)
                    # empty the oldest link and make it the new root
                    root = nonlocal_root[0] = oldroot[NEXT]
                    oldkey = root[KEY]
                    root[KEY] = root[RESULT] = None
                    # now update the cache dictionary for the new links
                    del cache[oldkey]
                    cache[key] = oldroot
                else:
                    # put result in a new link at the front of the list
                    last = root[PREV]
                    link = [last, root, key, _CacheValue(
                        now + ttl, now + nttl, result)]
                    last[NEXT] = root[PREV] = cache[key] = link
                stats[MISSES] += 1
            return result

        def cache_info():
            """Report cache statistics"""
            with lock:
                return _CacheInfo(stats[HITS], stats[MISSES], max_size, len(cache))

        def cache_clear():
            """Clear the cache and cache statistics"""
            with lock:
                cache.clear()
                root = nonlocal_root[0]
                root[:] = [root, root, None, None]
                stats[:] = [0, 0]

        wrapper.__wrapped__ = user_function
        wrapper.cache_info = cache_info
        wrapper.cache_clear = cache_clear
        return update_wrapper(wrapper, user_function)

    return decorating_function
