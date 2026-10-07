import json
from typing import Any

import redis.asyncio as redis
from redis.exceptions import RedisError


class MemoryUnavailableError(Exception):
    pass


class RedisConversationMemory:
    def __init__(
        self,
        redis_client: redis,
        ttl: int,
        key_prefix: str = "portfolio-assistant:chat:",
    ) -> None:
        self._client = redis_client
        self._ttl = ttl
        self._key_prefix = key_prefix

    def _key(self, conversation_id: str) -> str:
        return f"{self._key_prefix}{conversation_id}"

    async def ping(self) -> bool:
        try:
            return bool(await self._client.ping())
        except RedisError as exc:
            raise MemoryUnavailableError(
                "Redis is unavailable."
            ) from exc

    async def load(
        self,
        conversation_id: str,
    ) -> list[dict[str, Any]]:
        try:
            raw_messages = await self._client.lrange(
                self._key(conversation_id),
                0,
                -1,
            )
        except RedisError as exc:
            raise MemoryUnavailableError(
                "Conversation memory is unavailable."
            ) from exc

        messages = []

        for raw in raw_messages:
            try:
                messages.append(json.loads(raw))
            except json.JSONDecodeError:
                continue

        return messages

    async def append_many(
        self,
        conversation_id: str,
        messages: list[dict[str, Any]],
    ) -> None:
        if not messages:
            return

        key = self._key(conversation_id)

        try:
            async with self._client.pipeline(
                transaction=True
            ) as pipeline:
                for message in messages:
                    await pipeline.rpush(
                        key,
                        json.dumps(
                            message,
                            ensure_ascii=False,
                        ),
                    )

                await pipeline.expire(key, self._ttl)
                await pipeline.execute()

        except RedisError as exc:
            raise MemoryUnavailableError(
                "Conversation memory could not be saved."
            ) from exc

    async def close(self) -> None:
        await self._client.aclose()

