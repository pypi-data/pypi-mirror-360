import typing
from dramatiq import get_broker, Message
from pypeline.pipelines.composition.parallel_pipeline_composition import (
    parallel_pipeline,
)
from pypeline.dramatiq import LazyActor
from pypeline.utils.dramatiq_utils import register_lazy_actor
from pypeline.pipeline_settings_schema import (
    MissingSettingsException,
    create_pipeline_settings_schema,
    PipelineScenarioSchema,
)
from pypeline.pipelines.composition.pypeline_composition import Pypeline
from pypeline.utils.config_utils import retrieve_latest_pipeline_config
from pypeline.utils.module_utils import get_callable
from pypeline.utils.pipeline_utils import (
    get_execution_graph,
    topological_sort_with_parallelism,
)


def dag_generator(
    pipeline_id: str, scenarios: typing.List[typing.Dict] = [], *args, **kwargs
) -> typing.Union[parallel_pipeline, Pypeline]:
    """Generates a pipeline dag from a pre-defined pipeline yaml

    :param pipeline_id: Id of the pipeline to generate
    :param task_replacements: A dictionary of task names and handler index to run. E.g. {"a": 1} would run the handler
        in the second index position.
    :param scenarios:
    :param args:
    :param kwargs:
    :return: Returns a parallel_pipeline object which can be run
    """
    pipeline = retrieve_latest_pipeline_config(pipeline_id=pipeline_id)

    pipeline_config = pipeline["config"]
    broker = get_broker()
    broker.actors.clear()

    if pipeline["schemaVersion"] == 2:
        supplied_pipeline_settings_schema = create_pipeline_settings_schema(
            pipeline_config["settings"]
        )

        # Validate scenarios settings to make sure they look okay
        validated_scenarios = PipelineScenarioSchema(many=True).load(scenarios)

        for scenario in validated_scenarios:
            supplied_pipeline_settings_schema.load(scenario["settings"])

        p = Pypeline(pipeline, scenarios=scenarios, broker=broker)
        return p

    graph = get_execution_graph(pipeline_config)
    optimal_execution_graph = topological_sort_with_parallelism(graph.copy())
    registered_actors: typing.Dict[str, LazyActor] = {}

    messages: typing.List[typing.List[Message]] = []

    task_definitions = pipeline_config["taskDefinitions"]
    for task_group in optimal_execution_graph:
        message_group = []
        for task in task_group:
            module_path = task_definitions[task]["handler"]
            server_type = task_definitions[task].get("serverType", None)
            tmp_handler = get_callable(module_path)
            lazy_actor = register_lazy_actor(
                broker, tmp_handler, pipeline_config["metadata"], server_type
            )
            registered_actors[task] = lazy_actor
            if args and not kwargs:
                msg = registered_actors[task].message(*args)
            elif kwargs and not args:
                msg = registered_actors[task].message(**kwargs)
            elif args and kwargs:
                msg = registered_actors[task].message(*args, **kwargs)
            else:
                msg = registered_actors[task].message()
            msg.options["task_ttl"] = pipeline_config["metadata"]["maxTtl"]
            message_group.append(msg)

        messages.append(message_group)
    p = parallel_pipeline(messages)

    return p
