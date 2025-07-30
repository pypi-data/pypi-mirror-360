from marshmallow import Schema, fields, validate, ValidationError, validates_schema, INCLUDE


class MissingSettingsException(Exception):
    pass


def create_pipeline_settings_schema(pipeline_settings_schema_data):
    """
    Dynamically create a schema to validate user data based on settings.

    Args:
        pipeline_settings_schema_data (dict): The settings schema data containing
                                              field configurations.

    Returns:
        Schema: A dynamically created schema class for validating user data.
    """

    # Dictionary to store dynamically generated fields
    schema_fields = {}

    for key, config in pipeline_settings_schema_data["properties"].items():
        data_type = config.get("dataType")
        input_type = config.get("inputType")
        field_args = {}

        # Map dataType to Marshmallow field type
        field_type = {
            "string": fields.String,
            "int": fields.Integer,
            "float": fields.Float,
            "boolean": fields.Boolean,
            "datetime": fields.DateTime,
            "array": fields.List,
            "object": fields.Nested,
        }.get(data_type)

        if not field_type:
            raise ValidationError(f"Unsupported dataType `{data_type}` for `{key}`.")

        # Handle array type
        if data_type == "array":
            element_type = config.get("elementType")
            if not element_type:
                raise ValidationError(f"`elementType` is required for array `{key}`.")
            field_args["cls_or_instance"] = {
                "string": fields.String,
                "int": fields.Integer,
                "float": fields.Float,
                "boolean": fields.Boolean,
                "datetime": fields.DateTime,
            }.get(element_type)
            if not field_args["cls_or_instance"]:
                raise ValidationError(
                    f"Unsupported elementType `{element_type}` for array `{key}`."
                )

        # Handle object type
        if data_type == "object":
            properties = config.get("properties")
            if not properties:
                raise ValidationError(f"`properties` is required for object `{key}`.")
            # Recursively create a schema for the nested object
            nested_schema = create_pipeline_settings_schema({"properties": properties})
            field_args["schema"] = nested_schema

        # Handle range validation for numeric fields
        if data_type in ["int", "float"]:
            if "minimum" in config or "maximum" in config:
                field_args["validate"] = validate.Range(
                    min=config.get("minimum"), max=config.get("maximum")
                )

        # Handle dropdown or radio input options
        if input_type in ["dropdown", "radio"] and "options" in config:
            allowed_values = [option["value"] for option in config["options"]]
            field_args["validate"] = validate.OneOf(allowed_values)

        # Mark the field as required if specified
        if key in pipeline_settings_schema_data.get("required", []):
            field_args["required"] = True

        # Create the field and add to the schema fields dictionary
        schema_fields[key] = field_type(**field_args)

    # Dynamically create a schema class with the generated fields
    DynamicPipelineSettingsSchema = type(
        "DynamicPipelineSettingsSchema", (Schema,), schema_fields
    )

    return DynamicPipelineSettingsSchema()


