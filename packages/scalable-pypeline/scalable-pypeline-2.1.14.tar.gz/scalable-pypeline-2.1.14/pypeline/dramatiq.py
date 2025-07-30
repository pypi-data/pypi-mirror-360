import copy
import typing
import pika
import logging
import os

import click
from urllib.parse import urlparse

from dramatiq.brokers.redis import RedisBroker

from pypeline.extensions import pypeline_config
from warnings import warn
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from dramatiq import Broker, Middleware, set_broker, get_broker
from dramatiq.brokers.rabbitmq import RabbitmqBroker
from dramatiq.cli import (
    CPUS,
    HAS_WATCHDOG,
    main as dramatiq_worker,
    make_argument_parser as dramatiq_argument_parser,
    import_object,
)
from dramatiq.middleware import default_middleware, CurrentMessage
from dramatiq.results import Results
from dramatiq.results.backends.redis import RedisBackend
from flask import current_app, Flask
from flask.cli import with_appcontext

from pypeline.constants import (
    REDIS_URL,
    RABBIT_URL,
    DEFAULT_BROKER_CALLABLE,
    DEFAULT_BROKER_CONNECTION_HEARTBEAT,
    DEFAULT_BROKER_BLOCKED_CONNECTION_TIMEOUT,
    DEFAULT_BROKER_CONNECTION_ATTEMPTS,
    MESSAGE_BROKER,
    DEFAULT_BROKER_HEARTBEAT_TIMEOUT,
)
from pypeline.pipelines.middleware.get_active_worker_id_middleware import (
    GetActiveWorkerIdMiddleware,
)
from pypeline.pipelines.middleware.parallel_pipeline_middleware import ParallelPipeline
from pypeline.pipelines.middleware.pypeline_middleware import PypelineMiddleware
from pypeline.utils.config_utils import (
    retrieve_latest_schedule_config,
    get_service_config_for_worker,
)
from pypeline.utils.dramatiq_utils import (
    guess_code_directory,
    list_managed_actors,
    register_lazy_actor,
    LazyActor,
)
from pypeline.utils.graceful_shutdown_util import enable_graceful_shutdown
from pypeline.utils.module_utils import get_callable


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def configure_default_broker(broker: Broker = None):
    redis_backend = RedisBackend(url=REDIS_URL)

    if MESSAGE_BROKER == "RABBITMQ":
        parsed_url = urlparse(RABBIT_URL)
        credentials = pika.PlainCredentials(parsed_url.username, parsed_url.password)
        broker = (
            broker
            if broker is not None
            else RabbitmqBroker(
                host=parsed_url.hostname,
                port=parsed_url.port,
                credentials=credentials,
                heartbeat=DEFAULT_BROKER_CONNECTION_HEARTBEAT,
                connection_attempts=DEFAULT_BROKER_CONNECTION_ATTEMPTS,
                blocked_connection_timeout=DEFAULT_BROKER_BLOCKED_CONNECTION_TIMEOUT,
            )
        )

    elif MESSAGE_BROKER == "REDIS":
        broker = (
            broker
            if broker is not None
            else RedisBroker(
                url=REDIS_URL, heartbeat_timeout=DEFAULT_BROKER_HEARTBEAT_TIMEOUT
            )
        )

    broker.add_middleware(Results(backend=redis_backend))
    broker.add_middleware(ParallelPipeline(redis_url=REDIS_URL))
    broker.add_middleware(PypelineMiddleware(redis_url=REDIS_URL))
    broker.add_middleware(CurrentMessage())
    broker.add_middleware(GetActiveWorkerIdMiddleware())
    if (
        os.getenv("RESTRICT_WORKER_SHUTDOWN_WHILE_JOBS_RUNNING", "false").lower()
        == "true"
    ):
        enable_graceful_shutdown(broker=broker, redis_url=REDIS_URL)

    register_actors_for_workers(broker)
    set_broker(broker)


