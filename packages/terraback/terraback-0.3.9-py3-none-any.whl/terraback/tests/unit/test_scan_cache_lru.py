import time
from datetime import timedelta
from terraback.utils.scan_cache import ScanCache


def test_memory_cache_lru_eviction(tmp_path):
    cache = ScanCache(cache_dir=tmp_path, ttl=timedelta(hours=1))
    cache._memory_cache_max_size = 2

    params1 = {'id': 1}
    params2 = {'id': 2}
    params3 = {'id': 3}

    cache.set('svc', 'op1', params1, {'r': 1})
    cache.set('svc', 'op2', params2, {'r': 2})

    # Access first key to mark it as recently used
    cache.get('svc', 'op1', params1)

    cache.set('svc', 'op3', params3, {'r': 3})

    key1 = cache._generate_key('svc', 'op1', params1)
    key2 = cache._generate_key('svc', 'op2', params2)
    key3 = cache._generate_key('svc', 'op3', params3)

    # key2 should be evicted as it is least recently used
    assert key2 not in cache._memory_cache
    assert list(cache._memory_cache.keys()) == [key1, key3]
