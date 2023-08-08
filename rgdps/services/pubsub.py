# Not named `redis.py` as it would fight with the `redis` package.
from __future__ import annotations

import asyncio
import traceback
from typing import Awaitable
from typing import Callable

from redis.asyncio import Redis

from rgdps import logger
from rgdps.common.context import Context

RedisHandler = Callable[[Context, bytes], Awaitable[None]]


async def _listen_router(
    ctx: Context,
    redis: Redis,
    router: RedisPubsubRouter,
) -> None:
    redis_handlers = router.route_map()
    async with redis.pubsub() as pubsub:
        for channel in redis_handlers:
            await pubsub.subscribe(channel)
            logger.debug(f"Subscribed to {channel}.")

        while True:
            # TODO: Handle errors (different message types)
            message = await pubsub.get_message()
            if message is not None:
                if message.get("type") != "message":
                    continue
                try:
                    # TODO: Investigate if spinning up tasks for each message
                    # is a good idea.
                    handler = redis_handlers[message["channel"]]
                    await handler(ctx, message["data"])
                except Exception:
                    logger.error(
                        f"Error in redis handler for {message['channel']}\n"
                        + traceback.format_exc(),
                    )

            # FIXME: This is a hack to prevent the event loop from blocking.
            await asyncio.sleep(0.1)


def listen_router(
    ctx: Context,
    redis: Redis,
    router: RedisPubsubRouter,
) -> None:
    asyncio.create_task(_listen_router(ctx, redis, router))


async def listen_pubsubs(
    ctx: Context,
    redis: Redis,
    *routers: RedisPubsubRouter,
) -> None:
    main_handler = RedisPubsubRouter()

    for router in routers:
        main_handler.merge(router)

    listen_router(ctx, redis, main_handler)


class RedisPubsubRouter:
    """A router for Redis subscriptions."""

    def __init__(self) -> None:
        # NOTE: Redis pubsub channels are bytes, not strings.
        self._routes: dict[bytes, RedisHandler] = {}

    def register(
        self,
        channel: str,
    ) -> Callable[[RedisHandler], RedisHandler]:
        def decorator(handler: RedisHandler) -> RedisHandler:
            self._routes[channel.encode()] = handler
            return handler

        return decorator

    def merge(self, other: RedisPubsubRouter) -> None:
        self._routes |= other._routes

    def route_map(self) -> dict[bytes, RedisHandler]:
        return self._routes
