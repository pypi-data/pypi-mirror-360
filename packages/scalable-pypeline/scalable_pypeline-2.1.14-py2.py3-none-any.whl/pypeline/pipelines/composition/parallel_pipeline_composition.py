from __future__ import annotations

import copy
import json
import time
import typing
from uuid import uuid4

from dramatiq.broker import get_broker
from dramatiq.results import ResultMissing
from db_medley.redis_conf import RedisConnector
from redis.exceptions import RedisError

from pypeline.barrier import LockingParallelBarrier
from pypeline.constants import DEFAULT_RESULT_TTL
from pypeline.dramatiq import REDIS_URL

from dramatiq.message import Message


class parallel_pipeline:
    """Chain actors together, passing the result of one actor to the
    next one in line.

    Parameters:
      children(typing.List[typing.List[Message]]): A sequence of messages or
        pipelines.  Child pipelines are flattened into the resulting
        pipeline.
      broker(Broker): The broker to run the pipeline on.  Defaults to
        the current global broker.
    """

    messages: list[Message]

    def __init__(self, messages: typing.List[typing.List[Message]], broker=None):
        self.broker = broker or get_broker()
        self.messages = messages
        self.execution_id = str(uuid4())
        execution_graph = []

        for message_group in self.messages:
            sub_execution_group = []
            group_completion_uuid = str(uuid4())
            for m in message_group:
                m.kwargs["event"]["execution_id"] = self.execution_id
                m.options["group_completion_uuid"] = group_completion_uuid
                message_dict = copy.deepcopy(m.asdict())
                sub_execution_group.append(message_dict)
            # Last item in the group is the id of the group to be executed
            execution_graph.append(sub_execution_group)

        self.execution_graph = execution_graph

        for m in self.messages[0]:
            m.options["execution_graph"] = execution_graph

    def __len__(self):
        """Returns the length of the parallel_pipeline."""
        count = 0
        for message_group in self.messages:
            count = count + len(message_group)

        return count

    def __str__(self):  # pragma: no cover
        """Return a string representation of the parallel_pipeline.

        This representation shows the order of execution for each group of messages.
        """
        result = []

        for i, message_group in enumerate(self.messages):
            group_str = f"Group {i + 1}: [\n"
            for j, message in enumerate(message_group):
                message_str = f"  Message {j + 1}: {message.actor_name}\n"
                group_str += message_str
            group_str += "]\n"
            result.append(group_str)

        return "".join(result)

    @property
    def completed(self):
        return self.completed_count == len(self)

    @property
    def completed_count(self):
        count = 0

        for message_group in self.messages:
            for message in message_group:
                try:
                    message.get_result()
                    count = count + 1
                except ResultMissing:
                    pass
        return count

    def run(self, *, delay=None):
        """Run this parallel_pipeline.

        Parameters:
          delay(int): The minimum amount of time, in milliseconds, the
            parallel_pipeline should be delayed by. If both parallel_pipeline's delay and
            first message's delay are provided, the bigger value will be
            used.

        Returns:
          parallel_pipeline: Itself.
        """
        starting_group = self.messages[0]

        completion_uuid = starting_group[0].options["group_completion_uuid"]
        locking_parallel_barrier = LockingParallelBarrier(
            REDIS_URL, task_key=completion_uuid, lock_key=f"{completion_uuid}-lock"
        )
        locking_parallel_barrier.set_task_count(len(starting_group))

        for m in starting_group:
            self.broker.enqueue(m, delay=delay)

        return self

    def get_result(self, *, block=False, timeout=None):
        """Get the result of this pipeline.

        Pipeline results are represented by the result of the last
        message in the chain.

        Parameters:
          block(bool): Whether or not to block until a result is set.
          timeout(int): The maximum amount of time, in ms, to wait for
            a result when block is True.  Defaults to 10 seconds.

        Raises:
          ResultMissing: When block is False and the result isn't set.
          ResultTimeout: When waiting for a result times out.

        Returns:
          object: The result.
        """
        last_message = self.messages[-1][-1]

        backend = self.broker.get_results_backend()
        return last_message.get_result(backend=backend, block=block, timeout=timeout)

    def get_results(self, *, block=False, timeout=None):
        """Get the results of each job in the pipeline.

        Parameters:
          block(bool): Whether or not to block until a result is set.
          timeout(int): The maximum amount of time, in ms, to wait for
            a result when block is True.  Defaults to 10 seconds.

        Raises:
          ResultMissing: When block is False and the result isn't set.
          ResultTimeout: When waiting for a result times out.

        Returns:
          A result generator.
        """
        deadline = None
        if timeout:
            deadline = time.monotonic() + timeout / 1000

        for message_group in self.messages:
            for message in message_group:
                if deadline:
                    timeout = max(0, int((deadline - time.monotonic()) * 1000))

                backend = self.broker.get_results_backend()
                yield {
                    message.actor_name: message.get_result(
                        backend=backend, block=block, timeout=timeout
                    )
                }

    def to_json(self) -> str:
        """Convert the execution graph to a JSON string representation.

        This method serializes the execution graph of the pipeline into a JSON string.
        This serialized form can be used to save the pipeline state or share it across different systems,
        enabling the retrieval of a pipeline "run" for obtaining its results at a later time.

        :return: A JSON string representing the execution graph.
        :rtype: str
        """
        return json.dumps(self.execution_graph)

    @classmethod
    def from_json(cls, json_data: str) -> parallel_pipeline:
        """Create a ParallelPipeline object from a JSON string representation of the execution graph.

        This class method deserializes a JSON string into a list of messages, each representing
        a task or operation in the pipeline. The method reconstructs the execution graph using
        the `dramatiq.message.Message` objects and returns an instance of the `parallel_pipeline` class.

        :param json_data: A JSON string containing the serialized execution graph.
        :type json_data: str
        :return: An instance of `parallel_pipeline` reconstructed from the JSON data.
        :rtype: parallel_pipeline
        """
        execution_graph = json.loads(json_data)

        messages = []

        for message_group in execution_graph:
            temp_group = []
            for message in message_group:
                temp_group.append(Message(**message))
            messages.append(temp_group)

        return cls(messages)