def create_pipeline_settings_schema(pipeline_settings_schema_data):
    """
    Dynamically create a schema to validate user data based on settings.

    Args:
        pipeline_settings_schema_data (dict): The settings schema data containing
                                              field configurations.

    Returns:
        Schema: A dynamically created schema class for validating user data.
    """

    # Dictionary to store dynamically generated fields
    schema_fields = {}

    for key, config in pipeline_settings_schema_data["properties"].items():
        data_type = config.get("dataType")
        input_type = config.get("inputType")
        field_args = {}

        # Map dataType to Marshmallow field type
        field_type = {
            "string": fields.String,
            "int": fields.Integer,
            "float": fields.Float,
            "boolean": fields.Boolean,
            "datetime": fields.DateTime,
            "array": fields.List,
            "object": fields.Nested,
        }.get(data_type)

        if not field_type:
            raise ValidationError(f"Unsupported dataType `{data_type}` for `{key}`.")

        # Handle array type
        if data_type == "array":
            element_type = config.get("elementType")
            if not element_type:
                raise ValidationError(f"`elementType` is required for array `{key}`.")
            field_args["cls_or_instance"] = {
                "string": fields.String,
                "int": fields.Integer,
                "float": fields.Float,
                "boolean": fields.Boolean,
                "datetime": fields.DateTime,
            }.get(element_type)
            if not field_args["cls_or_instance"]:
                raise ValidationError(
                    f"Unsupported elementType `{element_type}` for array `{key}`."
                )

        # Handle object type
        if data_type == "object":
            properties = config.get("properties")
            if not properties:
                raise ValidationError(f"`properties` is required for object `{key}`.")
            # Recursively create a schema for the nested object
            nested_schema = create_pipeline_settings_schema({"properties": properties})
            # Use the nested schema as the `nested` argument for fields.Nested
            field_type = fields.Nested(nested_schema)

        # Handle range validation for numeric fields
        if data_type in ["int", "float"]:
            if "minimum" in config or "maximum" in config:
                field_args["validate"] = validate.Range(
                    min=config.get("minimum"), max=config.get("maximum")
                )

        # Handle dropdown or radio input options
        if input_type in ["dropdown", "radio"] and "options" in config:
            allowed_values = [option["value"] for option in config["options"]]
            field_args["validate"] = validate.OneOf(allowed_values)

        # Mark the field as required if specified
        if key in pipeline_settings_schema_data.get("required", []):
            field_args["required"] = True
        else:
            field_args["required"] = False
            field_args["allow_none"] = True

        # Create the field and add to the schema fields dictionary
        if data_type == "object":
            schema_fields[key] = field_type
        else:
            schema_fields[key] = field_type(**field_args)

    schema_fields["Meta"] = type(
        "Meta", (), {"unknown": INCLUDE}
    )
    # Dynamically create a schema class with the generated fields
    DynamicPipelineSettingsSchema = type(
        "DynamicPipelineSettingsSchema", (Schema,), schema_fields
    )

    return DynamicPipelineSettingsSchema()


class OptionSchema(Schema):
    label = fields.String(
        required=True,
        metadata={"description": "The display label for the option"},
    )
    value = fields.Raw(
        required=True,
        metadata={"description": "The value corresponding to the option"},
    )


def validate_min_max(data):
    """Custom validator to ensure min/max match the dataType."""
    data_type = data.get("dataType")
    minimum = data.get("minimum")
    maximum = data.get("maximum")

    if data_type in ["int", "float"]:
        if minimum is not None and not isinstance(
            minimum, (int if data_type == "int" else float)
        ):
            raise ValidationError(f"`minimum` must be of type {data_type}.")
        if maximum is not None and not isinstance(
            maximum, (int if data_type == "int" else float)
        ):
            raise ValidationError(f"`maximum` must be of type {data_type}.")
        if minimum is not None and maximum is not None and minimum > maximum:
            raise ValidationError("`minimum` must be less than or equal to `maximum`.")
    elif data_type not in ["int", "float"] and (
        minimum is not None or maximum is not None
    ):
        raise ValidationError(
            "`minimum` and `maximum` are only valid for numeric types (`int`, `float`)."
        )


