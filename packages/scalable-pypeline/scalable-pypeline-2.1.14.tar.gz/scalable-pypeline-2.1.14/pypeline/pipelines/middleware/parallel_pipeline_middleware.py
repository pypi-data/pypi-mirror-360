import copy
from dramatiq.middleware import Middleware

from pypeline.barrier import LockingParallelBarrier
from pypeline.constants import PARALLEL_PIPELINE_CALLBACK_BARRIER_TTL


class ParallelPipeline(Middleware):
    def __init__(self, redis_url):
        self.redis_url = redis_url

    def after_process_message(self, broker, message, *, result=None, exception=None):
        from dramatiq.message import Message

        if exception is None:
            group_completion_uuid = message.options.get("group_completion_uuid")
            if group_completion_uuid:
                locking_parallel_barrier = LockingParallelBarrier(
                    self.redis_url,
                    task_key=group_completion_uuid,
                    lock_key=f"{group_completion_uuid}-lock",
                )
                try:
                    locking_parallel_barrier.acquire_lock(
                        timeout=PARALLEL_PIPELINE_CALLBACK_BARRIER_TTL
                    )
                    remaining_tasks = locking_parallel_barrier.decrement_task_count()
                finally:
                    locking_parallel_barrier.release_lock()
                if remaining_tasks <= 0:
                    execution_graph = message.options.get("execution_graph")

                    for i in range(len(execution_graph)):
                        message_group = execution_graph[i]

                        # Check if the current group matches the group_completion_uuid
                        if (
                            message_group[0]["options"]["group_completion_uuid"]
                            == group_completion_uuid
                        ):
                            # Check if there is a next group
                            if i + 1 < len(execution_graph):
                                next_group = execution_graph[i + 1]

                                completion_uuid = next_group[0]["options"][
                                    "group_completion_uuid"
                                ]
                                locking_parallel_barrier = LockingParallelBarrier(
                                    self.redis_url,
                                    task_key=completion_uuid,
                                    lock_key=f"{completion_uuid}-lock",
                                )
                                locking_parallel_barrier.set_task_count(len(next_group))
                                execution_graph_copy = copy.deepcopy(execution_graph)

                                for next_message in next_group:
                                    next_message["options"][
                                        "execution_graph"
                                    ] = execution_graph_copy
                                    broker.enqueue(Message(**next_message))
