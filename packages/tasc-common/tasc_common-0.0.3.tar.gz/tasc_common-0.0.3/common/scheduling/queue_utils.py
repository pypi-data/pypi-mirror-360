import json
import time
import uuid
from collections.abc import Callable
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Any, Optional, Coroutine, Union

import aioredis
from loguru import logger
from pydantic import BaseModel

REDIS: aioredis.Redis | None = None
REDIS_PUBSUB: aioredis.client.PubSub | None = None
JSONSerializable = str | int | float | bool | None | dict | list


class RedisManager:
    # Configuration
    REDIS_URL = None

    # Instances
    REDIS: aioredis.Redis | None = None
    REDIS_PUBSUB: aioredis.client.PubSub | None = None

    @classmethod
    async def get_redis(cls) -> aioredis.Redis:
        if cls.REDIS is not None:
            return cls.REDIS
        assert cls.REDIS_URL is not None, "REDIS_URL must be set."
        cls.REDIS = await aioredis.from_url(cls.REDIS_URL)
        return cls.REDIS

    @classmethod
    async def get_redis_pubsub(cls) -> aioredis.client.PubSub:
        if cls.REDIS_PUBSUB is not None:
            return cls.REDIS_PUBSUB
        redis = await cls.get_redis()
        cls.REDIS_PUBSUB = redis.pubsub()
        return cls.REDIS_PUBSUB
    
    @classmethod
    async def close_redis(cls) -> None:
        if cls.REDIS is not None:
            await cls.REDIS.close()
            cls.REDIS = None

    @classmethod
    async def close_redis_pubsub(cls) -> None:
        if cls.REDIS_PUBSUB is not None:
            await cls.REDIS_PUBSUB.close()
            cls.REDIS_PUBSUB = None

    @classmethod
    @asynccontextmanager
    async def manage_redis(cls) -> aioredis.Redis:
        redis = await cls.get_redis()
        yield redis
        await cls.close_redis()


def serialize(obj: JSONSerializable | BaseModel, unique: bool = False) -> str:
    """
    Serialize an object to a JSON string. Supports both JSON-serializable objects and Pydantic models.

    Args:
        obj: The object to serialize.
        unique: Whether to make sure that the serialized string is unique for two
                objects that are otherwise the same.
    """
    if isinstance(obj, BaseModel):
        obj_type = obj.__class__.__qualname__
        obj = {"object_model": obj_type, "data": json.dumps(obj.model_dump())}
    else:
        obj = {"object_model": None, "data": json.dumps(obj)}

    if unique:
        obj["uuid"] = str(uuid.uuid4())

    to_serialize = json.dumps(obj)
    return to_serialize


def deserialize(
    serialized_obj: str | bytes, object_model: type
) -> JSONSerializable | BaseModel:
    """
    Deserialize an object from a JSON string. Supports both JSON-serializable objects and Pydantic models.

    Args:
        serialized_obj: The serialized object.
        object_model: The Pydantic / object model to deserialize the object into.
    """

    if isinstance(serialized_obj, bytes):
        serialized_obj = serialized_obj.decode("utf-8")
    obj = json.loads(serialized_obj)
    if object_model is not None:
        data = json.loads(obj["data"])
        return object_model(**data)

    return json.loads(obj["data"])


async def match_redis_keys(pattern: str) -> list[str]:
    redis = await RedisManager.get_redis()
    redis_keys = await redis.keys(pattern)
    return [k.decode() if isinstance(k, bytes) else str(k) for k in redis_keys]


async def enqueue(queue_name: str, obj: JSONSerializable | BaseModel) -> None:
    """
    Enqueue an object to the given queue. Supports both JSON-serializable objects and Pydantic models.

    Args:
        queue_name: The name of the queue to enqueue to.
        obj: The object to enqueue.
    """
    redis = await RedisManager.get_redis()
    await redis.rpush(queue_name, serialize(obj))
    return None


