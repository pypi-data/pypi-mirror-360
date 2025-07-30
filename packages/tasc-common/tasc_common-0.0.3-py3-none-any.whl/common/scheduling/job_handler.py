import json
from collections.abc import Callable
from enum import Enum
from typing import Optional, Union, List, Tuple
import asyncio

from loguru import logger
from pydantic import BaseModel

from common.core.utils import format_time
from common.database.utils import find_primary_key
from common.scheduling.queue_utils import (
    consume_exclusively_with_backlog,
    enqueue,
    schedule,
    check_if_locked,
    publish_to_channel,
    dequeue_scheduled,
)
from common.scheduling.utils import NotFoundInDatabaseError, get_job_parameters

# ******************
# *** Job Bizniz ***
# ******************


DEFAULT_JOB_QUEUE_NAME = "primary"
DEFAULT_SCHEDULE_QUEUE_NAME = "schedule"
LOW_PRIORITY_JOB_QUEUE_NAME = "low_priority"


class Job(BaseModel):
    module_name: str
    model_name: str
    method_name: str
    instance_primary_key: str
    method_kwargs_json: str | None = None
    status_channel: str | None = None
    status_extra_payload: dict | None = None
    next_job: Optional["Job"] = None
    queue_name: Optional[str] = None
    job_group: Optional[str] = None

    def identify(self) -> str:
        return f"{self.module_name}.{self.model_name}.{self.method_name}:{self.instance_primary_key}"

    def identify_in_queue(self) -> str:
        # IMPORTANT: We don't use identify() because we don't want to include the job name.
        # Including the job name would make it possible to enqueue multiple methods of the
        # same instance concurrently (instead of using backlogs), which we don't want to allow.
        # However, sometimes, we *want* to run multiple methods of the same instance concurrently,
        # and in those cases, we let the caller set a job_group. Jobs in the same job_group
        # don't run concurrently.
        if self.job_group is None:
            return f"{self.module_name}.{self.model_name}:{self.instance_primary_key}"
        else:
            return f"{self.module_name}.{self.model_name}:{self.instance_primary_key}:{self.job_group}"

    def get_method_kwargs(self):
        return json.loads(self.method_kwargs_json) if self.method_kwargs_json else {}

    @classmethod
    def new(
        cls,
        job_fn: str | Callable | None = None,
        *,
        module_name: str | None = None,
        model_name: str | type | None = None,
        method_name: str | None = None,
        instance_primary_key: str | None = None,
        status_channel: str | None = None,
        status_extra_payload: dict | None = None,
        next_job: Optional["Job"] = None,
        queue_name: Optional[str] = None,
        ensure_sql_model: bool = True,
        job_group: Optional[str] = None,
        **method_kwargs,
    ):
        # Check if model_name is provided, and if it is,
        # whether it's a class
        if model_name is not None:
            if isinstance(model_name, type):
                model_name = model_name.__name__
        # Check if job_fn is provided
        if job_fn is None:
            assert module_name is not None
            assert model_name is not None
            assert method_name is not None
            assert instance_primary_key is not None
            return cls(
                module_name=module_name,
                model_name=model_name,
                method_name=method_name,
                instance_primary_key=instance_primary_key,
                method_kwargs_json=json.dumps(method_kwargs),
                status_channel=status_channel,
                status_extra_payload=status_extra_payload,
                next_job=next_job,
                queue_name=queue_name,
                job_group=job_group,
            )
        elif isinstance(job_fn, str):
            # Assume syntax: "module_name.model_name.method_name:instance_primary_key"
            model_name_and_method_name, instance_primary_key = job_fn.split(":")
            *module_names, model_name, method_name = model_name_and_method_name.split(
                "."
            )
            module_name = ".".join(module_names)
            return cls(
                module_name=module_name,
                model_name=model_name,
                method_name=method_name,
                instance_primary_key=instance_primary_key,
                method_kwargs_json=json.dumps(method_kwargs),
                status_channel=status_channel,
                status_extra_payload=status_extra_payload,
                next_job=next_job,
                queue_name=queue_name,
                job_group=job_group,
            )
        else:
            # If we're here, job_fn is provided.
            # Get the job parameters
            job_parameters = {
                **dict(
                    module_name=module_name,
                    model_name=model_name,
                    instance_primary_key=instance_primary_key,
                    method_name=method_name,
                ),
                **get_job_parameters(job_fn, ensure_sql_model=ensure_sql_model),
            }
            assert job_parameters["model_name"] is not None, (
                "Model name could not be inferred "
                "(possibly because job_fn is not bound to an instance of a SQLModel)."
            )
            assert job_parameters["instance_primary_key"] is not None, (
                "Instance primary key could not be inferred "
                "(possibly because job_fn is not bound to an instance of a SQLModel)."
            )
            return cls(
                **job_parameters,
                method_kwargs_json=json.dumps(method_kwargs),
                status_channel=status_channel,
                status_extra_payload=status_extra_payload,
                next_job=next_job,
                queue_name=queue_name,
                job_group=job_group,
            )

    def follow_up_with(self, job: Union["Job", str, callable], **job_kwargs):
        if isinstance(job, str) or callable(job):
            job = Job.new(job, **job_kwargs)
        else:
            assert isinstance(job, Job)
        self.next_job = job
        return self

    def bind_to_queue(self, queue_name: str, overwrite: bool = True) -> "Job":
        if self.queue_name is None or overwrite:
            self.queue_name = queue_name
        # Get the next job and bind it to the same queue, if possible
        if self.next_job is not None:
            self.next_job.bind_to_queue(queue_name, overwrite=False)
        return self

    async def enqueue(self, queue_name: Optional[str] = None):
        if queue_name is None:
            # Check if the job specifies a queue name
            queue_name = self.queue_name
        if queue_name is None:
            # If the job doesn't specify a queue name, use the default queue name
            queue_name = DEFAULT_JOB_QUEUE_NAME
        logger.debug(f"Enqueueing job: {self.identify()} to queue {queue_name}")
        await enqueue_new_job(self.bind_to_queue(queue_name), queue_name=queue_name)
        return self

    async def schedule(self, at_time: float, schedule_queue_name: Optional[str] = None):
        if schedule_queue_name is None:
            schedule_queue_name = DEFAULT_SCHEDULE_QUEUE_NAME
        logger.debug(
            f"Scheduling job: {self.identify()} to run at {format_time(at_time)} "
            f"on queue {schedule_queue_name}"
        )
        await schedule_new_job(self, at_time, queue_name=schedule_queue_name)
        return self

    async def check_if_processing(self) -> bool:
        return await check_if_job_is_processing(self)


