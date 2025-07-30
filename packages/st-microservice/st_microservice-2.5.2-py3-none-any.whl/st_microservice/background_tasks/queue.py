import asyncio

from graphql import GraphQLError
from redis import from_url
from redis.asyncio import from_url as afrom_url
from rq import Queue
from rq.job import Job, JobStatus
from rq.types import FunctionReferenceType

from ..general_utils import get_required_env


BROKER_URI = get_required_env("BROKER_URI")
queue = Queue(connection=from_url(BROKER_URI))
aredis = afrom_url(BROKER_URI, decode_responses=True)


def enqueue_with_messaging(f: FunctionReferenceType, *args, **kwargs) -> Job:
    return queue.enqueue(f, *args, meta={"broker_messaging": True}, **kwargs)


async def wait_and_receive_messages(job: Job):
    """Waits for task execution to finish while yielding messages. Propagates exceptions from Task"""
    sub = aredis.pubsub(ignore_subscribe_messages=True)
    await sub.subscribe(f"task-messages-{job.id}")
    while job.get_status() not in [
        JobStatus.FINISHED,
        JobStatus.CANCELED,
        JobStatus.FAILED,
        JobStatus.STOPPED,
    ]:
        await asyncio.sleep(0.5)
        while (message_raw := await sub.get_message()) is not None:
            yield message_raw["data"]
    # Collect remaining messages
    while (message_raw := await sub.get_message()) is not None:
        yield message_raw["data"]
    # Propagate exceptions
    result = job.latest_result()
    if result.type == result.Type.FAILED:
        raise GraphQLError(result.exc_string.splitlines()[-1])