async def dequeue(
    queue_name: str,
    block: bool = False,
    timeout_seconds: float = 0.0,
    object_model: type | None = None,
) -> JSONSerializable | BaseModel | None:
    """
    Dequeue an object from the given queue. Supports both JSON-serializable objects and Pydantic models.

    Args:
        queue_name: The name of the queue to dequeue from.
        block: Whether to block until an object is available.
        timeout_seconds: The number of seconds to block for if blocking. If 0.0, block indefinitely.
        object_model: The Pydantic model to deserialize the object into.
    """
    redis = await RedisManager.get_redis()
    if block:
        item = await redis.blpop(queue_name, timeout=timeout_seconds)
        if item is None:
            serialized_obj = None
        else:
            _, serialized_obj = item
    else:
        serialized_obj = await redis.lpop(queue_name)

    if serialized_obj is None:
        return None
    else:
        return deserialize(serialized_obj, object_model=object_model)


async def schedule(
    queue_name: str,
    obj: JSONSerializable | BaseModel,
    delay_seconds: float | None = None,
    schedule_time: float | None = None,
    update: bool = False,
) -> None:
    """
    Schedule an object to be dequeued at a later time. Supports both JSON-serializable objects and Pydantic models.
    Either delay_seconds or schedule_time must be provided -- they are used to calculate the time at which the object
    should be dequeued by the `dequeue_scheduled` function.

    Args:
        queue_name: The name of the queue to schedule the object in.
        obj: The object to schedule.
        delay_seconds: The number of seconds to wait before scheduling the object for dequeueing.
        schedule_time: The time at which the object should be scheduled for dequeueing.
        update: Whether to update the scheduled time if the object is already scheduled. If not, a new object will be
                scheduled with the same data.
    """
    if delay_seconds is None:
        assert (
            schedule_time is not None
        ), "Either delay_seconds or schedule_time must be provided."
        output_time = schedule_time
    else:
        assert (
            schedule_time is None
        ), "Only one of delay_seconds or schedule_time should be provided."
        output_time = time.time() + delay_seconds
    redis = await RedisManager.get_redis()
    await redis.zadd(queue_name, {serialize(obj, unique=not update): output_time})
    return None


async def dequeue_scheduled(
    queue_name: str,
    object_model: type | None = None,
) -> tuple[JSONSerializable | BaseModel | None, float | None]:
    """
    Dequeue an object from the given schedule. Supports both JSON-serializable objects and Pydantic models.
    The dequeuing will happen if the current time (at which the function is called) is greater than the
    scheduled time of the object.

    Args:
        queue_name: The name of the schedule to dequeue from.
        object_model: The Pydantic model to deserialize the object into.
    """
    now = time.time()
    redis = await RedisManager.get_redis()
    item_and_scheduled_time = await redis.zrangebyscore(
        queue_name, min=0, max=now, start=0, num=1, withscores=True
    )
    if not item_and_scheduled_time:
        return None, None
    serialized_obj, scheduled_time = item_and_scheduled_time[0]
    await redis.zrem(queue_name, serialized_obj)
    return deserialize(serialized_obj, object_model=object_model), scheduled_time


@dataclass
class RemoveHandle:
    queue_name: str
    serialized_obj: str | bytes


async def peek_scheduled(
    queue_name: str, object_model: type | None = None
) -> tuple[JSONSerializable | BaseModel | None, float | None, RemoveHandle | None]:
    now = time.time()
    redis = await RedisManager.get_redis()
    item_and_scheduled_time = await redis.zrangebyscore(
        queue_name, min=0, max=now, start=0, num=1, withscores=True
    )
    if not item_and_scheduled_time:
        return None, None, None
    serialized_obj, scheduled_time = item_and_scheduled_time[0]
    return (
        deserialize(serialized_obj, object_model=object_model),
        scheduled_time,
        RemoveHandle(queue_name=queue_name, serialized_obj=serialized_obj),
    )


async def remove_scheduled(remove_handle: RemoveHandle) -> bool:
    redis = await RedisManager.get_redis()
    num_removed = await redis.zrem(
        remove_handle.queue_name, remove_handle.serialized_obj
    )
    # If the number of items removed is greater than 0, return True
    return num_removed > 0