class EventType(str, Enum):
    LOCK_CAPTURED = "LOCK_CAPTURED"
    LOCK_RELEASED = "LOCK_RELEASED"


class SchedulingEvent(BaseModel):
    job_identifier: str
    event_type: EventType
    event_data: dict | None = None


class ConversationTitleUpdateEvent(BaseModel):
    conversation_id: str
    new_title: str


async def executor(job: Job) -> None:
    """Outer executor that handles dynamic imports and creates the session-managed inner executor"""
    logger.debug(f"Currently executing: {job.identify()}")

    # Dynamically import the module
    try:
        module = __import__(job.module_name, fromlist=["*"])
    except ImportError:
        raise ImportError(f"Could not import module: {job.module_name}")

    # Import the appropriate SessionManager
    root_package = job.module_name.split(".")[0]
    try:
        session_manager_module = __import__(
            f"{root_package}.session_manager", fromlist=["*"]
        )
        SessionManager = getattr(session_manager_module, "SessionManager")
    except ImportError:
        logger.exception(
            f"Could not import SessionManager from {root_package}.session_manager"
        )
        raise ImportError(
            f"Could not import SessionManager from {root_package}.session_manager"
        )
    except AttributeError:
        logger.exception(f"SessionManager not found in {root_package}.session_manager")
        raise AttributeError(
            f"SessionManager not found in {root_package}.session_manager"
        )

    @SessionManager.with_sync_session
    async def _execute_with_session() -> None:
        model_cls = getattr(module, job.model_name)
        primary_key_name = find_primary_key(model_cls)

        # Try to get it from the session
        instances = await SessionManager.async_get(
            model_cls, mode="all", **{primary_key_name: job.instance_primary_key}
        )
        if len(instances) == 0:
            raise NotFoundInDatabaseError(
                f'Instance with primary key "{job.instance_primary_key}" '
                f'of model "{job.model_name}" not found in database.'
            )
        instance = instances[0]

        # Get the job function
        job_method = getattr(instance, job.method_name)
        method_kwargs = job.get_method_kwargs()

        # Run the job
        try:
            await job_method(**method_kwargs)
            logger.debug(f"Executed job: {job.identify()}")
        except Exception:
            logger.exception(f"Error while executing job {job}.")
            raise

        # If there is a follow-up job, enqueue it
        if job.next_job:
            logger.debug(f"Enqueueing follow-up job: {job.next_job.identify()}")
            await job.next_job.enqueue()
        logger.debug(f"Finished executing: {job.identify()}")

    await _execute_with_session()


async def enqueue_new_job(job: Job, queue_name: str = DEFAULT_JOB_QUEUE_NAME) -> Job:
    await enqueue(queue_name=queue_name, obj=job)
    return job