class SettingSchema(Schema):
    dataType = fields.String(
        required=True,
        validate=validate.OneOf(
            ["string", "int", "float", "boolean", "datetime", "array", "object"]
        ),
        metadata={"description": "The underlying data type of the setting"},
    )
    inputType = fields.String(
        required=True,
        validate=validate.OneOf(
            ["text", "dropdown", "radio", "checkbox", "searchable", "custom"]
        ),
        metadata={"description": "The type of input UI element"},
    )
    label = fields.String(
        required=True,
        metadata={"description": "The display label for the field"},
    )
    placeholder = fields.String(
        metadata={"description": "Placeholder text for text input fields"}
    )
    minimum = fields.Raw(
        metadata={"description": "Minimum value for numeric data types"}
    )
    maximum = fields.Raw(
        metadata={"description": "Maximum value for numeric data types"}
    )
    options = fields.List(
        fields.Nested(OptionSchema),
        metadata={"description": "Options for dropdown or radio input types"},
    )
    searchEndpoint = fields.String(
        metadata={"description": "Endpoint for searchable fields"}
    )
    component = fields.String(
        metadata={"description": "React component for custom input types"}
    )
    elementType = fields.String(
        metadata={"description": "Element type for array data types"}
    )
    properties = fields.Dict(
        keys=fields.String(),
        values=fields.Nested(lambda: SettingSchema),
        metadata={"description": "Properties for object data types"},
    )

    class Meta:
        ordered = True

    @validates_schema
    def validate_min_max(self, data, **kwargs):
        validate_min_max(data)

    @validates_schema
    def validate_options(self, data, **kwargs):
        """Ensure options are provided for dropdown or radio input types and validate value types."""
        input_type = data.get("inputType")
        options = data.get("options")
        data_type = data.get("dataType")

        if input_type in ["dropdown", "radio"]:
            if not options:
                raise ValidationError(
                    "`options` are required for dropdown and radio input types.",
                    field_name="options",
                )

            for option in options:
                value = option.get("value")
                if data_type == "int" and not isinstance(value, int):
                    raise ValidationError(
                        f"Option value `{value}` must be of type `int`."
                    )
                elif data_type == "float" and not isinstance(value, float):
                    raise ValidationError(
                        f"Option value `{value}` must be of type `float`."
                    )
                elif data_type == "boolean" and not isinstance(value, bool):
                    raise ValidationError(
                        f"Option value `{value}` must be of type `boolean`."
                    )
                elif data_type == "string" and not isinstance(value, str):
                    raise ValidationError(
                        f"Option value `{value}` must be of type `string`."
                    )
                elif data_type == "datetime" and not isinstance(
                    value, str
                ):  # Assuming ISO 8601 strings
                    raise ValidationError(
                        f"Option value `{value}` must be an ISO 8601 string for `datetime`."
                    )

    @validates_schema
    def validate_search_endpoint(self, data, **kwargs):
        """Ensure searchEndpoint is provided only for 'searchable' input types."""
        input_type = data.get("inputType")
        search_endpoint = data.get("searchEndpoint")

        if input_type == "searchable" and not search_endpoint:
            raise ValidationError(
                "`searchEndpoint` is required for `searchable` input types.",
                field_name="searchEndpoint",
            )
        elif input_type != "searchable" and search_endpoint:
            raise ValidationError(
                "`searchEndpoint` is not allowed for non-searchable input types.",
                field_name="searchEndpoint",
            )

    @validates_schema
    def validate_custom_component(self, data, **kwargs):
        """Ensure component is provided for custom input types."""
        input_type = data.get("inputType")
        component = data.get("component")

        if input_type == "custom" and not component:
            raise ValidationError(
                "`component` is required for `custom` input types.",
                field_name="component",
            )
        elif input_type != "custom" and component:
            raise ValidationError(
                "`component` is not allowed for non-custom input types.",
                field_name="component",
            )

    @validates_schema
    def validate_array_element_type(self, data, **kwargs):
        """Ensure elementType is provided for array data types."""
        data_type = data.get("dataType")
        element_type = data.get("elementType")

        if data_type == "array" and not element_type:
            raise ValidationError(
                "`elementType` is required for `array` data types.",
                field_name="elementType",
            )
        elif data_type != "array" and element_type:
            raise ValidationError(
                "`elementType` is not allowed for non-array data types.",
                field_name="elementType",
            )

    @validates_schema
    def validate_object_properties(self, data, **kwargs):
        """Ensure properties are provided for object data types."""
        data_type = data.get("dataType")
        properties = data.get("properties")

        if data_type == "object" and not properties:
            raise ValidationError(
                "`properties` is required for `object` data types.",
                field_name="properties",
            )
        elif data_type != "object" and properties:
            raise ValidationError(
                "`properties` is not allowed for non-object data types.",
                field_name="properties",
            )