async def attempt_lock_capture(
    lock_name: str, expire_in_seconds: float | None = None
) -> bool:
    """
    Attempt to capture a lock. If the lock is already held, this function will return False.
    Otherwise, it will capture the lock and return True.

    Args:
        lock_name: The name of the lock to capture.
        expire_in_seconds: The number of seconds after which the lock should expire.
    """
    redis = await RedisManager.get_redis()
    unique_value = str(uuid.uuid4())
    if expire_in_seconds is not None:
        lock_is_captured = await redis.set(
            lock_name, unique_value, ex=round(expire_in_seconds), nx=True
        )
    else:
        lock_is_captured = await redis.set(lock_name, unique_value, nx=True)
    return lock_is_captured


async def release_lock(lock_name: str) -> None:
    """
    Release a lock.

    Args:
        lock_name: The name of the lock to release.
    """
    redis = await RedisManager.get_redis()
    await redis.delete(lock_name)
    return None


async def is_lock_captured(lock_name: str) -> bool:
    """
    Check if a lock is in a captured state.

    Args:
        lock_name: The name of the lock to check.

    Returns:
        True if the lock is captured, False otherwise.
    """
    redis = await RedisManager.get_redis()
    lock_exists = await redis.exists(lock_name)
    return lock_exists == 1


async def consume_exclusively_with_backlog(
    fn: Callable,
    queue_name: str,
    object_identifier_fn: Callable[[Any], str],
    object_model: type | None = None,
    tick_interval_seconds: float = 60.0,
    backlog_delay_duration_seconds: float | None = 120.0,
    lock_name_prefix: str = "consumer_lock:",
    backlog_queue_name_prefix: str = "consumer_backlog:",
    post_lock_capture_callback: Optional[
        Callable[[Any], Coroutine[Any, Any, Any]]
    ] = None,
    post_lock_release_callback: Optional[
        Callable[[Any], Coroutine[Any, Any, Any]]
    ] = None,
    logging_enabled: bool = True,
):
    """
    Consume objects from a queue exclusively. Add object to a backlog queue if the lock cannot be captured.
    If the lock is captured, process any backlogged objects, then process the object.

    Args:
        fn: The function to call on each object.
        queue_name: The name of the queue to consume from.
        object_identifier_fn: A function that takes an object and returns a unique identifier for it.
        object_model: The Pydantic model to deserialize the object into.
        tick_interval_seconds: The number of seconds to wait between each iteration.
        backlog_delay_duration_seconds: The number of seconds to wait before scheduling a backlogged object for retry.
        lock_name_prefix: The prefix for the lock name.
        backlog_queue_name_prefix: The prefix for the backlog queue name.
        post_lock_capture_callback: A callback to call after capturing the lock.
        post_lock_release_callback: A callback to call after releasing the lock.
        logging_enabled: Whether to enable logging.
    """
    if not logging_enabled:
        logger.disable(__name__)

    while True:
        logger.debug(f"Attempting to dequeue from queue: {queue_name}.")
        obj = await dequeue(
            queue_name,
            object_model=object_model,
            block=True,
            timeout_seconds=tick_interval_seconds,
        )
        if obj is None:
            logger.debug(f"No items in queue: {queue_name}. Checking backlog.")
            # Check if there are any backlogged items
            await process_from_backlog(
                fn=fn,
                object_identifier_fn=object_identifier_fn,
                object_model=object_model,
                lock_name_prefix=lock_name_prefix,
                backlog_queue_name_prefix=backlog_queue_name_prefix,
                max_items_to_process=1,
            )
            continue

        logger.debug(f"Dequeued from queue: {queue_name}.")

        await process_with_lock_and_backlog(
            fn=fn,
            obj=obj,
            object_identifier_fn=object_identifier_fn,
            object_model=object_model,
            backlog_delay_duration_seconds=backlog_delay_duration_seconds,
            lock_name_prefix=lock_name_prefix,
            backlog_queue_name_prefix=backlog_queue_name_prefix,
            post_lock_capture_callback=post_lock_capture_callback,
            post_lock_release_callback=post_lock_release_callback,
        )