async def schedule_new_job(
    job: Job, at_time: float, queue_name: str = DEFAULT_SCHEDULE_QUEUE_NAME
) -> Job:
    await schedule(queue_name=queue_name, obj=job, schedule_time=at_time)
    return job


async def check_if_job_is_processing(job: Job) -> bool:
    return await check_if_locked(
        obj=job,
        object_identifier=job.identify_in_queue(),
    )


async def post_lock_capture_callback(job: Job):
    if job.status_channel is not None:
        await publish_to_channel(
            channel=job.status_channel,
            message=SchedulingEvent(
                job_identifier=job.identify(),
                event_type=EventType.LOCK_CAPTURED,
                event_data=dict(
                    job__model_name=job.model_name,
                    job__instance_primary_key=job.instance_primary_key,
                    job__method_name=job.method_name,
                    **(job.status_extra_payload or {}),
                ),
            ),
        )


async def post_lock_release_callback(job: Job):
    if job.status_channel is not None:
        await publish_to_channel(
            channel=job.status_channel,
            message=SchedulingEvent(
                job_identifier=job.identify(),
                event_type=EventType.LOCK_RELEASED,
                event_data=dict(
                    job__model_name=job.model_name,
                    job__instance_primary_key=job.instance_primary_key,
                    job__method_name=job.method_name,
                    **(job.status_extra_payload or {}),
                ),
            ),
        )


async def consume_jobs(queue_name: str = DEFAULT_JOB_QUEUE_NAME):
    await consume_exclusively_with_backlog(
        fn=executor,
        queue_name=queue_name,
        object_identifier_fn=lambda job: job.identify_in_queue(),
        object_model=Job,
        post_lock_capture_callback=post_lock_capture_callback,
        post_lock_release_callback=post_lock_release_callback,
    )


async def consume_schedule(
    schedule_queue_name: str = DEFAULT_SCHEDULE_QUEUE_NAME,
    queue_name: str | None = None,
    tick_interval_seconds: int = 10,
):
    """
    Consume scheduled jobs and move them to their target queues when their time arrives.
    """
    while True:
        # Dequeue any jobs that are ready to run
        job, scheduled_time = await dequeue_scheduled(
            queue_name=schedule_queue_name, object_model=Job
        )

        if job is None:
            # No jobs ready, wait a bit before checking again
            await asyncio.sleep(tick_interval_seconds)
            continue

        job: Job

        logger.debug(
            f"Moving scheduled job {job.identify()} from schedule queue to "
            f"target queue."
        )

        # Enqueue the job to its target queue
        await job.enqueue(queue_name=queue_name)


async def consume_multiple(queue_names: List[str]):
    """Run consumers for multiple queues concurrently with per-consumer error recovery."""
    logger.info(f"Starting consumers for queues: {', '.join(queue_names)}")

    def parse_queue_name(_queue_name: str) -> Tuple[str, callable]:
        if ":" in _queue_name:
            _queue_name, consumer_fn_name = _queue_name.split(":")
            if consumer_fn_name == "consume_schedule":
                consumer_fn = consume_schedule
            elif consumer_fn_name == "consume_jobs":
                consumer_fn = consume_jobs
            else:
                raise ValueError(f"Unknown consumer: {consumer_fn_name}")
            return _queue_name, consumer_fn
        else:
            if _queue_name == DEFAULT_SCHEDULE_QUEUE_NAME:
                return _queue_name, consume_schedule
            else:
                return _queue_name, consume_jobs

    async def run_consumer_with_restart(queue_name: str, consumer_fn: callable) -> None:
        while True:
            try:
                logger.info(f"Starting consumer for queue: {queue_name}")
                await consumer_fn(queue_name)
            except Exception:
                logger.exception(f"Consumer for queue {queue_name} failed. Restarting in 10 seconds.")
                await asyncio.sleep(10)
                continue

    # Parse all queue names first
    parsed_queues = [parse_queue_name(queue_name) for queue_name in queue_names]

    if len(parsed_queues) == 1:
        queue_name, consumer = parsed_queues[0]
        await run_consumer_with_restart(queue_name, consumer)
    else:
        # Create wrapped consumers for each queue
        wrapped_consumers = [
            run_consumer_with_restart(queue_name, consumer)
            for queue_name, consumer in parsed_queues
        ]
        await asyncio.gather(*wrapped_consumers)


async def consume_all(multiplicity: int = 1):
    available_queues = [
        f"{DEFAULT_JOB_QUEUE_NAME}:consume_jobs",
        f"{LOW_PRIORITY_JOB_QUEUE_NAME}:consume_jobs",
        f"{DEFAULT_SCHEDULE_QUEUE_NAME}:consume_schedule",
    ]

    if multiplicity > 1:
        available_queues = available_queues * multiplicity

    await consume_multiple(available_queues)