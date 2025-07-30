import redis
from datetime import timedelta


cache = {
    "time_period": None,
    "last_updated": None
}

def get_time_period():
    return cache.get('time_period')

def set_time_period(time_period):
    cache['time_period'] = time_period
    cache['last_updated'] = time_period


class SimpleCache:
    def __init__(self, host="redis", port=6379, db=0, prefix="cache"):
        self.redis = redis.Redis(host=host, port=port, db=db, decode_responses=True)
        self.prefix = prefix

    def _key(self, key):
        return f"{self.prefix}:{key}"

    def set(self, key, value="1", ttl_seconds=15):
        self.redis.setex(self._key(key), timedelta(seconds=ttl_seconds), value)

    def get(self, key):
        return self.redis.get(self._key(key))

    def exists(self, key):
        return self.redis.exists(self._key(key))

    def delete(self, key):
        self.redis.delete(self._key(key))
