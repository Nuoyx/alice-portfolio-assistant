import time

from redis.asyncio import Redis


class RateLimiter:
    def __init__(
            self,
            redis_client: Redis,
            max_requests: int = 10,
            window_seconds: int = 24 * 60 * 60,
            key_prefix: str = "portfolio-assistant:rate-limit:",
    ):
        self._client = redis_client
        self._max_requests = max_requests
        self._window_seconds = window_seconds
        self._key_prefix = key_prefix

    async def is_allowed(self, key: str) -> bool:
        now = int(time.time())

        redis_key = (
            f"{self._key_prefix}"
            f"{key}:"
            f"{now // self._window_seconds}"
        )

        count = await self._client.incr(redis_key)

        if count == 1:
            await self._client.expire(
                redis_key,
                self._window_seconds,
            )

        return count <= self._max_requests