async def process_with_lock_and_backlog(
    fn: Callable,
    obj: JSONSerializable | BaseModel,
    object_identifier_fn: Callable[[Any], str],
    object_model: type | None = None,
    backlog_delay_duration_seconds: float | None = 120.0,
    lock_name_prefix: str = "consumer_lock:",
    backlog_queue_name_prefix: str = "consumer_backlog:",
    post_lock_capture_callback: Optional[
        Callable[[Any], Coroutine[Any, Any, Any]]
    ] = None,
    post_lock_release_callback: Optional[
        Callable[[Any], Coroutine[Any, Any, Any]]
    ] = None,
) -> None:
    try:
        obj_identifier = object_identifier_fn(obj)
    except Exception:
        logger.exception(f"Failed to get object identifier for {obj}.")
        raise

    logger.debug(f"Processing dequeued object with identifier: {obj_identifier}.")
    # Get the name of the lock and that of the backlog queue
    lock_name = f"{lock_name_prefix}{obj_identifier}"
    backlog_queue_name = f"{backlog_queue_name_prefix}{obj_identifier}"
    # Check if the lock is held. Capture it if it isn't, with a 5-hour expiry.
    lock_is_captured = await attempt_lock_capture(lock_name, expire_in_seconds=18000)
    if not lock_is_captured:
        logger.debug(
            f"Failed to capture lock for object with identifier {obj_identifier}."
        )
        # Lock could not be captured. We cannot process the message, so we'll need to add it to a backlog queue.
        await schedule(
            backlog_queue_name,
            obj,
            delay_seconds=backlog_delay_duration_seconds,
            update=True,
        )
        logger.debug(
            f"Rescheduled object with identifier {obj_identifier}, "
            f"due in {backlog_delay_duration_seconds} seconds."
        )
        # That's the best we can do for now. We'll try again later.
        return
    # If we've reached here, we've successfully captured the lock and can process the message.
    # But first, we'll process any backlogged items.
    logger.debug(f"Captured lock for object with identifier: {obj_identifier}")
    # It's time to call the callback
    if post_lock_capture_callback is not None:
        try:
            await post_lock_capture_callback(obj)
            logger.debug("Post lock capture callback called.")
        except Exception:
            logger.exception("Post lock capture callback failed.")
    while True:
        backlog_obj, _ = await dequeue_scheduled(
            backlog_queue_name, object_model=object_model
        )
        if backlog_obj is None:
            break

        try:
            backlog_obj_identifier = object_identifier_fn(backlog_obj)
        except Exception:
            logger.exception(f"Failed to get object identifier for {backlog_obj}.")
            await release_lock(lock_name)
            logger.debug("Lock released, raising now.")
            raise

        logger.debug(
            f"Dequeued backlog object with identifier {backlog_obj_identifier}."
        )
        try:
            logger.debug(
                f"Processing backlog object with identifier: {backlog_obj_identifier}."
            )
            # TODO @now: Make this run in an executor
            await fn(backlog_obj)
            logger.debug(
                f"Processed backlog object with identifier: {backlog_obj_identifier}."
            )
        except Exception:
            logger.exception(
                f"Failed to process object with identifier: {backlog_obj_identifier}. "
                f"Exception follows."
            )
            await release_lock(lock_name)
            logger.debug("Lock released, raising now.")
            raise
    # Now we can process the message
    try:
        logger.debug(f"Processing object with identifier: {obj_identifier}")
        await fn(obj)
        logger.debug(f"Processed object with identifier: {obj_identifier}")
    except Exception:
        logger.exception(
            f"Failed to process object with identifier: {obj_identifier}. "
            f"Exception follows."
        )
        await release_lock(lock_name)
        logger.debug("Lock released, raising now.")
        raise
    # Release the lock
    await release_lock(lock_name)
    logger.debug(f"Lock released for object with identifier: {obj_identifier}")
    if post_lock_release_callback is not None:
        try:
            await post_lock_release_callback(obj)
            logger.debug("Post lock release callback called.")
        except Exception:
            logger.exception("Post lock release callback failed.")


