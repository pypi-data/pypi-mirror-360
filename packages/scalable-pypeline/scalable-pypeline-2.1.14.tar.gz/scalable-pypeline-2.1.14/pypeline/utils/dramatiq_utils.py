import os.path
import sys
import typing
from typing import Optional, Callable, Union, Awaitable
from functools import wraps
from typing import TYPE_CHECKING, TypeVar
from dramatiq import Broker, actor as register_actor

from pypeline.constants import (
    DEFAULT_TASK_MAX_RETRY,
    DEFAULT_TASK_MIN_BACKOFF,
    MS_IN_SECONDS,
    DEFAULT_TASK_MAX_BACKOFF,
    DEFAULT_TASK_TTL,
    DEFAULT_RESULT_TTL,
)

if TYPE_CHECKING:
    from typing_extensions import ParamSpec

    P = ParamSpec("P")
else:
    P = TypeVar("P")

R = TypeVar("R")


def guess_code_directory(broker):
    actor = next(iter(broker.actors.values()))
    modname, *_ = actor.fn.__module__.partition(".")
    mod = sys.modules[modname]
    return os.path.dirname(mod.__file__)


def list_managed_actors(broker, queues):
    queues = set(queues)
    all_actors = broker.actors.values()
    if not queues:
        return all_actors
    else:
        return [a for a in all_actors if a.queue_name in queues]


def register_lazy_actor(
    broker: Broker,
    fn: Optional[Callable[P, Union[Awaitable[R], R]]] = None,
    pipeline_meta: typing.Dict = {},
    server_type: Optional[str] = None,
    **kwargs,
) -> typing.Type["LazyActor"]:
    if server_type:
        kwargs["queue_name"] = server_type + "-" + pipeline_meta.get("queue", "default")
    else:
        kwargs["queue_name"] = pipeline_meta.get("queue", "default")
    kwargs["max_retries"] = pipeline_meta.get("maxRetry", DEFAULT_TASK_MAX_RETRY)
    # Convert from seconds to milliseconds
    kwargs["min_backoff"] = (
        pipeline_meta.get("retryBackoff", DEFAULT_TASK_MIN_BACKOFF) * MS_IN_SECONDS
    )
    kwargs["max_backoff"] = (
        pipeline_meta.get("retryBackoffMax", DEFAULT_TASK_MAX_BACKOFF) * MS_IN_SECONDS
    )
    kwargs["time_limit"] = pipeline_meta.get("maxTtl", DEFAULT_TASK_TTL) * MS_IN_SECONDS
    # Always store results for registered pipeline actors
    kwargs["store_results"] = pipeline_meta.get("store_results", True)
    if kwargs["store_results"]:
        kwargs["result_ttl"] = (
            pipeline_meta.get("result_ttl", DEFAULT_RESULT_TTL) * MS_IN_SECONDS
        )
    lazy_actor: LazyActor = LazyActor(fn, kwargs)
    lazy_actor.register(broker)
    return lazy_actor


def ensure_return_value(default_value=None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Call the original function
            result = func(*args, **kwargs)
            # Check if the function has returned a value
            if result is None:
                # Return the default value if the function returned None
                return default_value
            return result

        return wrapper

    return decorator


class LazyActor(object):
    # Intermediate object that register actor on broker an call.

    def __init__(self, fn, kw):
        self.fn = fn
        self.kw = kw
        self.actor = None

    def __call__(self, *a, **kw):
        return self.fn(*a, **kw)

    def __repr__(self):
        return "<%s %s.%s>" % (
            self.__class__.__name__,
            self.fn.__module__,
            self.fn.__name__,
        )

    def __getattr__(self, name):
        if not self.actor:
            raise AttributeError(name)
        return getattr(self.actor, name)

    def register(self, broker):
        self.actor = register_actor(
            actor_name=f"{self.fn.__module__}.{self.fn.__name__}-{self.kw['queue_name']}",
            broker=broker,
            **self.kw,
        )(ensure_return_value(default_value=True)(self.fn))

    # Next is regular actor API.
    def send(self, *a, **kw):
        return self.actor.send(*a, **kw)

    def message(self, *a, **kw):
        return self.actor.message(*a, **kw)

    def send_with_options(self, *a, **kw):
        return self.actor.send_with_options(*a, **kw)
