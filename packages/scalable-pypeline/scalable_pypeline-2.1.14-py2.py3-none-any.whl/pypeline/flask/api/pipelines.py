""" Pipeline APIs
"""

import importlib.metadata
import logging
from http import HTTPStatus

from flask import jsonify
from flask.views import MethodView
from flask_smorest import Blueprint
from marshmallow import Schema, fields
from marshmallow.exceptions import ValidationError
from webargs.flaskparser import abort
from packaging import version
from pypeline.pipelines.composition.parallel_pipeline_composition import PipelineResult
from pypeline.constants import API_DOC_RESPONSES, API_DOC_PARAMS, API_PATH_V1
from pypeline.flask.decorators import require_accesskey
from pypeline.pipeline_config_schema import BasePipelineSchema, PipelineSchemaV1
from pypeline.pipeline_settings_schema import (
    MissingSettingsException,
    PipelineScenarioSchema,
)
from pypeline.pipelines.factory import dag_generator
from pypeline.utils.config_utils import retrieve_latest_pipeline_config
from pypeline.utils.schema_utils import get_clean_validation_messages

logger = logging.getLogger(__name__)
bp = Blueprint("pipelines", __name__, url_prefix=API_PATH_V1 + "/pipelines")


try:
    flask_smorest_version = importlib.metadata.version("flask-smorest")
    flask_smorest_version_parsed = version.parse(flask_smorest_version)
except importlib.metadata.PackageNotFoundError:
    flask_smorest_version_parsed = None


def get_response_decorator(bp, status_code, *args, **kwargs):
    if flask_smorest_version is None:
        # Handle the case where flask-smorest is not installed
        raise ImportError("flask-smorest is not installed.")
    elif flask_smorest_version_parsed < version.parse("0.29"):
        # Adjust arguments for older versions if needed
        return bp.response(*args, **kwargs)
    else:
        # Adjust arguments for newer versions if needed
        return bp.response(status_code, *args, **kwargs)


class InvokePipelineSchema(Schema):
    """Incoming schema for invoking a pipeline"""

    chain_payload = fields.Raw(
        description="Payload contains whatever arguments the pipeline expects "
        "to be passed to each node in the graph.",
        example={"document_id": "123", "send_alert": True},
        required=False,
    )
    scenarios = fields.List(
        fields.Nested(PipelineScenarioSchema),
        metadata={"description": "List of scenarios to run for a given pipeline"},
        required=False,
    )


class InvokePipelineResponseSchema(Schema):
    execution_id = fields.String()
    pipeline_id = fields.String()
    status = fields.String()


class GetPipelineResultResponseSchema(Schema):
    execution_id = fields.String()
    result = fields.Raw()
    result_ttl = fields.Integer()
    results = fields.Raw()
    status = fields.String()
    status_message = fields.String()


@bp.route("/")
class Pipelines(MethodView):
    """Operations against all pipelines."""

    @require_accesskey
    @bp.doc(
        responses=API_DOC_RESPONSES,
        parameters=[API_DOC_PARAMS["accesskey"]],
        tags=["Pipelines"],
    )
    def get(self):
        """Retrieve list of available pipelines."""
        pipeline_config_api_resp = retrieve_latest_pipeline_config()

        if pipeline_config_api_resp is None:
            abort(404)

        try:
            pipelines = []
            for p in pipeline_config_api_resp:
                PipelineSchema = BasePipelineSchema.get_by_version(p["schemaVersion"])
                pipeline_config = PipelineSchema().load(p)
                pipelines.append(pipeline_config)
        except ValidationError as e:
            msg = f"Invalid pipeline configuration: {e}"
            return jsonify({"message": msg}), 202

        return jsonify(pipelines)


@bp.route("/<string:pipeline_id>")
class PipelineInfo(MethodView):
    """Operations against a single pipeline"""

    @require_accesskey
    @bp.doc(
        responses=API_DOC_RESPONSES,
        parameters=[
            API_DOC_PARAMS["accesskey"],
            {
                "in": "path",
                "name": "pipeline_id",
                "description": "pipeline_id for which to retrieve metrics.",
                "type": "string",
                "example": "my_pipeline",
                "required": True,
            },
        ],
        tags=["Pipelines"],
    )
    def get(self, pipeline_id: str):
        """Retrieve details about a specific pipeline."""
        pipeline_config_api_resp = retrieve_latest_pipeline_config(
            pipeline_id=pipeline_id
        )

        if pipeline_config_api_resp is None:
            abort(404)

        try:
            pipeline_config = PipelineSchemaV1().load(pipeline_config_api_resp)
        except ValidationError as e:
            msg = f"Invalid pipeline configuration: {e}"
            return jsonify({"message": msg}), 202

        return jsonify(pipeline_config)


