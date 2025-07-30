import logging
from typing import Union

from pypeline.constants import WORKER_NAME
from pypeline.pypeline_yaml import load_pypeline_config

logger = logging.getLogger(__name__)


def retrieve_latest_pipeline_config(
    pipeline_id: Union[str, None] = None
) -> Union[dict, list]:
    """Retrieve the 'latest' pipeline configuration for a given pipeline."""
    pypeline_config = load_pypeline_config()
    if "pipelines" in pypeline_config:
        pipelines = []
        found_pipeline = None
        for p_id, config in pypeline_config["pipelines"].items():
            if pipeline_id == p_id:
                found_pipeline = config
                break
            pipelines.append(config)

        if pipeline_id:
            if found_pipeline:
                return found_pipeline
            raise ValueError(f"Invalid pipeline {pipeline_id}")

        return pipelines
    return None


def retrieve_latest_schedule_config():
    """Retrieve the 'latest' scheduled tasks configuration."""
    pypeline_config = load_pypeline_config()
    if "scheduledTasks" in pypeline_config:
        tasks = []
        for task_id, config in pypeline_config["scheduledTasks"].items():
            tasks.append(config)
        return tasks
    return None


def get_service_config_for_worker(
    pypeline_config: dict, worker_name: str = None
) -> Union[dict, None]:
    """For the current WORKER_NAME (which must be present in the environment
    of this worker instance for a valid deployment), return the worker's
    serviceConfig object.
    """
    if pypeline_config is None:
        raise ValueError("Pypeline config was not provided")
    if worker_name is None:
        worker_name = WORKER_NAME
    if worker_name is None:
        return None

    service_config = pypeline_config.get("serviceConfig", [])
    for service in service_config:
        if service["name"] == worker_name:
            return service

    raise ValueError(
        "Could not find a service config for worker "
        f"`{worker_name}`. Make sure you have added the service in"
        f" your pypeline.yaml with `name: {worker_name}` and "
        "`type: celery-worker`."
    )
