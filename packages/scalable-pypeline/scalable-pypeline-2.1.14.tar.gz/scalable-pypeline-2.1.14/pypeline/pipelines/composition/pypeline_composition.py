import json
import typing
from copy import copy
from uuid import uuid4

import networkx as nx
from dramatiq import get_broker

from pypeline.barrier import LockingParallelBarrier
from pypeline.constants import REDIS_URL, PARALLEL_PIPELINE_CALLBACK_BARRIER_TTL
from pypeline.utils.dramatiq_utils import register_lazy_actor
from pypeline.utils.module_utils import get_callable
from pypeline.utils.pipeline_utils import get_execution_graph


class Pypeline:
    def __init__(
        self,
        pipeline: dict,
        scenarios: dict = {},
        broker=None,
    ):
        # Construct initial properties
        self.pipeline = pipeline
        self.broker = broker or get_broker()
        self._starting_messages = []
        self.scenarios = scenarios

        # Get pipeline dag graph and find first task
        pipeline_config = pipeline["config"]
        self.graph = get_execution_graph(pipeline_config)
        self.number_of_tasks = len(self.graph.nodes)
        task_definitions = pipeline_config["taskDefinitions"]
        first_task = list(pipeline_config["dagAdjacency"].keys())[0]

        base_case_execution_id = None

        # Process the scenarios one by one
        for scenario in self.scenarios:
            # The first scenario is the base case and always runs
            if self.scenarios.index(scenario) == 0:
                base_case_execution_id = scenario.get("execution_id", None) or str(
                    uuid4()
                )
                scenario["execution_id"] = base_case_execution_id
                scenario["base_case_execution_id"] = base_case_execution_id
                scenario["tasksToRunInScenario"] = list(self.graph.nodes)
                continue
            tasks_in_reruns = scenario["taskReruns"]

            # Find any tasks that have replacements for this scenario
            tasks_in_replacements = list(scenario["taskReplacements"].keys())

            distinct_scenario_tasks = list(set(tasks_in_reruns + tasks_in_replacements))
            tasks_to_be_rerun_in_scenario = distinct_scenario_tasks

            tasks_to_be_rerun_in_scenario = list(
                set(
                    task
                    for task in distinct_scenario_tasks
                    for task in nx.descendants(self.graph, task)
                )
                | set(tasks_to_be_rerun_in_scenario)
            )

            self.number_of_tasks = self.number_of_tasks + len(
                tasks_to_be_rerun_in_scenario
            )
            scenario["tasksToRunInScenario"] = tasks_to_be_rerun_in_scenario
            scenario["base_case_execution_id"] = base_case_execution_id
            scenario["execution_id"] = scenario.get("execution_id", None) or str(
                uuid4()
            )

            # Check if any of the scenarios need to be kicked off now
            if first_task in tasks_to_be_rerun_in_scenario:
                handler = task_definitions[first_task]["handlers"][
                    scenario["taskReplacements"].get(first_task, 0)
                ]
                server_type = task_definitions[first_task].get("serverType", None)
                lazy_actor = register_lazy_actor(
                    self.broker,
                    get_callable(handler),
                    pipeline_config["metadata"],
                    server_type,
                )
                message = lazy_actor.message()
                message.options["pipeline"] = pipeline
                if pipeline_config["metadata"].get("maxRetry", None) is not None:
                    message.options["max_retries"] = pipeline_config["metadata"][
                        "maxRetry"
                    ]
                message.options["task_replacements"] = copy(
                    scenario["taskReplacements"]
                )
                message.options["execution_id"] = scenario["execution_id"]
                message.options["task_name"] = first_task
                message.options["base_case_execution_id"] = base_case_execution_id
                if scenario["settings"]:
                    message.kwargs["settings"] = copy(scenario["settings"])
                    message.kwargs["settings"]["execution_id"] = scenario[
                        "execution_id"
                    ]
                    message.kwargs["settings"][
                        "base_case_execution_id"
                    ] = base_case_execution_id
                self._starting_messages.append(message)

        for m in self._starting_messages:
            m.options["scenarios"] = self.scenarios

        # Run the first task of the first scenario no matter what
        first_scenario_task_replacements = scenarios[0]["taskReplacements"]
        first_scenario_settings = scenarios[0].get("settings", None)

        handler = task_definitions[first_task]["handlers"][
            first_scenario_task_replacements.get(first_task, 0)
        ]
        server_type = task_definitions[first_task].get("serverType", None)
        lazy_actor = register_lazy_actor(
            self.broker,
            get_callable(handler),
            pipeline_config["metadata"],
            server_type,
        )
        message = lazy_actor.message()
        message.options["pipeline"] = pipeline
        if pipeline_config["metadata"].get("maxRetry", None) is not None:
            message.options["max_retries"] = pipeline_config["metadata"]["maxRetry"]
        message.options["task_replacements"] = first_scenario_task_replacements
        message.options["execution_id"] = base_case_execution_id
        message.options["task_name"] = first_task
        message.options["scenarios"] = self.scenarios
        message.options["base_case_execution_id"] = base_case_execution_id

        if first_scenario_settings:
            message.kwargs["settings"] = copy(first_scenario_settings)
            message.kwargs["settings"]["execution_id"] = base_case_execution_id
            message.kwargs["settings"][
                "base_case_execution_id"
            ] = base_case_execution_id

        self._starting_messages.append(message)

    def run(self, *, delay=None):
        for message in self._starting_messages:
            task_key = (
                f"{message.options['execution_id']}-{message.options['task_name']}"
            )
            locking_parallel_barrier = LockingParallelBarrier(
                REDIS_URL,
                task_key=task_key,
                lock_key=f"{message.options['base_case_execution_id']}-lock",
            )
            locking_parallel_barrier.set_task_count(1)
            self.broker.enqueue(message, delay=delay)

        return self

    def __len__(self):
        return self.number_of_tasks

    def completed(self):
        locks = []

        for scenario in self.scenarios:
            locks.append(
                {
                    "scenario_task_keys": [
                        f"{scenario['execution_id']}-{task}"
                        for task in scenario["tasksToRunInScenario"]
                    ],
                    "redis_lock_key": f"{scenario['base_case_execution_id']}-lock",
                }
            )

        for lock in locks:
            for task_key in lock["scenario_task_keys"]:
                locking_parallel_barrier = LockingParallelBarrier(
                    REDIS_URL, task_key=task_key, lock_key=lock["redis_lock_key"]
                )
                try:
                    locking_parallel_barrier.acquire_lock(
                        timeout=PARALLEL_PIPELINE_CALLBACK_BARRIER_TTL
                    )
                    task_complete = True
                    if locking_parallel_barrier.task_exists():
                        remaining_tasks = locking_parallel_barrier.get_task_count()
                        if remaining_tasks >= 1:
                            task_complete = False
                    else:
                        task_complete = False
                finally:
                    locking_parallel_barrier.release_lock()
                if not task_complete:
                    return task_complete

        return True

    def to_json(self) -> str:
        return json.dumps(
            {
                "pipeline": self.pipeline,
                "scenarios": self.scenarios,
            }
        )

    @classmethod
    def from_json(cls, json_data: str) -> typing.Type["Pypeline"]:
        data = json.loads(json_data)

        return cls(
            data["pipeline"],
            scenarios=data["scenarios"],
        )