@bp.route("/invoke/<string:pipeline_id>")
class PipelineInvoke(MethodView):
    """Operations involed with pipeline invocation"""

    @require_accesskey
    @bp.doc(
        responses=API_DOC_RESPONSES,
        parameters=[
            API_DOC_PARAMS["accesskey"],
            {
                "in": "path",
                "name": "pipeline_id",
                "description": "pipeline_id for which to retrieve metrics.",
                "type": "string",
                "example": "my_pipeline",
                "required": True,
            },
        ],
        tags=["Pipelines"],
    )
    @bp.arguments(InvokePipelineSchema)
    @get_response_decorator(bp, "200", InvokePipelineResponseSchema)
    def post(self, payload: dict, pipeline_id: str):
        """Invoke a pipeline by it's ID; optionally provide pipeline arguments."""
        pipeline_config = retrieve_latest_pipeline_config(pipeline_id=pipeline_id)

        if pipeline_config is None:
            return abort(404)

        retval = {"pipeline_id": pipeline_id, "status": "starting"}
        try:
            chain_payload = payload.get("chain_payload", {})
            scenarios = payload.get("scenarios", [])
            if pipeline_config["schemaVersion"] == 1:
                pipeline = dag_generator(
                    pipeline_id=pipeline_id,
                    event=chain_payload,
                )
            elif pipeline_config["schemaVersion"] == 2:
                pipeline = dag_generator(
                    pipeline_id=pipeline_id,
                    scenarios=scenarios,
                )
                retval["scenarios"] = pipeline.scenarios
            pipeline.run()
            pipeline_result = PipelineResult(pipeline.execution_id)
            pipeline_result.create_result_entry(pipeline.to_json())
            retval["execution_id"] = pipeline.execution_id
        except MissingSettingsException:
            abort(
                HTTPStatus.BAD_REQUEST,
                message="Missing required settings in the request.",
            )
        except ValidationError as ve:
            abort(
                HTTPStatus.BAD_REQUEST,
                message=get_clean_validation_messages(ve),
            )
        except Exception as e:
            msg = "Failed to invoke pipeline ... {}".format(pipeline_id)
            logger.error(msg)
            logger.exception(f"{e}")
            abort(500, message=msg)

        return jsonify(retval)


results_responses = API_DOC_RESPONSES.copy()
results_responses[202] = {
    "code": 202,
    "description": "Pipeline is still running. Try again later.",
}
results_responses[204] = {
    "code": 204,
    "description": "The execution results have expired. Re-run pipeline.",
}


@bp.route("/results/<string:execution_id>")
class PipelineResults(MethodView):
    """Operations with respect to pipeline results"""

    @require_accesskey
    @bp.doc(
        responses=results_responses,
        parameters=[
            API_DOC_PARAMS["accesskey"],
            {
                "in": "path",
                "name": "execution_id",
                "description": "execution_id for which to retrieve results",
                "type": "string",
                "example": "4c595cca-9bf1-4150-8c34-6b43faf276c8",
                "required": True,
            },
        ],
        tags=["Pipelines"],
    )
    @get_response_decorator(bp, "200", GetPipelineResultResponseSchema)
    def get(self, execution_id: str):
        """Retrieve results of a pipeline's execution based on execution_id

        NOTE: Cached results expire after a time window so are not available
        forever.
        """
        try:
            pr = PipelineResult(execution_id)
            pr.load()
            retval = {"execution_id": execution_id, "status": pr.status}
            if pr.status == "unavailable":
                retval["status_message"] = "Results expired. Re-run pipeline."
                return retval, 200

            if pr.status == "pending":
                retval["status_message"] = "Results pending. Check again soon."
                return retval, 202

            else:
                retval["status_message"] = "Results available."
                retval["results"] = pr.get_results()
                return retval, 200

        except Exception as e:
            msg = "Failed to retrieve results for execution id: {}".format(execution_id)
            logger.error(msg)
            logger.exception(f"{e}")
            abort(500, message=msg)