class PipelineResult:
    """
    A class to manage and retrieve the results of a parallel pipeline execution.

    The `PipelineResult` class provides methods for creating a result entry in a Redis database,
    loading pipeline data from Redis, and retrieving the status and results of the pipeline execution.

    Attributes:
        pipeline (parallel_pipeline): The pipeline object representing the execution graph.
        execution_id (str): A unique identifier for the execution of the pipeline.
        redis_key (str): The key used to store and retrieve pipeline data from Redis.
        redis_conn: A Redis connection object used to interact with the Redis database.
        result_ttl (int): Time-to-live (TTL) for the result entry in Redis, in seconds.
    """

    def __init__(self, execution_id: str, result_ttl: int = DEFAULT_RESULT_TTL):
        """
        Initialize a PipelineResult object with an execution ID and optional result TTL.

        :param execution_id: A unique identifier for the pipeline execution.
        :type execution_id: str
        :param result_ttl: The time-to-live (TTL) for the result entry in Redis. Defaults to DEFAULT_RESULT_TTL.
        :type result_ttl: int
        """
        self.pipeline: parallel_pipeline = None
        self.execution_id = execution_id
        self.redis_key = f"{execution_id}-results-key"
        self.redis_conn = RedisConnector().get_connection()
        self.result_ttl = result_ttl

    def create_result_entry(self, pipeline_json_str: str):
        """
        Store the serialized pipeline data in Redis with a specified TTL.

        This method saves the JSON string representation of the pipeline in the Redis database
        using the execution ID as the key. The entry is stored with a time-to-live (TTL) defined by `result_ttl`.

        :param pipeline_json_str: A JSON string representing the pipeline execution graph.
        :type pipeline_json_str: str
        :raises ValueError: If the provided pipeline data is None or an empty string.
        :raises RedisError: If there is an issue connecting to Redis or setting the value.
        """
        if not pipeline_json_str:
            raise ValueError("No pipeline data passed to create result store")

        try:
            self.redis_conn.setex(self.redis_key, self.result_ttl, pipeline_json_str)
        except RedisError as e:
            raise RuntimeError(f"Failed to store pipeline data in Redis: {e}")

    def load(self):
        """
        Load the pipeline data from Redis and reconstruct the pipeline object.

        This method retrieves the JSON string stored in Redis and deserializes it
        into a `parallel_pipeline` object, enabling access to the pipeline's execution details.

        :raises RedisError: If there is an issue connecting to Redis or retrieving the data.
        """
        try:
            pipeline_data = self.redis_conn.get(self.redis_key)
            if pipeline_data:
                self.pipeline = parallel_pipeline.from_json(pipeline_data)
            else:
                self.pipeline = None
        except RedisError as e:
            raise RuntimeError(f"Failed to load pipeline data from Redis: {e}")

    @property
    def status(self) -> str:
        """
        Get the current status of the pipeline execution.

        This property checks the completion status of the pipeline and returns its current state.

        :return: The status of the pipeline execution, which can be "complete", "pending", or "unavailable".
        :rtype: str
        """
        if not self.pipeline:
            return "unavailable"
        return "complete" if self.pipeline.completed else "pending"

    def get_results(self) -> dict:
        """
        Retrieve all results from the pipeline execution with unique actor identifiers.

        This method aggregates results from the pipeline and ensures that each actor's result
        has a unique identifier by appending a numeric suffix to duplicate actor names.

        :return: A dictionary containing all results from the pipeline execution, keyed by unique actor identifiers.
        :rtype: dict
        """
        if not self.pipeline:
            return {}

        results = {}
        for result in self.pipeline.get_results():
            for actor, res in result.items():
                unique_actor = self._get_unique_actor_name(actor, results)
                results[unique_actor] = res
        return results

    def get_result(self):
        """
        Retrieve a single result from the pipeline execution.

        This method returns the result of a single execution step from the pipeline, if available.

        :return: The result of a single execution step from the pipeline, or None if no pipeline is loaded.
        """
        if self.pipeline:
            return self.pipeline.get_result()

    def _get_unique_actor_name(self, actor: str, results: dict) -> str:
        """
        Generate a unique actor name by appending a numeric suffix if necessary.

        :param actor: The base name of the actor.
        :type actor: str
        :param results: The current dictionary of results to check for uniqueness.
        :type results: dict
        :return: A unique actor name.
        :rtype: str
        """
        if actor not in results:
            return actor

        suffix = 0
        new_actor = f"{actor}-{suffix}"
        while new_actor in results:
            suffix += 1
            new_actor = f"{actor}-{suffix}"
        return new_actor
