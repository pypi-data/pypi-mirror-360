"""
Provides HTTP requests
using aiohttp. It also includes a session management mechanism
for efficient request handling.

Attributes:
    _max_number_sessions (int): Maximum number of requests per session.
    _sessions (lru.LRU): LRU cache for storing client sessions.
    _counts (dict): Dictionary to store the count of requests per host.
    _connect_options (dict): Connection options for the client session.

Functions:
    session_purged(key, value): Callback function to close
      the session when purged from the LRU cache.
    get_session(url): Get the client session for the specified URL.
    close(): Close all client sessions and clear the session cache.
    post(url, *args, **kwargs): Make an HTTP POST request using the client session.
    get(url, *args, **kwargs): Make an HTTP GET request using the client session.
    patch(url, *args, **kwargs): Make an HTTP PATCH request using the client session.
    delete(url, *args, **kwargs): Make an HTTP DELETE request using the client session.
    head(url, *args, **kwargs): Make an HTTP HEAD request using the client session.
    put(url, *args, **kwargs): Make an HTTP PUT request using the client session.
    options(url, *args, **kwargs): Make an HTTP OPTIONS request using the client session.
"""

import asyncio
import os

import aiohttp
import lru
import ujson
import yarl

# max # of requests per session
_max_number_sessions = int(os.environ.get("AIOHTTP_SESSION_SIZE", "200"))

# pylint:disable=unused-argument


def session_purged(key, value):
    """ Set session purged """
    asyncio.ensure_future(value.close())


# pylint:disable=c-extension-no-member
_sessions = lru.LRU(_max_number_sessions, callback=session_purged)
_counts = {}

_connect_options = {
    "ttl_dns_cache": int(os.environ.get("AIOHTTP_SESSION_DNS_CACHE", "20")),
    "limit": int(os.environ.get("AIOHTTP_SESSION_LIMIT", "500")),
    "force_close": True,
    "enable_cleanup_closed": True,
}


def get_session(url):
    """ Get session """
    url = yarl.URL(url)
    if url.host not in _sessions:
        _sessions[url.host] = aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(**_connect_options),
            # pylint:disable=c-extension-no-member
            json_serialize=ujson.dumps,
        )
        _counts[url.host] = 0
    _counts[url.host] += 1
    return _sessions[url.host]


async def close():
    """ Close session """
    for session in _sessions.values():
        await session.close()
    _sessions.clear()
    _counts.clear()


def post(url, *args, **kwargs):
    """ Http Post Function """
    session = get_session(url)
    return session.post(url, *args, **kwargs)


def get(url, *args, **kwargs):
    """ Http Get Function """
    session = get_session(url)
    return session.get(url, *args, **kwargs)


def patch(url, *args, **kwargs):
    """ Http Patch Function """
    session = get_session(url)
    return session.patch(url, *args, **kwargs)


def delete(url, *args, **kwargs):
    """ Http Delete Function """
    session = get_session(url)
    return session.delete(url, *args, **kwargs)


def head(url, *args, **kwargs):
    """ Get session"""
    session = get_session(url)
    return session.head(url, *args, **kwargs)


def put(url, *args, **kwargs):
    """ Http Put Function """
    session = get_session(url)
    return session.put(url, *args, **kwargs)


def options(url, *args, **kwargs):
    """ Get Http Options  """
    session = get_session(url)
    return session.options(url, *args, **kwargs)
