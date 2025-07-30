""" Schemas for Pipelines
"""

import yaml
from marshmallow import Schema, fields, EXCLUDE, validates_schema
from marshmallow.exceptions import ValidationError
from marshmallow.validate import OneOf

from pypeline.pipeline_settings_schema import PipelineSettingsSchema


class ExcludeUnknownSchema(Schema):
    """Remove unknown keys from loaded dictionary"""

    class Meta:
        """Exclude unknown properties."""

        unknown = EXCLUDE


class MetadataSchema(Schema):
    """Schema for a pipeline's metadata object."""

    queue = fields.String(
        required=True,
        description="Default queue for all pipeline tasks.",
        example="default-queue-name",
    )
    maxRetry = fields.Integer(
        required=False,
        description="A number. Maximum number of retries before giving up. "
        "A value of None means task will retry forever. "
        "By default, this option is set to 3.",
        default=3,
        example=3,
    )

    maxTtl = fields.Integer(
        required=False,
        description="The soft time limit, in seconds, "
        "for this task. When not set the "
        "workers default is used.  The hard "
        "time limit will be derived from this"
        "field, by adding 10 seconds.",
        default=60,
        example=60,
    )

    retryBackoff = fields.Integer(
        required=False,
        description="A number. If this option is set , it is used as a delay"
        " factor. For example, if this option is set to 3, the"
        " first retry will delay 3 seconds, the second will delay"
        "  6 seconds, the third will delay 12 seconds, the fourth"
        " will delay 24 seconds, and so on. By default, this"
        " option is set to False, and autoretries will not"
        "  be delayed.",
        default=3,
        example=3,
    )

    retryJitter = fields.Boolean(
        required=False,
        description="A boolean. Jitter is used to introduce randomness into "
        "exponential backoff delays, to prevent all tasks in the "
        "queue from being executed simultaneously. If this option "
        "is set to True, the delay value calculated by "
        "retry_backoff is treated as a maximum, and the actual "
        "delay value will be a random number between zero and that "
        "maximum. By default, this option is set to True.",
        default=False,
        example=True,
    )

    retryBackoffMax = fields.Integer(
        required=False,
        description="A boolean. Jitter is used to introduce randomness into "
        "exponential backoff delays, to prevent all tasks in the "
        "queue from being executed simultaneously. If this option "
        "is set to True, the delay value calculated by "
        "retry_backoff is treated as a maximum, and the actual "
        "delay value will be a random number between zero and "
        "that maximum. By default, this option is set to True.",
        default=600,
        example=600,
    )

    groupName = fields.String(
        required=False,
        metadata={
            "description": "If two pipelines logically belong to a group the user can identify that two.  "
            "Imagine pipeline_a and pipeline_b both process data for images.  "
            'Logically we could give them a mutual group name of "Image Processing Pipelines"'
        },
    )


class TaskDefinitionsSchemaV1(ExcludeUnknownSchema):
    """Schema for a single task's configuration"""

    handler = fields.String(
        required=True,
        description="Path to the worker task definition",
        example="client.workers.my_task",
    )

    maxTtl = fields.Integer(
        required=False,
        description="Max TTL for a task in seconds.",
        default=60,
        example=60,
    )

    queue = fields.String(
        required=False,
        description="Non-default queue for this task.",
        example="custom-queue-name",
    )

    serverType = fields.String(
        required=False,
        validate=OneOf(
            ["xs", "s", "m", "l", "xl", "xxl", "xxxl", "cpu-xl"],
            error="Invalid serverType. Available options: 'xs', 's', 'm', 'l', 'xl', 'xxl', 'xxxl', 'cpu-xl'.",
        ),
    )


class TaskDefinitionsSchemaV2(ExcludeUnknownSchema):
    """Schema for a single task's configuration"""

    handlers = fields.List(
        fields.String(
            required=True,
            description="Path to the worker task definition",
            example="client.workers.my_task",
        )
    )
    maxTtl = fields.Integer(
        required=False,
        description="Max TTL for a task in seconds.",
        default=60,
        example=60,
    )

    queue = fields.String(
        required=False,
        description="Non-default queue for this task.",
        example="custom-queue-name",
    )

    serverType = fields.String(
        required=False,
        validate=OneOf(
            ["xs", "s", "m", "l", "xl", "xxl", "xxxl", "cpu-xl"],
            error="Invalid serverType. Available options: 'xs', 's', 'm', 'l', 'xl', 'xxl', 'xxxl', 'cpu-xl'.",
        ),
    )


class PipelineConfigSchemaBase(Schema):
    """Overall pipeline configuration schema"""

    metadata = fields.Nested(
        MetadataSchema,
        required=True,
        description="Metadata and configuration information for this pipeline.",
    )
    dagAdjacency = fields.Dict(
        keys=fields.String(
            required=True,
            description="Task's node name. *MUST* match key in taskDefinitions dict.",
            example="node_a",
        ),
        values=fields.List(
            fields.String(
                required=True,
                description="Task's node name. *Must* match key in taskDefinitions dict.",
            )
        ),
        required=True,
        description="The DAG Adjacency definition.",
    )


