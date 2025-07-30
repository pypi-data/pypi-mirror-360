from copy import copy

import networkx as nx
from dramatiq import Middleware

from pypeline.barrier import LockingParallelBarrier
from pypeline.constants import PARALLEL_PIPELINE_CALLBACK_BARRIER_TTL
from pypeline.utils.module_utils import get_callable
from pypeline.utils.pipeline_utils import get_execution_graph
from pypeline.utils.dramatiq_utils import register_lazy_actor


class PypelineMiddleware(Middleware):

    def __init__(self, redis_url):
        self.redis_url = redis_url

    def after_process_message(self, broker, message, *, result=None, exception=None):

        if exception is not None:
            return

        if "pipeline" not in message.options:
            return

        pipeline = message.options["pipeline"]
        max_retries = message.options.get("max_retries", None)
        pipeline_config = pipeline["config"]
        task_replacements = message.options["task_replacements"]
        execution_id = message.options["execution_id"]
        task_definitions = pipeline_config["taskDefinitions"]
        task_name = message.options["task_name"]
        task_key = f"{execution_id}-{task_name}"

        # Signal to other jobs that current task is finished
        locking_parallel_barrier = LockingParallelBarrier(
            self.redis_url,
            task_key=task_key,
            lock_key=f"{message.options['base_case_execution_id']}-lock",
        )
        try:
            locking_parallel_barrier.acquire_lock(timeout=10)
            _ = locking_parallel_barrier.decrement_task_count()
        finally:
            locking_parallel_barrier.release_lock()

        graph = get_execution_graph(pipeline_config)
        children_tasks = pipeline_config["dagAdjacency"].get(task_name, [])

        messages = []
        for child in children_tasks:
            child_ancestors = sorted(graph.predecessors(child))

            ancestor_tasks_complete = True

            for ancestor in child_ancestors:
                ancestor_task_key = f"{execution_id}-{ancestor}"

                locking_parallel_barrier = LockingParallelBarrier(
                    self.redis_url,
                    task_key=ancestor_task_key,
                    lock_key=f"{message.options['base_case_execution_id']}-lock",
                )
                try:
                    locking_parallel_barrier.acquire_lock(
                        timeout=PARALLEL_PIPELINE_CALLBACK_BARRIER_TTL
                    )

                    if locking_parallel_barrier.task_exists():
                        remaining_tasks = locking_parallel_barrier.get_task_count()
                    else:
                        remaining_tasks = None
                finally:
                    locking_parallel_barrier.release_lock()

                # If the lock didn't exist for the current tasks execution id then it would indicate
                # that this is the start of a new scenario.  Therefore we need to find the ancestor
                # that is executed in the base case execution id and make sure it has completed
                if remaining_tasks is None:
                    ancestor_task_key = (
                        f"{message.options['base_case_execution_id']}-{ancestor}"
                    )

                    locking_parallel_barrier = LockingParallelBarrier(
                        self.redis_url,
                        task_key=ancestor_task_key,
                        lock_key=f"{message.options['base_case_execution_id']}-lock",
                    )
                    try:
                        locking_parallel_barrier.acquire_lock(
                            timeout=PARALLEL_PIPELINE_CALLBACK_BARRIER_TTL
                        )

                        if locking_parallel_barrier.task_exists():
                            remaining_tasks = locking_parallel_barrier.get_task_count()
                        else:
                            raise Exception(
                                f"Parent task {ancestor} barrier lock not found"
                            )
                    finally:
                        locking_parallel_barrier.release_lock()
                if remaining_tasks is None or remaining_tasks >= 1:
                    ancestor_tasks_complete = False
                    break

            # If the child's ancestor tasks aren't complete move onto the next child to check
            if not ancestor_tasks_complete:
                break

            # Handle situation where base case kicks off new scenario
            if (
                message.options["base_case_execution_id"]
                == message.options["execution_id"]
            ):
                for scenario in message.options["scenarios"]:
                    child_predecessors = list(graph.predecessors(child))
                    if (
                        child in scenario["tasksToRunInScenario"]
                        and task_name in child_predecessors
                        and task_name not in scenario["tasksToRunInScenario"]
                    ):
                        task_key = f"{scenario['execution_id']}-{child}"
                        locking_parallel_barrier = LockingParallelBarrier(
                            self.redis_url,
                            task_key=task_key,
                            lock_key=f"{message.options['base_case_execution_id']}-lock",
                        )
                        locking_parallel_barrier.set_task_count(1)
                        handler = task_definitions[child]["handlers"][
                            task_replacements.get(child, 0)
                        ]
                        server_type = task_definitions[child].get("serverType", None)

                        lazy_actor = register_lazy_actor(
                            broker,
                            get_callable(handler),
                            pipeline_config["metadata"],
                            server_type,
                        )
                        scenario_message = lazy_actor.message()
                        scenario_message.options["pipeline"] = pipeline
                        if max_retries is not None:
                            scenario_message.options["max_retries"] = max_retries
                        scenario_message.options["task_replacements"] = (
                            task_replacements
                        )
                        scenario_message.options["execution_id"] = scenario[
                            "execution_id"
                        ]

                        scenario_message.options["task_name"] = child
                        scenario_message.options["base_case_execution_id"] = (
                            message.options["base_case_execution_id"]
                        )
                        scenario_message.options["scenarios"] = message.options[
                            "scenarios"
                        ]
                        if "settings" in message.kwargs:
                            scenario_message.kwargs["settings"] = copy(
                                message.kwargs["settings"]
                            )
                            scenario_message.kwargs["settings"]["execution_id"] = (
                                scenario["execution_id"]
                            )
                        messages.append(scenario_message)

            # Kick off child task for current scenario
            task_key = f"{execution_id}-{child}"
            locking_parallel_barrier = LockingParallelBarrier(
                self.redis_url,
                task_key=task_key,
                lock_key=f"{message.options['base_case_execution_id']}-lock",
            )
            locking_parallel_barrier.set_task_count(1)
            handler = task_definitions[child]["handlers"][
                task_replacements.get(child, 0)
            ]
            server_type = task_definitions[child].get("serverType", None)
            lazy_actor = register_lazy_actor(
                broker,
                get_callable(handler),
                pipeline_config["metadata"],
                server_type,
            )

            child_message = lazy_actor.message()
            child_message.options["pipeline"] = pipeline
            if max_retries is not None:
                child_message.options["max_retries"] = max_retries
            child_message.options["task_replacements"] = task_replacements
            child_message.options["execution_id"] = execution_id
            child_message.options["task_name"] = child
            child_message.options["base_case_execution_id"] = message.options[
                "base_case_execution_id"
            ]
            child_message.options["scenarios"] = message.options["scenarios"]
            if "settings" in message.kwargs:
                child_message.kwargs["settings"] = message.kwargs["settings"]
                child_message.kwargs["settings"]["execution_id"] = message.options[
                    "execution_id"
                ]

            messages.append(child_message)

        for new_message in messages:
            broker.enqueue(new_message)
