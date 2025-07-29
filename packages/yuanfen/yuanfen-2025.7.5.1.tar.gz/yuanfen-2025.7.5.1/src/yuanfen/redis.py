import redis
import time


class RedisLock:
    def __init__(self, redis_client, lock_key, timeout=10, retry_interval=None):
        self.redis_client = redis_client
        self.lock_key = lock_key
        self.timeout = timeout
        self.retry_interval = retry_interval
        self.locked = False

    def acquire(self):
        start_time = time.time()
        while time.time() - start_time < self.timeout:
            if self.redis_client.set(self.lock_key, "1", ex=self.timeout, nx=True):
                self.locked = True
                return True
            elif not self.retry_interval:
                return False
            else:
                time.sleep(self.retry_interval)

        return False

    def release(self):
        if self.locked:
            self.redis_client.delete(self.lock_key)
            self.locked = False


class Redis:
    def __init__(self, host: str, port: int = 6379, password: str = None, db: int = 0, prefix: str = None, decode_responses: bool = True):
        self.redis_client = redis.StrictRedis(
            host=host,
            port=port,
            password=password,
            db=db,
            decode_responses=decode_responses,
        )
        self.prefix = prefix

    def prefixed(self, key: str):
        return f"{self.prefix}:{key}" if self.prefix else key

    def get(self, key: str):
        return self.redis_client.get(self.prefixed(key))

    def set(self, key: str, value: str, ex=None, px=None, nx=False):
        return self.redis_client.set(self.prefixed(key), value, ex=ex, px=px, nx=nx)

    def delete(self, key: str):
        return self.redis_client.delete(self.prefixed(key))

    def incr(self, key: str, amount=1):
        return self.redis_client.incr(self.prefixed(key), amount)