class PipelineConfigSchemaV1(PipelineConfigSchemaBase):
    """Overall pipeline configuration schema"""

    taskDefinitions = fields.Dict(
        keys=fields.String(
            required=True,
            description="Task's node name. *Must* match related key in dagAdjacency.",
            example="node_a",
        ),
        values=fields.Nested(
            TaskDefinitionsSchemaV1,
            required=True,
            description="Definition of each task in the pipeline.",
            example={"handler": "abc.task", "maxRetry": 1},
        ),
        required=True,
        description="Configuration for each node defined in DAG.",
    )


class PipelineConfigSchemaV2(PipelineConfigSchemaBase):
    """Overall pipeline configuration schema"""

    taskDefinitions = fields.Dict(
        keys=fields.String(
            required=True,
            description="Task's node name. *Must* match related key in dagAdjacency.",
            example="node_a",
        ),
        values=fields.Nested(
            TaskDefinitionsSchemaV2,
            required=True,
            description="Definition of each task in the pipeline.",
            example={"handler": "abc.task", "maxRetry": 1},
        ),
        required=True,
        description="Configuration for each node defined in DAG.",
    )

    settings = fields.Nested(
        PipelineSettingsSchema,
        required=False,
        metadata={
            "description": "Settings schema to validate the actual settings being passed through to the pipelines."
        },
    )


class BasePipelineSchema(ExcludeUnknownSchema):
    __schema_version__ = None

    name = fields.String(required=True, description="Pipeline name")
    description = fields.String(
        required=False,
        missing=None,
        description="Description of the pipeline.",
        example="A valuable pipeline.",
    )
    schemaVersion = fields.Integer(required=True)
    config = fields.Dict(required=True)

    @classmethod
    def get_by_version(cls, version):
        for subclass in cls.__subclasses__():
            if subclass.__schema_version__ == version:
                return subclass

        return None

    @classmethod
    def get_latest(cls):
        max_version = 0
        max_class = None
        for subclass in cls.__subclasses__():
            if subclass.__schema_version__ > max_version:
                max_version = max_version
                max_class = subclass

        return max_class

    @validates_schema
    def validate_pipeline(self, data, **kwargs):
        schema_version = data["schemaVersion"]
        PipelineSchema = BasePipelineSchema.get_by_version(schema_version)
        schema = PipelineSchema(exclude=["name", "description"])
        schema.load(data)


class PipelineSchemaV2(BasePipelineSchema):
    __schema_version__ = 2

    class Meta:
        unknown = EXCLUDE

    config = fields.Nested(
        PipelineConfigSchemaV2,
        required=True,
        description="Metadata and configuration information for this pipeline.",
    )

    def validate_pipeline(self, data, **kwargs):
        # We need to add this function to avoid infinite recursion since
        # the BasePipelineSchema class above uses the same method for
        # validation
        pass


class PipelineSchemaV1(BasePipelineSchema):
    __schema_version__ = 1

    class Meta:
        unknown = EXCLUDE

    config = fields.Nested(
        PipelineConfigSchemaV1,
        required=True,
        description="Metadata and configuration information for this pipeline.",
    )

    def validate_pipeline(self, data, **kwargs):
        # We need to add this function to avoid infinite recursion since
        # the BasePipelineSchema class above uses the same method for
        # validation
        pass


class PipelineConfigValidator(object):
    """Validate a pipeline configuration.

    This is stored as a string in the database under `PipelineConfig.config`
    in order to keep it easy for custom features to be added over time.
    This model represents the required / valid features so we can
    programmatically validate when saving, updating, viewing.
    """

    def __init__(
        self,
        config_dict: dict = None,
        config_yaml: str = None,
        schema_version: int = None,
    ):
        super().__init__()

        # We validate this as a dictionary. Turn into dictionary if provided
        # as yaml.
        if config_dict is not None:
            self.config = config_dict
        elif config_yaml is not None:
            self.config = yaml.safe_load(config_yaml)

        if schema_version is None:
            PipelineSchema = BasePipelineSchema.get_latest()
        else:
            PipelineSchema = BasePipelineSchema.get_by_version(schema_version)

        self.is_valid = False
        self.validated_config = {}
        self.validation_errors = {}
        try:
            # https://github.com/marshmallow-code/marshmallow/issues/377
            # See issue above when migrating to marshmallow 3
            pcs = PipelineSchema._declared_fields["config"].schema
            self.validated_config = pcs.load(self.config)
            self.is_valid = True
        except ValidationError as e:
            self.validation_errors = e.messages
            raise e
        except Exception as e:
            raise e
