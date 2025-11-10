"""Redis service for caching and session management."""
import json
from typing import Optional, Any, Dict
from redis import asyncio as aioredis
from redis.asyncio import Redis
import structlog

from app.core.config import settings

logger = structlog.get_logger()


class RedisService:
    """Redis service for caching and real-time data."""

    def __init__(self) -> None:
        """Initialize Redis service."""
        self.redis: Optional[Redis] = None
        self.url = settings.REDIS_URL

    async def connect(self) -> None:
        """Connect to Redis."""
        try:
            self.redis = await aioredis.from_url(
                self.url,
                encoding="utf-8",
                decode_responses=True,
                max_connections=settings.REDIS_MAX_CONNECTIONS,
            )
            await self.redis.ping()
            logger.info("redis_connected", url=self.url)
        except Exception as e:
            logger.error("redis_connection_failed", error=str(e))
            raise

    async def disconnect(self) -> None:
        """Disconnect from Redis."""
        if self.redis:
            await self.redis.close()
            logger.info("redis_disconnected")

    async def get(self, key: str) -> Optional[str]:
        """
        Get value from Redis.

        Args:
            key: Cache key

        Returns:
            Cached value or None
        """
        if not self.redis:
            return None
        try:
            return await self.redis.get(key)
        except Exception as e:
            logger.error("redis_get_failed", key=key, error=str(e))
            return None

    async def get_json(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Get JSON value from Redis.

        Args:
            key: Cache key

        Returns:
            Deserialized JSON or None
        """
        value = await self.get(key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError as e:
                logger.error("redis_json_decode_failed", key=key, error=str(e))
        return None

    async def set(
        self,
        key: str,
        value: str,
        expire: Optional[int] = None
    ) -> bool:
        """
        Set value in Redis.

        Args:
            key: Cache key
            value: Value to cache
            expire: Expiration time in seconds

        Returns:
            True if successful
        """
        if not self.redis:
            return False
        try:
            if expire:
                await self.redis.setex(key, expire, value)
            else:
                await self.redis.set(key, value)
            return True
        except Exception as e:
            logger.error("redis_set_failed", key=key, error=str(e))
            return False

    async def set_json(
        self,
        key: str,
        value: Dict[str, Any],
        expire: Optional[int] = None
    ) -> bool:
        """
        Set JSON value in Redis.

        Args:
            key: Cache key
            value: Dictionary to cache
            expire: Expiration time in seconds

        Returns:
            True if successful
        """
        try:
            json_value = json.dumps(value)
            return await self.set(key, json_value, expire)
        except (TypeError, ValueError) as e:
            logger.error("redis_json_encode_failed", key=key, error=str(e))
            return False

    async def delete(self, key: str) -> bool:
        """
        Delete key from Redis.

        Args:
            key: Cache key

        Returns:
            True if successful
        """
        if not self.redis:
            return False
        try:
            await self.redis.delete(key)
            return True
        except Exception as e:
            logger.error("redis_delete_failed", key=key, error=str(e))
            return False

    async def exists(self, key: str) -> bool:
        """
        Check if key exists in Redis.

        Args:
            key: Cache key

        Returns:
            True if key exists
        """
        if not self.redis:
            return False
        try:
            return bool(await self.redis.exists(key))
        except Exception as e:
            logger.error("redis_exists_failed", key=key, error=str(e))
            return False

    async def incr(self, key: str, amount: int = 1) -> Optional[int]:
        """
        Increment value in Redis.

        Args:
            key: Cache key
            amount: Amount to increment by

        Returns:
            New value or None
        """
        if not self.redis:
            return None
        try:
            return await self.redis.incrby(key, amount)
        except Exception as e:
            logger.error("redis_incr_failed", key=key, error=str(e))
            return None

    async def publish(self, channel: str, message: str) -> bool:
        """
        Publish message to Redis channel.

        Args:
            channel: Channel name
            message: Message to publish

        Returns:
            True if successful
        """
        if not self.redis:
            return False
        try:
            await self.redis.publish(channel, message)
            return True
        except Exception as e:
            logger.error("redis_publish_failed", channel=channel, error=str(e))
            return False


# Global Redis instance
redis_service = RedisService()
