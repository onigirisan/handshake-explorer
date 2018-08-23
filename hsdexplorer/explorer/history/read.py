from django.conf import settings
from google.cloud import datastore
import hashlib
import os
import sys
from functools import lru_cache
if sys.version_info < (3, 6):
    import sha3


if not os.environ.get('COLLECTSTATIC'):
    datastore_client = datastore.Client(namespace=settings.DATASTORE_NAMESPACE)


def get_events(name=None, limit=50, offset=0):
    """Retrieve event history for a given name."""
    query = datastore_client.query(kind='HSEvent')
    if name:
        name_hash = _get_name_hash(name)
        query.add_filter('name_hash', '=', name_hash)
        query.order = ['-block', '-tx_index']
    else:
        query.order = ['-block']
    return list(query.fetch(limit=limit, offset=offset))


def get_names():
    query = datastore_client.query(kind='HSName')
    return list(query.fetch())


@lru_cache(maxsize=2048)
def lookup_name(name_hash):
    query = datastore_client.query(kind='HSName')
    query.add_filter('name_hash', '=', name_hash)
    return list(query.fetch())[0]['name']


def _get_name_hash(name):
    m = hashlib.sha3_256()
    m.update(name.encode('ascii'))
    return m.hexdigest()


def get_name(name):
    key = datastore_client.key('HSName', name)
    return datastore_client.get(key)