class PipelineSettingsSchema(Schema):
    properties = fields.Dict(
        keys=fields.String(),
        values=fields.Nested(SettingSchema),
        required=True,
        metadata={"description": "A dictionary of settings with their configurations"},
    )
    required = fields.List(
        fields.String(), required=True, description="List of required settings"
    )
    scenarioSettings = fields.List(
        fields.String(),
        required=False,
        description="List of settings that can be overriding for different pipeline scenarios.",
    )

    @validates_schema
    def validate_scenario_settings(self, data, **kwargs):
        """Ensure scenarioSettings only contains keys defined in properties."""
        properties = data.get("properties", {})
        scenario_settings = data.get("scenarioSettings", [])

        invalid_settings = [
            setting for setting in scenario_settings if setting not in properties
        ]
        if invalid_settings:
            raise ValidationError(
                {
                    "scenario_settings": (
                        f"The following settings in scenarioSettings are not defined "
                        f"in properties: {', '.join(invalid_settings)}"
                    )
                }
            )


class PipelineScenarioSchema(Schema):
    settings = fields.Dict(
        required=True,
        metadata={
            "description": "Settings to be used for a given scenario.  Should match the pypeline.yaml settings schema"
        },
    )
    taskReplacements = fields.Dict(
        keys=fields.String(),
        values=fields.Integer(),
        required=False,
        metadata={
            "description": "Tasks that should be replaced in a given scenario.  "
            "The key corresponds to the task definition in the pypeline.yaml and the value corresponds "
            "to the index of the task handlers where 0 is the default and first task.  Eg: {'a': 1}.  In this case "
            "if we have a task definition 'a' with 3 handlers fn_1, fn_2, fn_3 respectively then the handler to run "
            "for 'a' is fn_2."
        },
    )

    taskReruns = fields.List(
        fields.String(),
        required=False,
        metadata={
            "description": "List of task definitions that need to be run again for a given scenario.  Here "
            "the scenario's pipeline settings will be injected in the task being run again which could be used to "
            "produce alternative calculations and or results."
        },
    )


class PipelineScenariosSchema(Schema):
    required = fields.List(
        fields.Nested(PipelineScenarioSchema),
        metadata={"description": "List of scenarios to run for a given pipeline"},
    )


# Example usage
if __name__ == "__main__":
    pipeline_settings = {"param1": "test", "param2": 1}

    yaml_data = {
        "properties": {
            "param1": {
                "dataType": "string",
                "inputType": "text",
                "label": "Parameter 1",
                "placeholder": "Enter a string",
            },
            "param2": {
                "dataType": "int",
                "inputType": "text",
                "label": "Parameter 2",
                "minimum": -1,
                "maximum": 1,
            },
            "param3": {
                "dataType": "boolean",
                "inputType": "checkbox",
                "label": "Enable Feature",
            },
            "param4": {
                "dataType": "float",
                "inputType": "dropdown",
                "label": "Choose an Option",
                "minimum": 0.5,
                "maximum": 2.5,
                "options": [
                    {"label": "Option 1", "value": 0.5},
                    {"label": "Option 2", "value": 1.5},
                ],
            },
            "param5": {
                "dataType": "int",
                "inputType": "radio",
                "label": "Select a Mode",
                "options": [
                    {"label": "Mode A", "value": 1},
                    {"label": "Mode B", "value": 2},
                ],
            },
            "param6": {
                "dataType": "string",
                "inputType": "searchable",
                "label": "Select Pipeline",
                "searchEndpoint": "/api/pipelines",
            },
            "param7": {
                "dataType": "array",
                "inputType": "text",
                "label": "Array of Integers",
                "elementType": "int",
            },
            "param8": {
                "dataType": "object",
                "inputType": "custom",
                "label": "Custom Object",
                "component": "CustomObjectComponent",
                "properties": {
                    "subParam1": {
                        "dataType": "string",
                        "inputType": "text",
                        "label": "Sub Parameter 1",
                    },
                    "subParam2": {
                        "dataType": "int",
                        "inputType": "text",
                        "label": "Sub Parameter 2",
                    },
                },
            },
        },
        "required": ["param1", "param2", "param4"],
    }

    schema = PipelineSettingsSchema()
    errors = schema.validate(yaml_data)
    if errors:
        print("Validation errors:", errors)
    else:
        print("Validation successful!")