async def process_from_backlog(
    fn: Callable,
    object_identifier_fn: Callable[[Any], str],
    object_model: type | None = None,
    lock_name_prefix: str = "consumer_lock:",
    backlog_queue_name_prefix: str = "consumer_backlog:",
    max_items_to_process: int = 10,  # Limit the number of items processed in one call
) -> None:
    processed_count = 0

    # Get all backlog queue names
    backlog_queue_pattern = f"{backlog_queue_name_prefix}*"
    backlog_queues = await match_redis_keys(backlog_queue_pattern)

    for backlog_queue in backlog_queues:
        loop_count = 0
        while processed_count < max_items_to_process:
            loop_count += 1
            if loop_count > max_items_to_process * 10:
                # We've looped through the backlog queues too many times
                logger.error(
                    f"Exceeded maximum loop count for backlog queue: {backlog_queue}. "
                    f"Something is wrong, investigate ASAP."
                )
                break
            # Peek the next backlogged item. This does not dequeue the item.
            backlog_obj, scheduled_time, remove_handle = await peek_scheduled(
                backlog_queue, object_model=object_model
            )

            if backlog_obj is None:
                # No more backlogged items in this queue
                break

            try:
                obj_identifier = object_identifier_fn(backlog_obj)
            except Exception:
                logger.exception(f"Failed to get object identifier for {backlog_obj}.")
                continue  # Skip this item and move to the next

            logger.debug(
                f"Processing backlogged item from queue {backlog_queue} "
                f"with identifier: {obj_identifier}"
            )

            lock_name = f"{lock_name_prefix}{obj_identifier}"

            # Attempt to capture the lock
            lock_captured = await attempt_lock_capture(
                lock_name, expire_in_seconds=18000
            )

            if not lock_captured:
                # Lock is not available, so reschedule this item
                logger.debug(
                    f"Lock not available for backlog item {obj_identifier}. Skipping."
                )
                continue

            logger.debug(
                f"Lock captured for backlog item with identifier: {obj_identifier}"
            )

            # We have the lock, so let's try to remove the item from the backlog
            removed = await remove_scheduled(remove_handle)

            if not removed:
                logger.debug(
                    f"Item {obj_identifier} was removed from backlog by another process. Releasing lock."
                )
                await release_lock(lock_name)
                logger.debug(
                    f"Lock released for backlog item with identifier: {obj_identifier}"
                )
                continue

            logger.debug(
                f"Backlog item with identifier {obj_identifier} removed from backlog queue."
            )

            try:
                logger.debug(
                    f"Processing backlog item with identifier: {obj_identifier}"
                )
                await fn(backlog_obj)
                logger.debug(
                    f"Processed backlog item with identifier: {obj_identifier}"
                )
                processed_count += 1
            except Exception:
                logger.exception(
                    f"Failed to process backlog item with identifier: {obj_identifier}. "
                    f"Exception follows"
                )
                await release_lock(lock_name)
                logger.debug("Lock released, raising now.")
                raise

        if processed_count >= max_items_to_process:
            # We've reached the maximum number of items to process
            break

    logger.debug(f"Processed {processed_count} items from backlog queues")


async def check_if_locked(
    obj: Any,
    object_identifier_fn: Optional[Callable[[Any], str]] = None,
    object_identifier: Optional[str] = None,
    lock_name_prefix: str = "consumer_lock:",
) -> bool:
    if object_identifier is None:
        assert (
            object_identifier_fn is not None
        ), "Either object_identifier or object_identifier_fn must be provided."
        object_identifier = object_identifier_fn(obj)
    else:
        assert (
            object_identifier_fn is None
        ), "Only one of object_identifier or object_identifier_fn should be provided."
    lock_name = f"{lock_name_prefix}{object_identifier}"
    return await is_lock_captured(lock_name)


async def publish_to_channel(
    channel: str, message: Union[str, JSONSerializable], do_serialize: bool = True
) -> None:
    redis = await RedisManager.get_redis()
    if do_serialize:
        message = serialize(message)
    await redis.publish(channel, message)
    return None
