""" Schemas for Schedule Configuration
"""
import re

# from celery.schedules import crontab_parser
from croniter import croniter
from marshmallow.exceptions import ValidationError
from marshmallow import Schema, fields, EXCLUDE, pre_load, validates_schema


class ExcludeUnknownSchema(Schema):
    """Remove unknown keys from loaded dictionary"""

    class Meta:
        unknown = EXCLUDE


class CrontabScheduleSchema(Schema):
    minute = fields.String(required=True)
    hour = fields.String(required=True)
    dayOfWeek = fields.String(required=True)
    dayOfMonth = fields.String(required=True)
    monthOfYear = fields.String(required=True)

    @validates_schema
    def validate_values(self, data, **kwargs):
        if (
            data["minute"] is None
            or data["hour"] is None
            or data["dayOfWeek"] is None
            or data["dayOfMonth"] is None
            or data["monthOfYear"] is None
        ):
            raise ValidationError("Empty crontab value")

        test_cron_expression = (
            f"{data['minute']} {data['hour']} {data['dayOfMonth']} "
            f"{data['monthOfYear']} {data['dayOfWeek']}"
        )

        if not croniter.is_valid(test_cron_expression):
            return ValidationError("Invalid crontab value")


class Schedule(fields.Dict):
    def _serialize(self, value, attr, obj, **kwargs):
        return value

    def _deserialize(self, value, attr, data, **kwargs):
        schema = CrontabScheduleSchema()
        return schema.load(value)


class ScheduleConfigSchemaV1(ExcludeUnknownSchema):
    """Definition of a single schedule entry"""

    queue = fields.String(
        required=True,
        description="Name of queue on which to place task.",
        example="my-default-queue",
    )
    task = fields.String(
        required=True,
        description="Path to task to invoke.",
        example="my_app.module.method",
    )

    schedule = Schedule(required=True)


class BaseScheduleSchema(ExcludeUnknownSchema):
    __schema_version__ = 0

    name = fields.String(
        required=True,
        description="Name of schedule entry.",
        example="My Scheduled Task",
    )
    schemaVersion = fields.Integer(required=True)
    config = fields.Dict(required=True)
    enabled = fields.Boolean(
        required=True, description="Whether entry is enabled.", example=True
    )

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
    def validate_scheduled_tasks(self, data, **kwargs):
        schema_version = data["schemaVersion"]
        TaskSchema = BaseScheduleSchema.get_by_version(schema_version)
        schema = TaskSchema()
        schema.load(data)


class ScheduleSchemaV1(BaseScheduleSchema):
    __schema_version__ = 1

    config = fields.Nested(
        ScheduleConfigSchemaV1,
        required=True,
        description="Configuration information for this schedule.",
    )

    def validate_scheduled_tasks(self, data, **kwargs):
        # We need to add this function to avoid infinite recursion since
        # the BaseScheduleSchema class above uses the same method for
        # validation
        pass