def register_actors_for_workers(broker: Broker):
    service = get_service_config_for_worker(pypeline_config)
    scheduled_jobs_config = retrieve_latest_schedule_config()

    if not service:
        return

    worker_registered_tasks = [
        task_handler["handler"] for task_handler in service.get("registeredTasks")
    ]

    # Loop over the pipelines to get metadata and other information about the task for registration
    for pipeline_key, pipeline in pypeline_config["pipelines"].items():
        for task, task_handler_meta in pipeline["config"]["taskDefinitions"].items():
            if pipeline["schemaVersion"] == 1:
                # Check if any task in this pipeline is registered
                task_handlers = [task_handler_meta["handler"]]
            elif pipeline["schemaVersion"] == 2:
                task_handlers = [t for t in task_handler_meta["handlers"]]

            for task_handler in task_handlers:
                if task_handler in worker_registered_tasks:
                    server_type = task_handler_meta.get("serverType", None)

                    try:
                        pipeline_metadata = copy.deepcopy(
                            pipeline["config"]["metadata"]
                        )
                        tmp_handler = get_callable(task_handler)
                        if pipeline_metadata.get("maxRetry", 0) >= 0:
                            pipeline_metadata["store_results"] = True
                            _ = register_lazy_actor(
                                broker, tmp_handler, pipeline_metadata, server_type
                            )
                    except Exception as e:
                        logger.exception(
                            f"Unable to add a task {task_handler} to dramatiq: {e}"
                        )
    # Loop over the scheduled jobs and create metadata and other information about the task for registration
    for job in scheduled_jobs_config:
        config = job["config"]
        if config["task"] in worker_registered_tasks:
            pipeline_meta = {"queue": config.get("queue", "default")}
            try:
                tmp_handler = get_callable(config["task"])
                if pipeline_meta and pipeline_meta.get("maxRetry", 0) >= 0:
                    pipeline_meta["store_results"] = True
                    _ = register_lazy_actor(broker, tmp_handler, pipeline_meta, None)
            except Exception as e:
                logger.exception(f"Unable to add a task to dramatiq: {e}")


class Dramatiq:
    """Flask extension bridging Dramatiq broker and Flask app.

    Dramatiq API is eager. Broker initialisation precede actor declaration.
    This breaks application factory pattern and other way to initialize
    configuration after import.

    This class enables lazy initialization of Dramatiq. Actual Dramatiq broker
    is instanciated only once Flask app is created.

    .. automethod:: actor
    .. automethod:: init_app
    """

    def __init__(
        self,
        app: Flask = None,
        name: str = "dramatiq",
        config_prefix: str = None,
        middleware: typing.List[Middleware] = None,
    ):
        """
        :app: Flask application if created. See :meth:`init_app`.

        :param broker_configuration_callable_module: In order to work in fork and spawn mode
            we need to configure our broker using a callable function.  Default is specified as
            "pypeline.flask_dramatiq:configure_default_broker".  This allows the user to
            override if necessary.

        :param name: Unique identifier for multi-broker app.

        :param config_prefix: Flask configuration option prefix for this
            broker. By default, it is derived from ``name`` parameter,
            capitalized.

        :param middleware: List of Dramatiq middleware instances to override
             Dramatiq defaults.

        Flask-Dramatiq always prepend a custom middleware to the middleware
        stack that setup Flask context. This way, every middleware can use
        Flask app context.

        """
        self.actors = []
        self.app = None
        self.config_prefix = config_prefix or name.upper() + "_BROKER"
        self.name = name
        self.broker = None
        if middleware is None:
            middleware = [m() for m in default_middleware]
        self.middleware = middleware
        if app:
            self.init_app(app)

    def __repr__(self) -> str:
        return "<%s %s>" % (self.__class__.__name__, self.name)

    def init_app(self, app: Flask):
        """Initialize extension for one Flask application

        This method triggers Dramatiq broker instantiation and effective actor
        registration.

        """
        if self.app is not None:
            warn(
                "%s is used by more than one flask application. "
                "Actor's context may be set incorrectly." % (self,),
                stacklevel=2,
            )
        self.app = app
        app.extensions["dramatiq-" + self.name] = self

        module_name, broker_or_callable = import_object(DEFAULT_BROKER_CALLABLE)

        # Callable function is expected to setBroker()
        if callable(broker_or_callable):
            logger.info(f"Configuring broker via {DEFAULT_BROKER_CALLABLE}")
            broker_or_callable()
        else:
            raise TypeError("DEFAULT_BROKER_CALLABLE must point to a callable function")
        self.broker = get_broker()
        for actor in self.actors:
            actor.register(broker=self.broker)

    def actor(self, fn=None, **kw):
        """Register a callable as Dramatiq actor.

        This decorator lazily register a callable as a Dramatiq actor. The
        actor can't be called before :meth:`init_app` is called.

        :param kw: Keywords argument passed to :func:`dramatiq.actor`.

        """
        # Substitute dramatiq.actor decorator to return a lazy wrapper. This
        # allows to register actors in extension before the broker is
        # effectively configured by init_app.

        def decorator(fn):
            lazy_actor = LazyActor(self, fn, kw)
            self.actors.append(lazy_actor)
            if self.app:
                lazy_actor.register(self.broker)
            return lazy_actor

        if fn:
            return decorator(fn)
        return decorator


@click.command("cron-scheduler")
def cron_scheduler():  # pragma: no cover
    # Configure our broker that we will schedule registered tasks for
    scheduler = BlockingScheduler()
    module_name, broker_or_callable = import_object(DEFAULT_BROKER_CALLABLE)

    # Callable function is expected to setBroker()
    if callable(broker_or_callable):
        logger.info(f"Configuring broker via {DEFAULT_BROKER_CALLABLE}")
        broker_or_callable()
    else:
        raise TypeError("DEFAULT_BROKER_CALLABLE must point to a callable function")

    broker = get_broker()
    jobs = retrieve_latest_schedule_config()

    for job in jobs:
        if job["enabled"]:
            config = job["config"]
            worker_path = config["task"]
            tmp_handler = get_callable(worker_path)
            pipeline_meta = {"queue": config.get("queue", "default")}
            actor = register_lazy_actor(broker, tmp_handler, pipeline_meta)
            schedule = config["schedule"]
            scheduler.add_job(
                actor.send,
                CronTrigger.from_crontab(
                    f"{schedule['minute']} {schedule['hour']} {schedule['dayOfMonth']} {schedule['monthOfYear']} {schedule['dayOfWeek']}"
                ),
            )

    try:
        scheduler.start()
    except KeyboardInterrupt:
        scheduler.shutdown()


@click.command("pypeline-worker")
@click.argument("broker_name", default="dramatiq")
@click.option(
    "-v", "--verbose", default=0, count=True, help="turn on verbose log output"
)
@click.option(
    "-p",
    "--processes",
    default=CPUS,
    metavar="PROCESSES",
    show_default=True,
    help="the number of worker processes to run",
)
@click.option(
    "-t",
    "--threads",
    default=8,
    metavar="THREADS",
    show_default=True,
    help="the number of worker treads per processes",
)
@click.option(
    "-Q",
    "--queues",
    type=str,
    default=None,
    metavar="QUEUES",
    show_default=True,
    help="listen to a subset of queues, comma separated",
)
@click.option(
    "--use-spawn",
    type=bool,
    default=False,
    metavar="USE_SPAWN",
    show_default=True,
    help="start processes by spawning (default: fork on unix, spawn on windows)",
)
@with_appcontext
def pypeline_worker(
    verbose, processes, threads, queues, broker_name, use_spawn
):  # pragma: no cover
    """Run dramatiq workers.

    Setup Dramatiq with broker and task modules from Flask app.

    \b
    examples:
      # Run dramatiq with 1 thread per process.
      $ flask worker --threads 1

    \b
      # Listen only to the "foo" and "bar" queues.
      $ flask worker -Q foo,bar

    \b
      # Consuming from a specific broker
      $ flask worker mybroker
    """
    # Plugin for flask.commands entrypoint.
    #
    # Wraps dramatiq worker CLI in a Flask command. This is private API of
    # dramatiq.

    def format_actor(actor):
        return "%s@%s" % (actor.actor_name, actor.queue_name)

    parser = dramatiq_argument_parser()

    # Set worker broker globally.
    needle = "dramatiq-" + broker_name
    broker = current_app.extensions[needle].broker
    set_broker(broker)

    command = [
        "--processes",
        str(processes),
        "--threads",
        str(threads),
        # Fall back to flask_dramatiq global broker
        DEFAULT_BROKER_CALLABLE,
    ]

    if use_spawn:
        command += ["--use-spawn"]

    if current_app.config["DEBUG"]:
        verbose = max(1, verbose)
        if HAS_WATCHDOG:
            command += ["--watch", guess_code_directory(broker)]

    queues = queues.split(",") if queues else []
    if queues:
        command += ["--queues"] + queues
    command += verbose * ["-v"]
    args = parser.parse_args(command)
    logger.info("Able to execute the following actors:")
    for actor in list_managed_actors(broker, queues):
        logger.info("    %s.", format_actor(actor))

    dramatiq_worker(args)
